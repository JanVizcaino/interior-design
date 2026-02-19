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
<script>
import TopBar from "./components/TopBar.vue";
import SideBar from "./components/SideBar.vue";
import RoomScene from "./components/RoomScene.vue";

export default {
  name: "App",
  components: { TopBar, SideBar, RoomScene },

  data() {
    return {
      furnitureList: [],
      placedItems: [],

      selectedFloor: "WoodFloor051",
      selectedWall: "Bricks060",

      showGrid: false,

      floorMaterials: [
        {
          id: "WoodFloor051",
          name: "Madera",
          preview: "/textures/floors/WoodFloor051/Color.jpg",
        },
        {
          id: "Tiles131",
          name: "Baldosas",
          preview: "/textures/floors/Tiles131/Color.jpg",
        },
      ],
      wallMaterials: [
        {
          id: "Bricks060",
          name: "Enlucido",
          preview: "/textures/walls/Bricks060/Color.jpg",
        },
        {
          id: "Bricks092",
          name: "Ladrillo",
          preview: "/textures/walls/Bricks092/Color.jpg",
        },
      ],
    };
  },

  async mounted() {
    await this.loadFurnitureList();
  },

  methods: {
    async loadFurnitureList() {
      try {
        const res = await fetch("/models/index.json");
        const files = await res.json();

        this.furnitureList = files.map((filename, index) => {
          const name = filename
            .replace(".glb", "")

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
    },

    addItem(item) {
      this.placedItems = [...this.placedItems, item];
    },

    clearRoom() {
      this.placedItems = [];
    },
  },
};
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
