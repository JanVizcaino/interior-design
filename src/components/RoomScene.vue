<template>
  <div
    class="flex-1 overflow-hidden"
    ref="container"
    @drop="onDrop"
    @dragover.prevent
  ></div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const props = defineProps({
  placedItems: { type: Array, required: true },
  selectedFloor: { type: String, required: true },
  selectedWall: { type: String, required: true },
  showGrid: { type: Boolean, required: true },
});

const emit = defineEmits(["itemPlaced"]);
const container = ref(null); 

let scene, camera, renderer, controls;
let floorMesh = null;
let wallMeshes = [];
let gridHelper = null;
let mouseDownPos = null;
let isDragging = false;

const loader = new GLTFLoader();
const meshMap = {}; 

onMounted(() => {
  initThree();
  animate();
  window.addEventListener("resize", onResize);
  container.value.addEventListener("click", onSceneClick);
  container.value.addEventListener("mousedown", onMouseDown);
  container.value.addEventListener("mouseup", onMouseUp);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  container.value.removeEventListener("click", onSceneClick);
  container.value.removeEventListener("mousedown", onMouseDown);
  container.value.removeEventListener("mouseup", onMouseUp);
  
  if (renderer) {
    renderer.forceContextLoss(); 
    renderer.dispose();           
    renderer.domElement.remove(); 
  }
});

watch(() => props.placedItems, (newItems) => syncItems(newItems));
watch(() => props.selectedFloor, (newVal) => applyFloorTexture(newVal));
watch(() => props.selectedWall, (newVal) => applyWallTexture(newVal));
watch(() => props.showGrid, (val) => (val ? addGrid() : removeGrid()));

function initThree() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  camera = new THREE.PerspectiveCamera(
    60,
    container.value.clientWidth / container.value.clientHeight,
    0.1,
    1000
  );
  camera.position.set(0, 8, 10);
  camera.lookAt(0, 0, 0);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
  container.value.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(5, 10, 5);
  scene.add(dirLight);

  buildRoom();
}

function buildRoom() {
  const floorGeo = new THREE.PlaneGeometry(10, 10);
  floorMesh = new THREE.Mesh(floorGeo, buildPBRMaterial(`/textures/floors/${props.selectedFloor}`));
  floorMesh.rotation.x = -Math.PI / 2;
  scene.add(floorMesh);

  const wallGeo = new THREE.PlaneGeometry(10, 5);
  const wallMat = buildPBRMaterial(`/textures/walls/${props.selectedWall}`);

  const backWall = new THREE.Mesh(wallGeo, wallMat);
  backWall.position.set(0, 2.5, -5);

  const leftWall = new THREE.Mesh(wallGeo, wallMat);
  leftWall.position.set(-5, 2.5, 0);
  leftWall.rotation.y = Math.PI / 2;

  const rightWall = new THREE.Mesh(wallGeo, wallMat);
  rightWall.position.set(5, 2.5, 0);
  rightWall.rotation.y = -Math.PI / 2;

  wallMeshes = [backWall, leftWall, rightWall];
  scene.add(...wallMeshes);
}

function buildPBRMaterial(folder) {
  const texLoader = new THREE.TextureLoader();
  const colorMap = texLoader.load(`${folder}/Color.jpg`);
  const normalMap = texLoader.load(`${folder}/NormalGL.jpg`);
  const roughnessMap = texLoader.load(`${folder}/Roughness.jpg`);

  [colorMap, normalMap, roughnessMap].forEach((t) => {
    t.repeat.set(4, 4);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
  });

  return new THREE.MeshStandardMaterial({
    map: colorMap,
    normalMap: normalMap,
    roughnessMap: roughnessMap,
  });
}

function animate() {
  requestAnimationFrame(animate);
  if (controls) controls.update();

  Object.values(meshMap).forEach((model) => {
    let needsUpdate = false;

    if (model.userData.targetY !== undefined) {
      const diffY = model.userData.targetY - model.rotation.y;
      if (Math.abs(diffY) > 0.01) {
        model.rotation.y += diffY * 0.15;
        needsUpdate = true;
      } else {
        model.rotation.y = model.userData.targetY;
        delete model.userData.targetY;
      }
    }

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

    if (needsUpdate) model.updateMatrixWorld(true);
  });

  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

function onDrop(event) {
  const data = event.dataTransfer.getData("furniture");
  if (!data) return;

  const item = JSON.parse(data);
  const rect = container.value.getBoundingClientRect();

  const mouse = new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    ((event.clientY - rect.top) / rect.height) * -2 + 1
  );

  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(mouse, camera);

  const floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  const targetPoint = new THREE.Vector3();
  const hit = raycaster.ray.intersectPlane(floorPlane, targetPoint);

  if (!hit) return;

  const clamped = clampToRoom(targetPoint.x, targetPoint.z);

  const newItem = {
    ...item,
    uid: Date.now(),
    x: clamped.x,
    z: clamped.z,
  };

  emit("itemPlaced", newItem);
}

