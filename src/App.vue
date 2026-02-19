<template>
  <div class="app">
    <TopBar @clear="clearRoom" />
    <div class="main-layout">
      <SideBar :furniture="furnitureList" />
      <RoomScene :placedItems="placedItems" @itemPlaced="addItem" />
    </div>
  </div>
</template>

<script>
import TopBar from './components/TopBar.vue'
import SideBar from './components/SideBar.vue'
import RoomScene from './components/RoomScene.vue'

export default {
  name: 'App',
  components: { TopBar, SideBar, RoomScene },

  data() {
    return {
      // Lista de muebles disponibles en la barra lateral
      furnitureList: [
        { id: 1, name: 'Silla', color: 0x8B4513 },
        { id: 2, name: 'Mesa',  color: 0xDEB887 },
        { id: 3, name: 'Sofá',  color: 0x4169E1 },
        { id: 4, name: 'Lámpara', color: 0xFFD700 },
      ],
      // Muebles que el usuario ha colocado en la habitación
      placedItems: []
    }
  },

  methods: {
    addItem(item) {
      // Cuando RoomScene emite 'itemPlaced', añadimos el mueble a la lista
      this.placedItems.push(item)
    },
    clearRoom() {
      // Vaciamos la lista (TopBar emite 'clear')
      this.placedItems = []
    }
  }
}
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