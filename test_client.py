import os
import sys
import asyncio
import urllib.request
import urllib.parse
import json

# We can use edge-tts to generate a test voice file to upload to the server
try:
    import edge_tts
except ImportError:
    print("To run this test script, please install edge-tts: pip install edge-tts")
    sys.exit(1)

SERVER_URL = "http://127.0.0.1:8000/api/voice"
TEST_TEXT = "Hello! Tell me a very short joke."

async def generate_test_audio(text: str, filename: str):
    print(f"Generating test audio file: '{text}' -> {filename}...")
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save(filename)
    print("Audio file generated successfully.")

def upload_and_get_response(input_filename: str, output_filename: str):
    print(f"Sending audio to server: {SERVER_URL}...")
    
    # Read the audio bytes
    with open(input_filename, "rb") as f:
        audio_bytes = f.read()

    # Construct the multipart/form-data request manually using standard urllib
    boundary = "----VoiceAgentTestBoundary"
    parts = []
    parts.append(f"--{boundary}".encode('utf-8'))
    parts.append(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(input_filename)}"'.encode('utf-8'))
    parts.append(b"Content-Type: audio/mpeg")
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
            with open(output_filename, "wb") as out_f:
                out_f.write(response_audio)
            print(f"Saved agent reply audio to: {output_filename}")
            return True
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"Error communicating with server: {str(e)}")
    return False

async def main():
    input_file = "test_input.mp3"
    output_file = "test_response.mp3"
    
    try:
        # Generate dummy input speech
        await generate_test_audio(TEST_TEXT, input_file)
        
        # Post to server and save output speech
        success = upload_and_get_response(input_file, output_file)
        if success:
            print("\nSUCCESS! The voice agent backend successfully transcribed, queried the LLM, generated response speech, and sent it back.")
        else:
            print("\nFAILED: Server did not return voice response.")
            
    finally:
        # Clean up temporary test input file
        if os.path.exists(input_file):
            os.remove(input_file)

if __name__ == "__main__":
    asyncio.run(main())
