import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';

/* ── Emotion config ─────────────────────────── */
const EMOTION_META = {
  joy: { emoji: '😄', label: 'Joy', cls: 'joy', tip: 'You look genuinely happy right now!' },
  sadness: { emoji: '😢', label: 'Sadness', cls: 'sadness', tip: 'It\'s okay — emotions are data, not destiny.' },
  anger: { emoji: '😠', label: 'Anger', cls: 'anger', tip: 'High intensity detected. Take a breath.' },
  neutral: { emoji: '😶', label: 'Neutral', cls: 'neutral', tip: 'Calm and composed — a great baseline.' },
};

function getEmotionMeta(label = '') {
  return EMOTION_META[label.toLowerCase()] ?? EMOTION_META.neutral;
}

/* ── Confidence Ring ────────────────────────── */
function ConfidenceRing({ score, cls }) {
  const r = 30;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;
  return (
    <div className="confidence-ring-wrap">
      <svg viewBox="0 0 70 70" width="70" height="70">
        <circle className="ring-track" cx="35" cy="35" r={r} />
        <circle
          className={`ring-fill ${cls}`}
          cx="35" cy="35" r={r}
          strokeDasharray={c}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="ring-label">{Math.round(score)}%</div>
    </div>
  );
}

/* ── Main App ──────────────────────────────── */
export default function App() {
  const [inputMode, setInputMode] = useState('upload');
  const [filePreview, setFilePreview] = useState(null);
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [isLive, setIsLive] = useState(false);

  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);

  /* ── Live webcam loop ── */
  useEffect(() => {
    let iv;
    if (isLive && inputMode === 'webcam') {
      setStatus('processing');
      iv = setInterval(captureAndAnalyze, 800);
    } else if (inputMode === 'webcam' && !isLive) {
      setStatus('idle');
      setData(null);
    }
    return () => clearInterval(iv);
  }, [isLive, inputMode]);

  async function captureAndAnalyze() {
    if (!webcamRef.current) return;
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;
    try {
      const res = await fetch('http://127.0.0.1:8000/analyze-frame', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageSrc }),
      });
      const result = await res.json();
      if (!result.error) { setData(result); setStatus('completed'); }
    } catch (e) { console.error(e); }
  }

  async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setFilePreview(URL.createObjectURL(file));
    setStatus('processing');
    setData(null);
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch('http://127.0.0.1:8000/analyze', { method: 'POST', body: form });
      const result = await res.json();
      if (result.error) throw new Error(result.error);
      setData(result);
      setStatus('completed');
    } catch {
      setStatus('error');
    }
  }

  function resetUpload() {
    setFilePreview(null);
    setData(null);
    setStatus('idle');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  function switchMode(mode) {
    setInputMode(mode);
    setIsLive(false);
    setData(null);
    setStatus('idle');
    setFilePreview(null);
  }

  /* ── Bounding box ── */
  function BoundingBox() {
    if (!data?.region || data.region.w === 0) return null;
    const { x, y, w, h } = data.region;
    const { image_width: iw, image_height: ih } = data;
    const meta = getEmotionMeta(data.emotions[0]?.label);
    return (
      <div className="face-box" style={{
        position: 'absolute',
        left: `${(x / iw) * 100}%`,
        top: `${(y / ih) * 100}%`,
        width: `${(w / iw) * 100}%`,
        height: `${(h / ih) * 100}%`,
      }}>
        <div className="face-label">
          {meta.emoji} {data.emotions[0].label} · {data.emotions[0].score.toFixed(0)}%
        </div>
      </div>
    );
  }

  const statusText = { idle: 'Waiting', processing: 'Analyzing…', completed: 'Done', error: 'Error' };
  const dominant = data?.emotions?.[0];
  const domMeta = dominant ? getEmotionMeta(dominant.label) : null;

  return (
    <div className="shell">
      {/* ── Top Bar ── */}
      <header className="topbar">
        <div className="topbar-brand">
          <div className="brand-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a10 10 0 1 0 10 10" />
              <path d="M12 8v4l3 3" />
            </svg>
          </div>
          <span className="brand-name">Emotion<span>AI</span></span>
        </div>
        <div className="topbar-badge">
          <span className="live-dot" />
          DeepFace · Live
        </div>
      </header>

      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div>
          <p className="sidebar-label">Input Mode</p>

          <div className={`mode-card mode-card-upload ${inputMode === 'upload' ? 'active' : ''}`}
            onClick={() => switchMode('upload')}>
            <div className="mode-card-icon">📤</div>
            <div className="mode-card-text">
              <strong>Upload Image</strong>
              <span>JPG, PNG, WebP</span>
            </div>
          </div>

          <div className={`mode-card mode-card-webcam ${inputMode === 'webcam' ? 'active' : ''}`}
            onClick={() => switchMode('webcam')}>
            <div className="mode-card-icon">📷</div>
            <div className="mode-card-text">
              <strong>Live Webcam</strong>
              <span>Real-time scan</span>
            </div>
          </div>
        </div>

        <div className="emotion-legend">
          <p className="sidebar-label">Emotion Palette</p>
          {Object.values(EMOTION_META).map(m => (
            <div key={m.label} className="legend-item">
              <div className="legend-dot" style={{ background: `var(--${m.cls})` }} />
              <span>{m.emoji} {m.label}</span>
            </div>
          ))}
        </div>
      </aside>

      {/* ── Main ── */}
      <div className="main">

        {/* Canvas area */}
        <div className="canvas-area">
          <div className="canvas-header">
            <div>
              <h1 className="canvas-title">
                {inputMode === 'upload' ? <>Drop a <em>face photo</em>.</> : <>Go <em>live</em>, smile big.</>}
              </h1>
              <p className="canvas-subtitle">
                {inputMode === 'upload'
                  ? 'Upload any portrait and DeepFace will map every micro-expression in real time.'
                  : 'Your webcam feed is analyzed frame-by-frame at ~800ms intervals.'}
              </p>
            </div>
            <div className={`status-chip ${status}`}>
              <span className="status-dot" />
              {statusText[status]}
            </div>
          </div>

          {/* Viewport */}
          <div className="media-viewport">
            <AnimatePresence mode="wait">
              {inputMode === 'upload' ? (
                filePreview ? (
                  <motion.div key="preview" className="preview-wrap"
                    initial={{ opacity: 0, scale: 0.97 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.97 }}
                    transition={{ duration: 0.25 }}
                    style={{ position: 'absolute', inset: 0 }}
                  >
                    <img src={filePreview} alt="Preview" className="preview-image" />
                    <BoundingBox />
                    {status === 'processing' && (
                      <div className="processing-overlay">
                        <div className="spinner-ring" />
                        <p>Running DeepFace analysis…</p>
                      </div>
                    )}
                    <button className="preview-close" onClick={resetUpload} title="Remove">✕</button>
                  </motion.div>
                ) : (
                  <motion.div key="dropzone" className="dropzone"
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <div className="dropzone-emoji">🖼️</div>
                    <h3>Drop your photo here</h3>
                    <p>Portrait works best — make sure a face<br />is visible and well-lit.</p>
                    <button className="upload-btn" onClick={e => { e.stopPropagation(); fileInputRef.current?.click(); }}>
                      📤 Choose File
                    </button>
                    <input type="file" ref={fileInputRef} onChange={handleFileUpload}
                      accept="image/*" className="hidden-input" />
                  </motion.div>
                )
              ) : (
                <motion.div key="webcam" className="webcam-viewport"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                >
                  <Webcam audio={false} ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    videoConstraints={{ facingMode: 'user' }}
                    className="webcam-feed" />
                  <BoundingBox />
                  <div className="webcam-controls">
                    <button className={`scan-btn ${isLive ? 'stop' : 'start'}`}
                      onClick={() => setIsLive(v => !v)}>
                      {isLive ? '⏹ Stop Scan' : '▶ Start Scan'}
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Analysis panel */}
        <div className="analysis-panel">
          <div className="panel-header">
            <p className="panel-eyebrow">Neural Output</p>
            <h2 className="panel-title">Emotion Analysis</h2>
          </div>

          <div className="panel-body">
            <AnimatePresence mode="wait">
              {!data ? (
                <motion.div key="empty" className="empty-state"
                  initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                  <div className="empty-emoji">🧠</div>
                  <p className="empty-title">Nothing yet</p>
                  <p className="empty-desc">Upload a portrait or start your webcam scan to see results.</p>
                </motion.div>
              ) : (
                <motion.div key="results"
                  initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35 }}>

                  {/* Dominant card */}
                  {domMeta && (
                    <div className={`dominant-card ${domMeta.cls}`}>
                      <p className={`dominant-tag ${domMeta.cls}`}>Dominant Emotion</p>
                      <div className="dominant-row">
                        <div className="dominant-text">
                          <span className="dominant-emoji">{domMeta.emoji}</span>
                          <strong>{domMeta.label}</strong>
                          <span>Detected with confidence</span>
                        </div>
                        <ConfidenceRing score={dominant.score} cls={domMeta.cls} />
                      </div>
                    </div>
                  )}

                  {/* Spectrum */}
                  <div className="spectrum-section">
                    <p className="spectrum-label">Full Spectrum</p>
                    {data.emotions.map((emo, i) => {
                      const m = getEmotionMeta(emo.label);
                      return (
                        <div key={i} className="bar-row">
                          <div className="bar-label-group">
                            <span className="bar-emoji">{m.emoji}</span>
                            <span className="bar-name">{m.label}</span>
                          </div>
                          <div className="bar-track">
                            <motion.div
                              className={`bar-fill ${m.cls}`}
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.max(emo.score, 0.5)}%` }}
                              transition={{ duration: 0.55, ease: [0.34, 1.56, 0.64, 1], delay: i * 0.06 }}
                            />
                          </div>
                          <span className="bar-pct">{emo.score.toFixed(1)}%</span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Tip */}
                  {domMeta && (
                    <div className="tip-card">
                      <strong>💡 Insight</strong>
                      {domMeta.tip}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}