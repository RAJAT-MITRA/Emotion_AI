# 🧠 EmotionAI

> **Real-time facial expression analysis powered by DeepFace CNNs.**  
> Upload a portrait or stream your webcam — get instant emotion scores, face-bounding boxes, and contextual insights.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📤 **Image Upload** | Analyze any JPG/PNG/WebP portrait. Bounding box + emotion scores returned instantly. |
| 📷 **Live Webcam** | Frame-by-frame real-time analysis every ~800 ms via your browser camera. |
| 😄 **4-Class Emotion Detection** | Joy · Sadness · Anger · Neutral with percentage confidence scores. |
| 🎯 **Face Bounding Box** | Detected face is highlighted with a dynamic overlay that scales proportionally. |
| 📊 **Confidence Ring** | Animated radial progress ring for dominant emotion confidence. |
| 💡 **Contextual Insights** | Personality-driven tips per detected emotion state. |
| ⚡ **Hot Reload Dev** | Vite HMR frontend + Uvicorn backend, both run concurrently during development. |

---

## 🖼️ UI Preview

The interface is a **3-column dark dashboard**:

```
┌──────────────────────────────────────────────────────┐
│  🟠 EmotionAI                      ● DeepFace · Live │  ← Top Bar
├──────────────┬───────────────────────┬───────────────┤
│  INPUT MODE  │                       │  NEURAL OUTPUT│
│              │   Canvas / Viewport   │               │
│  📤 Upload   │   (drop zone or       │  Emotion      │
│  📷 Webcam   │    webcam feed)       │  Analysis     │
│              │                       │               │
│ EMOTION      │                       │  Confidence   │
│ PALETTE      │                       │  Ring + Bars  │
│  • Joy       │                       │  + Insight    │
│  • Sadness   │                       │               │
│  • Anger     │                       │               │
│  • Neutral   │                       │               │
└──────────────┴───────────────────────┴───────────────┘
```

