<template>
  <div
    class="w-70 bg-slate-50 p-5 border-r border-slate-200 overflow-y-auto flex flex-col gap-6"
  >
<div>
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Muebles</h3>
      </div>
      
      <div class="relative mb-4 group">
        <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
        
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Buscar mueble..." 
          class="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-sm transition-all"
        />
      </div>

      <div v-if="filteredFurniture.length === 0" class="text-center py-6 px-4 border-2 border-dashed border-slate-200 rounded-xl">
        <span class="text-sm text-slate-400">No se encontraron muebles que coincidan con "{{ searchQuery }}"</span>
      </div>

      <div v-else class="max-h-87.5 overflow-y-auto pr-2">
        <div
          v-for="item in filteredFurniture"
          :key="item.id"
          class="flex items-center gap-3 p-2 mb-2 bg-white border-2 border-transparent rounded-xl cursor-grab active:cursor-grabbing transition-all duration-200 shadow-sm hover:shadow-md hover:border-blue-300"
          draggable="true"
          @dragstart="onDragStart($event, item)"
        >
          <div class="w-12 h-12 shrink-0 bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center border border-slate-200">
            <FurniturePreview :model="item.model" :scale="item.scale" />
          </div>
          <span class="text-sm font-medium text-slate-700 truncate">{{ item.name }}</span>
        </div>
      </div>
    </div>

    <div class="flex-col">
      <h3
        class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3"
      >
        Herramientas
      </h3>
      <div class="flex flex-col gap-2">
        <button
          @click="$emit('gridChanged', !showGrid)"
          class="flex items-center gap-3 w-full p-3 rounded-xl border-2 transition-all duration-200 text-left group outline-none"
          :class="
            showGrid
              ? 'bg-blue-50 border-blue-500 shadow-sm'
              : 'bg-white border-slate-200 hover:border-blue-300 hover:bg-slate-50'
          "
        >
          <div
            :class="
              showGrid
                ? 'text-blue-600'
                : 'text-slate-400 group-hover:text-blue-500 transition-colors'
            "
          >
            <Grid2X2 class="w-5 h-5" />
          </div>
          <span
            class="text-sm font-medium flex-1"
            :class="showGrid ? 'text-blue-700' : 'text-slate-700'"
            >Grid en el Suelo</span
          >
          <div
            v-if="showGrid"
            class="w-2 h-2 rounded-full bg-blue-500 shadow-sm"
          ></div>
        </button>

        <button
          class="flex items-center gap-3 w-full p-3 rounded-xl border-2 transition-all duration-200 text-left group outline-none"
          :class="
            isMoving
              ? 'bg-blue-50 border-blue-500 shadow-sm'
              : 'bg-white border-slate-200 hover:border-blue-300 hover:bg-slate-50'
          "
        >
          <div
            :class="
              isMoving
                ? 'text-blue-600'
                : 'text-slate-400 group-hover:text-blue-500 transition-colors'
            "
          >
            <Move class="w-5 h-5" />
          </div>
          <span
            class="text-sm font-medium flex-1"
            :class="isMoving ? 'text-blue-700' : 'text-slate-700'"
            >Mover elementos</span
          >
          <div
            v-if="isMoving"
            class="w-2 h-2 rounded-full bg-blue-500 shadow-sm"
          ></div>
        </button>

        <button
          class="flex items-center gap-3 w-full p-3 rounded-xl border-2 transition-all duration-200 text-left group outline-none"
          :class="
            isDeleting
              ? 'bg-red-50 border-red-500 shadow-sm'
              : 'bg-white border-slate-200 hover:border-red-300 hover:bg-slate-50'
          "
        >
          <div
            :class="
              isDeleting
                ? 'text-red-600'
                : 'text-slate-400 group-hover:text-red-500 transition-colors'
            "
          >
            <Eraser class="w-5 h-5" />
          </div>
          <span
            class="text-sm font-medium flex-1"
            :class="isDeleting ? 'text-red-700' : 'text-slate-700'"
            >Eliminar elemento</span
          >
          <div
            v-if="isDeleting"
            class="w-2 h-2 rounded-full bg-red-500 shadow-sm"
          ></div>
        </button>

        <hr class="border-slate-200 my-1" />

        <button
          @click="$emit('clear')"
          class="flex items-center gap-3 w-full p-3 bg-white border-2 border-slate-200 rounded-xl hover:border-red-500 hover:bg-red-50 text-left group transition-all duration-200 active:scale-95 outline-none shadow-sm"
        >
          <div class="text-red-500 group-hover:scale-110 transition-transform">
            <Trash class="w-5 h-5" />
          </div>
          <span class="text-sm font-medium text-red-600 flex-1"
            >Limpiar sala</span
          >
        </button>
      </div>
    </div>

    <div>
      <h3
        class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3"
      >
        Suelo
      </h3>
      <div
        v-for="mat in floorMaterials"
        :key="mat.id"
        class="flex items-center gap-3 p-2 mb-2 bg-white border-2 rounded-xl cursor-pointer transition-all duration-200 shadow-sm hover:shadow-md hover:border-blue-300"
        :class="
          selectedFloor === mat.id
            ? 'border-blue-500 bg-blue-50'
            : 'border-transparent'
        "
        @click="$emit('floorChanged', mat.id)"
      >
        <img
          :src="mat.preview"
          class="w-12 h-12 object-cover rounded-lg shadow-sm"
        />
        <span class="text-sm font-medium text-slate-700">{{ mat.name }}</span>
      </div>
    </div>

    <div>
      <h3
        class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3"
      >
        Paredes
      </h3>
      <div
        v-for="mat in wallMaterials"
        :key="mat.id"
        class="flex items-center gap-3 p-2 mb-2 bg-white border-2 rounded-xl cursor-pointer transition-all duration-200 shadow-sm hover:shadow-md hover:border-blue-300"
        :class="
          selectedWall === mat.id
            ? 'border-blue-500 bg-blue-50'
            : 'border-transparent'
        "
        @click="$emit('wallChanged', mat.id)"
      >
        <img
          :src="mat.preview"
          class="w-12 h-12 object-cover rounded-lg shadow-sm"
        />
        <span class="text-sm font-medium text-slate-700">{{ mat.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"; // <-- 1. Importar ref y computed
import FurniturePreview from "./FurniturePreview.vue";
import { Trash, Search, Move, Eraser, LayoutGrid } from "lucide-vue-next";

const props = defineProps({
  furniture: { type: Array, required: true },
  floorMaterials: { type: Array, required: true },
  wallMaterials: { type: Array, required: true },
  selectedFloor: { type: String, required: true },
  selectedWall: { type: String, required: true },
  showGrid: { type: Boolean, required: true },
});

defineEmits(["wallChanged", "floorChanged", "gridChanged", "clear"]);

// 2. Variable reactiva para el texto de búsqueda
const searchQuery = ref("");

// 3. Propiedad computada que filtra los muebles automáticamente
const filteredFurniture = computed(() => {
  // Si el buscador está vacío, devolvemos toda la lista
  if (!searchQuery.value.trim()) {
    return props.furniture;
  }

  // Si hay texto, filtramos buscando coincidencias en el nombre
  const query = searchQuery.value.toLowerCase();
  return props.furniture.filter((item) =>
    item.name.toLowerCase().includes(query),
  );
});

function onDragStart(event, item) {
  event.dataTransfer.setData("furniture", JSON.stringify(item));
}
</script>
