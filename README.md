# AWS Glue + Athena

---

## Qué hay en este repo

```
aws_glue/
├── .gitignore
├── data/
│   ├── generar_datos_sinteticos.py # Genera datos: S3 CSV, RDS CSV/SQL, MongoDB JSON
│   ├── s3/empleados.csv
│   ├── rds/proyectos_empleados.csv
│   ├── rds/proyectos_empleados.sql
│   └── mongodb/evaluaciones.json
├── glue/etl_empleados_analitico.py # Script del Job ETL en Glue
├── athena/ddl_empleados_final.sql  # DDL para tabla final en Athena
└── docs/INFORME_ETL_EMPLEADOS.md   # Informe base para exportar a PDF
```

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

---

## Paso 1 (AWS). Crear bucket y estructura en S3

1) En S3 creamos un bucket: `empresa-analitica-datos`
2) Estructura de carpetas:
- `raw/empleados/`
- `analitica/empleados_final/`

![Estructura de carpetas](capturasReadme/Captura%20de%20pantalla%202026-03-18%20a%20las%201.03.11.png)

3) Subimos `data/s3/empleados.csv` a:
- `s3://empresa-analitica-datos/raw/empleados/empleados.csv`

![Bucket S3 y CSV empleados](capturasReadme/Captura%20de%20pantalla%202026-03-16%20a%20las%2011.59.34.png)

---

## Paso 2 (AWS). Crear la base de datos en Glue Data Catalog

Glue → **Data Catalog → Databases → Add database**  
- Nombre: **`empresa_db`**

![Base de datos empresa_db en Glue](capturasReadme/Captura%20de%20pantalla%202026-03-16%20a%20las%2012.00.58.png)

---

## Paso 3 (AWS). Crawler para S3 (tabla `empleados`)

Glue:
1) **Crawlers → Create crawler**
2) Data source: S3 → `s3://empresa-analitica-datos/raw/empleados/`
3) Output: Database `empresa_db`
4) Ejecutamos el crawler
5) Verificamos la tabla (ej. `empleados`) con columnas:
- `nombre`, `email`, `departamento`, `puesto`, `sueldo`, `antigüedad`

![Crawler S3](capturasReadme/Captura%20de%20pantalla%202026-03-16%20a%20las%2012.15.09.png)

![Tabla empleados en Data Catalog](capturasReadme/Captura%20de%20pantalla%202026-03-16%20a%20las%2012.17.21.png)

---

## Paso 4 (AWS). RDS/MariaDB: tabla + carga + catálogo

### 4A) Creamos una base de datos RDS (MariaDB)
- Motor recomendado: **MariaDB** en RDS.
- Debemos poder conectarnos desde nuestra máquina con **DBeaver** (o cliente SQL equivalente).

![Creación RDS](capturasReadme/Captura%20de%20pantalla%202026-03-18%20a%20las%201.17.56.png)

### 4B) Crear tabla y cargar datos con DBeaver
Tabla requerida (en la base de datos `database-mariadb`):
- `email`, `proyecto`, `horas_trabajadas`, `rol`

**Pasos en DBeaver:**

1) **Crear conexión**
   - Tipo de conexión: **MariaDB**.
   - Host: endpoint del RDS (ej. `mi-rds.mariadb.xxxxx.us-east-1.rds.amazonaws.com`).
   - Puerto: `3306`.
   - Database: `database-mariadb`.
   - Usuario/contraseña: los que configuramos al crear la instancia.

   ![Conexión DBeaver a MariaDB](capturasReadme/Captura%20de%20pantalla%202026-03-16%20a%20las%2022.53.58.png)

2) **Crear la tabla**
   - En DBeaver, abrimos un **SQL Editor** sobre la DB `database-mariadb`.
   - Ejecutamos:
     ```sql
     CREATE TABLE IF NOT EXISTS proyectos_empleados (
       email VARCHAR(255) NOT NULL,
       proyecto VARCHAR(100) NOT NULL,
       horas_trabajadas INT NOT NULL,
       rol VARCHAR(100) NOT NULL
     );
     ```

![Tabla proyectos_empleados creada](capturasReadme/Captura%20de%20pantalla%202026-03-16%20a%20las%2023.02.05.png)

3) **Importar el CSV generado**
   - Botón derecho sobre la tabla `proyectos_empleados` → **Import Data**.
   - Fuente: **CSV** → seleccionamos el archivo `data/rds/proyectos_empleados.csv` de este repositorio.
   - Mapeamos columnas:
     - `email` → `email`
     - `proyecto` → `proyecto`
     - `horas_trabajadas` → `horas_trabajadas`
     - `rol` → `rol`
   - Siguiente → Finish. DBeaver insertará todas las filas.
   - Comprobamos con:
     ```sql
     SELECT * FROM databasemariadb.proyectos_empleados LIMIT 10;
     ```

![Datos cargados en proyectos_empleados](capturasReadme/Captura%20de%20pantalla%202026-03-18%20a%20las%201.28.31.png)

---

## Paso 5 (AWS). MongoDB Atlas: importar + conexión en Glue

### 5A) En Atlas: DB/colección e import JSON
1) Creamos el cluster `awsCluster`
2) Importamos `data/mongodb/evaluaciones.json`

![Configuración inicial](capturasReadme/Captura%20de%20pantalla%202026-03-18%20a%20las%201.55.41.png)

![Proceso de importación](capturasReadme/Captura%20de%20pantalla%202026-03-18%20a%20las%202.03.56.png)

![Verificación final](capturasReadme/Captura%20de%20pantalla%202026-03-18%20a%20las%202.04.55.png)

Campos esperados:
- `email`, `rendimiento`, `feedback_ultimo_mes`, `fecha_ultima_evaluacion`

### 5B) En Glue: conexión MongoDB
1) Glue → **Connections** → MongoDB
2) Usa el connection string de Atlas
3) Asegura red (allowlist IP / peering, según tu caso)

---

## Paso 6 (AWS). Crear el ETL Job en Glue

1) Glue Studio → **Jobs → Create job**

# Proceso de configuración de red para AWS Glue con JDBC

### Creamos etl-empleados

![Creación de Job ETL](<capturasReadme/Captura de pantalla 2026-03-18 a las 2.13.15.png>)

Para que AWS Glue funcione dentro de una VPC personalizada necesita comunicarse con las APIs públicas (como S3). Como nuestra subred es privada, creamos un NAT Gateway en una subred pública para servir de puente.

![Creación de NAT Gateway](<capturasReadme/Captura de pantalla 2026-03-18 a las 2.25.58.png>)

Ahora le decimos a la subred de Glue que use el NAT:

![Actualización de Tabla de Rutas](<capturasReadme/Captura de pantalla 2026-03-18 a las 2.28.43.png>)

Y modificamos el grupo de seguridad para que permita todo el tráfico TCP. Esto soluciona el error `InvalidInputException` al permitir que los componentes de Glue se comuniquen entre sí:

![Configuración de Regla de Security Group](<capturasReadme/Captura de pantalla 2026-03-18 a las 2.41.05.png>)

Finalmente probamos la conexión:

![Test de Conexión Exitoso](<capturasReadme/Captura de pantalla 2026-03-18 a las 2.42.41.png>)

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

