# Fan Control UI - Feature Brainstorm & Design Document

## 🎯 Project Goal
Create an intuitive GUI application for Linux Mint that allows easy fan curve configuration with live system monitoring (CPU, Memory, GPU load).

## 🚀 Core Features

### 1. **Live System Monitoring Dashboard**
- **Real-time Metrics Display:**
  - CPU Usage (%) - per core and overall
  - CPU Temperature (°C) - per core if available
  - Memory Usage (%) - RAM usage, swap usage
  - GPU Usage (%) - NVIDIA GPU utilization
  - GPU Temperature (°C)
  - GPU Memory Usage (%)
  - Fan Speeds (RPM) - CPU fan, GPU fan, system fans
  - Power Draw (W) - CPU, GPU, total system
  - Clock Speeds - CPU frequency, GPU core/memory clocks

- **Visualization:**
  - Real-time line graphs for all metrics
  - Historical data (last 1min, 5min, 15min, 1hr)
  - Color-coded temperature warnings (green/yellow/red)
  - Mini gauges/dials for quick overview
  - Sparklines for compact monitoring

### 2. **Fan Curve Configuration**
- **Interactive Fan Curve Editor:**
  - Visual graph with draggable control points
  - Temperature (X-axis) vs Fan Speed % (Y-axis)
  - Separate curves for CPU, GPU, and system fans
  - Real-time preview of curve changes
  - Snap-to-grid option for precise control
  - Undo/Redo functionality

- **Curve Management:**
  - Multiple preset profiles (Quiet, Balanced, Performance, Custom)
  - Save/load custom fan curve profiles
  - Import/export fan curves (JSON/YAML)
  - Quick apply buttons for common configurations
  - Profile switching with visual feedback

- **Advanced Options:**
  - Hysteresis settings (prevent fan oscillation)
  - Minimum fan speed thresholds
  - Maximum fan speed limits
  - Temperature averaging window
  - Fan response time/delay settings

### 3. **Profile Management**
- **Power Profiles:**
  - Quick switch between Quiet/Balanced/Performance
  - Custom profile creation
  - Profile-specific fan curves
  - Auto-switch profiles based on:
    - AC/Battery power state
    - CPU/GPU load thresholds
    - Time of day
    - Application detection (gaming mode)

- **Profile Presets:**
  - Gaming Mode (aggressive cooling)
  - Office Mode (quiet operation)
  - Battery Saver (minimal fans)
  - Custom user-defined presets

### 4. **System Integration**
- **asusctl Integration:**
  - Read current fan curves
  - Apply new fan curves
  - Switch power profiles
  - Enable/disable fan curves
  - Real-time status monitoring

- **System Monitoring:**
  - Integration with `sensors` (lm-sensors)
  - NVIDIA GPU monitoring via `nvidia-smi`
  - CPU monitoring via `/proc/stat` and `/sys`
  - Memory monitoring via `/proc/meminfo`

### 5. **User Interface Features**
- **Main Window:**
  - Clean, modern design
  - Tabbed interface or sidebar navigation
  - Responsive layout
  - Dark/Light theme support
  - System tray integration (minimize to tray)
  - Always-on-top option

- **Dashboard View:**
  - Large, readable metrics
  - Customizable widget layout
  - Drag-and-drop widget arrangement
  - Collapsible sections
  - Full-screen monitoring mode

- **Fan Curve Editor:**
  - Large, interactive graph canvas
  - Zoom and pan capabilities
  - Grid overlay toggle
  - Temperature/fan speed input fields
  - Live preview of current vs. new curve
  - Validation warnings (e.g., non-monotonic curves)

### 6. **Notifications & Alerts**
- **Temperature Alerts:**
  - High temperature warnings
  - Critical temperature alerts
  - Customizable thresholds
  - Desktop notifications
  - Sound alerts (optional)

- **Fan Status:**
  - Fan failure detection
  - Unusual fan behavior warnings
  - Fan speed stuck alerts

### 7. **Data & Logging**
- **Historical Data:**
  - Log all metrics to file
  - Export data (CSV, JSON)
  - View historical graphs
  - Statistics (min/max/avg temperatures, fan speeds)

