# Guía paso a paso (entrega) – AWS Glue + Athena

Esta guía es “lo que tienes que hacer tú” para completar la práctica: **crear las fuentes**, **catalogarlas con Glue**, **ejecutar el Job ETL**, y **consultar el resultado con Athena**, dejando todo listo para el **PDF** con capturas.

---

## Qué hay en este repo (y qué vas a usar)

```
aws_glue/
├── .env_plantilla                 # Plantilla .env (NO subir al repo)
├── .gitignore
├── data/
│   ├── generar_datos_sinteticos.py # Genera datos: S3 CSV, RDS CSV/SQL, MongoDB JSON
│   ├── s3/empleados.csv
│   ├── rds/proyectos_empleados.csv
│   ├── rds/proyectos_empleados.sql
│   └── mongodb/evaluaciones.json
├── glue/etl_empleados_analitico.py # Script del Job ETL en Glue
├── athena/ddl_empleados_final.sql  # DDL para tabla final en Athena
└── docs/INFORME_ETL_EMPLEADOS.md   # Informe base para exportar a PDF (con placeholders)
```

---

## Antes de empezar (credenciales y región)

- **AWS**: Glue no usa `.env`. El Job corre con **IAM Role**.  
  El `.env` te sirve solo para cosas locales (AWS CLI, scripts, etc.).

1) Copia plantilla y rellena:

```bash
cp .env_plantilla .env
```

2) Edita `.env` y completa:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION` (ej. `eu-west-1`)

---

## Paso 0 (local). Generar datos sintéticos

```bash
pip install -r requirements.txt
python data/generar_datos_sinteticos.py
```

Se generan 3 fuentes con la misma clave `email` para el join:
- **S3**: `data/s3/empleados.csv`
- **RDS**: `data/rds/proyectos_empleados.csv` (y `proyectos_empleados.sql` de apoyo)
- **MongoDB**: `data/mongodb/evaluaciones.json`

Para el PDF:
- Pega 3–5 filas de ejemplo de cada fuente, o captura.

---

## Paso 1 (AWS). Crear bucket y estructura en S3

1) En S3 crea un bucket (ejemplo): `empresa-analitica-datos-<tu_nombre>`
2) Estructura de carpetas:
- `raw/empleados/`
- `analitica/empleados_final/`
3) Sube `data/s3/empleados.csv` a:
- `s3://TU_BUCKET/raw/empleados/empleados.csv`

Para el PDF:
- Captura del bucket mostrando el CSV en esa ruta.

---

## Paso 1.1 (AWS). Crear IAM Role para Glue

Antes de usar Crawlers o Jobs, crea un rol de servicio para Glue:

1) IAM → **Roles → Create role**
2) **Trusted entity**:
   - AWS service → elige **Glue**
3) **Permissions** (mínimo para la práctica):
   - `AWSGlueServiceRole`
   - `AmazonS3FullAccess` (o una política limitada a tu bucket)
4) Nombre del rol: por ejemplo `AWSGlueServiceRole-empresa-analitica`

Lo usarás:
- En los **Crawlers** (campo *IAM role*).
- En el **Job** de Glue (campo *IAM Role*).

> **Nota (entorno Vocareum / labs)**: si tu usuario **no puede crear roles** y ya existen roles como `labrole`, `vocareum` o `voclabs`, usa **`labrole`** tanto en los Crawlers como en los Jobs de Glue. Ese rol suele venir preconfigurado con los permisos necesarios para los laboratorios.

Para el PDF:
- Captura de la pantalla de IAM donde se ve el rol creado.

---

## Paso 2 (AWS). Crear la base de datos en Glue Data Catalog

Glue → **Data Catalog → Databases → Add database**  
- Nombre: **`empresa_db`**

Para el PDF:
- Captura donde se vea `empresa_db`.

---

## Paso 3 (AWS). Crawler para S3 (tabla `empleados`)

Glue:
1) **Crawlers → Create crawler**
2) Data source: S3 → `s3://TU_BUCKET/raw/empleados/`
3) Output: Database `empresa_db`
4) Ejecuta el crawler
5) Verifica la tabla (ej. `empleados`) con columnas:
- `nombre`, `email`, `departamento`, `puesto`, `sueldo`, `antigüedad`

Para el PDF:
- Captura del crawler (run “Succeeded”).
- Captura de la tabla en Data Catalog con columnas.

---

## Paso 4 (AWS). RDS/MariaDB: tabla + carga + catálogo

### 4A) Crear/usar una instancia RDS (MariaDB)
- Motor recomendado para la práctica: **MariaDB** en RDS.
- Debes poder conectarte desde tu máquina con **DBeaver** (o cliente SQL equivalente).

### 4B) Crear tabla y cargar datos con DBeaver
Tabla requerida (en la base de datos `empresa`):
- `email`, `proyecto`, `horas_trabajadas`, `rol`

**Pasos en DBeaver:**

1) **Crear conexión**
   - Tipo de conexión: **MariaDB**.
   - Host: endpoint del RDS (ej. `mi-rds.mariadb.xxxxx.us-east-1.rds.amazonaws.com`).
   - Puerto: `3306`.
   - Database: `empresa` (o la que hayas definido).
   - Usuario/contraseña: los que configuraste al crear la instancia.

