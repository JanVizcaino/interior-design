<template>
  <div
    class="room-container"
    ref="container"
    @drop="onDrop"
    @dragover.prevent
  >
  </div>
</template>

<script>
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

export default {
  name: 'RoomScene',

  props: {
    placedItems: {
      type: Array,
      required: true
    }
  },

  emits: ['itemPlaced'],

  // Guardamos las variables de Three.js fuera de data()
  // porque no necesitan ser reactivas (son objetos internos de Three)
  scene: null,
  camera: null,
  renderer: null,
  controls: null,
  meshMap: {},  // guarda { id: mesh } para poder eliminarlos

  mounted() {
    this.initThree()
    this.animate()
    window.addEventListener('resize', this.onResize)
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.onResize)
    this.renderer.dispose()
  },

  watch: {
    // Cuando placedItems cambia (se limpia o añade algo), redibujamos
    placedItems(newItems) {
      this.syncItems(newItems)
    }
  },

  methods: {

    initThree() {
      const container = this.$refs.container

      // --- ESCENA ---
      // La escena es el "mundo" donde viven todos los objetos 3D
      this.$options.scene = new THREE.Scene()
      this.$options.scene.background = new THREE.Color(0xf0f0f0)

      // --- CÁMARA ---
      // PerspectiveCamera(fov, aspect, near, far)
      // fov: ángulo de visión. aspect: proporción pantalla. near/far: distancia de recorte
      this.$options.camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
      )
      this.$options.camera.position.set(0, 8, 10)
      this.$options.camera.lookAt(0, 0, 0)

      // --- RENDERER ---
      // Es el motor que dibuja la escena en el canvas
      this.$options.renderer = new THREE.WebGLRenderer({ antialias: true })
      this.$options.renderer.setSize(container.clientWidth, container.clientHeight)
      container.appendChild(this.$options.renderer.domElement)

      // --- CONTROLES DE ÓRBITA ---
      // Permiten rotar, zoom y mover la cámara con el ratón
      this.$options.controls = new OrbitControls(
        this.$options.camera,
        this.$options.renderer.domElement
      )

      // --- LUZ ---
      // AmbientLight: ilumina todo por igual (sin sombras)
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
      this.$options.scene.add(ambientLight)

      // DirectionalLight: como el sol, viene de una dirección
      const dirLight = new THREE.DirectionalLight(0xffffff, 0.8)
      dirLight.position.set(5, 10, 5)
      this.$options.scene.add(dirLight)

      // Construir la habitación
      this.buildRoom()
    },

    buildRoom() {
      const scene = this.$options.scene

      // SUELO — un plano horizontal
      const floorGeo = new THREE.PlaneGeometry(10, 10)
      const floorMat = new THREE.MeshLambertMaterial({ color: 0xd2b48c })
      const floor = new THREE.Mesh(floorGeo, floorMat)
      floor.rotation.x = -Math.PI / 2  // rotamos 90° para que sea horizontal
      scene.add(floor)

      // PARED TRASERA
      const wallGeo = new THREE.PlaneGeometry(10, 5)
      const wallMat = new THREE.MeshLambertMaterial({ color: 0xffffff, side: THREE.DoubleSide })

      const backWall = new THREE.Mesh(wallGeo, wallMat)
      backWall.position.set(0, 2.5, -5)
      scene.add(backWall)

      // PARED IZQUIERDA
      const leftWall = new THREE.Mesh(wallGeo, wallMat)
      leftWall.position.set(-5, 2.5, 0)
      leftWall.rotation.y = Math.PI / 2
      scene.add(leftWall)

      // PARED DERECHA
      const rightWall = new THREE.Mesh(wallGeo, wallMat)
      rightWall.position.set(5, 2.5, 0)
      rightWall.rotation.y = -Math.PI / 2
      scene.add(rightWall)
    },

    // Crea un mueble 3D según su tipo
    createFurnitureMesh(item) {
      let geometry, material, mesh

      material = new THREE.MeshLambertMaterial({ color: item.color })

      switch (item.name) {
        case 'Silla':
          // Una silla simple: un cubo pequeño
          geometry = new THREE.BoxGeometry(0.6, 0.8, 0.6)
          break
        case 'Mesa':
          geometry = new THREE.BoxGeometry(1.5, 0.1, 0.8)
          break
        case 'Sofá':
          geometry = new THREE.BoxGeometry(2, 0.7, 0.8)
          break
        case 'Lámpara':
          geometry = new THREE.ConeGeometry(0.3, 1, 8)
          break
        default:
          geometry = new THREE.BoxGeometry(1, 1, 1)
      }

      mesh = new THREE.Mesh(geometry, material)
      return mesh
    },

    // Sincroniza los objetos 3D con el array de placedItems
    syncItems(items) {
      const scene = this.$options.scene
      const meshMap = this.$options.meshMap

      // Borramos todos los muebles anteriores de la escena
      Object.values(meshMap).forEach(mesh => scene.remove(mesh))
      this.$options.meshMap = {}

      // Volvemos a añadir los que hay ahora
      items.forEach(item => {
        const mesh = this.createFurnitureMesh(item)
        mesh.position.set(item.x, 0.5, item.z)
        scene.add(mesh)
        this.$options.meshMap[item.uid] = mesh
      })
    },

    // Cuando el usuario suelta un mueble en el canvas
    onDrop(event) {
      const data = event.dataTransfer.getData('furniture')
      if (!data) return

      const item = JSON.parse(data)

      // Calculamos posición aproximada dentro de la habitación
      // basándonos en dónde hizo el drop en pantalla
      const container = this.$refs.container
      const rect = container.getBoundingClientRect()
      const xNorm = ((event.clientX - rect.left) / rect.width) * 2 - 1
      const zNorm = ((event.clientY - rect.top) / rect.height) * 2 - 1

      // Mapeamos la posición 2D de pantalla a coordenadas 3D de la habitación
      const x = xNorm * 4
      const z = zNorm * 4

      // Emitimos al padre con un uid único para poder identificar el objeto
      this.$emit('itemPlaced', {
        ...item,
        uid: Date.now(),
        x,
        z
      })
    },

    // Bucle de animación — se llama ~60 veces por segundo
    animate() {
      requestAnimationFrame(this.animate)
      this.$options.controls.update()
      this.$options.renderer.render(this.$options.scene, this.$options.camera)
    },

    onResize() {
      const container = this.$refs.container
      this.$options.camera.aspect = container.clientWidth / container.clientHeight
      this.$options.camera.updateProjectionMatrix()
      this.$options.renderer.setSize(container.clientWidth, container.clientHeight)
    }
  }
}
</script>

<style scoped>
.room-container {
  flex: 1;
  overflow: hidden;
}
</style>