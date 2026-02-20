<template>
  <img v-if="imageUrl" :src="imageUrl" class="preview-img" />
  <div v-else class="preview-placeholder">...</div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";


let sharedRenderer = null;
let sharedScene = null;
let sharedCamera = null;

function getSharedRenderer() {
  if (window.__sharedThreeRenderer) {
    sharedScene = window.__sharedThreeScene;
    sharedCamera = window.__sharedThreeCamera;
    return window.__sharedThreeRenderer;
  }

  const canvas = document.createElement("canvas");
  canvas.width = 60;
  canvas.height = 60;

  sharedRenderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true,
  });
  sharedRenderer.setSize(60, 60);

  sharedScene = new THREE.Scene();
  sharedScene.background = new THREE.Color(0xf0f0f0);

  sharedCamera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  sharedCamera.position.set(2, 2, 2);
  sharedCamera.lookAt(0, 0, 0);

  sharedScene.add(new THREE.AmbientLight(0xffffff, 0.8));
  const dir = new THREE.DirectionalLight(0xffffff, 1);
  dir.position.set(3, 5, 3);
  sharedScene.add(dir);

  window.__sharedThreeRenderer = sharedRenderer;
  window.__sharedThreeScene = sharedScene;
  window.__sharedThreeCamera = sharedCamera;

  return sharedRenderer;
}

const loader = new GLTFLoader();

const props = defineProps({
  model: { type: String, required: true },
});

const imageUrl = ref(null);

function renderPreview() {
  loader.load(
    props.model,
    (gltf) => {
      const renderer = getSharedRenderer();
      const obj = gltf.scene;

      const box = new THREE.Box3().setFromObject(obj);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      
      obj.position.sub(center);
      obj.scale.setScalar(1.5 / maxDim);

      sharedScene.add(obj);
      renderer.render(sharedScene, sharedCamera);

      imageUrl.value = renderer.domElement.toDataURL();

      sharedScene.remove(obj);
    },
    undefined,
    (err) => {
      console.error("Preview error:", props.model, err);
    }
  );
}

onMounted(() => {
  renderPreview();
});
</script>

<style scoped>
.preview-img {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  flex-shrink: 0;
  object-fit: contain;
}
.preview-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #999;
  flex-shrink: 0;
}
</style>