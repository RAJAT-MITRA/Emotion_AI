import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Camera, UploadCloud, Activity, AlertCircle, Loader2, Sparkles, Image as ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css'; 

export default function App() {
  const [inputMode, setInputMode] = useState('upload'); 
  const [filePreview, setFilePreview] = useState(null);
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null); 
  const [isLive, setIsLive] = useState(false);
  
  const webcamRef = useRef(null);
  const fileInputRef = useRef(null);

  // --- Real-time Webcam Loop ---
  useEffect(() => {
    let interval;
    if (isLive && inputMode === 'webcam') {
      setStatus('processing');
      interval = setInterval(() => {
        captureAndAnalyzeFrame();
      }, 800); // Analyzes a frame every 800ms
    } else if (inputMode === 'webcam' && !isLive) {
      setStatus('idle');
      setData(null);
    }
    return () => clearInterval(interval);
  }, [isLive, inputMode]);

  const captureAndAnalyzeFrame = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) return;

      try {
        const response = await fetch("http://127.0.0.1:8000/analyze-frame", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image: imageSrc }),
        });
        const result = await response.json();
        
        if (!result.error) {
            setData(result);
            setStatus('completed');
        }
      } catch (err) {
        console.error("Webcam stream error:", err);
      }
    }
  };

  // --- File Upload Logic ---
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFilePreview(URL.createObjectURL(file));
    setStatus('processing');
    setData(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      
      if (result.error) throw new Error(result.error);
      
      setData(result);
      setStatus('completed');
    } catch (err) {
      setStatus('error');
      console.error("Upload error:", err);
    }
  };

  // --- Draw the Face Box Dynamically ---
  const renderBoundingBox = () => {
    if (!data || !data.region || data.region.w === 0) return null;
    
    // Convert pixels to percentages so the box scales perfectly with the container
    const { x, y, w, h } = data.region;
    const { image_width, image_height } = data;

    const left = (x / image_width) * 100;
    const top = (y / image_height) * 100;
    const width = (w / image_width) * 100;
    const height = (h / image_height) * 100;

    return (
      <div 
        style={{
          position: 'absolute',
          left: `${left}%`, top: `${top}%`, width: `${width}%`, height: `${height}%`,
          border: '3px solid #22d3ee',
          borderRadius: '8px',
          boxShadow: '0 0 15px rgba(34, 211, 238, 0.5), inset 0 0 15px rgba(34, 211, 238, 0.3)',
          transition: 'all 0.2s ease-out',
          zIndex: 20,
          pointerEvents: 'none'
        }}
      >
        <div style={{ position: 'absolute', top: '-25px', left: '-3px', background: '#22d3ee', color: '#000', padding: '2px 8px', fontSize: '12px', fontWeight: 'bold', borderRadius: '4px', whiteSpace: 'nowrap' }}>
          {data.emotions[0].label} {data.emotions[0].score.toFixed(0)}%
        </div>
      </div>
    );
  };

  const getEmotionClass = (label) => {
    switch(label.toLowerCase()) {
      case 'joy': return 'bar-joy';
      case 'sadness': return 'bar-sadness';
      case 'anger': return 'bar-anger';
      default: return 'bar-neutral';
    }
  };

  return (
    <div className="dashboard-container">
      <div className="ambient-background">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
      </div>

      <div className="dashboard-content">
        <header className="dashboard-header">
          <div className="header-title-wrapper">
            <div className="logo-icon"><Activity className="icon-cyan" size={24} /></div>
            <div>
              <h1 className="main-title">Emotion <span className="text-gradient"> AI</span></h1>
              <p className="subtitle">Real-time facial expression analysis powered by DeepFace CNNs.</p>
            </div>
          </div>
        </header>

        <main className="dashboard-grid">
          {/* LEFT COLUMN: Input Section */}
          <section className="input-section">
            <div className="mode-toggle">
              <button onClick={() => { setInputMode('upload'); setIsLive(false); setData(null); setStatus('idle'); }} className={`toggle-btn ${inputMode === 'upload' ? 'active' : ''}`}>
                <UploadCloud size={16} /> Upload
              </button>
              <button onClick={() => { setInputMode('webcam'); setData(null); setStatus('idle'); }} className={`toggle-btn ${inputMode === 'webcam' ? 'active' : ''}`}>
                <Camera size={16} /> Live Webcam
              </button>
            </div>

            <div className="media-container glass-card">
              {inputMode === 'upload' ? (
                <div className="media-wrapper">
                  {filePreview ? (
                    <div className="preview-container">
                      <img src={filePreview} alt="Preview" className="preview-image" />
                      {renderBoundingBox()}
                      <button onClick={() => { setFilePreview(null); setData(null); setStatus('idle'); }} className="reset-btn">
                        <Activity size={20} />
                      </button>
                    </div>
                  ) : (
                    <div className="drop-zone" onClick={() => fileInputRef.current.click()}>
                      <div className="drop-icon"><ImageIcon size={32} /></div>
                      <h3>Click to Upload Image</h3>
                      <p>Supports JPG, PNG up to 10MB.</p>
                      <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept="image/*" className="hidden-input" />
                    </div>
                  )}
                </div>
              ) : (
                <div className="media-wrapper webcam-wrapper">
                  <Webcam 
                    audio={false} 
                    ref={webcamRef} 
                    screenshotFormat="image/jpeg" 
                    videoConstraints={{ facingMode: "user" }}
                    className="webcam-feed"
                  />
                  {renderBoundingBox()}
                  
                  <button 
                    onClick={() => setIsLive(!isLive)}
                    className={`live-toggle-btn ${isLive ? 'stop' : 'start'}`}
                  >
                    {isLive ? "Stop Scanning" : "Start Live Scan"}
                  </button>
                </div>
              )}
            </div>
          </section>

          {/* RIGHT COLUMN: Results Section */}
          <section className="results-section glass-card">
            <h2 className="results-title"><Activity size={20} className="icon-indigo" /> Analysis Results</h2>
            <div className="results-content">
              
              {!data && status !== 'processing' && (
                 <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="empty-state">
                   <div className="empty-orb" />
                   <p>Awaiting input to generate neural confidence scores.</p>
                 </motion.div>
              )}
              
              {status === 'processing' && !data && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="loading-state">
                  <Loader2 size={48} className="spin-animation icon-cyan" style={{ margin: '0 auto 1rem' }} />
                  <p>Analyzing frame...</p>
                </motion.div>
              )}

              {data && data.emotions && (
                <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="results-data">
                  <div className="dominant-emotion">
                    <div>
                      <p className="label">Dominant Trait</p>
                      <h3>{data.emotions[0].label}</h3>
                    </div>
                    <div className="text-right">
                      <p className="label">Confidence</p>
                      <span className="score">{data.emotions[0].score.toFixed(1)}%</span>
                    </div>
                  </div>
                  <div className="progress-list">
                    <h4 className="label">Full Spectrum</h4>
                    {data.emotions.map((emo, idx) => (
                      <div key={idx} className="progress-item">
                        <div className="progress-info">
                          <span>{emo.label}</span>
                          <span className="progress-score">{emo.score.toFixed(1)}%</span>
                        </div>
                        <div className="progress-track">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${emo.score}%` }}
                            transition={{ duration: 0.5, ease: "easeOut" }}
                            className={`progress-fill ${getEmotionClass(emo.label)}`}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

            </div>
          </section>
        </main>
      </div>
    </div>
  );
}