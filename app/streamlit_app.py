from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "TPS fulltank - Rekap.csv"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from simulation.engine import run_mg1_simulation


st.set_page_config(
    page_title="Simulasi Antrian Pertamax Motor",
    layout="wide",
)


@st.cache_data
def load_observation_data():
    data = pd.read_csv(DATA_PATH)

    data["_service_seconds"] = pd.to_numeric(
        data["Rerata Waktu Pelayanan (s)"].replace("-", np.nan),
        errors="coerce",
    )
    data["_interarrival_seconds"] = pd.to_numeric(
        data["Interarrival Time (s)"].replace("-", np.nan),
        errors="coerce",
    )

    calibration_data = data.dropna(subset=["_service_seconds", "_interarrival_seconds"])

    recap_service_times = (calibration_data["_service_seconds"] / 60).tolist()
    raw_service_times = []
    for service_path in sorted((ROOT_DIR / "data").glob("sesi*/*Waktu Pelayanan.csv")):
        service_data = pd.read_csv(service_path)
        if "Detik" not in service_data.columns:
            continue
        service_seconds = pd.to_numeric(service_data["Detik"], errors="coerce").dropna()
        raw_service_times.extend((service_seconds[service_seconds > 0] / 60).tolist())

    service_times = raw_service_times or recap_service_times
    mean_interarrival_minute = calibration_data["_interarrival_seconds"].mean() / 60
    arrival_rate = 1 / mean_interarrival_minute

    return data.drop(columns=["_service_seconds", "_interarrival_seconds"]), service_times, arrival_rate


def run_simulation(arrival_rate, service_times, simulation_time, seed, num_nozzles):
    return run_mg1_simulation(
        arrival_rate=arrival_rate,
        service_times=service_times,
        simulation_time=simulation_time,
        seed=seed,
        num_servers=num_nozzles,
        max_queue=15,
        service_distribution="gamma",
    )


def metric_value(summary, key, suffix="", decimals=2):
    value = summary.get(key)
    if value is None:
        return "-"
    if isinstance(value, (int, np.integer)):
        return f"{value}{suffix}"
    return f"{value:.{decimals}f}{suffix}"


def show_summary(summary):
    cols = st.columns(4)
    cols[0].metric("Motor dilayani", metric_value(summary, "jumlah_motor_dilayani", decimals=0))
    cols[1].metric("Rata-rata waktu tunggu", metric_value(summary, "rata_rata_waktu_tunggu", " menit"))
    cols[2].metric("Rata-rata waktu dalam sistem", metric_value(summary, "rata_rata_waktu_dalam_sistem", " menit"))
    cols[3].metric("Motor ditolak", metric_value(summary, "jumlah_motor_ditolak", decimals=0))

    cols = st.columns(3)
    cols[0].metric("Rata-rata waktu pelayanan", metric_value(summary, "rata_rata_waktu_pelayanan", " menit"))
    cols[1].metric("Rata-rata panjang antrian", metric_value(summary, "rata_rata_panjang_antrian", " motor"))
    utilization = summary.get("utilisasi_server")
    cols[2].metric("Utilisasi server", "-" if utilization is None else f"{utilization * 100:.2f}%")


