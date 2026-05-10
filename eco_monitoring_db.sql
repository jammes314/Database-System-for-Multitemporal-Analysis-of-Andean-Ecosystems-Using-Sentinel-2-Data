CREATE TABLE `áreas_acha` (
  `id` integer PRIMARY KEY,
  `nombre` varchar(255),
  `geometria_poligonal` text,
  `prioridad_muestreo` integer
);

CREATE TABLE `puntos_muestreo` (
  `id` integer PRIMARY KEY,
  `area_id` integer,
  `latitud` decimal(10,8) NOT NULL,
  `longitud` decimal(11,8) NOT NULL,
  `altitud` decimal(8,2),
  `pixel_id_hash` varchar(255)
);

CREATE TABLE `catalogo_biomas` (
  `id` integer PRIMARY KEY,
  `nombre_clase` varchar(255),
  `descripcion_ecologica` text
);

CREATE TABLE `catalogo_imagenes` (
  `id_producto` varchar(255) PRIMARY KEY,
  `fecha_adquisicion` timestamp NOT NULL,
  `porcentaje_nubes` decimal(5,2),
  `sensor` varchar(255)
);

CREATE TABLE `especies` (
  `id` integer PRIMARY KEY,
  `nombre_cientifico` varchar(255),
  `estado_uicn` varchar(255)
);

CREATE TABLE `observaciones_espectrales` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `punto_id` integer,
  `imagen_id` varchar(255),
  `b2_blue` integer,
  `b3_green` integer,
  `b4_red` integer,
  `b8_nir` integer,
  `b11_swir1` integer,
  `b12_swir2` integer,
  `ndvi` decimal(10,6),
  `ndmi` decimal(10,6),
  `bsi` decimal(10,6),
  `clase_id` integer,
  `es_verdad_campo` boolean,
  `confianza_prediccion` decimal(5,2)
);

CREATE TABLE `registros_monitoreo` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `especie_id` integer,
  `punto_id` integer,
  `fecha_observacion` timestamp,
  `cantidad` integer,
  `notas_habitat` text
);

ALTER TABLE `puntos_muestreo` ADD FOREIGN KEY (`area_id`) REFERENCES `áreas_acha` (`id`);

ALTER TABLE `observaciones_espectrales` ADD FOREIGN KEY (`punto_id`) REFERENCES `puntos_muestreo` (`id`);

ALTER TABLE `observaciones_espectrales` ADD FOREIGN KEY (`imagen_id`) REFERENCES `catalogo_imagenes` (`id_producto`);

ALTER TABLE `observaciones_espectrales` ADD FOREIGN KEY (`clase_id`) REFERENCES `catalogo_biomas` (`id`);

ALTER TABLE `registros_monitoreo` ADD FOREIGN KEY (`especie_id`) REFERENCES `especies` (`id`);

ALTER TABLE `registros_monitoreo` ADD FOREIGN KEY (`punto_id`) REFERENCES `puntos_muestreo` (`id`);
