import os
import json
import logging
import urllib.request
import urllib.error

class AudioProcessingService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("DEEPGRAM_API_KEY")

    async def transcribe_audio_bytes(self, audio_bytes: bytes, mime_type: str) -> str:
        """
        Takes raw audio/video bytes, uploads to Deepgram via REST for fast transcription and 
        speaker diarization, and formats the output into a readable transcript 
        (e.g. Speaker 0: Words...).
        """
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY not configured natively.")
            
        url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&diarize=true&punctuate=true"
        
        req = urllib.request.Request(url, data=audio_bytes, method="POST")
        req.add_header("Authorization", f"Token {self.api_key}")
        req.add_header("Content-Type", mime_type)
        
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                data = json.loads(response_data)
                
            transcript_text = ""
            if "results" in data and "channels" in data["results"]:
                alternatives = data["results"]["channels"][0]["alternatives"]
                if not alternatives:
                    return ""
                    
                first_alt = alternatives[0]
                
                # Check for paragraphs feature
                if "paragraphs" in first_alt and "paragraphs" in first_alt["paragraphs"]:
                    for para in first_alt["paragraphs"]["paragraphs"]:
                        speaker = para.get("speaker", 0)
                        sentences = [s.get("text", "") for s in para.get("sentences", [])]
                        if sentences:
                            text = " ".join(sentences)
                            transcript_text += f"Speaker {speaker}: {text}\n\n"
                
                # Fallback to plain words list if paragraphs aren't generated
                elif "words" in first_alt:
                    words = first_alt["words"]
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
            if not transcript_text and "results" in data:
                transcript_text = data["results"]["channels"][0]["alternatives"][0].get("transcript", "")

            return transcript_text.strip()
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logging.error(f"Deepgram transcription failed: {e.code} - {error_body}")
            raise Exception(f"Deepgram HTTP {e.code}: {error_body}")
        except Exception as e:
            logging.error(f"Deepgram processing failed: {e}")
            raise

audio_processor = AudioProcessingService()