async function syncItems(items) {
  const currentUids = new Set(items.map((i) => String(i.uid)));

  for (const uid of Object.keys(meshMap)) {
    if (!currentUids.has(uid)) {
      scene.remove(meshMap[uid]);
      delete meshMap[uid];
    }
  }

  for (const item of items) {
    const uid = String(item.uid);
    if (!meshMap[uid]) {
      try {
        const model = await loadModel(item);

        model.updateMatrixWorld(true);
        const box = new THREE.Box3().setFromObject(model);
        const roomLimit = 5;
        let offsetX = 0, offsetZ = 0;

        if (box.min.x < -roomLimit) offsetX = -roomLimit - box.min.x;
        if (box.max.x > roomLimit) offsetX = roomLimit - box.max.x;
        if (box.min.z < -roomLimit) offsetZ = -roomLimit - box.min.z;
        if (box.max.z > roomLimit) offsetZ = roomLimit - box.max.z;

        model.position.x += offsetX;
        model.position.z += offsetZ;
        model.updateMatrixWorld(true);

        scene.add(model);
        meshMap[uid] = model;
      } catch (e) {
        const fallback = createFallbackMesh(item);
        scene.add(fallback);
        meshMap[uid] = fallback;
      }
    }
  }
}

function loadModel(item) {
  return new Promise((resolve, reject) => {
    loader.load(
      item.model,
      (gltf) => {
        const wrapper = new THREE.Group();
        const model = gltf.scene;

        const s = item.scale || 1;
        model.scale.set(s, s, s);

        wrapper.add(model);
        wrapper.position.set(item.x, 0, item.z);
        wrapper.userData.uid = item.uid;

        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        wrapper.userData.halfX = size.x / 2;
        wrapper.userData.halfZ = size.z / 2;

        resolve(wrapper);
      },
      undefined,
      (error) => reject(error)
    );
  });
}

function createFallbackMesh(item) {
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mat = new THREE.MeshLambertMaterial({ color: 0xff0000 });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(item.x, 0.5, item.z);
  mesh.userData.uid = item.uid;
  return mesh;
}

function onMouseDown(event) {
  mouseDownPos = { x: event.clientX, y: event.clientY };
}

function onMouseUp(event) {
  if (!mouseDownPos) return;
  const dx = event.clientX - mouseDownPos.x;
  const dy = event.clientY - mouseDownPos.y;
  isDragging = Math.sqrt(dx * dx + dy * dy) > 5;
}

function onSceneClick(event) {
  if (isDragging) return;

  const rect = container.value.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    ((event.clientY - rect.top) / rect.height) * -2 + 1
  );

  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(mouse, camera);

  const models = Object.values(meshMap);
  const intersects = raycaster.intersectObjects(models, true);

  if (intersects.length > 0) {
    const rootModel = getRootModel(intersects[0].object);
    if (rootModel) rotateModel(rootModel);
  }
}

function getRootModel(object) {
  const models = Object.values(meshMap);
  let current = object;
  while (current) {
    if (models.includes(current)) return current;
    current = current.parent;
  }
  return null;
}

function rotateModel(model) {
  const futureRotY = (model.userData.targetY ?? model.rotation.y) + Math.PI / 2;

  const previousRotY = model.rotation.y;
  model.rotation.y = futureRotY;
  model.updateMatrixWorld(true);

  const box = new THREE.Box3().setFromObject(model);
  const roomLimit = 5;
  let offsetX = 0, offsetZ = 0;

  if (box.min.x < -roomLimit) offsetX = -roomLimit - box.min.x;
  if (box.max.x > roomLimit) offsetX = roomLimit - box.max.x;
  if (box.min.z < -roomLimit) offsetZ = -roomLimit - box.min.z;
  if (box.max.z > roomLimit) offsetZ = roomLimit - box.max.z;

  model.rotation.y = previousRotY;
  model.updateMatrixWorld(true);

  model.userData.targetY = futureRotY;
  model.userData.targetX = model.position.x + offsetX;
  model.userData.targetZ = model.position.z + offsetZ;
}

function clampToRoom(x, z, halfX = 0, halfZ = 0) {
  const roomLimit = 5;
  return {
    x: Math.max(-roomLimit + halfX, Math.min(roomLimit - halfX, x)),
    z: Math.max(-roomLimit + halfZ, Math.min(roomLimit - halfZ, z)),
  };
}

function addGrid() {
  if (gridHelper) return;
  gridHelper = new THREE.GridHelper(10, 10, 0x555555, 0xaaaaaa);
  gridHelper.position.y = 0.01;
  scene.add(gridHelper);
}

function removeGrid() {
  if (!gridHelper) return;
  scene.remove(gridHelper);
  gridHelper = null;
}

function applyFloorTexture(materialId) {
  if (!floorMesh) return;
  floorMesh.material = buildPBRMaterial(`/textures/floors/${materialId}`);
}

function applyWallTexture(materialId) {
  if (wallMeshes.length === 0) return;
  const mat = buildPBRMaterial(`/textures/walls/${materialId}`);
  wallMeshes.forEach((wall) => (wall.material = mat));
}

function onResize() {
  if (!container.value || !camera || !renderer) return;
  camera.aspect = container.value.clientWidth / container.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
}
</script>