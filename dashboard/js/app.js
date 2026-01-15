/**
 * WongPrime Dashboard - Main Application
 */

const API_BASE = 'http://localhost:8000';

const app = {
    productos: [],
    categorias: [],
    marcas: [],

    // Initialize
    async init() {
        await this.loadStats();
        await this.loadCategorias();
        await this.loadMarcas();
        await this.loadProductos();
    },

    // Load Statistics
    async loadStats() {
        try {
            const response = await fetch(`${API_BASE}/estadisticas/`);
            const data = await response.json();

            document.getElementById('statProductos').textContent = data.total_productos;
            document.getElementById('statTiendas').textContent = data.total_tiendas;
            document.getElementById('statCategorias').textContent = data.total_categorias;
            document.getElementById('statAlertas').textContent = data.total_alertas_activas;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },

    // Load Categories
    async loadCategorias() {
        try {
            const response = await fetch(`${API_BASE}/estadisticas/categorias`);
            const data = await response.json();
            this.categorias = data;

            const select = document.getElementById('categoriaFilter');
            data.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.nombre;
                option.textContent = cat.nombre;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    },

    // Load Brands
    async loadMarcas() {
        try {
            const response = await fetch(`${API_BASE}/estadisticas/marcas`);
            const data = await response.json();
            this.marcas = data;

            const select = document.getElementById('marcaFilter');
            data.forEach(marca => {
                const option = document.createElement('option');
                option.value = marca.nombre;
                option.textContent = marca.nombre;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading brands:', error);
        }
    },

    // Load Products
    async loadProductos() {
        const searchTerm = document.getElementById('searchInput').value;
        const categoria = document.getElementById('categoriaFilter').value;
        const marca = document.getElementById('marcaFilter').value;

        let url = `${API_BASE}/productos/?limit=50`;
        if (searchTerm) url += `&buscar=${encodeURIComponent(searchTerm)}`;
        if (categoria) url += `&categoria=${encodeURIComponent(categoria)}`;
        if (marca) url += `&marca=${encodeURIComponent(marca)}`;

        try {
            const response = await fetch(url);
            const data = await response.json();
            this.productos = data;
            this.renderProductos();
        } catch (error) {
            console.error('Error loading products:', error);
            this.showError('Error cargando productos');
        }
    },

    // Render Products Table
    renderProductos() {
        const tbody = document.getElementById('productsTableBody');

        if (this.productos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 40px; color: #666;">No se encontraron productos</td></tr>';
            return;
        }

        tbody.innerHTML = this.productos.map(producto => `
            <tr class="fade-in">
                <td class="product-name">${producto.nombre}</td>
                <td>${producto.marca || '-'}</td>
                <td>${producto.categoria || '-'}</td>
                <td>
                    <span class="price">S/ ${this.getPrecioMinimo(producto)}</span>
                </td>
                <td class="action-btns">
                    <button class="btn btn-sm" onclick="app.viewProductDetail(${producto.id})">
                        Ver Detalle
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="app.compareProduct(${producto.id})">
                        Comparar
                    </button>
                </td>
            </tr>
        `).join('');
    },

    // Helper: Get minimum price (placeholder - in real scenario would come from API)
    getPrecioMinimo(producto) {
        return '0.00'; // Will be replaced when API returns price
    },

    // View Product Detail
    async viewProductDetail(productoId) {
        try {
            const response = await fetch(`${API_BASE}/productos/${productoId}`);
            const producto = await response.json();

            // Get price history
            const historyResponse = await fetch(`${API_BASE}/productos/${productoId}/historico?dias=30`);
            const history = await historyResponse.json();

            this.showProductModal(producto, history);
        } catch (error) {
            console.error('Error loading product detail:', error);
            this.showError('Error cargando detalle del producto');
        }
    },

    // Compare Product
    async compareProduct(productoId) {
        try {
            const response = await fetch(`${API_BASE}/productos/${productoId}/comparar`);
            const comparacion = await response.json();

            this.showComparisonModal(comparacion);
        } catch (error) {
            console.error('Error loading comparison:', error);
            this.showError('Error cargando comparación');
        }
    },

    // Show Product Modal
    showProductModal(producto, history) {
        const modal = document.getElementById('productModal');
        const content = document.getElementById('modalContent');

        const precios = producto.precios_actuales || [];

        content.innerHTML = `
            <h2>${producto.nombre}</h2>
            ${producto.marca ? `<p><strong>Marca:</strong> ${producto.marca}</p>` : ''}
            ${producto.categoria ? `<p><strong>Categoría:</strong> ${producto.categoria}</p>` : ''}
            
            <h3>Precios Actuales por Tienda</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                ${precios.map(precio => `
                    <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <div style="font-weight: 600; margin-bottom: 8px;">${precio.tienda}</div>
                        <div style="font-size: 1.5em; color: #4caf50; font-weight: bold;">S/ ${precio.precio.toFixed(2)}</div>
                        ${precio.stock ? `<div style="font-size: 0.9em; color: #666;">Stock: ${precio.stock}</div>` : ''}
                    </div>
                `).join('')}
            </div>
            
            <button class="btn" style="margin-top: 20px;" onclick="app.setAlertForProduct(${producto.id})">
                🔔 Crear Alerta para este Producto
            </button>
        `;

        modal.style.display = 'block';
    },

    // Show Comparison Modal
    showComparisonModal(comparacion) {
        const modal = document.getElementById('productModal');
        const content = document.getElementById('modalContent');

        content.innerHTML = `
            <h2>Comparación de Precios</h2>
            <h3>${comparacion.producto}</h3>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0;">
                <div style="padding: 25px; background: ${comparacion.mejor_tienda === 'Wong' ? '#e8f5e9' : '#f8f9fa'}; border-radius: 10px; text-align: center;">
                    <h4>Wong</h4>
                    <div style="font-size: 2em; color: #667eea; font-weight: bold;">
                        ${comparacion.precio_wong ? `S/ ${comparacion.precio_wong.toFixed(2)}` : '-'}
                    </div>
                    ${comparacion.mejor_tienda === 'Wong' ? '<div style="color: #4caf50; font-weight: 600; margin-top: 10px;">✓ Mejor Precio</div>' : ''}
                </div>
                
                <div style="padding: 25px; background: ${comparacion.mejor_tienda === 'Metro' ? '#e8f5e9' : '#f8f9fa'}; border-radius: 10px; text-align: center;">
                    <h4>Metro</h4>
                    <div style="font-size: 2em; color: #667eea; font-weight: bold;">
                        ${comparacion.precio_metro ? `S/ ${comparacion.precio_metro.toFixed(2)}` : '-'}
                    </div>
                    ${comparacion.mejor_tienda === 'Metro' ? '<div style="color: #4caf50; font-weight: 600; margin-top: 10px;">✓ Mejor Precio</div>' : ''}
                </div>
                
                <div style="padding: 25px; background: ${comparacion.mejor_tienda === 'Plaza Vea' ? '#e8f5e9' : '#f8f9fa'}; border-radius: 10px; text-align: center;">
                    <h4>Plaza Vea</h4>
                    <div style="font-size: 2em; color: #667eea; font-weight: bold;">
                        ${comparacion.precio_plaza_vea ? `S/ ${comparacion.precio_plaza_vea.toFixed(2)}` : '-'}
                    </div>
                    ${comparacion.mejor_tienda === 'Plaza Vea' ? '<div style="color: #4caf50; font-weight: 600; margin-top: 10px;">✓ Mejor Precio</div>' : ''}
                </div>
            </div>
            
            ${comparacion.ahorro_maximo ? `
                <div style="padding: 20px; background: #fff3cd; border-radius: 8px; text-align: center;">
                    <strong>💰 Ahorro potencial comprando en ${comparacion.mejor_tienda}:</strong> 
                    <span style="font-size: 1.3em; color: #4caf50; font-weight: bold;">S/ ${comparacion.ahorro_maximo.toFixed(2)}</span>
                </div>
            ` : ''}
        `;

        modal.style.display = 'block';
    },

    // Close Modal
    closeModal() {
        document.getElementById('productModal').style.display = 'none';
    },

    // Set Alert for Product
    setAlertForProduct(productoId) {
        document.getElementById('alertProductoId').value = productoId;
        this.closeModal();
        document.getElementById('alertEmail').focus();
    },

    // Create Alert
    async createAlert(event) {
        event.preventDefault();

        const productoId = parseInt(document.getElementById('alertProductoId').value);
        const email = document.getElementById('alertEmail').value;
        const precioObjetivo = parseFloat(document.getElementById('alertPrecio').value);

        try {
            const response = await fetch(`${API_BASE}/alertas/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    producto_id: productoId,
                    email: email,
                    precio_objetivo: precioObjetivo
                })
            });

            if (response.ok) {
                this.showSuccess('¡Alerta creada exitosamente!');
                document.getElementById('alertForm').reset();
                this.loadStats(); // Reload stats
            } else {
                this.showError('Error creando la alerta');
            }
        } catch (error) {
            console.error('Error creating alert:', error);
            this.showError('Error creando la alerta');
        }
    },

    // Download Report
    async downloadReport() {
        this.showInfo('Generando reporte... (funcionalidad en desarrollo)');
    },

    // Show Success Message
    showSuccess(message) {
        this.showAlert(message, 'success');
    },

    // Show Error Message
    showError(message) {
        this.showAlert(message, 'error');
    },

    // Show Info Message
    showInfo(message) {
        this.showAlert(message, 'info');
    },

    // Show Alert
    showAlert(message, type) {
        const container = document.getElementById('alertsContainer');
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} fade-in`;
        alert.textContent = message;
        container.appendChild(alert);

        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Modal styling
const style = document.createElement('style');
style.textContent = `
.modal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-content {
    background: white;
    padding: 30px;
    border-radius: 15px;
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.close {
    position: absolute;
    right: 20px;
    top: 15px;
    font-size: 28px;
    font-weight: bold;
    color: #999;
    cursor: pointer;
}

.close:hover {
    color: #333;
}
`;
document.head.appendChild(style);
