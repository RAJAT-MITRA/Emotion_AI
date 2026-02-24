import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
from deepface import DeepFace
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class FrameData(BaseModel):
    image: str

# Helper to aggressively convert any NumPy type into a safe Python type
def safe_float(val):
    try:
        return float(val.item() if hasattr(val, 'item') else val)
    except:
        return 0.0

def safe_int(val):
    try:
        return int(val.item() if hasattr(val, 'item') else val)
    except:
        return 0

def process_frame(img):
    # 1. Protect against empty frames during webcam initialization
    if img is None or img.size == 0:
        return {"error": "Awaiting clear webcam frame..."}

    try:
        results = DeepFace.analyze(img_path=img, actions=["emotion"], enforce_detection=False, silent=True)
        
        if isinstance(results, list):
            results = results[0]
            
        raw_emotions = results.get("emotion", {})
        region = results.get("region", {"x": 0, "y": 0, "w": 0, "h": 0}) 
        
        # 2. Aggressively cast everything to avoid 500 Serialization Errors
        formatted_emotions = [
            {"label": "Joy", "score": safe_float(raw_emotions.get("happy", 0))},
            {"label": "Sadness", "score": safe_float(raw_emotions.get("sad", 0))},
            {"label": "Anger", "score": safe_float(raw_emotions.get("angry", 0))},
            {"label": "Neutral", "score": safe_float(raw_emotions.get("neutral", 0))}
        ]
        
        formatted_emotions.sort(key=lambda x: x["score"], reverse=True)
        
        safe_region = {
            "x": safe_int(region.get("x", 0)),
            "y": safe_int(region.get("y", 0)),
            "w": safe_int(region.get("w", 0)),
            "h": safe_int(region.get("h", 0))
        }
        
        return {
            "emotions": formatted_emotions,
            "region": safe_region,
            "image_width": safe_int(img.shape[1]),
            "image_height": safe_int(img.shape[0])
        }
    except Exception as e:
        # Return cleanly so React can handle it without a 500 server crash
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_upload(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return process_frame(img)

@app.post("/analyze-frame")
async def analyze_frame(data: FrameData):
    try:
        header, encoded = data.image.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return process_frame(img)
    except Exception as e:
        return {"error": "Failed to decode base64 stream."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)