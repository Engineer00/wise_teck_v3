/**
 * WISE TECK — Premium Three.js hero (reference recreation)
 * Layered platform · glass logo badge · orbital rings · particles · connectors
 * Embedded in hero stage — global THREE, transparent page blend
 */
(function () {
  "use strict";
  var THEME = (function () {          // colour scheme from Site Settings: {default colour: new colour}
    try { return JSON.parse(document.documentElement.getAttribute("data-theme-map") || "{}"); } catch (e) { return {}; }
  })();
  function T(c) { return THEME[c.toLowerCase()] || c; }
  function T3(n) { return parseInt(T("#" + n.toString(16).padStart(6, "0")).slice(1), 16); }

  let THREE = window.THREE;            // set when the library arrives (see boot below)
  const PURPLE = T3(0x5730b5);
  const LIGHT_PURPLE = T3(0x9a73ff);
  const WHITE = T3(0xffffff);
  const SCENE_SCALE = 0.702;

  function clamp(v, min, max) {
    return Math.min(max, Math.max(min, v));
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function easeOutBack(t) {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function cylinder(radius, height, color, segments, metalness, roughness) {
    const mesh = new THREE.Mesh(
      new THREE.CylinderGeometry(radius, radius, height, segments || 96),
      new THREE.MeshPhysicalMaterial({
        color,
        metalness: metalness ?? 0.15,
        roughness: roughness ?? 0.28,
        clearcoat: 0.7,
        clearcoatRoughness: 0.18
      })
    );
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    return mesh;
  }

  class HeroThree {
    constructor(stage) {
      this.stage = stage;
      // Pedestal colours come from Site settings (data-coin-* on the stage); defaults = original design
      const hex = (v, d) => (/^#[0-9a-f]{6}$/i.test(v || "") ? parseInt(v.slice(1), 16) : d);
      this.cBase = hex(stage.dataset.coinBase, WHITE);
      this.cRing1 = hex(stage.dataset.coinRing, PURPLE);
      this.cRing2 = hex(stage.dataset.coinRing2, LIGHT_PURPLE);
      this.canvas = stage.querySelector("#heroThreeCanvas");
      this.connectorPaths = stage.querySelectorAll(".hero__connector");
      this.pillarCards = stage.querySelectorAll(".hero__pillar-card");
      this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      this.mouse = { x: 0, y: 0, tx: 0, ty: 0 };
      this.clock = new THREE.Clock();
      this.elapsed = 0;
      this.running = true;
      this.disposed = false;
      this.orbitNodes = [];
      this.connectorNodes3d = [];

      this._onResize = this._onResize.bind(this);
      this._onMouseMove = this._onMouseMove.bind(this);
      this._animate = this._animate.bind(this);

      this._initScene();
      this._initLights();
      this._initShadow();
      this._initPlatform();
      this._initLogo();
      this._initOrbits();
      this._initParticles();
      this._initConnectors3D();
      this._bindEvents();
      this._onResize();

      if (this.reducedMotion) {
        this.stage.classList.add("hero__three-stage--reduced");
        this._finishIntro();
        this.elapsed = 4;
        this._applyTimelineState(4);
        this._updateSvgConnectors(1);
      } else {
        this._startIntro();
      }

      this.stage.classList.add("is-ready");
      this.renderer.render(this.scene, this.camera);
      this._animate();
    }

    _initScene() {
      const w = Math.max(this.stage.clientWidth, 320);
      const h = Math.max(this.stage.clientHeight, 320);

      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(38, w / h, 0.1, 100);
      this.camera.position.set(0, 2.45, 11);
      this.camera.lookAt(0, 1.15, 0);

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        antialias: true,
        alpha: true,
        powerPreference: "high-performance"
      });
      if (!this.renderer.getContext()) throw new Error("WebGL is not available.");
      this.renderer.setClearColor(T3(0x000000), 0);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.setSize(w, h, false);
      this.renderer.outputColorSpace = THREE.SRGBColorSpace;
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 1.15;

      this.centralGroup = new THREE.Group();
      this.centralGroup.scale.setScalar(SCENE_SCALE);
      this.scene.add(this.centralGroup);
    }

    _initLights() {
      this.scene.add(new THREE.HemisphereLight(T3(0xffffff), T3(0xe8ddff), 2.8));

      this.keyLight = new THREE.DirectionalLight(T3(0xffffff), 4);
      this.keyLight.position.set(4, 7, 8);
      this.scene.add(this.keyLight);

      this.purpleLight = new THREE.PointLight(PURPLE, 8, 12);
      this.purpleLight.position.set(0, 1.7, 1.5);
      this.scene.add(this.purpleLight);

      this.purpleLight2 = new THREE.PointLight(LIGHT_PURPLE, 5, 9);
      this.purpleLight2.position.set(-3, 1, 2);
      this.scene.add(this.purpleLight2);
    }

    _initShadow() {
      const canvas = document.createElement("canvas");
      canvas.width = 512;
      canvas.height = 512;
      const ctx = canvas.getContext("2d");
      const gradient = ctx.createRadialGradient(256, 256, 10, 256, 256, 220);
      gradient.addColorStop(0, "rgba(60,30,120,.22)");
      gradient.addColorStop(1, "rgba(60,30,120,0)");
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 512, 512);

      const shadow = new THREE.Mesh(
        new THREE.PlaneGeometry(6, 3),
        new THREE.MeshBasicMaterial({
          map: new THREE.CanvasTexture(canvas),
          transparent: true,
          depthWrite: false
        })
      );
      shadow.rotation.x = -Math.PI / 2;
      shadow.position.set(0, -0.9, 0.05);
      this.centralGroup.add(shadow);
    }

    _initPlatform() {
      this.platformGroup = new THREE.Group();
      this.centralGroup.add(this.platformGroup);

      const base1 = cylinder(3.15, 0.28, this.cBase);
      base1.position.y = -0.75;
      this.platformGroup.add(base1);

      this.ring1 = cylinder(2.75, 0.16, this.cRing1, 96, 0.45, 0.2);
      this.ring1.position.y = -0.55;
      this.platformGroup.add(this.ring1);

      const base2 = cylinder(2.65, 0.36, this.cBase);
      base2.position.y = -0.4;
      this.platformGroup.add(base2);

      this.ring2 = cylinder(2.35, 0.13, this.cRing2, 96, 0.5, 0.18);
      this.ring2.position.y = -0.17;
      this.platformGroup.add(this.ring2);

      const base3 = cylinder(2.15, 0.3, this.cBase);
      base3.position.y = 0.02;
      this.platformGroup.add(base3);

      this.energyRing = new THREE.Mesh(
        new THREE.TorusGeometry(1.45, 0.11, 24, 128),
        new THREE.MeshPhysicalMaterial({
          color: LIGHT_PURPLE,
          emissive: PURPLE,
          emissiveIntensity: 1.8,
          metalness: 0.5,
          roughness: 0.15,
          transparent: true,
          opacity: 0.9
        })
      );
      this.energyRing.rotation.x = Math.PI / 2;
      this.energyRing.position.y = 0.25;
      this.platformGroup.add(this.energyRing);

      const energyDisc = new THREE.Mesh(
        new THREE.CylinderGeometry(1.25, 1.25, 0.05, 96),
        new THREE.MeshStandardMaterial({
          color: T3(0xeee8ff),
          emissive: PURPLE,
          emissiveIntensity: 1.2
        })
      );
      energyDisc.position.y = 0.3;
      this.platformGroup.add(energyDisc);
    }

    _initLogo() {
      this.logoGroup = new THREE.Group();
      this.logoGroup.position.y = 2.72;
      this.centralGroup.add(this.logoGroup);

      const radius = 1.45;
      const thickness = 0.32;
      const LOGO_SCALE = 1.5;

      this.logoBadge = new THREE.Group();
      this.logoBadge.scale.setScalar(LOGO_SCALE);
      this.logoGroup.add(this.logoBadge);

      const texture = new THREE.TextureLoader().load("data:image/webp;base64,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", () => {
        const fallback = this.stage.querySelector(".hero__three-fallback");
        if (fallback) fallback.hidden = true;
      });
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = Math.min(8, this.renderer.capabilities.getMaxAnisotropy());

      const logoMat = new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        depthWrite: true,
        side: THREE.FrontSide
      });

      // Front — exact circular brand mark
      this.logoPlane = new THREE.Mesh(new THREE.CircleGeometry(radius, 96), logoMat);
      this.logoPlane.position.z = thickness / 2 + 0.002;
      this.logoBadge.add(this.logoPlane);

      // Back — same mark, readable at 360°
      this.logoPlaneBack = new THREE.Mesh(new THREE.CircleGeometry(radius, 96), logoMat.clone());
      this.logoPlaneBack.position.z = -thickness / 2 - 0.002;
      this.logoPlaneBack.rotation.y = Math.PI;
      this.logoPlaneBack.scale.x = 1;
      this.logoBadge.add(this.logoPlaneBack);

      // The coin is the logo: its face, side, rim and glow keep the logo's colours in every colour scheme
      // (plain hex, not T3). The platform, rings and particles around it follow the scheme.
      // Thick coin side — visible during rotation
      const edge = new THREE.Mesh(
        new THREE.CylinderGeometry(radius, radius, thickness, 96, 1, true),
        new THREE.MeshPhysicalMaterial({
          color: 0x6b3fe8,
          metalness: 0.55,
          roughness: 0.18,
          clearcoat: 0.9,
          clearcoatRoughness: 0.1,
          emissive: 0x351477,
          emissiveIntensity: 0.18,
          side: THREE.DoubleSide
        })
      );
      edge.rotation.x = Math.PI / 2;
      this.logoBadge.add(edge);

      const rimMat = new THREE.MeshStandardMaterial({
        color: 0xd8ccff,
        emissive: 0xffffff,
        emissiveIntensity: 0.12,
        metalness: 0.92,
        roughness: 0.14
      });

      const rimFront = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.038, 14, 96), rimMat);
      rimFront.position.z = thickness / 2;
      this.logoBadge.add(rimFront);

      const rimBack = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.038, 14, 96), rimMat.clone());
      rimBack.position.z = -thickness / 2;
      this.logoBadge.add(rimBack);

      const glow = new THREE.Mesh(
        new THREE.CircleGeometry(radius * 1.04, 96),
        new THREE.MeshBasicMaterial({
          color: 0x7650dc,
          transparent: true,
          opacity: 0.1,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        })
      );
      glow.rotation.x = Math.PI / 2;
      glow.position.z = -thickness / 2 - 0.02;
      this.logoBadge.add(glow);

      this.orbitalGroup = new THREE.Group();
      this.logoGroup.add(this.orbitalGroup);
    }

    _initOrbits() {
      // Orbit rings and orbiting dots removed.
      this.orbitRings = [];
    }

    _initParticles() {
      // Floating / energy particles removed for a cleaner hero.
      this.particleGroup = new THREE.Group();
      this.centralGroup.add(this.particleGroup);
    }

    _initConnectors3D() {
      // Primary card→logo connectors are the SVG overlay paths.
      // Decorative 3D circuit tubes/nodes are intentionally omitted for a cleaner network.
      this.connectorGroup3d = new THREE.Group();
      this.centralGroup.add(this.connectorGroup3d);
    }

    _startIntro() {
      this.centralGroup.scale.set(0.01, 0.01, 0.01);
      this.platformGroup.position.y = -0.4;
      this.logoGroup.position.y = 2.0;
      this.introDone = false;
      this.introStart = performance.now();
    }

    _finishIntro() {
      this.centralGroup.scale.setScalar(SCENE_SCALE);
      this.platformGroup.position.y = 0;
      this.logoGroup.position.y = 2.72;
      this.introDone = true;
    }

    _bindEvents() {
      window.addEventListener("resize", this._onResize, { passive: true });
      this.stage.addEventListener("mousemove", this._onMouseMove, { passive: true });

      if ("ResizeObserver" in window) {
        this.ro = new ResizeObserver(() => this._onResize());
        this.ro.observe(this.stage);
      }

      this.io = new IntersectionObserver(
        (entries) => {
          const entry = entries[0];
          if (!entry) return;
          if (entry.isIntersecting) this.hasBeenVisible = true;
          this.running = entry.isIntersecting || !this.hasBeenVisible;
        },
        { threshold: 0, rootMargin: "80px 0px" }
      );
      this.io.observe(this.stage);
      this.hasBeenVisible = false;
      this.running = true;

      this.pillarCards.forEach((card) => {
        card.addEventListener("mouseenter", () => card.classList.add("is-hovered"));
        card.addEventListener("mouseleave", () => card.classList.remove("is-hovered"));
      });
    }

    _onMouseMove(e) {
      const rect = this.stage.getBoundingClientRect();
      this.mouse.tx = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      this.mouse.ty = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    }

    _onResize() {
      const w = Math.max(this.stage.clientWidth, 1);
      const h = Math.max(this.stage.clientHeight, 1);
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.setSize(w, h, false);
    }

    _applyTimelineState(t) {
      const stage = this.stage;
      stage.classList.toggle("is-platform", t >= 0.4);
      stage.classList.toggle("is-rings-active", t >= 0.7);
      stage.classList.toggle("is-logo", t >= 0.9);
      stage.classList.toggle("is-logo-glow", t >= 1.1);
      stage.classList.toggle("is-orbits", t >= 1.3);
      stage.classList.toggle("is-card-technology", t >= 1.5);
      stage.classList.toggle("is-card-innovation", t >= 1.7);
      stage.classList.toggle("is-card-entrepreneurship", t >= 1.9);
      stage.classList.toggle("is-card-skills", t >= 2.1);
      stage.classList.toggle("is-connectors", t >= 2.5);
      stage.classList.toggle("is-particles", t >= 2.7);
      stage.classList.toggle("is-idle", t >= 3);
    }

    _updateSvgConnectors() {
      // Connector lines removed from the hero.
    }

    _animate() {
      if (this.disposed) return;
      requestAnimationFrame(this._animate);

      const dt = this.running ? Math.min(this.clock.getDelta(), 0.05) : 0;
      const t = this.clock.elapsedTime;

      if (this.running && !this.reducedMotion) {
        if (!this.introDone) {
          const introT = clamp((performance.now() - this.introStart - 400) / 900, 0, 1);
          const eased = easeOutBack(introT);
          this.centralGroup.scale.setScalar(lerp(0.01, SCENE_SCALE, eased));
          this.platformGroup.position.y = lerp(-0.4, 0, eased);
          this.logoGroup.position.y = lerp(2.15, 2.72, eased);
          if (introT >= 1) this.introDone = true;
        }

        this.elapsed += dt;
        this._applyTimelineState(this.elapsed);

        const pConnect = clamp((this.elapsed - 2.5) / 0.6, 0, 1);
        this._updateSvgConnectors(pConnect);
      }

      this.mouse.x = lerp(this.mouse.x, this.mouse.tx, 0.06);
      this.mouse.y = lerp(this.mouse.y, this.mouse.ty, 0.06);
      const parallax = this.reducedMotion ? 0 : 1;
      const mx = this.mouse.x * 0.06 * parallax;
      const my = this.mouse.y * 0.05 * parallax;

      if (this.introDone || this.reducedMotion) {
        this.ring1.rotation.y = t * 0.28;
        this.ring2.rotation.y = -t * 0.38;
        this.energyRing.rotation.z = t * 0.55;

        // Keep logo fixed above the pedestal — no bobbing / sinking float
        this.logoGroup.position.y = 2.72;
        this.logoGroup.rotation.z = 0;
        this.logoGroup.rotation.x = my * 0.04;

        // Continuous 360° spin — front & back logo visible
        if (!this.reducedMotion) {
          this.logoBadge.rotation.y = t * 0.65;
        }
        this.logoGroup.rotation.y = mx * 0.08;

        this.orbitalGroup.rotation.y = t * 0.35 + mx * 0.1;
        this.orbitalGroup.rotation.x = Math.sin(t * 0.45) * 0.08;
        this.orbitalGroup.rotation.z = Math.sin(t * 0.28) * 0.08;

        this.orbitNodes.forEach((node, index) => {
          const d = node.userData;
          const a = d.angle + t * (0.25 + index * 0.025);
          node.position.x = Math.cos(a) * d.radius;
          node.position.y = Math.sin(a) * d.radius * d.orbitScale;
          node.position.z = Math.sin(a * 1.7) * 0.35;
          const pulse = 1 + Math.sin(t * 2 + index) * 0.25;
          node.scale.setScalar(pulse);
        });

        const pulse = 1 + Math.sin(t * 2.2) * 0.08;
        this.energyRing.scale.set(pulse, pulse, pulse);
        this.energyRing.material.opacity = 0.72 + Math.sin(t * 2) * 0.15;
        this.purpleLight.intensity = 7 + Math.sin(t * 2.1) * 2;

        this.connectorNodes3d.forEach((node, index) => {
          const s = 1 + Math.sin(t * 2.5 + index) * 0.2;
          node.scale.setScalar(s);
        });

        this.centralGroup.rotation.y = mx * 0.04;
        this.centralGroup.rotation.x = my * 0.03;
      }

      this.renderer.render(this.scene, this.camera);
    }

    dispose() {
      this.disposed = true;
      this.io?.disconnect();
      this.ro?.disconnect();
      window.removeEventListener("resize", this._onResize);
      this.stage.removeEventListener("mousemove", this._onMouseMove);
      this.renderer.dispose();
    }
  }

  function initHeroThree() {
    const stage = document.getElementById("heroThreeStage");
    if (!stage) return null;

    const fallback = stage.querySelector(".hero__three-fallback");
    THREE = window.THREE;

    if (!THREE) {
      console.error("Three.js library not loaded.");
      stage.classList.add("hero__three-stage--error");
      if (fallback) {
        fallback.hidden = false;
        fallback.textContent = "3D library failed to load. Refresh the page.";
      }
      return null;
    }

    if (fallback) fallback.hidden = false;

    try {
      const instance = new HeroThree(stage);
      if (fallback) fallback.hidden = true;
      window.__heroThree = instance;
      return instance;
    } catch (err) {
      console.error("HeroThree failed to start:", err);
      stage.classList.add("hero__three-stage--error");
      if (fallback) {
        fallback.hidden = false;
        fallback.textContent = "3D preview unavailable.";
      }
      return null;
    }
  }

  // Three.js (650 KB) is decorative: fetch it only after the page and its photos have loaded,
  // so it never competes with the first screen.
  function boot() {
    const stage = document.getElementById("heroThreeStage");
    if (!stage) return;
    if (window.THREE || !stage.dataset.three) { initHeroThree(); return; }
    const s = document.createElement("script");
    s.src = stage.dataset.three;
    s.onload = s.onerror = initHeroThree;
    document.head.appendChild(s);
  }
  if (document.readyState === "complete") boot();
  else window.addEventListener("load", boot, { once: true });

  window.HeroThree = HeroThree;
  window.initHeroThree = initHeroThree;
})();
