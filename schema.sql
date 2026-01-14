CREATE DATABASE ScrapingWong;
GO

USE ScrapingWong;
GO

/*TABLA PRINCIPAL*/
CREATE TABLE productos_wong (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    url VARCHAR(MAX) NOT NULL,
    fecha_extraccion DATETIME NOT NULL DEFAULT GETDATE()
);
GO

/*CONTROL DE DUPLICADOS (mismo producto, mismo día) */
CREATE UNIQUE INDEX UX_producto_fecha
ON productos_wong (nombre, CAST(fecha_extraccion AS DATE));
GO

/*VISTA: HISTÓRICO + VARIACIÓN */
CREATE VIEW vw_historico_precios AS
SELECT
    id,
    nombre,
    categoria,
    precio,
    fecha_extraccion,
    LAG(precio) OVER (
        PARTITION BY nombre
        ORDER BY fecha_extraccion
    ) AS precio_anterior,
    ROUND(
        (
            (precio - LAG(precio) OVER (PARTITION BY nombre ORDER BY fecha_extraccion))
            / NULLIF(LAG(precio) OVER (PARTITION BY nombre ORDER BY fecha_extraccion), 0)
        ) * 100,
        2
    ) AS variacion_porcentual,
    url
FROM productos_wong;
GO
