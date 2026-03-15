-- Crear tabla en Athena sobre la salida del ETL (Parquet particionado por departamento)
-- Sustituir 'TU_BUCKET' por el nombre de tu bucket.
-- Base de datos: empresa_db (creada en Glue)

CREATE EXTERNAL TABLE IF NOT EXISTS empresa_db.empleados_final (
  nombre STRING,
  email STRING,
  puesto STRING,
  sueldo INT,
  antigüedad INT,
  proyecto STRING,
  horas_trabajadas INT,
  rol STRING,
  rendimiento STRING,
  feedback_ultimo_mes STRING,
  fecha_ultima_evaluacion STRING,
  nivel_rendimiento STRING,
  categoria_sueldo STRING
)
PARTITIONED BY (departamento STRING)
STORED AS PARQUET
LOCATION 's3://TU_BUCKET/analitica/empleados_final/'
TBLPROPERTIES ('has_encrypted_data'='false');

-- Si las particiones se crean con el Job, ejecutar después del primer run:
-- MSCK REPAIR TABLE empresa_db.empleados_final;

-- Consultas de ejemplo (ver también docs/INFORME_ETL_EMPLEADOS.md)
-- SELECT departamento, COUNT(*) FROM empresa_db.empleados_final GROUP BY departamento;
-- SELECT * FROM empresa_db.empleados_final WHERE nivel_rendimiento = 'Muy Alto' LIMIT 10;