- **Settings Persistence:**
  - Auto-save configurations
  - Restore last session
  - Backup/restore settings

### 8. **Advanced Features**
- **Performance Testing:**
  - Stress test mode
  - Benchmark fan curves
  - Temperature stability testing
  - Fan noise level estimation

- **Automation:**
  - Script support for custom automation
  - Event triggers (e.g., "if GPU > 80°C, switch to Performance")
  - Scheduled profile changes
  - Application-specific profiles

## 🛠️ Technology Stack Options

### Option 1: Python + GTK4/PyGObject (Recommended for Linux Mint)
**Pros:**
- Native Linux look and feel
- Excellent system integration
- Lightweight and fast
- Good monitoring libraries (psutil, py3nvml)
- Easy asusctl integration (subprocess)

**Cons:**
- GTK4 learning curve
- Less modern UI framework

**Libraries:**
- `gi` (GObject Introspection) for GTK4
- `psutil` for CPU/memory monitoring
- `py3nvml` for NVIDIA GPU monitoring
- `matplotlib` or `pycairo` for graphs
- `pydbus` for D-Bus integration (asusctl)

### Option 2: Python + PyQt6/PySide6
**Pros:**
- Modern, polished UI framework
- Excellent documentation
- Great charting libraries (PyQtGraph, matplotlib)
- Cross-platform (if needed later)

**Cons:**
- Larger dependency footprint
- May feel less native on Linux

**Libraries:**
- `PyQt6` or `PySide6` for UI
- `PyQtGraph` for real-time graphs
- `psutil` for system monitoring
- `py3nvml` for GPU monitoring

### Option 3: Electron + Web Technologies
**Pros:**
- Modern web UI (HTML/CSS/JS)
- Rich ecosystem of charting libraries
- Easy to make beautiful UIs
- Can use Node.js for backend

**Cons:**
- Higher memory usage
- Larger application size
- Less native feel

**Stack:**
- Electron for desktop app
- React/Vue for UI framework
- Chart.js or D3.js for graphs
- Node.js child_process for asusctl

### Option 4: Rust + Slint (Extend rog-control-center)
**Pros:**
- Already exists in codebase
- Native performance
- Modern UI framework
- Can reuse existing code

**Cons:**
- Rust learning curve
- Less flexible for rapid prototyping

### Option 5: Web-based (Local Server)
**Pros:**
- Use any web framework
- Easy to develop and iterate
- Can run in browser or Electron wrapper

**Cons:**
- Requires local server
- More complex deployment

## 📊 Recommended Architecture

### Backend Services
1. **Monitoring Service:**
   - Polls system metrics (CPU, GPU, memory, temps, fans)
   - Updates at configurable interval (default: 1 second)
   - Publishes data via D-Bus or local socket

2. **Fan Control Service:**
   - Interfaces with asusctl via D-Bus or CLI
   - Manages fan curve configurations
   - Applies profile changes
   - Validates fan curve settings

3. **Configuration Manager:**
   - Saves/loads user settings
   - Manages profiles
   - Handles import/export

### Frontend Components
1. **Dashboard Widget:**
   - Real-time metric displays
   - Mini graphs/sparklines
   - Alert indicators

2. **Fan Curve Editor:**
   - Interactive graph canvas
   - Control point manipulation
   - Preview and validation

3. **Profile Manager:**
   - Profile list/selector
   - Quick switch buttons
   - Profile editor

4. **Settings Panel:**
   - Application preferences
   - Monitoring intervals
   - Alert thresholds
   - Theme selection

## 🎨 UI/UX Design Ideas

### Layout Options

**Option A: Single Window with Tabs**
```
┌─────────────────────────────────────────┐
│  [Dashboard] [Fan Curves] [Profiles] [Settings] │
├─────────────────────────────────────────┤
│                                         │
│  Dashboard Content                      │
│  - Live metrics                         │
│  - Graphs                               │
│                                         │
└─────────────────────────────────────────┘
```

**Option B: Sidebar Navigation**
```
┌─────┬───────────────────────────────────┐
│ 📊 │  Dashboard                        │
│ 🌡️ │  Fan Curves                      │
│ ⚙️ │  Profiles                         │
│ 🔧 │  Settings                         │
├─────┼───────────────────────────────────┤
│     │                                   │
│     │  Content Area                    │
│     │                                   │
└─────┴───────────────────────────────────┘
```

