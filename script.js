/**
 * Roadmap Flowchart Engine
 * - Positions nodes in a flowchart layout (center spine + left/right branches + day nodes)
 * - Draws SVG connector lines between parent/child nodes
 * - Handles detail drawer on click
 * - Persists completion state in localStorage
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'roadmap_completed_nodes';
  const canvas = document.getElementById('roadmapCanvas');
  const svg = document.getElementById('connectorSvg');

  // Drawer elements
  const drawer = document.getElementById('detailDrawer');
  const drawerOverlay = document.getElementById('drawerOverlay');
  const drawerTitle = document.getElementById('drawerTitle');
  const drawerList = document.getElementById('drawerList');
  const drawerClose = document.getElementById('drawerClose');

  // Progress
  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');

  // Connector color (CSS vars don't work in SVG attributes)
  const CONNECTOR_COLOR = '#4299e1';
  const DAY_CONNECTOR_COLOR = '#90cdf4';

  // ------------------------------------------------------------------
  // 1. Layout Engine
  // ------------------------------------------------------------------

  function layoutNodes() {
    const centerX = canvas.offsetWidth / 2;
    let cursorY = 50;
    const mainGapY = 24;       // smaller vertical gap between main-path (month) items
    const sideGapY = 10;       // gap between stacked sub-nodes
    const dayGapY = 4;         // gap between day nodes
    const branchGapX = 70;     // gap between center node edge and sub-node edge
    const dayBranchGapX = 60;  // larger horizontal gap to push day nodes further outwards

    const elements = Array.from(canvas.children).filter(
      (el) => el.classList.contains('node') || el.classList.contains('year-label') || el.classList.contains('tip-callout')
    );

    const positionMap = {};

    const centerElements = elements.filter(
      (el) => el.classList.contains('main-node') || el.classList.contains('year-label') || el.classList.contains('milestone-node')
    );

    centerElements.forEach((el) => {
      const w = el.offsetWidth;
      const h = el.offsetHeight;
      const x = centerX - w / 2;

      el.style.position = 'absolute';
      el.style.left = x + 'px';
      el.style.top = cursorY + 'px';

      positionMap[el.id] = {
        x, y: cursorY, w, h, el,
        cx: centerX,
        cy: cursorY + h / 2,
        bottom: cursorY + h
      };

      // Find sub-node children (left/right branches)
      const sideChildren = elements.filter(
        (c) => c.dataset.parent === el.id &&
          (c.classList.contains('sub-node') || c.classList.contains('habit-node') || c.classList.contains('tip-callout'))
      );

      const leftChildren = sideChildren.filter((c) => c.dataset.side === 'left');
      const rightChildren = sideChildren.filter((c) => c.dataset.side === 'right');

      const isMainCollapsed = el.classList.contains('collapsed');

      // Position left sub-nodes
      let leftY = cursorY;
      leftChildren.forEach((child) => {
        if (isMainCollapsed) {
          child.style.display = 'none';
          elements.filter((d) => d.dataset.parent === child.id && d.classList.contains('day-node'))
            .forEach((d) => d.style.display = 'none');
          return;
        }
        child.style.display = 'block';

        const cw = child.offsetWidth;
        const ch = child.offsetHeight;

        // Check if this sub-node has day children (needs extra space to the left)
        const hasDayChildren = elements.some(
          (d) => d.dataset.parent === child.id && d.classList.contains('day-node')
        );
        // Find first day node to measure actual width; fallback to 160px
        const firstDayNode = hasDayChildren
          ? elements.find((d) => d.dataset.parent === child.id && d.classList.contains('day-node'))
          : null;
        const dayReserve = firstDayNode
          ? firstDayNode.offsetWidth + dayBranchGapX
          : hasDayChildren ? 160 + dayBranchGapX : 0;

        const idealX = centerX - w / 2 - branchGapX - cw;
        // Minimum X: leave room for day nodes (dayReserve px) from the left edge
        const minX = hasDayChildren ? dayReserve + 8 : 8;
        const childX = Math.max(minX, idealX);

        child.style.position = 'absolute';
        child.style.left = childX + 'px';
        child.style.top = leftY + 'px';

        positionMap[child.id] = {
          x: childX, y: leftY, w: cw, h: ch, el: child,
          cx: childX + cw / 2,
          cy: leftY + ch / 2,
          rightEdge: childX + cw,
          side: 'left'
        };

        const isCollapsed = child.classList.contains('collapsed');

        // Position day-node children of this sub-node
        const dayChildren = elements.filter(
          (d) => d.dataset.parent === child.id && d.classList.contains('day-node')
        );

        let dayY = leftY;
        dayChildren.forEach((day) => {
          if (isCollapsed) {
            day.style.display = 'none';
            return;
          }
          day.style.display = 'block';
          const dw = day.offsetWidth;
          const dh = day.offsetHeight;
          // Day nodes go further left from the sub-node, guaranteed not to overlap
          const dx = Math.max(4, childX - dayBranchGapX - dw);

          day.style.position = 'absolute';
          day.style.left = Math.max(4, dx) + 'px';
          day.style.top = dayY + 'px';

          const dayX = Math.max(4, dx);
          positionMap[day.id] = {
            x: dayX, y: dayY, w: dw, h: dh, el: day,
            cx: dayX + dw / 2,
            cy: dayY + dh / 2,
            rightEdge: dayX + dw,
            side: 'left'
          };
          dayY += dh + dayGapY;
        });

        // The sub-node block height is the max of itself and its day children
        const subBottom = isCollapsed ? leftY + ch : Math.max(leftY + ch, dayY - dayGapY);
        leftY = subBottom + sideGapY;
      });

      // Position right sub-nodes
      let rightY = cursorY;
      rightChildren.forEach((child) => {
        if (isMainCollapsed) {
          child.style.display = 'none';
          elements.filter((d) => d.dataset.parent === child.id && d.classList.contains('day-node'))
            .forEach((d) => d.style.display = 'none');
          return;
        }
        child.style.display = 'block';

        const cw = child.offsetWidth;
        const ch = child.offsetHeight;
        const cx = centerX + w / 2 + branchGapX;
        


        child.style.position = 'absolute';
        child.style.left = cx + 'px';
        child.style.top = rightY + 'px';

        positionMap[child.id] = {
          x: cx, y: rightY, w: cw, h: ch, el: child,
          cx: cx + cw / 2,
          cy: rightY + ch / 2,
          leftEdge: cx,
          side: 'right'
        };

        const isCollapsed = child.classList.contains('collapsed');

        // Position day-node children of this sub-node
        const dayChildren = elements.filter(
          (d) => d.dataset.parent === child.id && d.classList.contains('day-node')
        );

        let dayY = rightY;
        dayChildren.forEach((day) => {
          if (isCollapsed) {
            day.style.display = 'none';
            return;
          }
          day.style.display = 'block';
          const dw = day.offsetWidth;
          const dh = day.offsetHeight;
          // Day nodes go further right from the sub-node
          const dx = cx + cw + dayBranchGapX;

          day.style.position = 'absolute';
          day.style.left = dx + 'px';
          day.style.top = dayY + 'px';

          positionMap[day.id] = {
            x: dx, y: dayY, w: dw, h: dh, el: day,
            cx: dx + dw / 2,
            cy: dayY + dh / 2,
            leftEdge: dx,
            side: 'right'
          };
          dayY += dh + dayGapY;
        });

        const subBottom = isCollapsed ? rightY + ch : Math.max(rightY + ch, dayY - dayGapY);
        rightY = subBottom + sideGapY;
      });

      const maxSideBottom = Math.max(leftY, rightY, cursorY + h);
      cursorY = maxSideBottom + mainGapY;
    });

    canvas.style.height = (cursorY + 60) + 'px';
    return positionMap;
  }

  // ------------------------------------------------------------------
  // 2. SVG Connector Lines
  // ------------------------------------------------------------------

  function drawConnectors(positionMap) {
    svg.innerHTML = '';
    svg.setAttribute('width', canvas.offsetWidth);
    svg.setAttribute('height', parseInt(canvas.style.height) || canvas.offsetHeight);

    const allNodes = canvas.querySelectorAll('.node, .tip-callout');

    // Group by parent+side for sub-nodes (children of main-nodes)
    const subGroups = {};
    // Group by parent+side for day-nodes (children of sub-nodes)
    const dayGroups = {};

    allNodes.forEach((node) => {
      const parentId = node.dataset.parent;
      if (!parentId || !positionMap[parentId] || !positionMap[node.id]) return;

      if (node.classList.contains('day-node')) {
        // Day node: child of sub-node
        const side = node.dataset.side || 'left';
        const key = parentId + ':' + side;
        if (!dayGroups[key]) dayGroups[key] = { parentId, side, children: [] };
        dayGroups[key].children.push(node);
        return;
      }

      const isSide = node.classList.contains('sub-node') ||
                     node.classList.contains('habit-node') ||
                     node.classList.contains('tip-callout');
      if (!isSide) return;

      const side = node.dataset.side || 'left';
      const key = parentId + ':' + side;
      if (!subGroups[key]) subGroups[key] = { parentId, side, children: [] };
      subGroups[key].children.push(node);
    });

    // Draw sub-node connectors (same as before)
    Object.values(subGroups).forEach((group) => {
      const parent = positionMap[group.parentId];
      const children = group.children.map((n) => positionMap[n.id]).filter(Boolean);
      if (children.length === 0) return;

      const side = group.side;
      const parentAnchorY = parent.cy;
      let parentEdgeX, railX;

      if (side === 'left') {
        parentEdgeX = parent.x;
        railX = parentEdgeX - 20;
      } else {
        parentEdgeX = parent.x + parent.w;
        railX = parentEdgeX + 20;
      }

      drawLine(parentEdgeX, parentAnchorY, railX, parentAnchorY, false, CONNECTOR_COLOR);
      const childYs = children.map((c) => c.cy);
      const minY = Math.min(parentAnchorY, ...childYs);
      const maxY = Math.max(parentAnchorY, ...childYs);
      if (maxY > minY) drawLine(railX, minY, railX, maxY, false, CONNECTOR_COLOR);

      children.forEach((child) => {
        let childEdgeX;
        if (side === 'left') {
          childEdgeX = child.rightEdge || (child.x + child.w);
        } else {
          childEdgeX = child.leftEdge || child.x;
        }
        drawLine(railX, child.cy, childEdgeX, child.cy, true, CONNECTOR_COLOR);
        drawDot(childEdgeX, child.cy, CONNECTOR_COLOR);
      });
    });

    // Draw day-node connectors (lighter, thinner)
    Object.values(dayGroups).forEach((group) => {
      const parent = positionMap[group.parentId];
      const children = group.children.map((n) => positionMap[n.id]).filter(Boolean);
      if (children.length === 0) return;

      const side = group.side;
      const parentAnchorY = parent.cy;
      let parentEdgeX, railX;

      if (side === 'left') {
        parentEdgeX = parent.x;
        railX = parentEdgeX - 16;
      } else {
        parentEdgeX = parent.x + parent.w;
        railX = parentEdgeX + 16;
      }

      drawLine(parentEdgeX, parentAnchorY, railX, parentAnchorY, false, DAY_CONNECTOR_COLOR, 1.5);
      const childYs = children.map((c) => c.cy);
      const minY = Math.min(parentAnchorY, ...childYs);
      const maxY = Math.max(parentAnchorY, ...childYs);
      if (maxY > minY) drawLine(railX, minY, railX, maxY, false, DAY_CONNECTOR_COLOR, 1.5);

      children.forEach((child) => {
        let childEdgeX;
        if (side === 'left') {
          childEdgeX = child.rightEdge || (child.x + child.w);
        } else {
          childEdgeX = child.leftEdge || child.x;
        }
        drawLine(railX, child.cy, childEdgeX, child.cy, true, DAY_CONNECTOR_COLOR, 1.5);
        drawDot(childEdgeX, child.cy, DAY_CONNECTOR_COLOR, 2.5);
      });
    });
  }

  function drawLine(x1, y1, x2, y2, dashed, color, width) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('stroke', color || CONNECTOR_COLOR);
    line.setAttribute('stroke-width', width || '2');
    if (dashed) line.setAttribute('stroke-dasharray', '5 3');
    svg.appendChild(line);
  }

  function drawDot(cx, cy, color, r) {
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('cx', cx);
    dot.setAttribute('cy', cy);
    dot.setAttribute('r', r || '3');
    dot.setAttribute('fill', color || CONNECTOR_COLOR);
    svg.appendChild(dot);
  }

  // ------------------------------------------------------------------
  // 3. Detail Drawer
  // ------------------------------------------------------------------

  function openDrawer(node) {
    const title = node.textContent.replace(/Months \d+-\d+/g, '').replace(/[DLRS]$/g, '').trim();
    const details = node.dataset.details;
    if (!details) return;

    drawerTitle.textContent = title;
    drawerList.innerHTML = '';
    details.split('|').forEach((item) => {
      const li = document.createElement('li');
      li.textContent = item.trim();
      drawerList.appendChild(li);
    });

    drawer.classList.add('open');
    drawerOverlay.classList.add('open');
  }

  function closeDrawer() {
    drawer.classList.remove('open');
    drawerOverlay.classList.remove('open');
  }

  canvas.addEventListener('click', (e) => {
    const node = e.target.closest('.node');
    if (!node) return;
    if (statusMenu.classList.contains('open')) return;

    // Toggle children if it's a sub-node or main-node
    if (node.classList.contains('sub-node') || node.classList.contains('main-node')) {
      let hasChildren = false;
      if (node.classList.contains('sub-node')) {
        hasChildren = Array.from(canvas.children).some(
          (d) => d.dataset.parent === node.id && d.classList.contains('day-node')
        );
      } else if (node.classList.contains('main-node')) {
        hasChildren = Array.from(canvas.children).some(
          (c) => c.dataset.parent === node.id && (c.classList.contains('sub-node') || c.classList.contains('habit-node') || c.classList.contains('tip-callout'))
        );
      }

      if (hasChildren) {
        node.classList.toggle('collapsed');
        const posMap = layoutNodes();
        drawConnectors(posMap);
      }
    }

    if (node.dataset.details) {
      openDrawer(node);
    }
  });

  drawerClose.addEventListener('click', closeDrawer);
  drawerOverlay.addEventListener('click', closeDrawer);

  // ------------------------------------------------------------------
  // 4. Status Context Menu
  // ------------------------------------------------------------------

  const statusMenu = document.getElementById('statusMenu');
  const statusMenuClose = document.getElementById('statusMenuClose');
  let activeStatusNode = null;

  const STATUS_CLASSES = ['status-done', 'status-in-progress', 'status-skip'];
  const STATUS_KEY = 'roadmap_node_statuses';

  function getStatuses() {
    try {
      return JSON.parse(localStorage.getItem(STATUS_KEY)) || {};
    } catch {
      return {};
    }
  }

  function saveStatuses(map) {
    localStorage.setItem(STATUS_KEY, JSON.stringify(map));
  }

  function clearNodeStatus(node) {
    STATUS_CLASSES.forEach((cls) => node.classList.remove(cls));
  }

  function setNodeStatus(node, status) {
    clearNodeStatus(node);
    const statuses = getStatuses();

    if (status === 'reset' || !status) {
      delete statuses[node.id];
    } else {
      node.classList.add('status-' + status);
      statuses[node.id] = status;
    }

    saveStatuses(statuses);
    updateProgress();
  }

  function openStatusMenu(node, x, y) {
    activeStatusNode = node;

    const currentStatus = getStatuses()[node.id] || null;
    statusMenu.querySelectorAll('.status-menu-item').forEach((btn) => {
      const btnStatus = btn.dataset.status;
      btn.classList.toggle('active', btnStatus === currentStatus);
    });

    const menuW = 190;
    const menuH = 180;
    const safeX = Math.min(x, window.innerWidth - menuW - 10);
    const safeY = Math.min(y, window.innerHeight - menuH - 10);

    statusMenu.style.left = safeX + 'px';
    statusMenu.style.top = safeY + 'px';
    statusMenu.classList.add('open');
  }

  function closeStatusMenu() {
    statusMenu.classList.remove('open');
    activeStatusNode = null;
  }

  canvas.addEventListener('contextmenu', (e) => {
    const node = e.target.closest('.node');
    if (!node) return;
    e.preventDefault();
    closeDrawer();
    openStatusMenu(node, e.clientX, e.clientY);
  });

  statusMenu.addEventListener('click', (e) => {
    const btn = e.target.closest('.status-menu-item');
    if (!btn || !activeStatusNode) return;
    setNodeStatus(activeStatusNode, btn.dataset.status);
    closeStatusMenu();
  });

  statusMenuClose.addEventListener('click', closeStatusMenu);

  document.addEventListener('click', (e) => {
    if (!statusMenu.contains(e.target) && statusMenu.classList.contains('open')) {
      closeStatusMenu();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (statusMenu.classList.contains('open')) {
        closeStatusMenu();
      } else {
        closeDrawer();
      }
      return;
    }

    if (!statusMenu.classList.contains('open') || !activeStatusNode) return;

    const key = e.key.toLowerCase();
    const keyMap = { d: 'done', l: 'in-progress', r: 'reset', s: 'skip' };
    if (keyMap[key]) {
      e.preventDefault();
      setNodeStatus(activeStatusNode, keyMap[key]);
      closeStatusMenu();
    }
  });

  // ------------------------------------------------------------------
  // 5. Progress Tracking
  // ------------------------------------------------------------------

  function updateProgress() {
    const allNodes = canvas.querySelectorAll('.node');
    const total = allNodes.length;
    const done = canvas.querySelectorAll('.node.status-done').length;
    const pct = total > 0 ? Math.round((done / total) * 100) : 0;
    progressBar.style.width = pct + '%';
    progressText.textContent = pct + '%';
  }

  function restoreStatuses() {
    const statuses = getStatuses();
    Object.entries(statuses).forEach(([id, status]) => {
      const el = document.getElementById(id);
      if (el && status !== 'reset') {
        el.classList.add('status-' + status);
      }
    });
    updateProgress();
  }

  function migrateOldData() {
    const oldKey = 'roadmap_completed_nodes';
    try {
      const old = JSON.parse(localStorage.getItem(oldKey));
      if (Array.isArray(old) && old.length > 0) {
        const statuses = getStatuses();
        old.forEach((id) => { statuses[id] = 'done'; });
        saveStatuses(statuses);
        localStorage.removeItem(oldKey);
      }
    } catch { /* noop */ }
  }

  // ------------------------------------------------------------------
  // 6. Init
  // ------------------------------------------------------------------

  function init() {
    migrateOldData();
    restoreStatuses();

    const elements = Array.from(canvas.children);
    elements.filter((el) => el.classList.contains('sub-node')).forEach((sub) => {
      const hasDays = elements.some((d) => d.dataset.parent === sub.id && d.classList.contains('day-node'));
      if (hasDays) {
        sub.classList.add('has-days');
        sub.classList.add('collapsed');
      }
    });

    const posMap = layoutNodes();
    drawConnectors(posMap);
  }

  init();

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const posMap = layoutNodes();
      drawConnectors(posMap);
    }, 100);
  });
})();
