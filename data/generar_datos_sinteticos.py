#!/usr/bin/env python3
"""
Generador de datos sintéticos para el repositorio analítico de empleados.
Genera: CSV para S3, CSV/SQL para RDS, JSON para MongoDB Atlas.
Los emails se mantienen consistentes entre fuentes para permitir el JOIN en el ETL.
"""

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuración
NUM_EMPLEADOS = 80
OUTPUT_DIR = Path(__file__).resolve().parent

DEPARTAMENTOS = ["Ventas", "IT", "RRHH", "Marketing", "Finanzas", "Operaciones"]
PUESTOS = {
    "Ventas": ["Comercial", "Jefe de Ventas", "Account Manager"],
    "IT": ["Desarrollador", "DevOps", "Arquitecto de Software"],
    "RRHH": ["Técnico RRHH", "Responsable de Formación"],
    "Marketing": ["Content Manager", "Analista Digital", "Community Manager"],
    "Finanzas": ["Contable", "Analista Financiero", "Controller"],
    "Operaciones": ["Coordinador", "Jefe de Proyecto", "Analista de Procesos"],
}
SUELDO_BASE = (22000, 65000)
ANTIGUEDAD_ANOS = (0, 15)
PROYECTOS = ["Alpha", "Beta", "Gamma", "Delta", "Omega", "Nexus"]
ROLES = ["Desarrollador", "Analista", "Líder técnico", "Consultor", "Soporte"]
RENDIMIENTO_VALORES = ["Bajo", "Medio", "Alto", "Muy Alto"]
FEEDBACK_OPCIONES = ["Necesita mejorar", "Cumple expectativas", "Supera expectativas", "Excelente"]


def generar_emails(n: int) -> list[str]:
    """Genera n emails únicos sintéticos."""
    base = "empleado"
    dominio = "empresa-analitica.com"
    return [f"{base}{i:04d}@{dominio}" for i in range(1, n + 1)]


def generar_nombres(n: int) -> list[str]:
    """Genera n nombres sintéticos (nombre apellido)."""
    nombres = ["Ana", "Luis", "María", "Carlos", "Elena", "Pablo", "Laura", "Miguel", "Sara", "Jorge",
               "Carmen", "David", "Isabel", "Antonio", "Lucía", "Francisco", "Paula", "Javier", "Marta", "Daniel"]
    apellidos = ["García", "Martínez", "López", "Sánchez", "Pérez", "González", "Rodríguez", "Fernández", "Díaz", "Moreno"]
    return [f"{random.choice(nombres)} {random.choice(apellidos)}" for _ in range(n)]


def generar_csv_s3(emails: list, nombres: list) -> Path:
    """Genera empleados.csv para S3: nombre, email, departamento, puesto, sueldo, antigüedad."""
    path = OUTPUT_DIR / "s3" / "empleados.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (email, nombre) in enumerate(zip(emails, nombres)):
        dept = random.choice(DEPARTAMENTOS)
        puesto = random.choice(PUESTOS[dept])
        sueldo = random.randint(*SUELDO_BASE)
        antiguedad = random.randint(*ANTIGUEDAD_ANOS)
        rows.append({
            "nombre": nombre,
            "email": email,
            "departamento": dept,
            "puesto": puesto,
            "sueldo": sueldo,
            "antigüedad": antiguedad,
        })
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre", "email", "departamento", "puesto", "sueldo", "antigüedad"])
        w.writeheader()
        w.writerows(rows)
    # Añadir algunos duplicados y valores nulos/vacíos para probar limpieza (opcional)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre", "email", "departamento", "puesto", "sueldo", "antigüedad"])
        w.writerow({"nombre": "Duplicado Test", "email": emails[0], "departamento": "IT", "puesto": "Desarrollador", "sueldo": 35000, "antigüedad": 2})
        w.writerow({"nombre": "", "email": "incompleto@empresa.com", "departamento": "Ventas", "puesto": "", "sueldo": 0, "antigüedad": 0})
    print(f"Generado: {path}")
    return path


def generar_rds(emails: list) -> tuple[Path, Path]:
    """Genera datos para RDS: email, proyecto, horas_trabajadas, rol. Devuelve CSV y SQL."""
    path_csv = OUTPUT_DIR / "rds" / "proyectos_empleados.csv"
    path_sql = OUTPUT_DIR / "rds" / "proyectos_empleados.sql"
    path_csv.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for email in emails:
        # Varios proyectos por empleado o uno; para simplificar 1 registro por empleado
        rows.append({
            "email": email,
            "proyecto": random.choice(PROYECTOS),
            "horas_trabajadas": random.randint(80, 180),
            "rol": random.choice(ROLES),
        })
    with open(path_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["email", "proyecto", "horas_trabajadas", "rol"])
        w.writeheader()
        w.writerows(rows)
    # SQL para crear tabla e insertar (PostgreSQL/MySQL compatible)
    with open(path_sql, "w", encoding="utf-8") as f:
        f.write("-- Crear tabla en RDS (ejemplo PostgreSQL)\n")
        f.write("""
CREATE TABLE IF NOT EXISTS proyectos_empleados (
    email VARCHAR(255),
    proyecto VARCHAR(100),
    horas_trabajadas INT,
    rol VARCHAR(100)
);
\n""")
        f.write("-- Inserts (ejemplo)\n")
        for r in rows[:10]:
            f.write(f"INSERT INTO proyectos_empleados VALUES ('{r['email']}', '{r['proyecto']}', {r['horas_trabajadas']}, '{r['rol']}');\n")
        f.write("-- ... (usar CSV para carga masiva o repetir INSERT para todos)\n")
    print(f"Generado: {path_csv}, {path_sql}")
    return path_csv, path_sql


def generar_mongodb(emails: list) -> Path:
    """Genera documentos para MongoDB: email, rendimiento, feedback_ultimo_mes, fecha_ultima_evaluacion."""
    path = OUTPUT_DIR / "mongodb" / "evaluaciones.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    docs = []
    for email in emails:
        fecha = (datetime.now() - timedelta(days=random.randint(5, 90))).strftime("%Y-%m-%d")
        docs.append({
            "email": email,
            "rendimiento": random.choice(RENDIMIENTO_VALORES),
            "feedback_ultimo_mes": random.choice(FEEDBACK_OPCIONES),
            "fecha_ultima_evaluacion": fecha,
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"Generado: {path}")
    return path


def main():
    random.seed(42)
    emails = generar_emails(NUM_EMPLEADOS)
    nombres = generar_nombres(NUM_EMPLEADOS)
    generar_csv_s3(emails, nombres)
    generar_rds(emails)
    generar_mongodb(emails)
    print("Datos sintéticos generados correctamente.")


if __name__ == "__main__":
    main()
