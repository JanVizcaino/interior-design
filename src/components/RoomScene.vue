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

  props: {
    placedItems: { type: Array, required: true },
    selectedFloor: { type: String, required: true },
    selectedWall: { type: String, required: true },
  },

  emits: ["itemPlaced"],

  mounted() {
    this.$options.loader = new GLTFLoader();
    this.$options.meshMap = {};
    this.initThree();
    this.animate();
    window.addEventListener("resize", this.onResize);
  },

  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    this.$options.renderer?.dispose(); // ← corregido
  },

  watch: {
    placedItems(newItems) {
      this.syncItems(newItems);
    },

    selectedFloor(newVal) {
      this.applyFloorTexture(newVal);
    },
    selectedWall(newVal) {
      this.applyWallTexture(newVal);
    },
  },

  methods: {
    buildPBRMaterial(folder) {
      const loader = new THREE.TextureLoader();

      const colorMap = loader.load(`${folder}/Color.jpg`);
      const normalMap = loader.load(`${folder}/NormalGL.jpg`);
      const roughnessMap = loader.load(`${folder}/Roughness.jpg`);

      [colorMap, normalMap, roughnessMap].forEach((t) => {
        t.repeat.set(4, 4);
        t.wrapS = t.wrapT = THREE.RepeatWrapping;
      });

      return new THREE.MeshStandardMaterial({
        map: colorMap,
        normalMap: normalMap,
        roughnessMap: roughnessMap,
      });
    },

    applyFloorTexture(materialId) {
      if (!this.$options.floorMesh) return;
      const folder = `/textures/floors/${materialId}`;
      this.$options.floorMesh.material = this.buildPBRMaterial(folder);
    },

    applyWallTexture(materialId) {
      if (!this.$options.wallMeshes) return;
      const folder = `/textures/walls/${materialId}`;
      const mat = this.buildPBRMaterial(folder);
      this.$options.wallMeshes.forEach((wall) => (wall.material = mat));
    },

    initThree() {
      const container = this.$refs.container;

      this.$options.scene = new THREE.Scene();
      this.$options.scene.background = new THREE.Color(0xf0f0f0);

      this.$options.camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.1,
        1000,
      );
      this.$options.camera.position.set(0, 8, 10);
      this.$options.camera.lookAt(0, 0, 0);

      this.$options.renderer = new THREE.WebGLRenderer({ antialias: true });
      this.$options.renderer.setSize(
        container.clientWidth,
        container.clientHeight,
      );
      container.appendChild(this.$options.renderer.domElement);

      this.$options.controls = new OrbitControls(
        this.$options.camera,
        this.$options.renderer.domElement,
      );

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      this.$options.scene.add(ambientLight);

      const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
      dirLight.position.set(5, 10, 5);
      this.$options.scene.add(dirLight);

      this.buildRoom();
    },

    buildRoom() {
      const scene = this.$options.scene;

      const floorGeo = new THREE.PlaneGeometry(10, 10);
      const floor = new THREE.Mesh(
        floorGeo,
        this.buildPBRMaterial(`/textures/floors/${this.selectedFloor}`),
      );
      floor.rotation.x = -Math.PI / 2;
      scene.add(floor);
      this.$options.floorMesh = floor;

      const wallGeo = new THREE.PlaneGeometry(10, 5);
      const wallMat = this.buildPBRMaterial(
        `/textures/walls/${this.selectedWall}`,
      );

      const backWall = new THREE.Mesh(wallGeo, wallMat);
      backWall.position.set(0, 2.5, -5);

      const leftWall = new THREE.Mesh(wallGeo, wallMat);
      leftWall.position.set(-5, 2.5, 0);
      leftWall.rotation.y = Math.PI / 2;

      const rightWall = new THREE.Mesh(wallGeo, wallMat);
      rightWall.position.set(5, 2.5, 0);
      rightWall.rotation.y = -Math.PI / 2;

      scene.add(backWall, leftWall, rightWall);
      this.$options.wallMeshes = [backWall, leftWall, rightWall]; 
    },

    loadModel(item) {
      return new Promise((resolve, reject) => {
        this.$options.loader.load(
          item.model,
          (gltf) => {
            const model = gltf.scene;
            const s = item.scale || 1;
            model.scale.set(s, s, s);
            model.position.set(item.x, 0, item.z);
            model.userData.uid = item.uid;
            resolve(model);
          },
          undefined,
          (error) => {
            console.error("Error cargando modelo:", item.model, error);
            reject(error);
          },
        );
      });
    },

    onDrop(event) {
      const data = event.dataTransfer.getData("furniture");
      if (!data) return;

      const item = JSON.parse(data);
      const container = this.$refs.container;
      const rect = container.getBoundingClientRect();

      const xNorm = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      const zNorm = ((event.clientY - rect.top) / rect.height) * 2 - 1;

      const newItem = {
        ...item,
        uid: Date.now(),
        x: xNorm * 4,
        z: zNorm * 4,
      };

      this.$emit("itemPlaced", newItem);

      this.loadModel(newItem)
        .then((model) => {
          console.log("✅ Modelo cargado y añadido");
          this.$options.scene.add(model);
          this.$options.meshMap[newItem.uid] = model;
        })
        .catch((e) => {
          console.error("❌ Falló GLB, usando fallback", e);
          const fallback = this.createFallbackMesh(newItem);
          this.$options.scene.add(fallback);
          this.$options.meshMap[newItem.uid] = fallback;
        });
    },

    async syncItems(items) {
      console.log("3. syncItems llamado con:", items.length, "items");
      const scene = this.$options.scene;
      const meshMap = this.$options.meshMap;

      const currentUids = new Set(items.map((i) => i.uid));
      const sceneUids = new Set(Object.keys(meshMap).map(Number));

      for (const uid of sceneUids) {
        if (!currentUids.has(uid)) {
          scene.remove(meshMap[uid]);
          delete meshMap[uid];
        }
      }

      for (const item of items) {
        if (!meshMap[item.uid]) {
          console.log("4. Cargando modelo:", item.model);
          try {
            const model = await this.loadModel(item);
            scene.add(model);
            meshMap[item.uid] = model;
            console.log("5. Modelo añadido a escena en:", item.x, item.z);
          } catch (e) {
            console.error("5. ERROR, usando fallback:", e);
            const fallback = this.createFallbackMesh(item);
            scene.add(fallback);
            meshMap[item.uid] = fallback;
          }
        }
      }
    },

    createFallbackMesh(item) {
      const geo = new THREE.BoxGeometry(1, 1, 1);
      const mat = new THREE.MeshLambertMaterial({ color: 0xff0000 });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(item.x, 0.5, item.z);
      mesh.userData.uid = item.uid;
      return mesh;
    },

    animate() {
      requestAnimationFrame(this.animate);
      this.$options.controls.update();
      this.$options.renderer.render(this.$options.scene, this.$options.camera);
    },

    onResize() {
      const container = this.$refs.container;
      this.$options.camera.aspect =
        container.clientWidth / container.clientHeight;
      this.$options.camera.updateProjectionMatrix();
      this.$options.renderer.setSize(
        container.clientWidth,
        container.clientHeight,
      );
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
