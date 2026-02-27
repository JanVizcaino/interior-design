<template>
  <div class="flex flex-col h-screen w-full bg-slate-50 text-slate-900 font-sans antialiased">
    <TopBar @clear="clearRoom" />
    
    <div class="flex flex-1 overflow-hidden relative">
      <SideBar
        :furniture="furnitureList"
        :floorMaterials="floorMaterials"
        :wallMaterials="wallMaterials"
        :selectedFloor="selectedFloor"
        :selectedWall="selectedWall"
        :showGrid="showGrid"
        :currentMode="currentMode"
        @floorChanged="selectedFloor = $event"
        @wallChanged="selectedWall = $event"
        @gridChanged="showGrid = $event"
        @modeChanged="setMode"
      />
      <RoomScene
        :placedItems="placedItems"
        :selectedFloor="selectedFloor"
        :selectedWall="selectedWall"
        :showGrid="showGrid"
        :currentMode="currentMode"
        @itemPlaced="addItem"
        @itemRemoved="removeItem"
        @itemUpdated="updateItem"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import TopBar from "./components/TopBar.vue";
import SideBar from "./components/SideBar.vue";
import RoomScene from "./components/RoomScene.vue";

const furnitureList = ref([]);
const placedItems = ref([]);

const selectedFloor = ref("WoodFloor051");
const selectedWall = ref("Bricks060");
const showGrid = ref(false);

const currentMode = ref("rotate");

const floorMaterials = [
  { id: "WoodFloor051", name: "Parquet", preview: "/textures/floors/WoodFloor051/Color.jpg" },
  { id: "Tiles131", name: "Baldosas", preview: "/textures/floors/Tiles131/Color.jpg" },
];

const wallMaterials = [
  { id: "Bricks060", name: "Ladrillo Rojo", preview: "/textures/walls/Bricks060/Color.jpg" },
  { id: "Bricks092", name: "Ladrillo Blanco", preview: "/textures/walls/Bricks092/Color.jpg" },
];

async function loadFurnitureList() {
  try {
    const res = await fetch("/models/index.json");
    const files = await res.json();
    furnitureList.value = files.map((filename, index) => {
      return {
        id: index + 1,
        name: filename.replace(".glb", ""),
        model: `/models/${filename}`,
        scale: 3,
      };
    });
  } catch (e) {
    console.error("Error cargando index.json:", e);
  }
}

function addItem(item) {
  placedItems.value = [...placedItems.value, item];
}

function removeItem(uid) {
  placedItems.value = placedItems.value.filter((item) => item.uid !== uid);
}

function updateItem(updatedItem) {
  const index = placedItems.value.findIndex((i) => i.uid === updatedItem.uid);
  if (index !== -1) placedItems.value[index] = updatedItem;
}

function clearRoom() {
  placedItems.value = [];
}

function setMode(mode) {
  currentMode.value = currentMode.value === mode ? "rotate" : mode;
}

onMounted(async () => {
  await loadFurnitureList();
});
</script>