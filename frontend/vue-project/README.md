# SISTEMAS Explotacion - Vue 3

Sistema de gestión de inventario construido con Vue 3, Composition API, TypeScript, Axios y CSS puro.

## 🚀 Instalación

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Compilar para producción
npm run build
```

## 📁 Estructura del Proyecto

```
vue-app/
├── components/           # Componentes Vue
│   ├── AppSidebar.vue   # Sidebar colapsable
│   ├── AppHeader.vue    # Header con info de usuario
│   ├── ActionBar.vue    # Botones CRUD
│   ├── InventoryTable.vue  # Tabla de inventario
│   └── ArticuloModal.vue   # Modal para operaciones
├── types/               # Tipos TypeScript
│   └── index.ts
├── services/            # Servicios API
│   └── api.ts          # Axios API service
├── src/
│   └── main.ts         # Entry point
├── App.vue             # Componente principal
├── index.html
├── vite.config.ts
└── package.json
```

## 🔌 Conectar con tu Backend

Edita el archivo `services/api.ts` y cambia la URL base:

```typescript
const API_URL = "https://tu-backend.com/api";
```

O crea un archivo `.env`:

```
VITE_API_URL=https://tu-backend.com/api
```

## 📋 Características

- ✅ **Sidebar colapsable** con navegación por secciones
- ✅ **CRUD completo** (Crear, Actualizar, Buscar, Retirar, Agregar, Eliminar)
- ✅ **Tabla de inventario** con selección múltiple
- ✅ **Modales** para todas las operaciones
- ✅ **Gestión de stock** con control de cantidades
- ✅ **Visibilidad por rol** (admin, usuario, visualizador)
- ✅ **TypeScript** para type safety
- ✅ **CSS puro** con estilos modernos
- ✅ **Axios** para peticiones HTTP

## 🎨 Personalización

Los estilos están en cada componente `.vue` dentro de `<style scoped>`. Puedes personalizar:

- Colores en las clases CSS
- Tamaños de fuente
- Espaciados y márgenes
- Transiciones y animaciones

## 📡 API Endpoints

El servicio espera los siguientes endpoints:

- `GET /api/articulos` - Listar artículos (opcional: `?q=busqueda`)
- `POST /api/articulos` - Crear artículo
- `PUT /api/articulos` - Actualizar artículo
- `DELETE /api/articulos?ids=1,2,3` - Eliminar artículos
- `PATCH /api/articulos` - Ajustar stock (agregar/retirar)

## 👤 Usuario de Ejemplo

Usuario simulado en `App.vue`:

```typescript
{
  username: "carlos.mendez",
  nombre: "Carlos Mendez",
  rol: "admin",
  localidad: "Ciudad de Mexico"
}
```

Puedes modificarlo o conectarlo con tu sistema de autenticación.
