# QASO System — Vue 3 + TypeScript

Sistema de Control de Inventario construido con **Vue 3**, **TypeScript**, **Pinia** y **Vue Router**, conectado a una API REST Flask.

---

## Estructura del proyecto

```
src/
├── api/
│   └── inventario.ts       # Capa de servicio (axios → Flask)
├── assets/
│   └── main.css            # Estilos globales
├── components/
│   ├── AppSidebar.vue      # Navegación lateral
│   ├── AppMessage.vue      # Alertas reutilizables
│   ├── AutocompleteInput.vue  # Input con búsqueda de productos
│   └── StatCard.vue        # Tarjetas del dashboard
├── router/
│   └── index.ts            # Rutas (lazy-loaded)
├── stores/
│   └── inventario.ts       # Pinia store (listas + resumen)
├── types/
│   └── index.ts            # Interfaces y enums TypeScript
├── views/
│   ├── DashboardView.vue
│   ├── ProductosView.vue
│   ├── MovimientosView.vue
│   ├── InventarioView.vue
│   ├── ReportesView.vue
│   ├── BuscarView.vue
│   └── ConfiguracionView.vue
├── App.vue
└── main.ts
```

---

## Instalación y uso

```bash
npm install
npm run dev       # desarrollo (http://localhost:5173)
npm run build     # producción
```

---

## Endpoints Flask esperados

| Método | Ruta                           | Descripción                      |
|--------|--------------------------------|----------------------------------|
| GET    | `/api/resumen`                 | Estadísticas del dashboard       |
| GET    | `/api/stock`                   | Lista completa de productos+stock|
| GET    | `/api/listas`                  | Unidades y grupos disponibles    |
| GET    | `/api/productos/buscar?q=`     | Búsqueda por texto               |
| GET    | `/api/productos/buscar-codigo?codigo=` | Sugerencias autocomplete |
| POST   | `/api/productos`               | Registrar nuevo producto         |
| POST   | `/api/movimientos`             | Registrar movimiento             |
| GET    | `/api/historial`               | Historial filtrado               |
| GET    | `/api/exportar-stock`          | Exportar CSV (devuelve `{url}`)  |
| POST   | `/api/inicializar`             | Inicializar sistema              |
| GET    | `/api/validar-integridad`      | Validar datos                    |

> El proxy de Vite redirige `/api` → `http://localhost:5000` en desarrollo.
> En producción, configurar nginx o el mismo Flask para servir la app.

---

## Estructura esperada de respuestas Flask

```python
# GET /api/resumen
{ "totalProductos": 10, "totalMovimientos": 50, "sinStock": 2,
  "stockBajo": 3, "valorTotalInventario": 150.0, "movimientosUltimoMes": 12 }

# GET /api/stock  →  lista de:
{ "codigo": "P001", "nombre": "Tornillo", "unidad": "Unidades",
  "grupo": "General", "stockMin": 10, "cantidad": 25,
  "estado": "Normal" }   # "Normal" | "Stock Bajo" | "Sin Stock"

# GET /api/listas
{ "unidades": ["Unidades", "Kilogramos", ...], "grupos": ["General", ...] }

# POST /api/productos  →  { "mensaje": "Producto registrado correctamente." }
# POST /api/movimientos → { "mensaje": "Movimiento registrado correctamente." }

# GET /api/historial?fechaDesde=2024-01-01&fechaHasta=2024-12-31&tipo=
# → lista de: { "codigo", "fecha", "tipo", "cantidad", "producto",
#               "observaciones", "usuario" }

# GET /api/exportar-stock → { "url": "https://..." }
# POST /api/inicializar   → { "mensaje": "..." }
# GET /api/validar-integridad → { "errores": [] }
```

---

## Configurar Flask para CORS (requerido)

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

```bash
pip install flask-cors
```