def show_charts(results, queue_log):
    left, right = st.columns(2)

    with left:
        st.subheader("Panjang Antrian terhadap Waktu")
        if queue_log.empty:
            st.info("Queue log kosong.")
        else:
            queue_chart = queue_log[["time", "queue_length"]].set_index("time")
            st.line_chart(queue_chart)

    with right:
        st.subheader("Waiting Time per Customer")
        if results.empty:
            st.info("Belum ada customer yang selesai dilayani.")
        else:
            waiting_chart = results[["customer_id", "waiting_time"]].set_index("customer_id")
            st.line_chart(waiting_chart)


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
      <button id="play">Play</button>
      <button id="reset" class="secondary">Reset</button>
      <input id="timeline" type="range" min="0" max="__SIMULATION_TIME__" value="0" step="0.1">
      <div id="readout" class="readout">0.0 menit</div>
    </div>

    <div id="scene">
      <div class="hint">Drag: rotate/pan | Scroll: zoom | Alur: masuk -> antre 1 baris max 15 -> nozzle -> keluar</div>
      <div id="error">Animasi 3D gagal dimuat. Pastikan browser punya koneksi internet untuk mengambil Three.js CDN.</div>
    </div>

    <div class="stats">
      <div class="stat">
        <div class="stat-label">Menunggu</div>
        <div id="waitingCount" class="stat-value">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Dilayani</div>
        <div id="servingCount" class="stat-value">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Selesai</div>
        <div id="departedCount" class="stat-value">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Ditolak</div>
        <div id="rejectedCount" class="stat-value">0</div>
      </div>
      <div class="stat">
        <div class="stat-label">Total divisualkan</div>
        <div class="stat-value">__TOTAL_VISUALIZED__</div>
      </div>
    </div>
  </div>

  <script>
    function showThreeError(message) {
      const errorBox = document.getElementById("error");
      if (errorBox) {
        errorBox.style.display = "flex";
        errorBox.textContent = message || "Animasi 3D gagal dimuat.";
      }
    }
    window.addEventListener("error", function(event) {
      showThreeError("Animasi 3D gagal dijalankan: " + event.message);
    });
  </script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js" onerror="showThreeError('Three.js gagal dimuat dari CDN. Periksa koneksi internet browser.')"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js" onerror="showThreeError('OrbitControls gagal dimuat dari CDN. Periksa koneksi internet browser.')"></script>
  <script>
    if (!window.THREE || !THREE.OrbitControls) {
      showThreeError("Three.js atau OrbitControls belum tersedia. Coba refresh halaman atau cek koneksi internet.");
    } else {

    const vehicles = __VEHICLES__;
    const simulationTime = __SIMULATION_TIME__;
    const numNozzles = __NUM_NOZZLES__;
    const sceneHost = document.getElementById("scene");
    const errorBox = document.getElementById("error");
    const playButton = document.getElementById("play");
    const resetButton = document.getElementById("reset");
    const timeline = document.getElementById("timeline");
    const readout = document.getElementById("readout");
    const waitingCount = document.getElementById("waitingCount");
    const servingCount = document.getElementById("servingCount");
    const departedCount = document.getElementById("departedCount");
    const rejectedCount = document.getElementById("rejectedCount");

    let currentTime = 0;
    let playing = false;
    let lastFrame = null;
    const clockScale = Math.max(1.8, Math.min(2.8, 84 / Math.max(simulationTime, 30)));
    const VISUAL = {
      clockScale: clockScale,
      arrivalScale: clockScale,
      queueApproachDuration: 1.6,
      queueAdvanceDuration: 0.7,
      directApproachDuration: 2.4,
      minQueueDuration: 1.2,
      queueScale: clockScale,
      minServiceDuration: 2.8,
      serviceScale: Math.max(2.8, clockScale * 1.15),
      pumpPause: 0.8,
      nozzleClearDuration: 0.95,
      exitDuration: 1.7,
      playbackRate: 1.0,
    };
    const TRACK = {
      entryX: -24,
      centerX: -4,
      width: 60,
      queueGap: 1.65,
    };

    const visualVehicles = [];
    let previousNozzleReleaseVisual = 0;
    const queueReleaseTimes = [];

    vehicles
      .slice()
      .sort((a, b) => a.arrival_time - b.arrival_time)
      .forEach((vehicle, index) => {
        const arrivalVisual = vehicle.arrival_time * VISUAL.arrivalScale;
        const serviceDuration = Math.max(
          VISUAL.minServiceDuration,
          vehicle.service_time * VISUAL.serviceScale
        );
        let hasQueueWait = vehicle.waiting_time > 0.02;

        if (!hasQueueWait) {
          const tentativeApproachEnd = arrivalVisual + VISUAL.directApproachDuration;
          if (previousNozzleReleaseVisual > tentativeApproachEnd + 0.01) {
            hasQueueWait = true;
          }
        }

        let approachStartVisual = arrivalVisual;
        let approachEndVisual;
        let queueEnterVisual = null;
        let serviceStartVisual;
        let queueDuration = 0;
        let queueEntrySlot = 0;
        let queueAdvanceMoments = [];

        if (hasQueueWait) {
          while (queueReleaseTimes.length > 0 && queueReleaseTimes[0] <= approachStartVisual) {
            queueReleaseTimes.shift();
          }

          while (queueReleaseTimes.length >= 15) {
            approachStartVisual = queueReleaseTimes[0];
            while (queueReleaseTimes.length > 0 && queueReleaseTimes[0] <= approachStartVisual) {
              queueReleaseTimes.shift();
            }
          }

          queueEnterVisual = approachStartVisual + VISUAL.queueApproachDuration;
          queueEntrySlot = Math.min(queueReleaseTimes.length, 14);
          queueDuration = Math.max(VISUAL.minQueueDuration, vehicle.waiting_time * VISUAL.queueScale);
          approachEndVisual = queueEnterVisual;
          serviceStartVisual = Math.max(queueEnterVisual + queueDuration, previousNozzleReleaseVisual);
          queueAdvanceMoments = queueReleaseTimes.filter((time) => time > queueEnterVisual);
          queueReleaseTimes.push(serviceStartVisual);
          queueReleaseTimes.sort((a, b) => a - b);
        } else {
          approachEndVisual = approachStartVisual + VISUAL.directApproachDuration;
          serviceStartVisual = Math.max(approachEndVisual, previousNozzleReleaseVisual);
        }

        const serviceEndVisual = serviceStartVisual + serviceDuration;
        const nozzleClearVisual = serviceEndVisual + VISUAL.nozzleClearDuration;
        const exitEndVisual = nozzleClearVisual + VISUAL.exitDuration;

        visualVehicles.push({
          ...vehicle,
          visualIndex: index,
          nozzleLane: 0,
          hasQueueWait,
          arrivalVisual,
          approachStartVisual,
          approachEndVisual,
          queueEnterVisual,
          serviceStartVisual,
          serviceEndVisual,
          nozzleClearVisual,
          exitEndVisual,
          queueDurationVisual: queueDuration,
          serviceDurationVisual: serviceDuration,
          queueEntrySlot,
          queueAdvanceMoments,
        });

        previousNozzleReleaseVisual = serviceEndVisual;
      });

    const visualDuration = Math.max(
      24,
      ...visualVehicles.map((vehicle) => vehicle.exitEndVisual + 0.4)
    );
    timeline.max = visualDuration.toFixed(1);
    const totalRejected = __TOTAL_REJECTED__;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xe5e7eb);

    const camera = new THREE.PerspectiveCamera(48, sceneHost.clientWidth / 500, 0.1, 1000);
    camera.position.set(0, 16, 28);
    camera.lookAt(TRACK.centerX, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(sceneHost.clientWidth, 500);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    sceneHost.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(TRACK.centerX, 0, 0);
    controls.maxPolarAngle = Math.PI / 2.15;
    controls.minDistance = 8;
    controls.maxDistance = 60;

    scene.add(new THREE.HemisphereLight(0xffffff, 0x64748b, 1.6));
    const sun = new THREE.DirectionalLight(0xffffff, 1.7);
    sun.position.set(-8, 15, 8);
    sun.castShadow = true;
    sun.shadow.mapSize.width = 2048;
    sun.shadow.mapSize.height = 2048;
    scene.add(sun);

    const asphalt = new THREE.MeshStandardMaterial({ color: 0x374151, roughness: 0.9 });
    const grass = new THREE.MeshStandardMaterial({ color: 0xbbf7d0, roughness: 0.9 });
    const marking = new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.7 });
    const pumpGreen = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.6 });
    const pumpDark = new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.6 });
    const black = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.8 });
    const metal = new THREE.MeshStandardMaterial({ color: 0x9ca3af, roughness: 0.45, metalness: 0.35 });
    const white = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.65 });
    const tireMaterial = new THREE.MeshStandardMaterial({ color: 0x020617, roughness: 0.82 });
    const glassMaterial = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.25, metalness: 0.05 });
    const lampMaterial = new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.35 });

    function addBox(width, height, depth, x, y, z, material, castShadow = false) {
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
      mesh.position.set(x, y, z);
      mesh.receiveShadow = true;
      mesh.castShadow = castShadow;
      scene.add(mesh);
      return mesh;
    }

    addBox(TRACK.width, 0.12, 10, TRACK.centerX, -0.06, 0, asphalt);
    addBox(TRACK.width, 0.08, 4, TRACK.centerX, -0.04, 7, grass);
    addBox(TRACK.width, 0.08, 4, TRACK.centerX, -0.04, -7, grass);

    for (let x = TRACK.entryX; x < 5; x += 2.0) {
      addBox(0.9, 0.02, 0.08, x, 0.02, 0, marking);
    }

    addBox(0.16, 0.03, 6.0, 7.7, 0.03, 0, pumpGreen);
    addBox(4.8, 0.04, 0.16, 9.9, 0.04, -3.0, pumpGreen);
    addBox(4.8, 0.04, 0.16, 9.9, 0.04, 3.0, pumpGreen);

    function serviceZ(slotIndex) {
      if (numNozzles === 1) return 0;
      const top = -2.2;
      const bottom = 2.2;
      return top + ((bottom - top) / Math.max(numNozzles - 1, 1)) * slotIndex;
    }

    for (let index = 0; index < numNozzles; index += 1) {
      const z = serviceZ(index);
      addBox(0.9, 1.5, 0.55, 9.4, 0.75, z, pumpGreen, true);
      addBox(0.55, 0.25, 0.35, 9.4, 1.62, z, pumpDark, true);
      addBox(1.65, 0.03, 0.75, 7.4, 0.04, z, white);
      addBox(1.55, 0.06, 0.08, 7.4, 0.08, z - 0.42, pumpGreen);
      addBox(1.55, 0.06, 0.08, 7.4, 0.08, z + 0.42, pumpGreen);
    }

    function makeTextSprite(text, color = "#111827", bg = "rgba(255,255,255,0.92)") {
      const canvas = document.createElement("canvas");
      canvas.width = 256;
      canvas.height = 96;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = bg;
      ctx.strokeStyle = "#d1d5db";
      ctx.lineWidth = 6;
      ctx.roundRect(8, 8, 240, 80, 18);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = color;
      ctx.font = "700 30px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(text, 128, 50);
      const texture = new THREE.CanvasTexture(canvas);
      const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
      const sprite = new THREE.Sprite(material);
      sprite.scale.set(2.2, 0.82, 1);
      return sprite;
    }

    const entryLabel = makeTextSprite("Motor datang");
    entryLabel.position.set(TRACK.entryX, 1.2, -2.7);
    scene.add(entryLabel);
    const exitLabel = makeTextSprite("Keluar");
    exitLabel.position.set(15.5, 1.2, -2.7);
    scene.add(exitLabel);
    const titleLabel = makeTextSprite("SPBU Pertamax Motor 3D", "#064e3b", "rgba(220,252,231,0.94)");
    titleLabel.position.set(0, 2.2, -5.7);
    titleLabel.scale.set(4.2, 1.1, 1);
    scene.add(titleLabel);

    function createMotor(id) {
      const group = new THREE.Group();
      const motorShell = new THREE.Group();
      motorShell.scale.set(0.68, 0.68, 0.68);
      motorShell.position.y = 0.04;
      group.add(motorShell);

      const numericId = Number(id) || 0;
      const paintColor = new THREE.Color().setHSL((numericId * 0.61803398875) % 1, 0.78, 0.48);
      const paint = new THREE.MeshStandardMaterial({ color: paintColor, roughness: 0.48, metalness: 0.08 });

      const rearWheelX = -0.56;
      const frontWheelX = 0.62;
      const wheelY = 0.24;
      const wheelZ = 0;
      const wheelRadius = 0.26;

      const tireGeometry = new THREE.TorusGeometry(wheelRadius, 0.055, 12, 36);
      const rimGeometry = new THREE.CylinderGeometry(0.115, 0.115, 0.08, 28);
      [rearWheelX, frontWheelX].forEach((x) => {
        const tire = new THREE.Mesh(tireGeometry, tireMaterial);
        tire.position.set(x, wheelY, wheelZ);
        tire.castShadow = true;
        motorShell.add(tire);

        const rim = new THREE.Mesh(rimGeometry, metal);
        rim.position.set(x, wheelY, wheelZ);
        rim.rotation.x = Math.PI / 2;
        rim.castShadow = true;
        motorShell.add(rim);
      });

      const frame = new THREE.Mesh(new THREE.BoxGeometry(0.96, 0.07, 0.08), black);
      frame.position.set(0.0, 0.49, 0);
      frame.rotation.z = 0.08;
      frame.castShadow = true;
      motorShell.add(frame);

      const tank = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.24, 0.24), paint);
      tank.position.set(0.08, 0.67, 0);
      tank.rotation.z = -0.08;
      tank.castShadow = true;
      motorShell.add(tank);

      const rearFairing = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.18, 0.22), paint);
      rearFairing.position.set(-0.38, 0.62, 0);
      rearFairing.rotation.z = 0.18;
      rearFairing.castShadow = true;
      motorShell.add(rearFairing);

      const frontFairing = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.22, 0.2), paint);
      frontFairing.position.set(0.48, 0.68, 0);
      frontFairing.rotation.z = -0.25;
      frontFairing.castShadow = true;
      motorShell.add(frontFairing);

      const seat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.1, 0.25), black);
      seat.position.set(-0.24, 0.81, 0);
      seat.rotation.z = -0.08;
      seat.castShadow = true;
      motorShell.add(seat);

      const fork = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.58, 12), metal);
      fork.position.set(0.55, 0.52, 0);
      fork.rotation.z = -0.35;
      fork.castShadow = true;
      motorShell.add(fork);

      const rearArm = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.58, 12), metal);
      rearArm.position.set(-0.42, 0.43, 0);
      rearArm.rotation.z = 1.08;
      rearArm.castShadow = true;
      motorShell.add(rearArm);

      const handlebar = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.52, 12), black);
      handlebar.position.set(0.72, 0.93, 0);
      handlebar.rotation.x = Math.PI / 2;
      handlebar.rotation.z = -0.1;
      handlebar.castShadow = true;
      motorShell.add(handlebar);

      const windshield = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.18, 0.18), glassMaterial);
      windshield.position.set(0.65, 0.84, 0);
      windshield.rotation.z = -0.38;
      windshield.castShadow = true;
      motorShell.add(windshield);

      const headlamp = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), lampMaterial);
      headlamp.position.set(0.68, 0.7, 0);
      headlamp.scale.set(1, 0.7, 0.75);
      headlamp.castShadow = true;
      motorShell.add(headlamp);

      const tailLamp = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.08, 0.14), new THREE.MeshStandardMaterial({ color: 0xdc2626, roughness: 0.35 }));
      tailLamp.position.set(-0.62, 0.64, 0);
      tailLamp.castShadow = true;
      motorShell.add(tailLamp);

      const riderBody = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.11, 0.38, 16), new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 0.65 }));
      riderBody.position.set(-0.08, 1.0, 0);
      riderBody.rotation.z = -0.22;
      riderBody.castShadow = true;
      motorShell.add(riderBody);

      const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.11, 18, 14), paint);
      helmet.position.set(0.0, 1.25, 0);
      helmet.castShadow = true;
      motorShell.add(helmet);

      const label = makeTextSprite(`#${id}`);
      label.position.set(0, 1.25, 0);
      label.scale.set(1.25, 0.48, 1);
      group.add(label);

      group.visible = false;
      scene.add(group);
      return group;
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function lerp(start, end, ratio) {
      return start + (end - start) * clamp(ratio, 0, 1);
    }

    function setupVehicles() {
      visualVehicles.forEach((vehicle) => {
        vehicle.model = createMotor(vehicle.customer_id);
      });
    }

    function getState(vehicle, t) {
      if (t < vehicle.approachStartVisual) return "hidden";
      if (t < vehicle.approachEndVisual) return "approaching";
      if (t < vehicle.serviceStartVisual) return "waiting";
      if (t < vehicle.nozzleClearVisual) return "serving";
      if (t < vehicle.exitEndVisual) return "leaving";
      return "departed";
    }

    function queuePosition(slot) {
      return {
        x: 3.6 - Math.min(slot, 14) * TRACK.queueGap,
        z: 0,
      };
    }

    function queuePositionWithAdvance(vehicle, currentSlot, t) {
      if (!vehicle.hasQueueWait || !vehicle.queueAdvanceMoments || vehicle.queueAdvanceMoments.length === 0) {
        return queuePosition(currentSlot);
      }

      let activeAdvanceTime = null;
      for (let index = vehicle.queueAdvanceMoments.length - 1; index >= 0; index -= 1) {
        const advanceTime = vehicle.queueAdvanceMoments[index];
        if (advanceTime <= t && t <= advanceTime + VISUAL.queueAdvanceDuration) {
          activeAdvanceTime = advanceTime;
          break;
        }
      }

      if (activeAdvanceTime === null) return queuePosition(currentSlot);

      const elapsed = t - activeAdvanceTime;
      const previousSlot = Math.min(14, currentSlot + 1);
      const progress = elapsed / Math.max(VISUAL.queueAdvanceDuration, 0.1);
      const previous = queuePosition(previousSlot);
      const target = queuePosition(currentSlot);
      return {
        x: lerp(previous.x, target.x, progress),
        z: lerp(previous.z, target.z, progress),
      };
    }

    function renderSimulation(t) {
      currentTime = clamp(t, 0, visualDuration);
      timeline.value = currentTime.toFixed(1);
      const simulatedMinute = Math.min(simulationTime, currentTime / Math.max(VISUAL.clockScale, 0.1));
      readout.textContent = `${currentTime.toFixed(1)} dtk visual | ~${simulatedMinute.toFixed(1)} menit simulasi`;

      const queued = visualVehicles
        .filter((vehicle) => {
          if (!vehicle.hasQueueWait) return false;
          return currentTime >= vehicle.approachStartVisual && currentTime < vehicle.serviceStartVisual;
        })
        .sort((a, b) => {
          return a.serviceStartVisual - b.serviceStartVisual || a.arrivalVisual - b.arrivalVisual;
        })
        .slice(0, 15);
      const queuedIds = new Set(queued.map((vehicle) => vehicle.customer_id));
      const waiting = queued.filter((vehicle) => currentTime >= (vehicle.queueEnterVisual ?? vehicle.approachEndVisual));
      const serving = visualVehicles
        .filter((vehicle) => getState(vehicle, currentTime) === "serving")
        .sort((a, b) => a.serviceStartVisual - b.serviceStartVisual);
      const departed = visualVehicles
        .filter((vehicle) => currentTime >= vehicle.exitEndVisual);

      waitingCount.textContent = waiting.length;
      servingCount.textContent = serving.length;
      departedCount.textContent = departed.length;
      rejectedCount.textContent = totalRejected;

      const waitingSlots = new Map(queued.map((vehicle, index) => [vehicle.customer_id, index]));

      const minMotorGap = TRACK.queueGap;
      const activeX = new Map();

      function rawActiveX(vehicle, state) {
        if (state === "approaching") {
          if (!vehicle.hasQueueWait) {
            const progress = (currentTime - vehicle.approachStartVisual) / Math.max(VISUAL.directApproachDuration, 0.1);
            return lerp(TRACK.entryX, 6.2, progress);
          }
          const slot = waitingSlots.get(vehicle.customer_id) ?? vehicle.queueEntrySlot ?? 0;
          const entryTarget = queuePosition(vehicle.queueEntrySlot ?? slot);
          const dynamicTarget = queuePosition(slot);
          const approachSpeed = (entryTarget.x - TRACK.entryX) / Math.max(VISUAL.queueApproachDuration, 0.1);
          const elapsed = clamp(currentTime - vehicle.approachStartVisual, 0, VISUAL.queueApproachDuration);
          return Math.min(TRACK.entryX + approachSpeed * elapsed, dynamicTarget.x);
        }
        if (state === "waiting") {
          const slot = waitingSlots.get(vehicle.customer_id) ?? 0;
          return queuePositionWithAdvance(vehicle, slot, currentTime).x;
        }
        if (state === "serving") {
          const atPumpTime = currentTime - vehicle.serviceStartVisual;
          const dockingDuration = Math.min(1.1, vehicle.serviceDurationVisual * 0.22);
          const servingStartX = vehicle.hasQueueWait ? queuePosition(0).x : 6.2;
          if (atPumpTime < dockingDuration) {
            return lerp(servingStartX, 7.05, atPumpTime / Math.max(dockingDuration, 0.1));
          }
          if (currentTime <= vehicle.serviceEndVisual) return 7.05;
          return lerp(7.05, 9.2, (currentTime - vehicle.serviceEndVisual) / Math.max(VISUAL.nozzleClearDuration, 0.1));
        }
        return TRACK.entryX;
      }

      visualVehicles
        .map((vehicle) => ({ vehicle, state: getState(vehicle, currentTime) }))
        .filter(({ vehicle, state }) => {
          if (state !== "approaching" && state !== "waiting" && state !== "serving") return false;
          return !(vehicle.hasQueueWait && (state === "approaching" || state === "waiting") && !queuedIds.has(vehicle.customer_id));
        })
        .sort((a, b) => {
          return a.vehicle.serviceStartVisual - b.vehicle.serviceStartVisual || a.vehicle.arrivalVisual - b.vehicle.arrivalVisual;
        })
        .forEach(({ vehicle, state }, index) => {
          const rawX = rawActiveX(vehicle, state);
          const previousX = index === 0 ? Infinity : Math.min(...activeX.values());
          activeX.set(vehicle.customer_id, Math.min(rawX, previousX - minMotorGap));
        });

      visualVehicles.forEach((vehicle) => {
        const state = getState(vehicle, currentTime);
        const model = vehicle.model;
        let x = TRACK.entryX;
        let z = 0;
        let visible = true;
        let rotation = 0;

        if (state === "hidden" || state === "departed") {
          visible = false;
        } else if (vehicle.hasQueueWait && (state === "approaching" || state === "waiting") && !queuedIds.has(vehicle.customer_id)) {
          visible = false;
        } else if (state === "approaching") {
          x = activeX.get(vehicle.customer_id) ?? rawActiveX(vehicle, state);
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


def show_sensitivity_analysis(base_arrival_rate, service_times, simulation_time, seed, num_nozzles):
    st.subheader("Analisis Sensitivitas")

    scenarios = [
        ("Sepi", base_arrival_rate * 0.7),
        ("Normal", base_arrival_rate),
        ("Ramai", base_arrival_rate * 1.3),
    ]

    rows = []
    for offset, (name, scenario_arrival_rate) in enumerate(scenarios):
        output = run_simulation(
            arrival_rate=scenario_arrival_rate,
            service_times=service_times,
            simulation_time=simulation_time,
            seed=seed + offset,
            num_nozzles=num_nozzles,
        )
        summary = output["summary"]
        rows.append(
            {
                "skenario": name,
                "arrival_rate": scenario_arrival_rate,
                "rata_rata_waktu_tunggu": summary.get("rata_rata_waktu_tunggu", 0),
                "rata_rata_panjang_antrian": summary.get("rata_rata_panjang_antrian", 0),
                "utilisasi_server": summary.get("utilisasi_server", 0),
            }
        )

    sensitivity_df = pd.DataFrame(rows)
    st.dataframe(
        sensitivity_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "skenario": "Skenario",
            "arrival_rate": st.column_config.NumberColumn("Arrival rate", format="%.3f motor/menit"),
            "rata_rata_waktu_tunggu": st.column_config.NumberColumn("Rata-rata waktu tunggu", format="%.2f menit"),
            "rata_rata_panjang_antrian": st.column_config.NumberColumn("Rata-rata panjang antrian", format="%.2f motor"),
            "utilisasi_server": st.column_config.NumberColumn("Utilisasi server", format="%.2f"),
        },
    )


st.title("Simulasi dan Analisis Antrian Pertamax Motor")
st.caption("SPBU Pertamina Jalan Sudirman - model M/G/1 dari data observasi")

try:
    observation_data, service_times, default_arrival_rate = load_observation_data()
except FileNotFoundError:
    st.error(f"File data tidak ditemukan: {DATA_PATH}")
    st.stop()
except KeyError as exc:
    st.error(f"Kolom data tidak sesuai: {exc}")
    st.stop()

if not service_times:
    st.error("Kolom waktu pelayanan tidak punya nilai numerik yang bisa dipakai.")
    st.stop()

with st.sidebar:
    st.header("Parameter Simulasi")
    arrival_rate = st.slider(
        "Arrival rate (motor/menit)",
        min_value=0.1,
        max_value=float(max(3.0, default_arrival_rate * 2)),
        value=float(default_arrival_rate),
        step=0.01,
    )
    simulation_time = st.slider(
        "Durasi simulasi (menit)",
        min_value=30,
        max_value=240,
        value=120,
        step=10,
    )
    num_nozzles = st.slider(
        "Jumlah nozzle aktif",
        min_value=1,
        max_value=4,
        value=1,
        step=1,
    )
    seed = st.number_input(
        "Seed random",
        min_value=0,
        max_value=9999,
        value=42,
        step=1,
    )
    run_button = st.button("Jalankan Simulasi", type="primary")

st.markdown("### Data Observasi")
left, right = st.columns([2, 1])
with left:
    st.dataframe(observation_data, use_container_width=True, hide_index=True)
with right:
    st.metric("Arrival rate dari data", f"{default_arrival_rate:.3f} motor/menit")
    st.metric("Sampel waktu pelayanan", f"{len(service_times)} sesi")
    st.metric("Rata-rata pelayanan", f"{np.mean(service_times):.2f} menit")

if run_button or "simulation_output" not in st.session_state:
    st.session_state.simulation_output = run_simulation(
        arrival_rate=arrival_rate,
        service_times=service_times,
        simulation_time=simulation_time,
        seed=int(seed),
        num_nozzles=num_nozzles,
    )
    st.session_state.last_params = {
        "arrival_rate": arrival_rate,
        "simulation_time": simulation_time,
        "seed": int(seed),
        "num_nozzles": num_nozzles,
    }

output = st.session_state.simulation_output
params = st.session_state.last_params
summary = output["summary"]
results = output["results"]
queue_log = output["queue_log"]

st.markdown("### Hasil Simulasi")
st.caption(
    "Parameter aktif: "
    f"arrival_rate={params['arrival_rate']:.3f} motor/menit, "
    f"durasi={params['simulation_time']} menit, "
    f"nozzle={params['num_nozzles']}, seed={params['seed']}"
)

if not summary:
    st.warning("Belum ada motor yang selesai dilayani pada simulasi ini.")
else:
    show_summary(summary)

show_charts(results, queue_log)
show_animation(
    results,
    queue_log,
    params["num_nozzles"],
    params["simulation_time"],
    summary.get("jumlah_motor_ditolak", 0),
)
show_sensitivity_analysis(
    base_arrival_rate=params["arrival_rate"],
    service_times=service_times,
    simulation_time=params["simulation_time"],
    seed=params["seed"],
    num_nozzles=params["num_nozzles"],
)
