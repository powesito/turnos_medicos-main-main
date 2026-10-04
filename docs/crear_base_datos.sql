-- Ejecutar en MySQL como administrador (root)
CREATE DATABASE IF NOT EXISTS turnos_medicos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario con contraseña (local y remoto)
CREATE USER IF NOT EXISTS 'turnos_user'@'localhost' IDENTIFIED BY 'Turnos2026';
CREATE USER IF NOT EXISTS 'turnos_user'@'%' IDENTIFIED BY 'Turnos2026';

-- Conceder privilegios solo sobre la base de datos del proyecto
GRANT ALL PRIVILEGES ON turnos_medicos.* TO 'turnos_user'@'localhost';
GRANT ALL PRIVILEGES ON turnos_medicos.* TO 'turnos_user'@'%';

-- Aplicar los cambios de privilegios
FLUSH PRIVILEGES;
