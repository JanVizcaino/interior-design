<template>
  <div class="app">
    <TopBar @clear="clearRoom" />
    <div class="main-layout">
      <SideBar
        :furniture="furnitureList"
        :floorMaterials="floorMaterials"
        :wallMaterials="wallMaterials"
        :selectedFloor="selectedFloor"
        :selectedWall="selectedWall"
        :showGrid="showGrid"
        @floorChanged="selectedFloor = $event"
        @wallChanged="selectedWall = $event"
        @gridChanged="showGrid = $event"
      />
      <RoomScene
        :placedItems="placedItems"
        :selectedFloor="selectedFloor"
        :selectedWall="selectedWall"
        :showGrid="showGrid"
        @itemPlaced="addItem"
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

const floorMaterials = [
  {
    id: "WoodFloor051",
    name: "Parquet",
    preview: "/textures/floors/WoodFloor051/Color.jpg",
  },
  {
    id: "Tiles131",
    name: "Baldosas",
    preview: "/textures/floors/Tiles131/Color.jpg",
  },
];

const wallMaterials = [
  {
    id: "Bricks060",
    name: "Ladrillo Rojo",
    preview: "/textures/walls/Bricks060/Color.jpg",
  },
  {
    id: "Bricks092",
    name: "Ladrillo Blanco",
    preview: "/textures/walls/Bricks092/Color.jpg",
  },
];


async function loadFurnitureList() {
  try {
    const res = await fetch("/models/index.json");
    const files = await res.json();

    furnitureList.value = files.map((filename, index) => {
      const name = filename.replace(".glb", "");

      return {
        id: index + 1,
        name,
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

function clearRoom() {
  placedItems.value = [];
}

onMounted(async () => {
  await loadFurnitureList();
});
</script>

<style>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}
</style>