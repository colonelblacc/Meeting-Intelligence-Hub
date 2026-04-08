# 🎙️ Meeting Intelligence Hub

Transform raw audio recordings and transcripts into actionable intelligence. The **Meeting Intelligence Hub** is an end-to-end, privacy-focused pipeline designed to ingest enterprise meetings, securely anonymize sensitive speakers/data, and perfectly extract decisions and action items.

##  Key Features

### Seamless Audio Processing Pipeline
Upload native media formats (`.mp3`, `.wav`, `.m4a`, and `.mp4`) directly. The application automatically pipes raw data to **Deepgram's Nova-2 model** for blistering-fast Speech-to-Text (STT) and out-of-the-box speaker diarization (e.g., separating "Speaker 0" vs "Speaker 1").

###  Local PII Scrubbing Firewall
Enterprise security is built-in. Using **Microsoft Presidio** and regional **SpaCy** NLP models, the system intercepts locally generated transcripts, instantly locating and redacting sensitive PII entities (Names, Emails, Phone Numbers, Organizations). 
* **Vaulting & Tokenization:** Sensitive data is swapped with isolated tokens (e.g., `<PERSON_1>`) before the text is allowed to hit any third-party external LLM APIs.

###  Advanced NLP Intelligence Extraction
The scrubbed payloads are beamed to **Google Gemini**. A fine-tuned extraction prompt is executed to derive critical context:
- Identifies **Decisions** made during the call.
- Generates precise **Action Items** mapped to specific task assignees.

### Intelligent Re-hydration Engine 
Once the Gemini model returns the summarized action items regarding `<PERSON_1>`, the backend seamlessly intercepts the payload. It queries the local proxy vault, matches the token, and securely re-hydrates the response back to the original name ("John Smith") before displaying it on the frontend. Data privacy is maintained without compromising User Experience!

---

##  Technology Stack

* **Frontend:** Vanilla JS / HTML / Modern CSS
* **Backend:** Python (FastAPI), Uvicorn
* **Audio Pipeline:** Deepgram STT API (`deepgram-sdk`)
* **Security Layer:** Microsoft Presidio (`presidio-analyzer`, `presidio-anonymizer`), SpaCy (`en_core_web_sm`)
* **LLM Core:** Google Gemini Flash (`google-generativeai`)
* **Hosting:** Fully configured for 1-Click Blueprints via **Render.com** 

---

##  Getting Started Locally

### Prerequisites
You will need API keys from **Deepgram** and **Google Gemini (Google AI Studio)**.

### Local Installation
1. **Clone the repo:**
   ```bash
   git clone https://github.com/colonelblacc/Meeting-Intelligence-Hub.git
   cd Meeting-Intelligence-Hub
   ```

2. **Configure your Secrets:**
   Create a `.env` file in the `backend/` directory:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   DEEPGRAM_API_KEY=your_deepgram_key_here
   ```



---

##  Live Demo

You can interact with the live deployed intelligence hub here:
**[View Live Application](https://meeting-intelligence-hub1.onrender.com/)**

*(Note: Hosted on a free Render instance, the server may take up to 60 seconds to wake from a cold start).*
