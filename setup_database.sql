-- Script para crear la base de datos MySQL para el Core API
-- Ejecutar este script en MySQL antes de iniciar el Core API

CREATE DATABASE IF NOT EXISTS unified_messaging 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Crear usuario específico para la aplicación (opcional)
-- CREATE USER 'unified_user'@'localhost' IDENTIFIED BY 'tu_password_seguro';
-- GRANT ALL PRIVILEGES ON unified_messaging.* TO 'unified_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Usar la base de datos
USE unified_messaging;

-- Las tablas se crearán automáticamente cuando inicies el Core API
-- gracias a SQLAlchemy y el método init_db()

-- Para verificar que todo está funcionando:
-- SHOW TABLES;
