CREATE DATABASE ScrapingWong;
GO

USE ScrapingWong;
GO

CREATE TABLE productos_wong (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    url VARCHAR(MAX) NOT NULL,
    fecha_extraccion DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- Índice único para evitar duplicados del mismo producto el mismo día
CREATE UNIQUE INDEX UX_producto_fecha
ON productos_wong (nombre, CAST(fecha_extraccion AS DATE));
GO
