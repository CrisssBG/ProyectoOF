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

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    usuario VARCHAR(255),
    password VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS docente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNIQUE, -- Clave externa que referencia al usuario correspondiente
    nombre VARCHAR(255),
    apellido VARCHAR(255),
    cedula VARCHAR(255) UNIQUE,
    celular VARCHAR(15),    
    genero ENUM('Masculino', 'Femenino', 'Otro') NOT NULL,
    nvl_estudio VARCHAR(255),
    carrera VARCHAR(255),
    imagen_p BLOB,
    disponibilidad_c INT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

ALTER TABLE docente
MODIFY imagen_p VARCHAR(255);

-- CREATE TABLE IF NOT EXISTS habilidades_t_b (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     id_docente INT UNIQUE, -- Clave externa que referencia al docente correspondiente
--     programacion INT, -- Habilidades Tecnicas
--     desarrollo_software INT,
--     analisis_datos INT,
--     gestion_base_datos INT,
--     diseño_interfaz INT,
--     redes INT,
--     sistemas_operativos INT,
--     desarrollo_frontend INT,
--     desarrollo_backend INT,
--     seguridad_informatica INT,
--     gestion_servidores_nube INT,
--     resolucion_problemas INT,
--     trabajo_equipo INT,
--     desarrollo_web INT,
--     diseño_grafico INT,
--     diseño_3d INT,
--     diseño_branding INT,
--     animacion_grafica INT,
--     comunicacion_efectiva INT, -- Habilidades Blandas
--     trabajo_equipo_soft INT,
--     resolucion_problemas_soft INT,
--     adaptabilidad INT,
--     empatia INT,
--     liderazgo INT,
--     gestion_tiempo INT,
--     resiliencia INT,
--     pensamiento_critico INT,
--     creatividad INT,
--     FOREIGN KEY (id_docente) REFERENCES docente(id)
-- );




-- /****************************************************/


-- CREATE TABLE IF NOT EXISTS habilidades_t_b (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     id_usuario INT UNIQUE, -- Clave externa que referencia al docente correspondiente
--     programacion INT, -- Habilidades Tecnicas
--     desarrollo_software INT,
--     analisis_datos INT,
--     gestion_base_datos INT,
--     diseño_interfaz INT,
--     redes INT,
--     sistemas_operativos INT,
--     desarrollo_frontend INT,
--     desarrollo_backend INT,
--     seguridad_informatica INT,
--     gestion_servidores_nube INT,
--     resolucion_problemas INT,
--     trabajo_equipo INT,
--     desarrollo_web INT,
--     diseño_grafico INT,
--     diseño_3d INT,
--     diseño_branding INT,
--     animacion_grafica INT,
--     comunicacion_efectiva INT, -- Habilidades Blandas
--     trabajo_equipo_soft INT,
--     resolucion_problemas_soft INT,
--     adaptabilidad INT,
--     empatia INT,
--     liderazgo INT,
--     gestion_tiempo INT,
--     resiliencia INT,
--     pensamiento_critico INT,
--     creatividad INT,
--     FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
-- );




CREATE TABLE IF NOT EXISTS habilidades_t_b (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_docente INT UNIQUE, -- Clave externa que referencia al docente correspondiente
    programacion INT, -- Habilidades Tecnicas
    desarrollo_software INT,
    analisis_datos INT,
    gestion_base_datos INT,
    disenio_interfaz INT,
    redes INT,
    sistemas_operativos INT,
    desarrollo_frontend INT,
    desarrollo_backend INT,
    seguridad_informatica INT,
    gestion_servidores_nube INT,
    animacion_grafica INT,
    comunicacion_asertiva INT, -- Habilidades Blandas
    trabajo_equipo INT,
    resolucion_problemas INT,
    adaptabilidad INT,
    empatia INT,
    tolerancia_estres INT,
    creatividad INT,
    liderazgo INT,
    gestion_tiempo INT,
    resiliencia INT,
    pensamiento_critico INT,
    manejo_inteligencia_emocional INT,
    FOREIGN KEY (id_docente) REFERENCES docente(id)
);

CREATE TABLE IF NOT EXISTS resultados_difusos_h_t (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_docente INT UNIQUE, -- Clave externa que referencia al docente correspondiente
    resultado_difuso FLOAT, -- Desarrollo y Arquitectura de Software
    resultado_difuso_g FLOAT, -- Gestión y Análisis de Datos
    resultado_difuso_d FLOAT, -- Diseño de Interfaz y Multimedia
    resultado_difuso_s FLOAT, -- Seguridad y Cloud Computing
    resultado_difuso_i FLOAT, -- Infraestructura y Comunicaciones
    FOREIGN KEY (id_docente) REFERENCES docente(id)
);

CREATE TABLE IF NOT EXISTS resultados_difusos_h_t (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_habilidades_t_b INT UNIQUE, -- Clave externa que referencia al docente correspondiente
    resultado_difuso FLOAT, -- Desarrollo y Arquitectura de Software
    resultado_difuso_g FLOAT, -- Gestión y Análisis de Datos
    resultado_difuso_d FLOAT, -- Diseño de Interfaz y Multimedia
    resultado_difuso_s FLOAT, -- Seguridad y Cloud Computing
    resultado_difuso_i FLOAT, -- Infraestructura y Comunicaciones
    FOREIGN KEY (id_habilidades_t_b) REFERENCES habilidades_t_b(id)
);


CREATE TABLE IF NOT EXISTS intereses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_docente INT UNIQUE, -- Clave externa que referencia al docente correspondiente
    tipos_intereses VARCHAR(255),
    otros VARCHAR(255),
    FOREIGN KEY (id_docente) REFERENCES docente(id)
);



 INSERT INTO historial_busquedas (usuario_id, fecha, desarrollo_arquitectura, gestion_analisis_datos, disenio_interfaz_multimedia, seguridad_cloud_computing, infraestructura_comunicaciones)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s)
            """


        