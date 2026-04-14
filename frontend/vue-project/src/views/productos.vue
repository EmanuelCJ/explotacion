<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-6">Gestión de Productos</h1>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <input 
        v-model="filters.search" 
        @input="debounceSearch"
        type="text" 
        placeholder="Buscar por nombre o código..." 
        class="border p-2 rounded"
      />

      <select v-model="filters.categoria_id" @change="fetchProductos" class="border p-2 rounded">
        <option value="">Todas las categorías</option>
        <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
          {{ cat.nombre }}
        </option>
      </select>

      <select v-model="filters.activo" @change="fetchProductos" class="border p-2 rounded">
        <option :value="null">Todos los estados</option>
        <option :value="true">Activos</option>
        <option :value="false">Inactivos</option>
      </select>
    </div>

    <div class="overflow-x-auto bg-white shadow-md rounded">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-100 border-b">
            <th class="p-3">Código</th>
            <th class="p-3">Nombre</th>
            <th class="p-3">Categoría</th>
            <th class="p-3">Stock Total</th>
            <th class="p-3">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="prod in productos" :key="prod.id_producto" class="border-b hover:bg-gray-50">
            <td class="p-3">{{ prod.codigo }}</td>
            <td class="p-3 font-semibold">{{ prod.nombre }}</td>
            <td class="p-3">
              <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                {{ prod.categoria_nombre }}
              </span>
            </td>
            <td class="p-3 text-center">
              <strong :class="prod.stock_total <= 0 ? 'text-red-500' : 'text-green-600'">
                {{ prod.stock_total }}
              </strong>
            </td>
            <td class="p-3">
              <span :class="prod.activo ? 'text-green-500' : 'text-red-500'">
                {{ prod.activo ? '● Activo' : '● Inactivo' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex justify-between items-center mt-6">
      <span class="text-sm text-gray-600">
        Página {{ pagination.page }} de {{ pagination.total_pages }} (Total: {{ pagination.total }})
      </span>
      <div class="space-x-2">
        <button 
          :disabled="pagination.page === 1"
          @click="changePage(pagination.page - 1)"
          class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Anterior
        </button>
        <button 
          :disabled="pagination.page === pagination.total_pages"
          @click="changePage(pagination.page + 1)"
          class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Siguiente
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

// Estado de los datos
const productos = ref([]);
const categorias = ref([]); // Deberías cargar esto de otro endpoint
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0,
  total_pages: 1
});

// Filtros
const filters = reactive({
  search: '',
  categoria_id: '',
  activo: null
});

// Función principal para obtener productos
const fetchProductos = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/productos/', {
      params: {
        page: pagination.page,
        limit: pagination.limit,
        search: filters.search || undefined,
        categoria_id: filters.categoria_id || undefined,
        activo: filters.activo === null ? undefined : filters.activo
      },
      withCredentials: true // Crucial porque tu API usa jwt_required_cookie
    });

    productos.ref = response.data.productos;
    Object.assign(pagination, response.data.pagination);
  } catch (error) {
    console.error("Error cargando productos:", error);
    alert("No tienes permisos o la sesión expiró");
  }
};

// Cambiar de página
const changePage = (newPage) => {
  pagination.page = newPage;
  fetchProductos();
};

// Evitar peticiones excesivas al escribir (Debounce)
let timeout = null;
const debounceSearch = () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    pagination.page = 1; // Reset a página 1 al buscar
    fetchProductos();
  }, 500);
};

onMounted(() => {
  fetchProductos();
});
</script>