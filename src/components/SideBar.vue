<template>
  <div class="sidebar">
    <h3 class="section-title">Opciones</h3>
    <div class="toggle-option">
      <span>Mostrar grid</span>
      <div
        class="toggle"
        :class="{ active: showGrid }"
        @click="$emit('gridChanged', !showGrid)"
      >
        <div class="toggle-knob"></div>
      </div>
    </div>

    <h3 class="section-title">Suelo</h3>
    <div
      v-for="mat in floorMaterials"
      :key="mat.id"
      class="material-option"
      :class="{ active: selectedFloor === mat.id }"
      @click="$emit('floorChanged', mat.id)"
    >
      <img :src="mat.preview" class="material-thumb" />
      {{ mat.name }}
    </div>

    <h3 class="section-title">Paredes</h3>
    <div
      v-for="mat in wallMaterials"
      :key="mat.id"
      class="material-option"
      :class="{ active: selectedWall === mat.id }"
      @click="$emit('wallChanged', mat.id)"
    >
      <img :src="mat.preview" class="material-thumb" />
      {{ mat.name }}
    </div>

    <h3 class="section-title">Muebles</h3>
    <div
      v-for="item in furniture"
      :key="item.id"
      class="furniture-item"
      draggable="true"
      @dragstart="onDragStart($event, item)"
    >
      <FurniturePreview :model="item.model" :scale="item.scale" />
      <span>{{ item.name }}</span>
    </div>
  </div>
</template>

<script>
import FurniturePreview from "./FurniturePreview.vue";

export default {
  name: "SideBar",
  components: { FurniturePreview },

  props: {
    furniture: { type: Array, required: true },
    floorMaterials: { type: Array, required: true },
    wallMaterials: { type: Array, required: true },
    selectedFloor: { type: String, required: true },
    selectedWall: { type: String, required: true },
    showGrid: { type: Boolean, required: true },
  },
  emits: ["wallChanged", "floorChanged", "gridChanged"],

  methods: {
    onDragStart(event, item) {
      event.dataTransfer.setData("furniture", JSON.stringify(item));
    },
  },
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  background: #ecf0f1;
  padding: 15px;
  border-right: 1px solid #bdc3c7;
  overflow-y: auto;
}
h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}
.section-title {
  margin-top: 20px;
}
.furniture-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px;
  margin-bottom: 6px;
  background: white;
  border: 2px solid #bdc3c7;
  border-radius: 4px;
  cursor: grab;
}
.furniture-item:hover {
  border-color: #3498db;
}
.material-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  margin-bottom: 6px;
  background: white;
  border: 2px solid #bdc3c7;
  border-radius: 4px;
  cursor: pointer;
}
.material-option:hover {
  border-color: #3498db;
}
.material-option.active {
  border-color: #3498db;
  background: #ebf5fb;
}
.material-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 3px;
}

.toggle-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: white;
  border: 2px solid #bdc3c7;
  border-radius: 4px;
  font-size: 14px;
  color: #2c3e50;
}

.toggle {
  width: 40px;
  height: 22px;
  background: #bdc3c7;
  border-radius: 11px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
}

.toggle.active {
  background: #3498db;
}

.toggle-knob {
  width: 16px;
  height: 16px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: left 0.2s;
}

.toggle.active .toggle-knob {
  left: 21px;
}
</style>