**Option C: Dashboard-First with Overlays**
```
┌─────────────────────────────────────────┐
│  Main Dashboard (always visible)        │
│  ┌──────────┐  ┌──────────┐            │
│  │ CPU      │  │ GPU      │            │
│  │ 45°C     │  │ 55°C     │            │
│  │ [graph]  │  │ [graph]  │            │
│  └──────────┘  └──────────┘            │
│                                         │
│  [Edit Fan Curves] [Profiles] [Settings]│
└─────────────────────────────────────────┘
```

### Fan Curve Editor Design
```
┌─────────────────────────────────────────┐
│  Fan Curve Editor - CPU Fan              │
├─────────────────────────────────────────┤
│                                         │
│  100% ┤                    ●─────●    │
│   80% ┤              ●─────●           │
│   60% ┤        ●─────●                 │
│   40% ┤  ●─────●                        │
│   20% ┤●                                │
│    0% └─────────────────────────────── │
│       30°C  40°C  50°C  60°C  70°C    │
│                                         │
│  [CPU] [GPU] [System]                   │
│  [Enable] [Reset] [Save] [Apply]       │
└─────────────────────────────────────────┘
```

## 🔌 Integration Points

### asusctl Commands
- `asusctl profile -P <profile>` - Switch profile
- `asusctl fan-curve --mod-profile <profile> --fan <fan> --data <curve>` - Set curve
- `asusctl fan-curve --get-enabled` - Get current curves
- `asusctl fan-curve --mod-profile <profile> --enable-fan-curves true` - Enable curves

### System Monitoring
- `/proc/stat` - CPU usage
- `/proc/meminfo` - Memory usage
- `/sys/class/thermal/` - Temperature sensors
- `nvidia-smi --query-gpu=... --format=csv` - GPU metrics
- `sensors` command or `/sys/class/hwmon/` - Hardware sensors

## 📋 Implementation Phases

### Phase 1: MVP (Minimum Viable Product)
- [ ] Basic system monitoring (CPU, GPU, memory, temps)
- [ ] Simple fan curve editor (text input)
- [ ] Apply fan curves via asusctl
- [ ] Basic UI with metrics display

### Phase 2: Enhanced Features
- [ ] Interactive fan curve graph editor
- [ ] Profile management
- [ ] Historical data logging
- [ ] Notifications/alerts

### Phase 3: Polish
- [ ] Advanced automation
- [ ] Performance testing tools
- [ ] Export/import functionality
- [ ] Theme support
- [ ] Documentation

## 🎯 Recommended Starting Point

**I recommend: Python + GTK4** because:
1. Native Linux Mint integration
2. Good system monitoring libraries available
3. Relatively easy to learn
4. Lightweight and performant
5. Excellent for system utilities

**Alternative: Python + PyQt6** if you want:
- More modern UI framework
- Better charting capabilities out of the box
- Easier to make polished interfaces

## 📚 Useful Libraries & Resources

### Python Monitoring
- `psutil` - System and process utilities
- `py3nvml` - NVIDIA GPU monitoring
- `pydbus` - D-Bus integration
- `python-systemd` - Systemd integration

### Python UI
- `gi` (GObject Introspection) - GTK4
- `PyQt6` / `PySide6` - Qt framework
- `matplotlib` - Plotting/graphs
- `PyQtGraph` - Real-time plotting

### Documentation
- GTK4 Python Tutorial: https://docs.gtk.org/gtk4/
- PyGObject API Reference: https://pygobject.readthedocs.io/
- asusctl Documentation: See MANUAL.md

## 💡 Next Steps

1. **Choose technology stack** (recommend Python + GTK4)
2. **Set up development environment**
3. **Create basic project structure**
4. **Implement system monitoring first**
5. **Build simple fan curve editor**
6. **Integrate with asusctl**
7. **Iterate and improve**

Would you like me to:
- Create a starter project with one of these technologies?
- Set up the basic monitoring infrastructure?
- Design the UI mockups in more detail?
- Start implementing a specific feature?

