import os
import json
import tempfile
import subprocess
import urllib.request
import urllib.error
import speech_recognition as sr
import pypdf
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Pure Backend Voice Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL_ID = "meta-llama/llama-3.3-70b-instruct"

# Simple in-memory conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful, extremely concise, and friendly AI voice assistant. Since you are speaking out loud, keep your answers to 1 or 2 short sentences. Do not use markdown, code blocks, or emojis. Speak naturally."}
]

class ChatTextRequest(BaseModel):
    message: str

def query_openrouter(user_msg: str) -> str:
    conversation_history.append({"role": "user", "content": user_msg})
    
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": MODEL_ID,
            "messages": conversation_history
        }).encode('utf-8')
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read()
            res_json = json.loads(res_body.decode('utf-8'))
            agent_reply = res_json['choices'][0]['message']['content']
            conversation_history.append({"role": "assistant", "content": agent_reply})
            return agent_reply
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        raise RuntimeError(f"OpenRouter API Error: {e.code} - {error_msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to query OpenRouter: {str(e)}")

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Pure Backend Voice Agent",
        "endpoints": {
            "POST /api/voice": "Send audio file via form-data (key: 'file'), returns speech MP3 output directly."
        }
    }

@app.post("/api/voice")
async def voice_endpoint(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    suffix = os.path.splitext(file.filename)[1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_input:
        temp_input.write(await file.read())
        temp_input_path = temp_input.name

    temp_wav_path = None
    try:
        user_text = ""
        
        # Check if the upload is a text file
        if suffix.lower() == ".txt":
            with open(temp_input_path, "r", encoding="utf-8", errors="ignore") as f:
                user_text = f.read()
            print(f"\n[TXT] User uploaded text: {user_text}")
            if not user_text.strip():
                raise HTTPException(status_code=400, detail="Uploaded text file is empty.")
                
        # Check if the upload is a PDF file
        elif suffix.lower() == ".pdf":
            try:
                reader = pypdf.PdfReader(temp_input_path)
                extracted_text = []
                for page in reader.pages:
                    extracted_text.append(page.extract_text() or "")
                user_text = "\n".join(extracted_text)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse PDF file: {str(e)}")
                
            print(f"\n[PDF] User uploaded PDF, extracted text length: {len(user_text)}")
            if not user_text.strip():
                raise HTTPException(status_code=400, detail="Could not extract any text from the uploaded PDF file.")
                
        # Otherwise, process as an audio file (Speech-to-Text)
        else:
            if suffix.lower() != ".wav":
                temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_wav_path = temp_wav.name
                temp_wav.close()
                
                # Run ffmpeg conversion
                cmd = ["ffmpeg", "-y", "-i", temp_input_path, "-ac", "1", "-ar", "16000", temp_wav_path]
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        raise HTTPException(status_code=400, detail=f"FFmpeg audio conversion failed: {result.stderr}")
                except FileNotFoundError:
                    raise HTTPException(
                        status_code=500, 
                        detail="FFmpeg is not installed on this host system. Please install FFmpeg, or run the agent inside its Docker container where FFmpeg is pre-configured."
                    )
                transcribe_path = temp_wav_path
            else:
                transcribe_path = temp_input_path

            # Perform Speech-to-Text using speech_recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(transcribe_path) as source:
                audio_data = recognizer.record(source)
            
            try:
                user_text = recognizer.recognize_google(audio_data)
                print(f"\n[STT] User said: {user_text}")
            except sr.UnknownValueError:
                raise HTTPException(status_code=400, detail="Speech Recognition could not understand the audio.")
            except sr.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Speech Recognition service error: {str(e)}")

        # Query LLM (OpenRouter)
        try:
            agent_text = query_openrouter(user_text)
            print(f"[LLM] Agent reply: {agent_text}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

        # Perform Text-to-Speech offline using espeak command-line
        output_wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        try:
            subprocess.run([
                "espeak", 
                "-w", output_wav_path, 
                agent_text
            ], check=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Offline espeak TTS failed: {str(e)}")
        print(f"[TTS] Generated offline speech at: {output_wav_path}")

        # Return the generated audio response
        return FileResponse(
            output_wav_path, 
            media_type="audio/wav", 
            filename="response.wav"
        )

    finally:
        # Cleanup temporary files
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
