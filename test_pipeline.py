import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Load env FIRST so global instantiations catch it
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from services.audio_processor import audio_processor
from services.gemini_extractor import extract_meeting_intelligence, configure_gemini
from services.pii_scrubber import pii_scrubber

configure_gemini(os.environ.get("GEMINI_API_KEY"))

async def main():
    file_path = "Product Marketing Meeting (weekly) 2021-06-28 [lBVtvOpU80Q].mp3"
    print(f"Reading {file_path}...")
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    print("Transcribing with Deepgram...")
    try:
        transcript = await audio_processor.transcribe_audio_bytes(audio_bytes, "audio/mp3")
        print(f"Transcription length: {len(transcript)} chars.")
        print(f"Preview: {transcript[:200]}...")
    except Exception as e:
        print(f"Transcription failed: {e}")
        return

    print("Scrubbing PII...")
    sanitized_text, vault = pii_scrubber.scrub_and_vault(transcript)
    print(f"Scrubbed Preview: {sanitized_text[:200]}...")
    print(f"Tokens saved: {len(vault)}")

    print("Extracting Intelligence with Gemini...")
    intelligence = await extract_meeting_intelligence(sanitized_text)
    
    print("Re-hydrating PII...")
    rehydrated_intelligence = pii_scrubber.rehydrate(intelligence, vault)
    
    print("\n\nFINAL EXTRACTED INTELLIGENCE:")
    print(json.dumps(rehydrated_intelligence, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
