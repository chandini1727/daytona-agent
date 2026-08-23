import os
import urllib.request
import urllib.parse

WAV_URL = "https://www.voiptroubleshooter.com/open_speech/american/OSR_us_000_0010_8k.wav"
WAV_FILENAME = "harvard_speech_sample.wav"
SERVER_URL = "http://127.0.0.1:8000/api/voice"
OUTPUT_FILENAME = "harvard_agent_reply.mp3"

def download_sample_wav():
    if not os.path.exists(WAV_FILENAME):
        print(f"Downloading sample speech WAV file from: {WAV_URL}...")
        try:
            req = urllib.request.Request(
                WAV_URL,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                with open(WAV_FILENAME, "wb") as f:
                    f.write(response.read())
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download sample audio: {e}")
            return False
    return True

def upload_wav_and_get_response():
    print(f"Sending standard WAV audio directly to server: {SERVER_URL}...")
    
    # Read the audio bytes
    with open(WAV_FILENAME, "rb") as f:
        audio_bytes = f.read()

    # Construct the multipart/form-data request manually
    boundary = "----VoiceAgentWavBoundary"
    parts = []
    parts.append(f"--{boundary}".encode('utf-8'))
    parts.append(f'Content-Disposition: form-data; name="file"; filename="{WAV_FILENAME}"'.encode('utf-8'))
    parts.append(b"Content-Type: audio/wav")
    parts.append(b"")
    parts.append(audio_bytes)
    parts.append(f"--{boundary}--".encode('utf-8'))
    parts.append(b"")
    
    body = b"\r\n".join(parts)
    
    req = urllib.request.Request(
        SERVER_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body))
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print("Received response from server!")
            response_audio = response.read()
            with open(OUTPUT_FILENAME, "wb") as out_f:
                out_f.write(response_audio)
            print(f"Success! Saved agent reply audio to: {OUTPUT_FILENAME}")
            
            # Print success info
            print("\nThe voice agent successfully received the WAV file, processed STT -> LLM -> TTS, and returned the speech response.")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Error communicating with server: {str(e)}")
    return False

def main():
    if download_sample_wav():
        upload_wav_and_get_response()

if __name__ == "__main__":
    main()
