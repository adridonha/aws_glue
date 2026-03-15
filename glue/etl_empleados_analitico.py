"""
AWS Glue ETL Job: Repositorio analítico de empleados.
Integra: S3 (CSV), RDS (proyectos), MongoDB Atlas (evaluaciones).
Limpieza: duplicados, nulos, outliers. Filtro: sueldo > 0. Join por email.
Salida: S3 particionado por departamento, consultable con Athena.
"""

import sys
from pyspark import SparkContext
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

# Parámetros del job: configurar en Glue Studio > Job > "Job details" > "Job parameters"
args = getResolvedOptions(sys.argv, [
    "JOB_NAME",
    "s3_database",           # ej: empresa_db
    "s3_table_empleados",    # ej: empleados
    "rds_database",          # ej: empresa_db
    "rds_table",             # ej: proyectos_empleados
    "mongodb_connection",    # nombre de la conexión Glue a MongoDB Atlas
    "mongodb_database",
    "mongodb_collection",
    "output_path",           # s3://bucket/analitica/empleados_final/
])

glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# ---------- 1. LEER FUENTES ----------
# S3: tabla catalogada por el Crawler (empleados)
dyf_s3 = glueContext.create_dynamic_frame.from_catalog(
    database=args["s3_database"],
    table_name=args["s3_table_empleados"],
)

# RDS: tabla proyectos_empleados vía conexión JDBC
dyf_rds = glueContext.create_dynamic_frame.from_catalog(
    database=args["rds_database"],
    table_name=args["rds_table"],
)

# MongoDB Atlas: colección de evaluaciones
dyf_mongo = glueContext.create_dynamic_frame.from_options(
    connection_type="mongodb",
    connection_name=args["mongodb_connection"],
    database=args["mongodb_database"],
    collection=args["mongodb_collection"],
)

# Convertir a DataFrame para usar Spark SQL y transformaciones
df_s3 = dyf_s3.toDF()
df_rds = dyf_rds.toDF()
df_mongo = dyf_mongo.toDF()

# ---------- 2. LIMPIEZA DE DATOS ----------
# 2.1 Eliminar duplicados (por email en cada fuente; después del join por email)
df_s3 = df_s3.dropDuplicates(["email"])
df_rds = df_rds.dropDuplicates(["email"])
df_mongo = df_mongo.dropDuplicates(["email"])

# 2.2 Eliminar registros con email nulo o vacío
df_s3 = df_s3.filter(F.col("email").isNotNull() & (F.trim(F.col("email")) != ""))
df_rds = df_rds.filter(F.col("email").isNotNull() & (F.trim(F.col("email")) != ""))
df_mongo = df_mongo.filter(F.col("email").isNotNull() & (F.trim(F.col("email")) != ""))

# 2.3 Normalización de columnas: asegurar tipos y nombres consistentes
# S3: sueldo numérico, antigüedad numérica (por si el crawler detecta string)
for c in ["sueldo", "antigüedad"]:
    if c in df_s3.columns:
        df_s3 = df_s3.withColumn(c, F.col(c).cast("int"))

# Outliers: sueldo en rango razonable (ej. 15.000 - 120.000), horas_trabajadas (0-250)
df_s3 = df_s3.filter(
    (F.col("sueldo").between(15000, 120000)) &
    (F.col("antigüedad").between(0, 30))
)
if "horas_trabajadas" in df_rds.columns:
    df_rds = df_rds.withColumn("horas_trabajadas", F.col("horas_trabajadas").cast("int"))
    df_rds = df_rds.filter(F.col("horas_trabajadas").between(0, 250))

# ---------- 3. FILTRADO DE EMPLEADOS ----------
# Empleados activos: sueldo > 0 (y opcionalmente con datos mínimos)
df_s3 = df_s3.filter(F.col("sueldo") > 0)

# ---------- 4. JOIN ENTRE LAS TRES FUENTES ----------
# Renombrar columnas que se repiten para evitar ambigüedad
df_rds = df_rds.withColumnRenamed("email", "email_rds")
df_mongo = df_mongo.withColumnRenamed("email", "email_mongo")

df_join = df_s3.alias("s3") \
    .join(df_rds.alias("rds"), F.col("s3.email") == F.col("rds.email_rds"), "inner") \
    .join(df_mongo.alias("m"), F.col("s3.email") == F.col("m.email_mongo"), "inner")

# Seleccionar columnas finales y eliminar duplicados de join
df_final = df_join.select(
    F.col("s3.nombre"),
    F.col("s3.email"),
    F.col("s3.departamento"),
    F.col("s3.puesto"),
    F.col("s3.sueldo"),
    F.col("s3.antigüedad"),
    F.col("rds.proyecto"),
    F.col("rds.horas_trabajadas"),
    F.col("rds.rol"),
    F.col("m.rendimiento"),
    F.col("m.feedback_ultimo_mes"),
    F.col("m.fecha_ultima_evaluacion"),
).distinct()

# ---------- 5. COLUMNAS DERIVADAS ----------
# nivel_rendimiento: se mantiene el campo rendimiento como nivel_rendimiento (o mapeo numérico)
df_final = df_final.withColumn("nivel_rendimiento", F.col("rendimiento"))

# categoria_sueldo: Bajo (< 30000), Medio (30000-45000), Alto (> 45000)
df_final = df_final.withColumn(
    "categoria_sueldo",
    F.when(F.col("sueldo") < 30000, "Bajo")
    .when(F.col("sueldo") <= 45000, "Medio")
    .otherwise("Alto")
)

# ---------- 6. GUARDAR EN S3 PARTICIONADO POR DEPARTAMENTO ----------
# Eliminar columna duplicada rendimiento si se desea solo nivel_rendimiento (opcional)
# df_final = df_final.drop("rendimiento")

output_path = args["output_path"]
df_final.write \
    .mode("overwrite") \
    .format("parquet") \
    .partitionBy("departamento") \
    .save(output_path)

# Opcional: registrar la tabla en el catálogo para Athena (vía Crawler posterior o Glue API)
# Aquí solo escribimos; el usuario puede ejecutar un Crawler sobre output_path para que Athena lo vea.

job.commit()
