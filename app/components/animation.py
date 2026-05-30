import json
import streamlit as st
import streamlit.components.v1 as components

def build_animation_html(results, num_nozzles, simulation_time, rejected_count):
    animation_data = (
        results[
            [
                "customer_id",
                "arrival_time",
                "service_start",
                "departure_time",
                "waiting_time",
                "service_time",
            ]
        ]
        .sort_values("arrival_time")
        .head(120)
        .to_dict(orient="records")
    )

    vehicles_json = json.dumps(animation_data)

    html = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0;
      background: #f8fafc;
      color: #111827;
      font-family: Arial, sans-serif;
    }

    .sim-shell {
      border: 1px solid #d1d5db;
      border-radius: 8px;
      overflow: hidden;
      background: #ffffff;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 12px;
      background: #ffffff;
      border-bottom: 1px solid #d1d5db;
    }

    .toolbar button {
      border: 1px solid #111827;
      border-radius: 6px;
      background: #111827;
      color: #ffffff;
      cursor: pointer;
      font-size: 13px;
      line-height: 1;
      padding: 8px 12px;
    }

    .toolbar button.secondary {
      background: #ffffff;
      color: #111827;
    }

    .toolbar input {
      flex: 1;
      min-width: 120px;
    }

    .readout {
      min-width: 120px;
      font-size: 13px;
      color: #4b5563;
      text-align: right;
    }

    #scene {
      position: relative;
      height: 500px;
      background: #e5e7eb;
    }

    #scene canvas {
      display: block;
    }

    .hint {
      position: absolute;
      left: 12px;
      bottom: 12px;
      border-radius: 6px;
      background: rgba(17, 24, 39, 0.72);
      color: #ffffff;
      font-size: 12px;
      padding: 7px 9px;
      pointer-events: none;
    }

    #error {
      display: none;
      position: absolute;
      inset: 0;
      align-items: center;
      justify-content: center;
      background: #fee2e2;
      color: #7f1d1d;
      font-size: 14px;
      padding: 24px;
      text-align: center;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      border-top: 1px solid #d1d5db;
      background: #ffffff;
    }

    .stat {
      padding: 10px 12px;
      border-right: 1px solid #d1d5db;
    }

    .stat:last-child {
      border-right: 0;
    }

    .stat-label {
      color: #6b7280;
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 700;
    }

    .stat-value {
      margin-top: 4px;
      font-size: 18px;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <div class="sim-shell">
    <div class="toolbar">
      <button id="playBtn">Play</button>
      <button id="resetBtn" class="secondary">Reset</button>
      <input type="range" id="timeline" min="0" step="0.1" value="0">
      <div class="readout">Time: <span id="timeReadout">0.0</span> min</div>
    </div>
    <div id="scene">
      <div id="error"></div>
      <div class="hint">Left click + drag to rotate • Scroll to zoom • Right click to pan</div>
    </div>
    <div class="stats">
      <div class="stat">
        <div class="stat-label">Total Motors</div>
        <div class="stat-value" id="statTotal">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Wait Queue</div>
        <div class="stat-value" id="statQueue">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Being Served</div>
        <div class="stat-value" id="statServing">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Finished</div>
        <div class="stat-value" id="statFinished">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Rejected</div>
        <div class="stat-value">__TOTAL_REJECTED__</div>
      </div>
    </div>
  </div>

  <script type="importmap">
    {
      "imports": {
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
      }
    }
  </script>

  <script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

    const rawVehicles = __VEHICLES__;
    const visualDuration = __SIMULATION_TIME__;
    const numNozzles = __NUM_NOZZLES__;

    const VISUAL = {
      playbackRate: 1.5,
      enterDuration: 0.3,
      exitDuration: 0.3,
      unitScale: 0.5,
    };

    const vehicles = rawVehicles.map(v => {
      const waitStartVisual = v.arrival_time + VISUAL.enterDuration;
      const serviceStartVisual = v.service_start;
      const nozzleClearVisual = v.departure_time;
      const exitClearVisual = v.departure_time + VISUAL.exitDuration;

      return {
        ...v,
        waitStartVisual,
        serviceStartVisual,
        nozzleClearVisual,
        exitClearVisual
      };
    });

    const sceneHost = document.getElementById("scene");
    const playButton = document.getElementById("playBtn");
    const resetButton = document.getElementById("resetBtn");
    const timeline = document.getElementById("timeline");
    const timeReadout = document.getElementById("timeReadout");
    const errorBox = document.getElementById("error");

    const statTotal = document.getElementById("statTotal");
    const statQueue = document.getElementById("statQueue");
    const statServing = document.getElementById("statServing");
    const statFinished = document.getElementById("statFinished");

    timeline.max = visualDuration;

    if (!vehicles.length) {
      errorBox.style.display = "flex";
      errorBox.textContent = "No valid data to visualize.";
    } else {

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, sceneHost.clientWidth / 500, 0.1, 100);
    camera.position.set(2, 6, 12);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(sceneHost.clientWidth, 500);
    renderer.setPixelRatio(window.devicePixelRatio);
    sceneHost.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 - 0.05;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 5);
    scene.add(dirLight);

    const groundGeo = new THREE.PlaneGeometry(30, 20);
    const groundMat = new THREE.MeshLambertMaterial({ color: 0x9ca3af });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    scene.add(ground);

    const islandGeo = new THREE.BoxGeometry(4, 0.2, 8);
    const islandMat = new THREE.MeshLambertMaterial({ color: 0xd1d5db });
    const island = new THREE.Mesh(islandGeo, islandMat);
    island.position.set(1.5, 0.1, 0);
    scene.add(island);

    const roofGeo = new THREE.BoxGeometry(5, 0.2, 9);
    const roofMat = new THREE.MeshLambertMaterial({ color: 0xef4444 });
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.position.set(1.5, 3, 0);
    scene.add(roof);

    for (let i = 0; i < 4; i++) {
      const pillarGeo = new THREE.CylinderGeometry(0.1, 0.1, 3);
      const pillarMat = new THREE.MeshLambertMaterial({ color: 0xffffff });
      const pillar = new THREE.Mesh(pillarGeo, pillarMat);
      pillar.position.set(1.5 + (i % 2 === 0 ? 2 : -2), 1.5, (i < 2 ? 4 : -4));
      scene.add(pillar);
    }

    const nozzleSlots = [];
    for (let i = 0; i < numNozzles; i++) {
      const dispGeo = new THREE.BoxGeometry(0.6, 1.2, 0.4);
      const dispMat = new THREE.MeshLambertMaterial({ color: 0x3b82f6 });
      const disp = new THREE.Mesh(dispGeo, dispMat);
      
      const zPos = -2 + (i * 1.3);
      disp.position.set(1.5, 0.6 + 0.2, zPos);
      scene.add(disp);
      nozzleSlots.push({
        z: zPos,
        occupiedBy: null
      });
    }

    const vehicleModels = new Map();
    const cycleColors = [0xef4444, 0x3b82f6, 0x10b981, 0xf59e0b, 0x8b5cf6, 0xec4899];

    function createMotorcycle(colorHex) {
      const group = new THREE.Group();
      
      const bodyGeo = new THREE.BoxGeometry(0.8, 0.5, 0.4);
      const bodyMat = new THREE.MeshLambertMaterial({ color: colorHex });
      const body = new THREE.Mesh(bodyGeo, bodyMat);
      body.position.y = 0.4;
      group.add(body);

      const wheelGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.1, 16);
      const wheelMat = new THREE.MeshLambertMaterial({ color: 0x111827 });
      
      const frontWheel = new THREE.Mesh(wheelGeo, wheelMat);
      frontWheel.rotation.x = Math.PI / 2;
      frontWheel.position.set(0.35, 0.2, 0);
      group.add(frontWheel);

      const backWheel = new THREE.Mesh(wheelGeo, wheelMat);
      backWheel.rotation.x = Math.PI / 2;
      backWheel.position.set(-0.35, 0.2, 0);
      group.add(backWheel);

      const headGeo = new THREE.BoxGeometry(0.3, 0.4, 0.3);
      const headMat = new THREE.MeshLambertMaterial({ color: 0xfca5a5 });
      const head = new THREE.Mesh(headGeo, headMat);
      head.position.set(0, 0.8, 0);
      group.add(head);

      return group;
    }

    function setupVehicles() {
      vehicles.forEach((v, index) => {
        const color = cycleColors[index % cycleColors.length];
        const model = createMotorcycle(color);
        model.visible = false;
        scene.add(model);
        vehicleModels.set(v.customer_id, model);
      });
    }

    let playing = false;
    let currentTime = 0;
    let lastFrame = null;

    function lerp(start, end, t) {
      return start * (1 - t) + end * t;
    }

    function serviceZ(slotIndex) {
      if (slotIndex < 0 || slotIndex >= nozzleSlots.length) return 0;
      return nozzleSlots[slotIndex].z;
    }

    function rawActiveX(vehicle, state) {
      if (state === "entering") {
        const progress = (currentTime - vehicle.arrival_time) / VISUAL.enterDuration;
        return lerp(-12.5, -4.5, progress);
      }
      return -4.5;
    }

    function renderSimulation(time) {
      currentTime = Math.max(0, Math.min(time, visualDuration));
      timeline.value = currentTime;
      timeReadout.textContent = currentTime.toFixed(1);

      let waitCount = 0;
      let servingCount = 0;
      let finishedCount = 0;
      let activeX = new Map();

      nozzleSlots.forEach(slot => slot.occupiedBy = null);

      const activeVehicles = [];

      vehicles.forEach(vehicle => {
        let state = "hidden";
        if (currentTime >= vehicle.arrival_time && currentTime < vehicle.waitStartVisual) {
          state = "entering";
          activeVehicles.push({ vehicle, state });
        } else if (currentTime >= vehicle.waitStartVisual && currentTime < vehicle.serviceStartVisual) {
          state = "waiting";
          waitCount++;
          activeVehicles.push({ vehicle, state });
        } else if (currentTime >= vehicle.serviceStartVisual && currentTime < vehicle.nozzleClearVisual) {
          state = "serving";
          servingCount++;
          const nozzleIndex = servingCount % numNozzles; 
          nozzleSlots[nozzleIndex].occupiedBy = vehicle.customer_id;
          activeVehicles.push({ vehicle, state });
        } else if (currentTime >= vehicle.nozzleClearVisual && currentTime < vehicle.exitClearVisual) {
          state = "leaving";
          activeVehicles.push({ vehicle, state });
        } else if (currentTime >= vehicle.exitClearVisual) {
          state = "finished";
          finishedCount++;
        }

        const model = vehicleModels.get(vehicle.customer_id);
        if (state === "hidden" || state === "finished") {
          model.visible = false;
        } else {
          model.userData.state = state;
        }
      });

      statTotal.textContent = vehicles.length;
      statQueue.textContent = waitCount;
      statServing.textContent = servingCount;
      statFinished.textContent = finishedCount;

      const waitList = activeVehicles.filter(item => item.state === "waiting").sort((a,b) => a.vehicle.arrival_time - b.vehicle.arrival_time);
      
      waitList.forEach((item, idx) => {
        activeX.set(item.vehicle.customer_id, -3 - (idx * 1.2));
      });

      activeVehicles.forEach(item => {
        const { vehicle, state } = item;
        const model = vehicleModels.get(vehicle.customer_id);
        let visible = true;
        let x = 0;
        let z = 0;
        let rotation = -Math.PI / 2;

        if (state === "entering") {
          x = rawActiveX(vehicle, state);
          z = 0;
        } else if (state === "waiting") {
          x = activeX.get(vehicle.customer_id) ?? rawActiveX(vehicle, state);
          z = 0;
        } else if (state === "serving") {
          const nozzleSlot = 0;
          x = activeX.get(vehicle.customer_id) ?? rawActiveX(vehicle, state);
          z = serviceZ(nozzleSlot);
        } else if (state === "leaving") {
          const slot = 0;
          const progress = (currentTime - vehicle.nozzleClearVisual) / VISUAL.exitDuration;
          x = lerp(9.2, 16.5, progress);
          z = lerp(serviceZ(slot), -1.5, progress);
          rotation = lerp(0, -0.22, progress);
        }

        model.visible = visible;
        model.position.set(x, 0, z);
        model.rotation.y = rotation;
      });
    }

    function animate(timestamp) {
      if (lastFrame === null) lastFrame = timestamp;
      const deltaSeconds = (timestamp - lastFrame) / 1000;
      lastFrame = timestamp;

      if (playing) {
        const nextTime = currentTime + deltaSeconds * VISUAL.playbackRate;

        if (nextTime >= visualDuration) {
          playing = false;
          playButton.textContent = "Play";
          renderSimulation(visualDuration);
        } else {
          renderSimulation(nextTime);
        }
      }

      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }

    playButton.addEventListener("click", () => {
      playing = !playing;
      playButton.textContent = playing ? "Pause" : "Play";
      lastFrame = null;
    });

    resetButton.addEventListener("click", () => {
      playing = false;
      playButton.textContent = "Play";
      renderSimulation(0);
    });

    timeline.addEventListener("input", (event) => {
      playing = false;
      playButton.textContent = "Play";
      renderSimulation(Number(event.target.value));
    });

    window.addEventListener("resize", () => {
      camera.aspect = sceneHost.clientWidth / 500;
      camera.updateProjectionMatrix();
      renderer.setSize(sceneHost.clientWidth, 500);
    });

    setupVehicles();
    renderSimulation(0);
    requestAnimationFrame(animate);
    }
  </script>
</body>
</html>
"""

    return (
        html.replace("__VEHICLES__", vehicles_json)
        .replace("__SIMULATION_TIME__", f"{simulation_time:.4f}")
        .replace("__NUM_NOZZLES__", str(num_nozzles))
        .replace("__TOTAL_VISUALIZED__", str(len(animation_data)))
        .replace("__TOTAL_REJECTED__", str(int(rejected_count)))
    )


def show_animation(results, queue_log, num_nozzles, simulation_time, rejected_count):
    st.subheader("Animasi Simulasi Pengisian Bensin")
    if results.empty:
        st.info("Belum ada hasil customer yang bisa divisualisasikan.")
        return

    if len(results) > 120:
        st.caption("Animasi menampilkan 120 motor pertama agar browser tetap ringan.")

    animation_html = build_animation_html(results, num_nozzles, simulation_time, rejected_count)
    components.html(animation_html, height=650, scrolling=False)