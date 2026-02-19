<template>
  <div class="sidebar">
    <h3>Muebles</h3>
    <div
      v-for="item in furniture"
      :key="item.id"
      class="furniture-item"
      draggable="true"
      @dragstart="onDragStart($event, item)"
    >
      {{ item.name }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'SideBar',
  props: {
    furniture: {
      type: Array,
      required: true
    }
  },
  methods: {
    onDragStart(event, item) {
      // Guardamos los datos del mueble en el evento de drag
      // JSON.stringify porque el dataTransfer solo acepta strings
      event.dataTransfer.setData('furniture', JSON.stringify(item))
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 180px;
  background: #ecf0f1;
  padding: 15px;
  border-right: 1px solid #bdc3c7;
  overflow-y: auto;
}
h3 {
  margin-bottom: 12px;
  color: #2c3e50;
}
.furniture-item {
  padding: 10px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  cursor: grab;
  text-align: center;
}
.furniture-item:hover {
  background: #3498db;
  color: white;
}
</style>