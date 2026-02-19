<template>
  <div
    class="room-container"
    ref="container"
    @drop="onDrop"
    @dragover.prevent
  ></div>
</template>

<script>
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

export default {
  name: "RoomScene",

  // ─────────────────────────────────────────────
  // PROPS & EMITS
  // ─────────────────────────────────────────────
  props: {
    placedItems:   { type: Array,   required: true },
    selectedFloor: { type: String,  required: true },
    selectedWall:  { type: String,  required: true },
    showGrid:      { type: Boolean, required: true },
  },

  emits: ["itemPlaced"],

  // ─────────────────────────────────────────────
  // CICLO DE VIDA
  // ─────────────────────────────────────────────
  mounted() {
    this.$options.loader  = new GLTFLoader();
    this.$options.meshMap = {};
    this.initThree();
    this.animate();
    window.addEventListener("resize", this.onResize);
    this.$refs.container.addEventListener("click",     this.onSceneClick);
    this.$refs.container.addEventListener("mousedown", this.onMouseDown);
    this.$refs.container.addEventListener("mouseup",   this.onMouseUp);
  },

  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    this.$refs.container.removeEventListener("click",     this.onSceneClick);
    this.$refs.container.removeEventListener("mousedown", this.onMouseDown);
    this.$refs.container.removeEventListener("mouseup",   this.onMouseUp);
    this.$options.renderer?.dispose();
  },

  // ─────────────────────────────────────────────
  // WATCHERS — reaccionan a cambios de props
  // ─────────────────────────────────────────────
  watch: {
    placedItems(newItems)  { this.syncItems(newItems);         },
    selectedFloor(newVal)  { this.applyFloorTexture(newVal);   },
    selectedWall(newVal)   { this.applyWallTexture(newVal);    },
    showGrid(val)          { val ? this.addGrid() : this.removeGrid(); },
  },

  methods: {

    // ═══════════════════════════════════════════
    // 1. INICIALIZACIÓN DE THREE.JS
    // ═══════════════════════════════════════════

    initThree() {
      const container = this.$refs.container;

      // Escena: el "mundo" 3D donde viven todos los objetos
      this.$options.scene = new THREE.Scene();
      this.$options.scene.background = new THREE.Color(0xf0f0f0);

      // Cámara perspectiva: simula ojo humano
      // Parámetros: fov(ángulo), aspect(proporción), near, far(límites de recorte)
      this.$options.camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
      );
      this.$options.camera.position.set(0, 8, 10);
      this.$options.camera.lookAt(0, 0, 0);

      // Renderer: dibuja la escena en un <canvas>
      this.$options.renderer = new THREE.WebGLRenderer({ antialias: true });
      this.$options.renderer.setSize(container.clientWidth, container.clientHeight);
      container.appendChild(this.$options.renderer.domElement);

      // OrbitControls: permite rotar/zoom/mover la cámara con el ratón
      this.$options.controls = new OrbitControls(
        this.$options.camera,
        this.$options.renderer.domElement
      );

      // Luces
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6); // ilumina todo por igual
      this.$options.scene.add(ambientLight);

      const dirLight = new THREE.DirectionalLight(0xffffff, 0.8); // como el sol
      dirLight.position.set(5, 10, 5);
      this.$options.scene.add(dirLight);

      this.buildRoom();
    },

    // ─────────────────────────────────────────────
    // Construye suelo y paredes de la habitación
    // ─────────────────────────────────────────────
    buildRoom() {
      const scene = this.$options.scene;

      // SUELO — PlaneGeometry es un plano plano. Lo rotamos -90° en X para que quede horizontal
      const floorGeo = new THREE.PlaneGeometry(10, 10);
      const floor    = new THREE.Mesh(floorGeo, this.buildPBRMaterial(`/textures/floors/${this.selectedFloor}`));
      floor.rotation.x = -Math.PI / 2;
      scene.add(floor);
      this.$options.floorMesh = floor; // guardamos referencia para cambiar textura después

      // PAREDES — mismo plano, diferente posición y rotación
      const wallGeo = new THREE.PlaneGeometry(10, 5);
      const wallMat = this.buildPBRMaterial(`/textures/walls/${this.selectedWall}`);

      const backWall = new THREE.Mesh(wallGeo, wallMat);
      backWall.position.set(0, 2.5, -5);

      const leftWall = new THREE.Mesh(wallGeo, wallMat);
      leftWall.position.set(-5, 2.5, 0);
      leftWall.rotation.y = Math.PI / 2;

      const rightWall = new THREE.Mesh(wallGeo, wallMat);
      rightWall.position.set(5, 2.5, 0);
      rightWall.rotation.y = -Math.PI / 2;

      scene.add(backWall, leftWall, rightWall);
      this.$options.wallMeshes = [backWall, leftWall, rightWall]; // referencia para cambiar textura
    },

    // ─────────────────────────────────────────────
    // Crea un material PBR (físicamente realista) cargando 3 texturas
    // ─────────────────────────────────────────────
    buildPBRMaterial(folder) {
      const loader       = new THREE.TextureLoader();
      const colorMap     = loader.load(`${folder}/Color.jpg`);
      const normalMap    = loader.load(`${folder}/NormalGL.jpg`);
      const roughnessMap = loader.load(`${folder}/Roughness.jpg`);

      // RepeatWrapping: la textura se repite en mosaico (no se estira)
      ;[colorMap, normalMap, roughnessMap].forEach((t) => {
        t.repeat.set(4, 4);
        t.wrapS = t.wrapT = THREE.RepeatWrapping;
      });

      return new THREE.MeshStandardMaterial({
        map:          colorMap,     // color base
        normalMap:    normalMap,    // simula relieve sin añadir polígonos
        roughnessMap: roughnessMap, // controla si brilla o es mate
      });
    },

    // ═══════════════════════════════════════════
    // 2. BUCLE DE ANIMACIÓN
    // ═══════════════════════════════════════════

    // Se ejecuta ~60 veces por segundo gracias a requestAnimationFrame
    animate() {
      requestAnimationFrame(this.animate);
      this.$options.controls.update();

      // Procesar animaciones de rotación pendientes
      Object.values(this.$options.meshMap).forEach((model) => {
        let needsUpdate = false;

        // Animación de rotación Y (lerp = interpolación suave)
        if (model.userData.targetY !== undefined) {
          const diffY = model.userData.targetY - model.rotation.y;
          if (Math.abs(diffY) > 0.01) {
            model.rotation.y += diffY * 0.15; // acercamos un 15% cada frame
            needsUpdate = true;
          } else {
            model.rotation.y = model.userData.targetY; // snap al valor final exacto
            delete model.userData.targetY;
          }
        }

        // Animación de desplazamiento X (corrección de pared)
        if (model.userData.targetX !== undefined) {
          const diffX = model.userData.targetX - model.position.x;
          if (Math.abs(diffX) > 0.005) {
            model.position.x += diffX * 0.15;
            needsUpdate = true;
          } else {
            model.position.x = model.userData.targetX;
            delete model.userData.targetX;
          }
        }

        // Animación de desplazamiento Z (corrección de pared)
        if (model.userData.targetZ !== undefined) {
          const diffZ = model.userData.targetZ - model.position.z;
          if (Math.abs(diffZ) > 0.005) {
            model.position.z += diffZ * 0.15;
            needsUpdate = true;
          } else {
            model.position.z = model.userData.targetZ;
            delete model.userData.targetZ;
          }
        }

        // Actualizar matrices internas solo si hubo movimiento
        if (needsUpdate) model.updateMatrixWorld(true);
      });

      this.$options.renderer.render(this.$options.scene, this.$options.camera);
    },

    // ═══════════════════════════════════════════
    // 3. DRAG & DROP — soltar muebles en la escena
    // ═══════════════════════════════════════════

    // El usuario suelta un elemento de la sidebar sobre el canvas
    onDrop(event) {
      const data = event.dataTransfer.getData("furniture");
      if (!data) return;

      const item      = JSON.parse(data);
      const container = this.$refs.container;
      const rect      = container.getBoundingClientRect();

      // Convertir coordenadas de pantalla a NDC (Normalized Device Coordinates: -1 a +1)
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width)  *  2 - 1,
        ((event.clientY - rect.top)  / rect.height) * -2 + 1  // Y invertida en WebGL
      );

      // Raycaster: lanza un rayo desde la cámara hacia donde apunta el ratón
      const raycaster  = new THREE.Raycaster();
      raycaster.setFromCamera(mouse, this.$options.camera);

      // Intersectamos con el plano matemático del suelo (Y=0)
      const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
      const targetPoint = new THREE.Vector3();
      const hit = raycaster.ray.intersectPlane(floorPlane, targetPoint);

      // Si el rayo no llega al suelo (cámara casi paralela), ignoramos
      if (!hit) return;

      // Limitamos la posición para que no salga de la habitación
      const clamped = this.clampToRoom(targetPoint.x, targetPoint.z);

      const newItem = {
        ...item,
        uid: Date.now(), // identificador único para este mueble concreto
        x:   clamped.x,
        z:   clamped.z,
      };

      // Notificamos al padre (App.vue) para que guarde el estado
      this.$emit("itemPlaced", newItem);
    },

    // ═══════════════════════════════════════════
    // 4. SINCRONIZACIÓN — Vue → Three.js
    // ═══════════════════════════════════════════

    // Se llama cuando placedItems cambia (watcher)
    // Mantiene los objetos 3D sincronizados con el estado de Vue
    async syncItems(items) {
      const scene   = this.$options.scene;
      const meshMap = this.$options.meshMap;

      // Convertimos UIDs a strings para comparación segura
      const currentUids = new Set(items.map((i) => String(i.uid)));

      // 1. Eliminar modelos que ya no están en la lista
      for (const uid of Object.keys(meshMap)) {
        if (!currentUids.has(uid)) {
          scene.remove(meshMap[uid]);
          delete meshMap[uid];
        }
      }

      // 2. Cargar modelos nuevos que aún no están en escena
      for (const item of items) {
        const uid = String(item.uid);
        if (!meshMap[uid]) {
          try {
            const model = await this.loadModel(item);

            // Ajustar posición según el tamaño real del modelo
            model.updateMatrixWorld(true);
            const box      = new THREE.Box3().setFromObject(model);
            const roomLimit = 5;
            let offsetX = 0, offsetZ = 0;

            if (box.min.x < -roomLimit) offsetX = -roomLimit - box.min.x;
            if (box.max.x >  roomLimit) offsetX =  roomLimit - box.max.x;
            if (box.min.z < -roomLimit) offsetZ = -roomLimit - box.min.z;
            if (box.max.z >  roomLimit) offsetZ =  roomLimit - box.max.z;

            model.position.x += offsetX;
            model.position.z += offsetZ;
            model.updateMatrixWorld(true);

            scene.add(model);
            meshMap[uid] = model;
          } catch (e) {
            // Si falla la carga del GLB, mostramos un cubo rojo de error
            const fallback = this.createFallbackMesh(item);
            scene.add(fallback);
            meshMap[uid] = fallback;
          }
        }
      }
    },

    // ─────────────────────────────────────────────
    // Carga un archivo GLB y lo envuelve en un Group
    // ─────────────────────────────────────────────
    loadModel(item) {
      return new Promise((resolve, reject) => {
        this.$options.loader.load(
          item.model,
          (gltf) => {
            // Creamos un Group contenedor — lo que rotamos y guardamos en meshMap
            const wrapper = new THREE.Group();
            const model   = gltf.scene;

            const s = item.scale || 1;
            model.scale.set(s, s, s);

            wrapper.add(model);
            wrapper.position.set(item.x, 0, item.z);
            wrapper.userData.uid = item.uid;

            // Guardamos el tamaño real para el clamping de paredes
            const box  = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3());
            wrapper.userData.halfX = size.x / 2;
            wrapper.userData.halfZ = size.z / 2;

            console.log("Modelo cargado:", item.model);
            console.log("  Tamaño real:", size.x.toFixed(2), "x", size.z.toFixed(2));

            resolve(wrapper);
          },
          undefined,
          (error) => {
            console.error("Error cargando modelo:", item.model, error);
            reject(error);
          }
        );
      });
    },

    // Cubo rojo de emergencia si el GLB falla
    createFallbackMesh(item) {
      const geo  = new THREE.BoxGeometry(1, 1, 1);
      const mat  = new THREE.MeshLambertMaterial({ color: 0xff0000 });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(item.x, 0.5, item.z);
      mesh.userData.uid = item.uid;
      return mesh;
    },

    // ═══════════════════════════════════════════
    // 5. INTERACCIÓN — click para rotar muebles
    // ═══════════════════════════════════════════

    // Detecta si el click fue real o era un drag de cámara
    onMouseDown(event) {
      this.$options.mouseDownPos = { x: event.clientX, y: event.clientY };
    },

    onMouseUp(event) {
      if (!this.$options.mouseDownPos) return;
      const dx = event.clientX - this.$options.mouseDownPos.x;
      const dy = event.clientY - this.$options.mouseDownPos.y;
      // Si el ratón se movió más de 5px, era un drag. Si no, era un click real
      this.$options.isDragging = Math.sqrt(dx * dx + dy * dy) > 5;
    },

    // Detecta qué mueble fue clickado usando Raycasting
    onSceneClick(event) {
      if (this.$options.isDragging) return; // ignorar si era drag de cámara

      const container = this.$refs.container;
      const rect      = container.getBoundingClientRect();

      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width)  *  2 - 1,
        ((event.clientY - rect.top)  / rect.height) * -2 + 1
      );

      const raycaster = new THREE.Raycaster();
      raycaster.setFromCamera(mouse, this.$options.camera);

      // Intersectamos con todos los modelos colocados
      // true = buscar también en los hijos del grupo (necesario para GLB)
      const models     = Object.values(this.$options.meshMap);
      const intersects = raycaster.intersectObjects(models, true);

      if (intersects.length > 0) {
        // El objeto clickado puede ser un hijo del modelo — subimos al padre raíz
        const rootModel = this.getRootModel(intersects[0].object);
        if (rootModel) this.rotateModel(rootModel);
      }
    },

    // Sube por object.parent hasta encontrar el wrapper registrado en meshMap
    getRootModel(object) {
      const models = Object.values(this.$options.meshMap);
      let current  = object;
      while (current) {
        if (models.includes(current)) return current;
        current = current.parent;
      }
      return null;
    },

    // Rota el modelo 90° y calcula si hay que desplazarlo para no atravesar paredes
    rotateModel(model) {
      const futureRotY = (model.userData.targetY ?? model.rotation.y) + Math.PI / 2;

      // 1. Simulamos la rotación futura temporalmente
      const previousRotY = model.rotation.y;
      model.rotation.y   = futureRotY;
      model.updateMatrixWorld(true);

      // 2. Medimos el bounding box con la rotación futura aplicada
      const box      = new THREE.Box3().setFromObject(model);
      const roomLimit = 5;
      let offsetX = 0, offsetZ = 0;

      if (box.min.x < -roomLimit) offsetX = -roomLimit - box.min.x;
      if (box.max.x >  roomLimit) offsetX =  roomLimit - box.max.x;
      if (box.min.z < -roomLimit) offsetZ = -roomLimit - box.min.z;
      if (box.max.z >  roomLimit) offsetZ =  roomLimit - box.max.z;

      // 3. Restauramos la rotación actual (el lerp la llevará al destino)
      model.rotation.y = previousRotY;
      model.updateMatrixWorld(true);

      // 4. Guardamos destinos — el bucle animate() los interpolará suavemente
      model.userData.targetY = futureRotY;
      model.userData.targetX = model.position.x + offsetX;
      model.userData.targetZ = model.position.z + offsetZ;
    },

    // ═══════════════════════════════════════════
    // 6. UTILIDADES — grid, texturas, límites
    // ═══════════════════════════════════════════

    // Limita x,z dentro de los muros de la habitación
    clampToRoom(x, z, halfX = 0, halfZ = 0) {
      const roomLimit = 5;
      return {
        x: Math.max(-roomLimit + halfX, Math.min(roomLimit - halfX, x)),
        z: Math.max(-roomLimit + halfZ, Math.min(roomLimit - halfZ, z)),
      };
    },

    addGrid() {
      if (this.$options.gridHelper) return;
      // GridHelper(tamaño, divisiones, colorLineas, colorCentro)
      const grid = new THREE.GridHelper(10, 10, 0x555555, 0xaaaaaa);
      grid.position.y = 0.01; // ligeramente sobre el suelo para evitar z-fighting
      this.$options.scene.add(grid);
      this.$options.gridHelper = grid;
    },

    removeGrid() {
      if (!this.$options.gridHelper) return;
      this.$options.scene.remove(this.$options.gridHelper);
      this.$options.gridHelper = null;
    },

    applyFloorTexture(materialId) {
      if (!this.$options.floorMesh) return;
      this.$options.floorMesh.material = this.buildPBRMaterial(`/textures/floors/${materialId}`);
    },

    applyWallTexture(materialId) {
      if (!this.$options.wallMeshes) return;
      const mat = this.buildPBRMaterial(`/textures/walls/${materialId}`);
      this.$options.wallMeshes.forEach((wall) => (wall.material = mat));
    },

    onResize() {
      const container = this.$refs.container;
      this.$options.camera.aspect = container.clientWidth / container.clientHeight;
      this.$options.camera.updateProjectionMatrix();
      this.$options.renderer.setSize(container.clientWidth, container.clientHeight);
    },
  },
};
</script>

<style scoped>
.room-container {
  flex: 1;
  overflow: hidden;
}
</style>