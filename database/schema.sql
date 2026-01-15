-- =============================
-- WONGPRIME - BASE DE DATOS COMPLETA
-- =============================

-- Crear base de datos
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ScrapingWong')
BEGIN
    CREATE DATABASE ScrapingWong;
END
GO

USE ScrapingWong;
GO

-- =============================
-- TABLA: TIENDAS
-- =============================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'tiendas')
BEGIN
    CREATE TABLE tiendas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL UNIQUE,
        url_base VARCHAR(MAX),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    
    -- Insertar tiendas iniciales
    INSERT INTO tiendas (nombre, url_base) VALUES 
        ('Wong', 'https://www.wong.pe'),
        ('Metro', 'https://www.metro.pe'),
        ('Plaza Vea', 'https://www.plazavea.com.pe');
END
GO

-- =============================
-- TABLA: CATEGORIAS
-- =============================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'categorias')
BEGIN
    CREATE TABLE categorias (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        url_path VARCHAR(MAX),
        descripcion VARCHAR(255),
        activo BIT DEFAULT 1
    );
    
    -- Insertar categorías iniciales
    INSERT INTO categorias (nombre, url_path) VALUES 
        ('Salud', 'higiene-salud-y-belleza/salud'),
        ('Cuidado Personal', 'higiene-salud-y-belleza/cuidado-personal'),
        ('Alimentos Orgánicos', 'bebes-y-ninos/alimentos-organicos');
END
GO

-- =============================
-- TABLA: MARCAS
-- =============================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'marcas')
BEGIN
    CREATE TABLE marcas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL UNIQUE
    );
END
GO

-- =============================
-- TABLA: PRODUCTOS
-- =============================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'productos')
BEGIN
    CREATE TABLE productos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(500) NOT NULL,
        descripcion VARCHAR(MAX),
        url_imagen VARCHAR(MAX),
        marca_id INT,
        categoria_id INT,
        sku VARCHAR(100),
        fecha_creacion DATETIME DEFAULT GETDATE(),
        ultima_actualizacion DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (marca_id) REFERENCES marcas(id),
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    );
    
    -- Índice para búsqueda por nombre
    CREATE INDEX IX_productos_nombre ON productos(nombre);
END
GO

-- =============================
-- TABLA: PRECIOS
-- =============================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'precios')
BEGIN
    CREATE TABLE precios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        producto_id INT NOT NULL,
        tienda_id INT NOT NULL,
        precio DECIMAL(10,2) NOT NULL,
        precio_anterior DECIMAL(10,2),
        stock INT,
        rating DECIMAL(3,2),
        num_reviews INT,
        descuento DECIMAL(5,2),
        url VARCHAR(MAX),
        fecha DATETIME NOT NULL DEFAULT GETDATE(),
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
        FOREIGN KEY (tienda_id) REFERENCES tiendas(id)
    );
    
    -- Índice compuesto para consultas rápidas
    CREATE INDEX IX_precios_producto_tienda_fecha ON precios(producto_id, tienda_id, fecha DESC);
    
    -- Índice único para evitar duplicados en mismo día
    CREATE UNIQUE INDEX UX_precio_producto_tienda_fecha 
    ON precios (producto_id, tienda_id, CAST(fecha AS DATE));
END
GO

-- =============================
-- TABLA: ALERTAS
-- =============================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'alertas')
BEGIN
    CREATE TABLE alertas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        producto_id INT NOT NULL,
        email VARCHAR(255) NOT NULL,
        precio_objetivo DECIMAL(10,2) NOT NULL,
        activa BIT DEFAULT 1,
        notificado BIT DEFAULT 0,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_notificacion DATETIME,
        FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
    );
    
    CREATE INDEX IX_alertas_activa ON alertas(activa) WHERE activa = 1;
END
GO

