-- MySQL Schema for Ramadan Character Styling App
-- Database: ramadan_app (create this database first)

CREATE DATABASE IF NOT EXISTS ramadan_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ramadan_app;

CREATE TABLE IF NOT EXISTS generations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prompt TEXT NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
