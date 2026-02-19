<template>
  <div class="topbar">
    <h1>intdesing - JAN VIZCAÍNO</h1>
    <button @click="$emit('clear')">Limpiar todo</button>
  </div>
</template>

<script>
export default {
  name: "TopBar",
  emits: ["clear"],
};
</script>

<style scoped>
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #2c3e50;
  color: white;
}
button {
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}
</style>