-- =============================
-- TABLA: LOGS DE SCRAPING
-- =============================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'scraping_logs')
BEGIN
    CREATE TABLE scraping_logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        tienda_id INT NOT NULL,
        categoria_id INT,
        productos_encontrados INT,
        productos_nuevos INT,
        productos_actualizados INT,
        errores INT DEFAULT 0,
        tiempo_ejecucion INT, -- en segundos
        mensaje VARCHAR(MAX),
        fecha DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (tienda_id) REFERENCES tiendas(id),
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    );
END
GO

-- =============================
-- VISTAS
-- =============================

-- Vista: Precios actuales (último precio de cada producto por tienda)
IF OBJECT_ID('vw_precios_actuales', 'V') IS NOT NULL
    DROP VIEW vw_precios_actuales;
GO

CREATE VIEW vw_precios_actuales AS
SELECT 
    p.id as producto_id,
    p.nombre as producto_nombre,
    p.descripcion,
    p.url_imagen,
    m.nombre as marca,
    c.nombre as categoria,
    t.nombre as tienda,
    pr.precio,
    pr.precio_anterior,
    pr.stock,
    pr.rating,
    pr.descuento,
    pr.url,
    pr.fecha as fecha_actualizacion
FROM productos p
LEFT JOIN marcas m ON p.marca_id = m.id
LEFT JOIN categorias c ON p.categoria_id = c.id
INNER JOIN precios pr ON p.id = pr.producto_id
INNER JOIN tiendas t ON pr.tienda_id = t.id
WHERE pr.fecha = (
    SELECT MAX(fecha) 
    FROM precios 
    WHERE producto_id = p.id AND tienda_id = pr.tienda_id
);
GO

-- Vista: Comparación de precios entre tiendas
IF OBJECT_ID('vw_comparacion_tiendas', 'V') IS NOT NULL
    DROP VIEW vw_comparacion_tiendas;
GO

CREATE VIEW vw_comparacion_tiendas AS
SELECT 
    p.id as producto_id,
    p.nombre as producto,
    m.nombre as marca,
    c.nombre as categoria,
    MAX(CASE WHEN t.nombre = 'Wong' THEN pr.precio END) as precio_wong,
    MAX(CASE WHEN t.nombre = 'Metro' THEN pr.precio END) as precio_metro,
    MAX(CASE WHEN t.nombre = 'Plaza Vea' THEN pr.precio END) as precio_plaza_vea,
    (SELECT MIN(precio) FROM precios WHERE producto_id = p.id 
     AND fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id)) as precio_minimo,
    (SELECT MAX(precio) FROM precios WHERE producto_id = p.id 
     AND fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id)) as precio_maximo
FROM productos p
LEFT JOIN marcas m ON p.marca_id = m.id
LEFT JOIN categorias c ON p.categoria_id = c.id
LEFT JOIN precios pr ON p.id = pr.producto_id
LEFT JOIN tiendas t ON pr.tienda_id = t.id
WHERE pr.fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id AND tienda_id = pr.tienda_id)
GROUP BY p.id, p.nombre, m.nombre, c.nombre;
GO

-- Vista: Histórico de precios con variación
IF OBJECT_ID('vw_historico_precios', 'V') IS NOT NULL
    DROP VIEW vw_historico_precios;
GO

CREATE VIEW vw_historico_precios AS
SELECT
    pr.id,
    p.nombre as producto,
    t.nombre as tienda,
    c.nombre as categoria,
    pr.precio,
    pr.fecha,
    LAG(pr.precio) OVER (
        PARTITION BY pr.producto_id, pr.tienda_id
        ORDER BY pr.fecha
    ) AS precio_anterior_registro,
    ROUND(
        (
            (pr.precio - LAG(pr.precio) OVER (PARTITION BY pr.producto_id, pr.tienda_id ORDER BY pr.fecha))
            / NULLIF(LAG(pr.precio) OVER (PARTITION BY pr.producto_id, pr.tienda_id ORDER BY pr.fecha), 0)
        ) * 100,
        2
    ) AS variacion_porcentual,
    pr.url
