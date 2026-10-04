/**
 * Chavara Living — Modern Interactive Cursor Animations & 3D Tilt
 * Adds cursor-reactive 3D tilt, dynamic shine, ambient parallax, and glowing tracker
 * across all page templates.
 */

(function () {
  'use strict';

  // 1. Inject Cursor Glow Tracker if not present
  let glow = document.getElementById('cursorGlow');
  if (!glow) {
    glow = document.createElement('div');
    glow.id = 'cursorGlow';
    glow.className = 'cursor-glow-tracker';
    document.body.appendChild(glow);
  }

  // 2. Inject Ambient Floating Orbs for Parallax Depth
  let orbContainer = document.getElementById('ambientOrbs');
  if (!orbContainer) {
    orbContainer = document.createElement('div');
    orbContainer.id = 'ambientOrbs';
    orbContainer.className = 'ambient-orbs-container';
    orbContainer.innerHTML = `
      <div class="ambient-orb orb-1"></div>
      <div class="ambient-orb orb-2"></div>
      <div class="ambient-orb orb-3"></div>
    `;
    document.body.prepend(orbContainer);
  }

  // Mouse Coordinates
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let currentX = mouseX;
  let currentY = mouseY;
  let isHovering = false;

  window.addEventListener('mousemove', function (e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    if (!isHovering) {
      glow.style.opacity = '1';
      isHovering = true;
    }
  });

  window.addEventListener('mouseleave', function () {
    glow.style.opacity = '0';
    isHovering = false;
  });

  // Smooth lerp loop for glow and ambient orbs
  function updateCursorAnimation() {
    currentX += (mouseX - currentX) * 0.15;
    currentY += (mouseY - currentY) * 0.15;

    glow.style.transform = `translate3d(${currentX - 120}px, ${currentY - 120}px, 0)`;

    // Ambient orbs subtle parallax
    const orb1 = document.querySelector('.ambient-orb.orb-1');
    const orb2 = document.querySelector('.ambient-orb.orb-2');
    const orb3 = document.querySelector('.ambient-orb.orb-3');

    const moveX = (mouseX / window.innerWidth - 0.5);
    const moveY = (mouseY / window.innerHeight - 0.5);

    if (orb1) orb1.style.transform = `translate3d(${moveX * -30}px, ${moveY * -30}px, 0)`;
    if (orb2) orb2.style.transform = `translate3d(${moveX * 45}px, ${moveY * 35}px, 0)`;
    if (orb3) orb3.style.transform = `translate3d(${moveX * -20}px, ${moveY * 20}px, 0)`;

    requestAnimationFrame(updateCursorAnimation);
  }
  requestAnimationFrame(updateCursorAnimation);

  // 3. Interactive 3D Card Tilt & Dynamic Highlight on Cursor Move
  function initCardTilt() {
    const cardSelectors = [
      '.stat-card',
      '.card-custom',
      '.mess-stat',
      '.mess-card',
      '.auth-card',
      '.day-menu-card',
      '.plan-card',
      '.quick-action-card',
      '.dash-card'
    ];

    const cards = document.querySelectorAll(cardSelectors.join(', '));

    cards.forEach((card) => {
      // Avoid re-attaching
      if (card.dataset.tiltInitialized) return;
      card.dataset.tiltInitialized = 'true';
      card.classList.add('cursor-tilt-target');

      // Create or ensure shine element inside
      let shine = card.querySelector('.card-cursor-shine');
      if (!shine) {
        shine = document.createElement('div');
        shine.className = 'card-cursor-shine';
        card.appendChild(shine);
      }

      card.addEventListener('mousemove', function (e) {
        const rect = card.getBoundingClientRect();
        const cardX = e.clientX - rect.left;
        const cardY = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const deltaX = (cardX - centerX) / centerX; // -1 to 1
        const deltaY = (cardY - centerY) / centerY; // -1 to 1

        const maxTilt = 8; // degrees
        const tiltX = -deltaY * maxTilt;
        const tiltY = deltaX * maxTilt;

        card.style.transform = `perspective(900px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) translateZ(4px)`;

        // Update radial shine position
        shine.style.opacity = '1';
        shine.style.background = `radial-gradient(circle at ${cardX}px ${cardY}px, rgba(37, 99, 235, 0.16) 0%, transparent 65%)`;
      });

      card.addEventListener('mouseleave', function () {
        card.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        if (shine) shine.style.opacity = '0';
      });
    });
  }

  // Initialize on DOMContentLoaded and on demand
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCardTilt);
  } else {
    initCardTilt();
  }

  // Observer for dynamically added cards or tab switches
  const observer = new MutationObserver(function () {
    initCardTilt();
  });
  observer.observe(document.body, { childList: true, subtree: true });
})();
