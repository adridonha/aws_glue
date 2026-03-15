# Repositorio analítico de empleados – ETL con AWS Glue

Pipeline ETL que integra datos de empleados desde **S3 (CSV)**, **RDS** y **MongoDB Atlas**, con AWS Glue y consultas en Amazon Athena.

## Estructura del proyecto

```
aws_glue/
├── data/
│   ├── generar_datos_sinteticos.py   # Genera CSV (S3), RDS y MongoDB
│   ├── s3/
│   │   └── empleados.csv
│   ├── rds/
│   │   ├── proyectos_empleados.csv
│   │   └── proyectos_empleados.sql
│   └── mongodb/
│       └── evaluaciones.json
├── glue/
│   └── etl_empleados_analitico.py    # Script del Glue ETL Job
├── docs/
│   └── INFORME_ETL_EMPLEADOS.md      # Informe para entregar (exportar a PDF)
├── athena/
│   └── ddl_empleados_final.sql       # DDL para tabla en Athena
├── requirements.txt
└── README.md
```

## Uso rápido

### 1. Generar datos sintéticos

```bash
pip install -r requirements.txt
python data/generar_datos_sinteticos.py
```

Se generan:
- `data/s3/empleados.csv` → subir a `s3://TU_BUCKET/raw/empleados/`
- `data/rds/` → cargar en la tabla RDS `proyectos_empleados`
- `data/mongodb/evaluaciones.json` → importar en la colección MongoDB

### 2. En AWS

1. **S3:** Crear bucket, subir `empleados.csv` a `raw/empleados/`.
2. **Glue:** Crear base de datos `empresa_db`, Crawlers para S3 y RDS, conexión MongoDB, Job con el script en `glue/etl_empleados_analitico.py` y los parámetros indicados en el informe.
3. **Athena:** Crear tabla sobre la ruta de salida del Job (ver `athena/ddl_empleados_final.sql`) o ejecutar un Crawler sobre esa ruta.

### 3. Documento PDF

- Abrir `docs/INFORME_ETL_EMPLEADOS.md` en un editor o en [Mermaid Live](https://mermaid.live) para el diagrama.
- Añadir las capturas de pantalla en los lugares indicados.
- Exportar a PDF (p. ej. desde VS Code con extensión Markdown PDF, o desde Word/LibreOffice pegando el contenido).

## Parámetros del Job Glue

| Parámetro | Ejemplo |
|-----------|---------|
| `s3_database` | empresa_db |
| `s3_table_empleados` | empleados |
| `rds_database` | empresa_db |
| `rds_table` | proyectos_empleados |
| `mongodb_connection` | nombre de la conexión Glue a MongoDB |
| `mongodb_database` | empresa |
| `mongodb_collection` | evaluaciones |
| `output_path` | s3://TU_BUCKET/analitica/empleados_final/ |
