<template>
  <div
    class="w-[280px] bg-slate-50 p-5 border-r border-slate-200 overflow-y-auto flex flex-col gap-6"
  >
    <div class="flex-col gap-4">
      <h3
        class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3"
      >
        Opciones
      </h3>
      <div
        class="flex justify-between items-center p-3 bg-white border border-slate-200 rounded-xl shadow-sm"
      >
        <span class="text-sm font-medium text-slate-700">Grid magnético</span>

        <div
          class="w-11 h-6 rounded-full cursor-pointer relative transition-colors duration-300 ease-in-out"
          :class="showGrid ? 'bg-blue-500' : 'bg-slate-300'"
          @click="$emit('gridChanged', !showGrid)"
        >
          <div
            class="w-5 h-5 bg-white rounded-full absolute top-[2px] left-[2px] shadow-sm transition-transform duration-300 ease-in-out"
            :class="showGrid ? 'translate-x-5' : 'translate-x-0'"
          ></div>
        </div>
      </div>
      <div
        class="flex justify-between items-center p-3 bg-white border border-slate-200 rounded-xl shadow-sm"
      >
        <span class="text-sm font-medium text-slate-700">Eliminar todo</span>

        <button
          @click="$emit('clear')"
          class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-sm font-semibold rounded-lg shadow-sm transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 focus:ring-offset-slate-800 active:scale-95"
        >
          <Trash></Trash>
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

    <div>
      <h3
        class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3"
      >
        Muebles
      </h3>
      <div
        v-for="item in furniture"
        :key="item.id"
        class="flex items-center gap-3 p-2 mb-2 bg-white border-2 border-transparent rounded-xl cursor-grab active:cursor-grabbing transition-all duration-200 shadow-sm hover:shadow-md hover:border-blue-300"
        draggable="true"
        @dragstart="onDragStart($event, item)"
      >
        <div
          class="w-12 h-12 shrink-0 bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center border border-slate-200"
        >
          <FurniturePreview :model="item.model" :scale="item.scale" />
        </div>
        <span class="text-sm font-medium text-slate-700 truncate">{{
          item.name
        }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import FurniturePreview from "./FurniturePreview.vue";
import { Trash } from "lucide-vue-next";

defineProps({
  furniture: { type: Array, required: true },
  floorMaterials: { type: Array, required: true },
  wallMaterials: { type: Array, required: true },
  selectedFloor: { type: String, required: true },
  selectedWall: { type: String, required: true },
  showGrid: { type: Boolean, required: true },
});

defineEmits(["wallChanged", "floorChanged", "gridChanged"]);

function onDragStart(event, item) {
  event.dataTransfer.setData("furniture", JSON.stringify(item));
}
</script>