FROM precios pr
INNER JOIN productos p ON pr.producto_id = p.id
INNER JOIN tiendas t ON pr.tienda_id = t.id
LEFT JOIN categorias c ON p.categoria_id = c.id;
GO

-- Vista: Alertas activas con información del producto
IF OBJECT_ID('vw_alertas_activas', 'V') IS NOT NULL
    DROP VIEW vw_alertas_activas;
GO

CREATE VIEW vw_alertas_activas AS
SELECT 
    a.id as alerta_id,
    a.email,
    a.precio_objetivo,
    a.fecha_creacion,
    p.id as producto_id,
    p.nombre as producto,
    m.nombre as marca,
    (SELECT MIN(precio) 
     FROM precios pr 
     WHERE pr.producto_id = p.id 
     AND pr.fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id)) as precio_actual_minimo,
    CASE 
        WHEN (SELECT MIN(precio) FROM precios WHERE producto_id = p.id 
              AND fecha = (SELECT MAX(fecha) FROM precios WHERE producto_id = p.id)) <= a.precio_objetivo 
        THEN 1 
        ELSE 0 
    END as objetivo_alcanzado
FROM alertas a
INNER JOIN productos p ON a.producto_id = p.id
LEFT JOIN marcas m ON p.marca_id = m.id
WHERE a.activa = 1 AND a.notificado = 0;
GO

-- =============================
-- PROCEDIMIENTOS ALMACENADOS
-- =============================

-- Procedimiento: Insertar o actualizar producto
IF OBJECT_ID('sp_upsert_producto', 'P') IS NOT NULL
    DROP PROCEDURE sp_upsert_producto;
GO

CREATE PROCEDURE sp_upsert_producto
    @nombre VARCHAR(500),
    @descripcion VARCHAR(MAX) = NULL,
    @url_imagen VARCHAR(MAX) = NULL,
    @marca VARCHAR(100) = NULL,
    @categoria VARCHAR(100) = NULL,
    @sku VARCHAR(100) = NULL,
    @producto_id INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @marca_id INT = NULL;
    DECLARE @categoria_id INT = NULL;
    
    -- Obtener o crear marca
    IF @marca IS NOT NULL
    BEGIN
        SELECT @marca_id = id FROM marcas WHERE nombre = @marca;
        IF @marca_id IS NULL
        BEGIN
            INSERT INTO marcas (nombre) VALUES (@marca);
            SET @marca_id = SCOPE_IDENTITY();
        END
    END
    
    -- Obtener categoria
    IF @categoria IS NOT NULL
    BEGIN
        SELECT @categoria_id = id FROM categorias WHERE nombre = @categoria;
    END
    
    -- Buscar producto existente por nombre o SKU
    SELECT @producto_id = id 
    FROM productos 
    WHERE nombre = @nombre OR (@sku IS NOT NULL AND sku = @sku);
    
    IF @producto_id IS NULL
    BEGIN
        -- Crear nuevo producto
        INSERT INTO productos (nombre, descripcion, url_imagen, marca_id, categoria_id, sku)
        VALUES (@nombre, @descripcion, @url_imagen, @marca_id, @categoria_id, @sku);
        SET @producto_id = SCOPE_IDENTITY();
    END
    ELSE
    BEGIN
        -- Actualizar producto existente
        UPDATE productos 
        SET descripcion = COALESCE(@descripcion, descripcion),
            url_imagen = COALESCE(@url_imagen, url_imagen),
            marca_id = COALESCE(@marca_id, marca_id),
            categoria_id = COALESCE(@categoria_id, categoria_id),
            sku = COALESCE(@sku, sku),
            ultima_actualizacion = GETDATE()
        WHERE id = @producto_id;
    END
END
GO

PRINT 'Base de datos ScrapingWong creada exitosamente con todas las tablas, vistas y procedimientos.';
GO
