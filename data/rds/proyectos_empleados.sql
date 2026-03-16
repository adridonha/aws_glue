-- Crear tabla en RDS (ejemplo PostgreSQL)

CREATE TABLE IF NOT EXISTS proyectos_empleados (
    email VARCHAR(255),
    proyecto VARCHAR(100),
    horas_trabajadas INT,
    rol VARCHAR(100)
);

-- Inserts (ejemplo)
INSERT INTO proyectos_empleados VALUES ('empleado0001@empresa-analitica.com', 'Gamma', 106, 'Líder técnico');
INSERT INTO proyectos_empleados VALUES ('empleado0002@empresa-analitica.com', 'Beta', 113, 'Consultor');
INSERT INTO proyectos_empleados VALUES ('empleado0003@empresa-analitica.com', 'Beta', 165, 'Líder técnico');
INSERT INTO proyectos_empleados VALUES ('empleado0004@empresa-analitica.com', 'Delta', 120, 'Desarrollador');
INSERT INTO proyectos_empleados VALUES ('empleado0005@empresa-analitica.com', 'Alpha', 138, 'Soporte');
INSERT INTO proyectos_empleados VALUES ('empleado0006@empresa-analitica.com', 'Omega', 92, 'Desarrollador');
INSERT INTO proyectos_empleados VALUES ('empleado0007@empresa-analitica.com', 'Omega', 107, 'Soporte');
INSERT INTO proyectos_empleados VALUES ('empleado0008@empresa-analitica.com', 'Gamma', 96, 'Líder técnico');
INSERT INTO proyectos_empleados VALUES ('empleado0009@empresa-analitica.com', 'Alpha', 111, 'Líder técnico');
INSERT INTO proyectos_empleados VALUES ('empleado0010@empresa-analitica.com', 'Gamma', 100, 'Consultor');
-- ... (usar CSV para carga masiva o repetir INSERT para todos)
