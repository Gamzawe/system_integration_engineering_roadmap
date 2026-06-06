# Systems Integration Engineering Roadmap

Welcome to the **Interactive Systems Integration Engineering Roadmap**. This repository holds a comprehensive 19-month (45 weeks, 228 daily exercises) technical roadmap mapped into a fully interactive flowchart built from scratch using purely vanilla HTML, CSS, and JS. 

The primary goal of this curriculum is to prepare individuals for systems integration engineering — bridging the gap between edge hardware (biometric scanners, PLCs, IoT gateways), industrial protocols (Beckhoff ADS, BACnet, KNX, MQTT, OPC UA), and enterprise cloud backends with dual-cloud sovereignty (Azure & AWS).

---

## 🎨 Features & Functionality

This is much more than a plain-text markdown file. Open `index.html` in your browser to experience the roadmap engine:

- **Interactive Flowchart Engine:** Custom SVG rendering system written in vanilla JavaScript (`script.js`). Generates pixel-perfect pathways between nodes spanning multiple conceptual axes.
- **Section Collapsing:** Click anywhere on a `Month` or `Week` block to collapse it! The page automatically recalculates dimensions, closes the child nodes (`Day` nodes), and gracefully reconnects the SVGs around the remaining visible nodes.
- **State Persistence (Local Storage):** The system tracks your completion status. Right-click any node to open the custom action menu and mark it as **Done**, **In Progress**, or **Skip**. Your state will be fully retained even if you refresh the browser!
- **Data Detail Drawers:** Left-click on any `Week` or `Day` block to slide out a side drawer presenting full task definitions and technical directives straight from the core syllabus. 
- **Thematic Styling:** CSS custom design tokens built into `style.css` present a modern, space-efficient, "neo-cyber" dark mode theme.

---

## 📚 Curriculum Structure (From Zero to Deployment)

The journey comprises 5 main phases, escalating from zero-allocation C# programming to cloud-native production deployments and market positioning:

1. **Phase 1 (Months 1–3): Zero-Allocation C#, Python Injection & Interop** — Memory stack, Span\<T\>, Memory\<T\>, LibraryImport, async/await, Channels, serial/UART, TCP Pipelines, and the local gateway concept.
2. **Phase 2 (Months 4–7): Edge Orchestration & Industrial Protocols** — Linux systemd daemons, Docker, K3s, CI/CD, Beckhoff TwinCAT 3 (ADS), BACnet/KNX, MQTT, and OPC UA.
3. **Phase 3 (Months 8–10): CQRS, Kafka, & Observability** — SQLite edge queuing, sync recovery, hybrid CQRS (EF Core + Dapper), Apache Kafka, InfluxDB, Grafana, and Serilog.
4. **Phase 4 (Months 11–13): Cloud Sovereignty & Cybersecurity** — Azure IoT Edge, AWS IoT Core (dual-cloud), IEC 62443, NCA OTCC-1:2022, mTLS, and multi-site topology.
5. **Phase 5 (Months 14–19): Capstone, UI, C4 Models, & Market Execution** — React config UI, C4 architecture diagrams, ADRs, load testing, DACH/KSA market positioning, mock interviews, and job execution.

---

## 🚀 Getting Started

No dependencies, no `npm install`, no build steps. 

1. Clone or download this repository.
2. Double-click `index.html` to open it in your web browser.
3. **Left Click** on nodes to peek at detailed learning tasks.
4. **Click the node body (Weeks or Months)** to collapse or expand branches.
5. **Right Click** to mark tracking states and map your journey!

---

## 🔧 Rebuilding

If you modify `roadmap.txt`, regenerate `index.html` by running:

```bash
python build_from_roadmap.py
```

---

*"Code is easy. Decoupled distributed integration systems are hard."*
