-- Crear BD Proyecto_IOF
CREATE DATABASE proyecto_iof;

-- Crear tabla docentes con IDs autoincrementables
CREATE TABLE docentes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(255),
  experiencia INT,
  universidades VARCHAR(255),
  nivel_academico VARCHAR(255)
);

-- Crear tabla habilidades con IDs autoincrementables
CREATE TABLE habilidades (
  id INT PRIMARY KEY AUTO_INCREMENT,
  habilidad VARCHAR(255)
);

-- Crear tabla docente_habilidades (relación many-to-many)
CREATE TABLE docente_habilidades (
  id INT PRIMARY KEY AUTO_INCREMENT,
  id_docente INT,
  id_habilidad INT,
  FOREIGN KEY (id_docente) REFERENCES docentes(id),
  FOREIGN KEY (id_habilidad) REFERENCES habilidades(id)
);