import os
import json
import logging
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

# The Deepgram SDK checks for DEEPGRAM_API_KEY environment variable.

class AudioProcessingService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("DEEPGRAM_API_KEY")
        if self.api_key:
            self.deepgram = DeepgramClient(self.api_key)
        else:
            self.deepgram = None

    async def transcribe_audio_bytes(self, audio_bytes: bytes, mime_type: str) -> str:
        """
        Takes raw audio/video bytes, uploads to Deepgram for fast transcription and 
        speaker diarization, and formats the output into a readable transcript 
        (e.g. Speaker 0: Words...).
        """
        if not self.deepgram:
            raise ValueError("DEEPGRAM_API_KEY not configured natively.")
            
        payload: FileSource = {
            "buffer": audio_bytes,
        }

        options: PrerecordedOptions = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            diarize=True,
            punctuate=True
        )

        try:
            # Note: Deepgram SDK v3 provides an sync and async client. 
            # We use the blocking interface inside our async function for simplicity 
            # or the async version if available in the client.
            # Using listen.rest.v("1").transcribe_file for Deepgram v3 SDK
            response = self.deepgram.listen.rest.v("1").transcribe_file(payload, options)
            
            # Format the output into text transcript blocks based on paragraphs and speakers
            transcript_text = ""
            if "results" in response and "channels" in response["results"]:
                paragraphs = response["results"]["channels"][0]["alternatives"][0].get("paragraphs", {})
                
                if paragraphs and "transcript" in paragraphs:
                    # Deepgram optionally returns formatted paragraph blocks
                    # Let's extract speaker-separated paragraphs
                    for para in paragraphs.get("paragraphs", []):
                        speaker = para.get("speaker", 0)
                        text = para.get("sentences", [{"text": para.get("text", "")}])[0].get("text", "")
                        # Combine sentences
                        sentences = [s.get("text", "") for s in para.get("sentences", [])]
                        if sentences:
                            text = " ".join(sentences)
                        
                        transcript_text += f"Speaker {speaker}: {text}\n\n"
                        
                else:
                    # Fallback to plain words list if paragraphs aren't generated
                    words = response["results"]["channels"][0]["alternatives"][0].get("words", [])
                    current_speaker = None
                    for word in words:
                        speaker = word.get("speaker", 0)
                        word_text = word.get("punctuated_word", word.get("word", ""))
                        if speaker != current_speaker:
                            if current_speaker is not None:
                                transcript_text += "\n\n"
                            transcript_text += f"Speaker {speaker}: "
                            current_speaker = speaker
                        transcript_text += f"{word_text} "
            
            # Fallback if structure is unexpected
            if not transcript_text:
                transcript_text = response["results"]["channels"][0]["alternatives"][0]["transcript"]

            return transcript_text.strip()
            
        except Exception as e:
            logging.error(f"Deepgram transcription failed: {e}")
            raise

audio_processor = AudioProcessingService()
