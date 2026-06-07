# 20-Week Market-Readiness Sprint

Welcome to the **Interactive 20-Week Market-Readiness Sprint**. This repository holds a focused 20-week (100 daily exercises) technical roadmap mapped into a fully interactive flowchart built from scratch using purely vanilla HTML, CSS, and JS.

**Target:** C#/.NET Integration Engineer — Biometric, Kiosk, Identity & Edge Systems — Germany.

---

## 🎨 Features & Functionality

This is much more than a plain-text markdown file. Open `index.html` in your browser to experience the roadmap engine:

- **Interactive Flowchart Engine:** Custom SVG rendering system written in vanilla JavaScript (`script.js`). Generates pixel-perfect pathways between nodes spanning multiple conceptual axes.
- **Section Collapsing:** Click anywhere on a `Phase` or `Week` block to collapse it! The page automatically recalculates dimensions, closes the child nodes (`Day` nodes), and gracefully reconnects the SVGs around the remaining visible nodes.
- **State Persistence (Local Storage):** The system tracks your completion status. Right-click any node to open the custom action menu and mark it as **Done**, **In Progress**, or **Skip**. Your state will be fully retained even if you refresh the browser!
- **Data Detail Drawers:** Left-click on any `Week` or `Day` block to slide out a side drawer presenting full task definitions — Morning (C#) and Evening (German) sessions.
- **Thematic Styling:** CSS custom design tokens built into `style.css` present a modern, space-efficient, clean theme.

---

## 📚 Sprint Structure

The sprint comprises 4 phases escalating from C# foundations to active market entry:

1. **Phase 1 (Weeks 1–5): Foundation Repair** — OOP, DI, testing, async/await, resilience, native interop, gRPC, and a minimal React dashboard.
2. **Phase 2 (Weeks 6–10): Cloud & Distribution** — Docker, CI/CD, Azure IoT Hub, messaging, EF Core, SOAP legacy, MQTT/OPC UA/Modbus basics, security, fleet simulation.
3. **Phase 3 (Weeks 11–13): Documentation & Proof** — C4 architecture diagrams, ADRs, bilingual README, demo video, LinkedIn/XING profiles, CV, test applications.
4. **Phase 4 (Weeks 14–20): Market Entry** — Outreach waves, recruiter engagement, interview prep, sustained applications, feedback loops, offer negotiation.

---

## 🚀 Getting Started

No dependencies, no `npm install`, no build steps.

1. Clone or download this repository.
2. Double-click `index.html` to open it in your web browser.
3. **Left Click** on nodes to peek at detailed learning tasks.
4. **Click the node body (Phases or Weeks)** to collapse or expand branches.
5. **Right Click** to mark tracking states and map your journey!

---

## 🔧 Rebuilding

If you modify `roadmap.txt`, regenerate `index.html` by running:

```bash
python build_from_roadmap.py
```

---

*"The enemy is no longer a bad plan. The enemy is planning addiction. Execute."*