**Design System:**
- **Fonts:** [Syne](https://fonts.google.com/specimen/Syne) (headings) + [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) (body)
- **Palette:** Warm orange accent (`#FF6B35`), emotion-coded colors (Joy = amber, Sadness = blue, Anger = red, Neutral = slate)
- **Animations:** Framer Motion transitions, floating emoji idle states, springy bar reveals

---

## 🏗️ Architecture

```
EmotionAI/
│
├── emotion.py              ← Python FastAPI backend (port 8000)
├── requirements.txt        ← Python dependencies
│
└── frontend/               ← React + Vite frontend (port 5173)
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── main.jsx        ← React entry point
        ├── index.css       ← Global reset + Google Fonts import
        ├── App.jsx         ← Main app component (all UI + logic)
        └── App.css         ← Full design system & layout styles
```

### Data Flow

```
Browser (React)
    │
    │  POST /analyze         (image upload → multipart/form-data)
    │  POST /analyze-frame   (webcam frame → base64 JSON)
    ▼
FastAPI Backend (emotion.py)
    │
    │  cv2.imdecode()        → numpy array
    │  DeepFace.analyze()    → raw emotion dict + face region
    │  safe_float/safe_int() → serialization guard
    ▼
JSON Response
    {
      "emotions": [
        { "label": "Joy",     "score": 87.4 },
        { "label": "Neutral", "score": 8.1  },
        { "label": "Sadness", "score": 3.1  },
        { "label": "Anger",   "score": 1.4  }
      ],
      "region": { "x": 110, "y": 45, "w": 220, "h": 280 },
      "image_width": 640,
      "image_height": 480
    }
```

---

## 🛠️ Tech Stack

### Backend
| Package | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **DeepFace** | CNN-based facial emotion analysis |
| **OpenCV (`cv2`)** | Image decoding from bytes/base64 |
| **NumPy** | Array handling for image data |
| **TensorFlow / Keras** | DeepFace model runtime |

### Frontend
| Package | Purpose |
|---|---|
| **React 19** | UI component framework |
| **Vite 8** | Dev server + bundler with HMR |
| **Framer Motion** | Smooth animations & transitions |
| **react-webcam** | Webcam access & frame capture |
| **lucide-react** | Icon set |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- A webcam (optional, for live mode)

---

### 1. Clone the repo

```bash
git clone https://github.com/your-username/EmotionAI.git
cd EmotionAI
```

---

### 2. Set up the Python backend

```bash
# Install all Python dependencies
pip install -r requirements.txt
```

> ⚠️ **Note:** This installs TensorFlow + DeepFace which are large (~2 GB). First run will also auto-download the DeepFace model weights.

```bash
# Start the backend server
python emotion.py
```

Backend will be live at → **`http://localhost:8000`**

---

### 3. Set up the React frontend

```bash
cd frontend

# Install Node dependencies
npm install --legacy-peer-deps

# Start the dev server
npm run dev
```

Frontend will be live at → **`http://localhost:5173`**

---

### 4. Open the app

Navigate to **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 📡 API Reference

Base URL: `http://localhost:8000`

### `POST /analyze`
Analyze an uploaded image file.

**Request:** `multipart/form-data`
| Field | Type | Description |
|---|---|---|
| `file` | `UploadFile` | Image file (JPG, PNG, WebP) |

**Response:**
```json
{
  "emotions": [
    { "label": "Joy",     "score": 87.4 },
    { "label": "Neutral", "score": 8.1  },
    { "label": "Sadness", "score": 3.1  },
    { "label": "Anger",   "score": 1.4  }
  ],
  "region": { "x": 110, "y": 45, "w": 220, "h": 280 },
  "image_width": 640,
  "image_height": 480
}
```

---

### `POST /analyze-frame`
Analyze a base64-encoded webcam frame (used for live mode).

**Request:** `application/json`
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgAB..."
}
```

**Response:** Same structure as `/analyze`.

---

**Error response (non-500):**
```json
{ "error": "Awaiting clear webcam frame..." }
```

> The backend always returns HTTP 200 with an `error` key rather than throwing 500s — this keeps the React frontend resilient during webcam startup.

---

## ⚙️ How DeepFace Analysis Works

Inside `emotion.py`, the `process_frame()` function:

1. **Guards against empty frames** — returns a soft error if the image is null or zero-size (common during webcam init).
2. **Calls `DeepFace.analyze()`** with:
   - `actions=["emotion"]` — only emotion analysis, skipping age/gender/race for speed.
   - `enforce_detection=False` — allows analysis even if no face is confidently detected.
   - `silent=True` — suppresses verbose TF logs.
3. **Extracts & remaps** raw emotion keys (`happy`, `sad`, `angry`, `neutral`) into labeled objects.
4. **Casts all NumPy types** to plain Python `float`/`int` via `safe_float()` / `safe_int()` to avoid JSON serialization errors.
5. **Sorts emotions** by score descending so the dominant emotion is always `emotions[0]`.
6. **Returns face region** in absolute pixel coordinates — the frontend converts these to percentages for responsive overlay rendering.

---

## 🎮 Using the App

### Upload Mode
1. Click **"Upload Image"** in the sidebar (or it's selected by default).
2. Click **"Choose File"** or click anywhere in the drop zone.
3. Select a portrait photo — DeepFace processes it and the results appear within 1–3 seconds.
4. A **golden bounding box** appears around the detected face with the dominant emotion label.
5. The right panel shows the **dominant emotion card** with a confidence ring + full spectrum bars.
6. Click **✕** to clear and try another image.

### Live Webcam Mode
1. Click **"Live Webcam"** in the sidebar.
2. Allow browser camera permissions if prompted.
3. Click **"▶ Start Scan"** — the app begins analyzing your face every 800 ms.
4. Watch the emotion bars animate in real-time as your expression changes.
5. Click **"⏹ Stop Scan"** to pause analysis.

---

## 🧩 Frontend Component Map

```
App.jsx
│
├── <ConfidenceRing />          — SVG radial ring showing % confidence
│
├── Shell Layout
│   ├── <header.topbar>         — Brand logo + DeepFace live badge
│   │
│   ├── <aside.sidebar>         — Mode selector + emotion palette legend
│   │
│   └── <div.main>
│       │
│       ├── <div.canvas-area>   — Left: viewport + header + status chip
│       │   ├── <div.dropzone>  — Upload idle state
│       │   ├── <img.preview>   — Uploaded image + bounding box
│       │   └── <Webcam>        — Live webcam feed + scan button
│       │
│       └── <div.analysis-panel>  — Right: results panel
│           ├── <div.dominant-card>  — Top emotion + ring
│           ├── <div.spectrum-section> — Animated bar rows
│           └── <div.tip-card>   — Contextual insight message
```

---

## 🐛 Known Quirks & Fixes Applied

| Issue | Fix Applied |
|---|---|
| `deepface` not installed | Run `pip install -r requirements.txt` |
| `lucide-react` missing in frontend | Install with `npm install lucide-react --legacy-peer-deps` |
| Vite PostCSS crash (`<<<<<<< HEAD`) | Resolved git merge conflict markers in root `package.json` and `package-lock.json` |
| NumPy serialization → HTTP 500 | `safe_float()` / `safe_int()` helpers wrap all DeepFace output values |
| Empty webcam frames on startup | `process_frame()` returns `{"error": "..."}` instead of crashing |

---

## 📦 Production Build

### Frontend
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

### Backend (with Gunicorn)
```bash
pip install gunicorn
gunicorn emotion:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📄 License

MIT License — see [LICENSE](./LICENSE) for details.

---

<div align="center">
  <p>Built with ❤️ using DeepFace, FastAPI & React</p>
</div>