2) **Crear la tabla**
   - En DBeaver, abre un **SQL Editor** sobre la DB `empresa`.
   - Ejecuta:
     ```sql
     CREATE TABLE IF NOT EXISTS proyectos_empleados (
       email VARCHAR(255) NOT NULL,
       proyecto VARCHAR(100) NOT NULL,
       horas_trabajadas INT NOT NULL,
       rol VARCHAR(100) NOT NULL
     );
     ```

3) **Importar el CSV generado**
   - Botón derecho sobre la tabla `proyectos_empleados` → **Import Data**.
   - Fuente: **CSV** → selecciona el archivo `data/rds/proyectos_empleados.csv` de este repositorio.
   - Mapea columnas:
     - `email` → `email`
     - `proyecto` → `proyecto`
     - `horas_trabajadas` → `horas_trabajadas`
     - `rol` → `rol`
   - Siguiente → Finish. DBeaver insertará todas las filas.
   - Comprueba con:
     ```sql
     SELECT * FROM proyectos_empleados LIMIT 10;
     ```

Para el PDF:
- Captura de DBeaver con la conexión a RDS/MariaDB.
- Captura de la tabla `proyectos_empleados` con algunas filas cargadas.

### 4C) Conexión JDBC + Crawler en Glue
1) Glue → **Connections** → JDBC (RDS)
2) (Si está en VPC) configura VPC/Subnet/SG para que Glue llegue al RDS
3) Crawler usando esa conexión, output a `empresa_db`
4) Ejecuta y verifica la tabla (ej. `proyectos_empleados`) con columnas correctas

Para el PDF:
- Captura de la Connection JDBC.
- Captura del crawler + tabla catalogada.

---

## Paso 5 (AWS). MongoDB Atlas: importar + conexión en Glue

### 5A) En Atlas: DB/colección e import JSON
1) Crea DB (ej. `empresa`) y colección (ej. `evaluaciones`)
2) Importa `data/mongodb/evaluaciones.json`

Campos esperados:
- `email`, `rendimiento`, `feedback_ultimo_mes`, `fecha_ultima_evaluacion`

### 5B) En Glue: conexión MongoDB
1) Glue → **Connections** → MongoDB
2) Usa el connection string de Atlas
3) Asegura red (allowlist IP / peering, según tu caso)

Para el PDF:
- Captura de la conexión MongoDB en Glue.
- (Opcional) Si haces crawler, captura del crawler + tabla.

---

## Paso 6 (AWS). Crear el ETL Job en Glue (Spark)

1) Glue Studio → **Jobs → Create job**
2) Tipo: Spark (script)
3) Pega el script: `glue/etl_empleados_analitico.py`
4) IAM Role con permisos:
   - S3 (leer `raw/`, escribir `analitica/`)
   - Glue Data Catalog
   - RDS (red VPC/SG si aplica)
   - MongoDB (vía la conexión)
5) **Job parameters**:

- `--s3_database` = `empresa_db`
- `--s3_table_empleados` = `empleados`
- `--rds_database` = `empresa_db`
- `--rds_table` = `proyectos_empleados`
- `--mongodb_connection` = `NOMBRE_CONEXION_MONGO`
- `--mongodb_database` = `empresa`
- `--mongodb_collection` = `evaluaciones`
- `--output_path` = `s3://TU_BUCKET/analitica/empleados_final/`

6) Ejecuta el Job y valida estado **Succeeded**

Para el PDF:
- Captura del Job (script + parámetros).
- Captura del run “Succeeded”.

---

## Paso 7–9 (ETL). Qué hace el script (para justificar en la memoria)

En `glue/etl_empleados_analitico.py`:
- **Limpieza**:
  - `dropDuplicates([\"email\"])`
  - elimina `email` nulo/vacío
  - outliers: sueldo 15k–120k; antigüedad 0–30; horas 0–250
- **Filtro**: sueldo > 0
- **Join**: INNER de las 3 fuentes por `email`
- **Nuevas columnas**:
  - `nivel_rendimiento` (= `rendimiento`)
  - `categoria_sueldo` (Bajo/Medio/Alto)
- **Salida**: Parquet en S3 particionado por `departamento`

Para el PDF:
- Captura del fragmento del código con limpieza+filtro+join+columnas derivadas.

---

## Paso 10 (AWS). Athena: tabla final + particiones + consultas

### Opción A (directo con DDL)
1) Athena → Query editor
2) Ejecuta `athena/ddl_empleados_final.sql` (cambia `TU_BUCKET`)
3) Carga particiones:

```sql
MSCK REPAIR TABLE empresa_db.empleados_final;
```

### Opción B (Crawler sobre la salida)
1) Crawler apuntando a `s3://TU_BUCKET/analitica/empleados_final/`
2) Output a `empresa_db`
3) Ejecuta y consulta en Athena

Para el PDF:
- Captura de la tabla y de 2–4 consultas con resultados.

---

## Checklist de capturas (rúbrica)

- S3 bucket + `raw/empleados/empleados.csv`
- Glue Database `empresa_db`
- Crawler S3 + tabla `empleados` con columnas
- Connection JDBC RDS + crawler + tabla `proyectos_empleados`
- Connection MongoDB (y crawler/tabla si aplica)
- Glue Job (script+parámetros) + Run “Succeeded”
- S3 salida `analitica/empleados_final/` con carpetas `departamento=...`
- Athena: tabla + `MSCK REPAIR` + resultados de consultas

---

## PDF (memoria)

Usa `docs/INFORME_ETL_EMPLEADOS.md`:
- Inserta las capturas en los placeholders
- Exporta a PDF (VS Code “Markdown PDF” o copiar a Word/LibreOffice)
