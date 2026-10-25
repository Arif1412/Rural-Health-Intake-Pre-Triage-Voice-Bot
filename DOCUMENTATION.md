# 📄 Technical Development & System Architecture Documentation

**Project Name:** AarogyaVoice — Sovereign Rural Health Intake & Pre-Triage Voice Assistant

**Developer:** Md. Golam Morshed

**Platform Stack:** Gnani AI Artha Stack (Prisma v2.5 STT, Timbre v2.5 TTS)

**Environment & Hosting:** Python 3.10+ / FastAPI / Render Cloud PaaS

---

## 1. Executive Summary & Problem Statement

In rural and semi-urban Indian healthcare settings, frontline health workers (ASHA/ANM workers) face significant challenges during initial patient intake:

* **Literacy & Language Barriers:** Patients often cannot read or fill out written health forms and articulate symptoms exclusively in spoken regional Indic dialects (Hindi, Hinglish).
* **Triage Bottlenecks:** Primary Health Centers (PHCs) are frequently overcrowded, leading to delays in identifying life-threatening emergency cases versus routine outpatient consultations.

**Solution:** An end-to-end sovereign voice AI application built on **Gnani AI’s Artha Stack**. The system ingests patient audio uploads, transcribes Indic speech with high precision using **Prisma v2.5**, classifies clinical risk using a multi-keyword Triage Logic Engine, and generates natural spoken audio advice in Hindi via **Timbre v2.5** through a responsive, developer-grade web dashboard deployed on Render.

---

## 2. Technical Stack & API Specs

| Component | Technology / Service | Endpoint / Library | Purpose |
| --- | --- | --- | --- |
| **Speech Recognition (STT)** | Gnani AI Prisma v2.5 | `POST [https://api.vachana.ai/stt/v3](https://api.vachana.ai/stt/v3)`

 | High-accuracy transcription of Hindi/Hinglish audio files. |
| **Clinical Triage Engine** | Custom Python Engine | Rule-Based Parser (Devanagari + Hinglish) | Risk stratification (**RED**, **YELLOW**, **GREEN**) & action plan synthesis. |
| **Speech Synthesis (TTS)** | Gnani AI Timbre v2.5 | `POST [https://api.vachana.ai/api/v1/tts/inference](https://api.vachana.ai/api/v1/tts/inference)`

 | Generates 24kHz localized Hindi audio advice (`Nalini` voice).

 |
| **Backend Framework** | FastAPI + Uvicorn | `fastapi`, `uvicorn`, `requests` | Asynchronous python API execution with minimal memory overhead. |
| **Frontend Web UI** | Tailwind CSS + HTML5 | Custom Single Page Application | Responsive dark UI supporting audio file upload with instant local preview. |
| **Deployment Platform** | Render Cloud PaaS | Automated GitHub CI/CD container hosting | Persistent cloud hosting with secure environment variable configuration (`GNANIAPIKEY`). |

---

## 3. End-to-End System Architecture

```text
               ┌─────────────────────────────────────────────────────────┐
               │ Patient Voice Input File Upload (.wav / .mp3 w/ Preview)│
               └────────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: SPEECH-TO-TEXT TRANSCRIPTION                                                  │
│ API Endpoint: POST https://api.vachana.ai/stt/v3[cite: 3]                            │
│ Model: prisma-v2.5 | Language: hi-IN[cite: 3]                                        │
│ Output: Transcribed Devanagari / Hinglish Text                                        │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: CLINICAL PRE-TRIAGE LOGIC ENGINE                                              │
│ Multi-Keyword Evaluation (Devanagari + Romanized Hinglish Matching)                   │
│ • RED (Emergency): Critical signs (chest pain, breathlessness / सांस / दर्द)          │
│ • YELLOW (Moderate): Fever, stomach issues (bukhar / बुखार / पेट)                      │
│ • GREEN (Mild): Routine self-care / observation                                       │
│ Output: Risk Categorization + Actionable Medical Solutions                            │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: TEXT-TO-SPEECH VOICE SYNTHESIS                                                │
│ API Endpoint: POST https://api.vachana.ai/api/v1/tts/inference[cite: 3]              │
│ Model: timbre-v2.5 | Voice: Nalini | Container: wav (24kHz)[cite: 1, 3]              │
│ Output: Generated Audio Response File (response.wav)                                  │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
               ┌─────────────────────────────────────────────────────────┐
               │         Spoken Audio Output & Action Plan UI            │
               └─────────────────────────────────────────────────────────┘

```

---

## 4. Step-by-Step Development Roadmap

### Phase 1: Authentication & Environment Setup

1. **API Key Provisioning:** Created and verified developer API credentials on the Gnani AI platform.
2. **Secure Secret Management:** Configured Render environment variables (`GNANIAPIKEY`) to securely manage keys in production.
3. **HTTP Client Configuration:** Standardized request headers using `X-API-Key-ID` for authentication.

### Phase 2: Speech-to-Text Integration (Prisma v2.5)

1. **Endpoint Alignment:** Evaluated REST API parameters and mapped the primary STT endpoint to `/stt/v3`.


2. **Payload Construction:** Formatted multipart form-data to pass the `audio_file` binary stream alongside control flags (`language_code="hi-IN"`, `format="transcribe"`, `itn_native_numerals="true"`).


3. **Response Parsing:** Robustly handled JSON payloads to extract the transcription string across varying response keys (`transcript` / `text`).

### Phase 3: Clinical Triage & Solution Parser

1. **Initial Prototype (Hinglish):** Implemented basic keyword matching for Romanized terms (`bukhar`, `pet`, `dard`).
2. **Iterative Refinement (Bilingual Support):** Expanded the parser to evaluate Devanagari script (`बुखार`, `पेट`, `दर्द`, `सांस`) after real-world STT test runs revealed native Hindi transcription outputs from Prisma v2.5.
3. **Structured Advice Output:** Segmented outputs into:

* **Spoken Advice (Hindi):** Simple, reassuring spoken audio text for the patient.
* **Actionable Next Steps (English):** Concise, bulleted clinical recommendations for frontline healthcare workers.

### Phase 4: Text-to-Speech Integration (Timbre v2.5)

1. **Payload Specification:** Built JSON request bodies targeting `/api/v1/tts/inference` using `model: "timbre-v2.5"`, `voice: "Nalini"`, and 24kHz WAV configuration.


2. **Audio File Rendering:** Handled binary byte response streams (`response.content`) and saved them to disk (`response.wav`).
3. **In-Browser Playback:** Rendered HTML5 audio elements on the frontend for both instant audio preview before analysis and synthesized audio response playback.

### Phase 5: Production Web Application & Render Deployment

1. **FastAPI Backend Setup (`app.py`):** Configured REST endpoints (`/api/analyze` and `/api/audio`) to handle file uploads, process speech analysis, and return structured JSON results.
2. **Tailwind CSS Frontend Dashboard:** Designed an ultra-modern, dark-themed single-page application with smooth hover animations, file upload dropzones, and instant audio preview players.
3. **Cloud Deployment:** Deployed the application to Render PaaS with automated GitHub CI/CD build and start commands (`uvicorn app:app --host 0.0.0.0 --port $PORT`).

---

## 5. Key Challenges & Technical Solutions

| Challenge Experienced | Root Cause | Technical Fix Applied |
| --- | --- | --- |
| **`401 Unauthorized`** | Missing or uninitialized API key variable. | Switched to Render Environment Secrets (`GNANIAPIKEY`) for secure runtime injection. |
| **`404 Not Found` on STT** | Invalid legacy REST endpoint route (`/stt/transcribe`). | Updated STT request routing to Gnani AI's official REST path: `[https://api.vachana.ai/stt/v3](https://api.vachana.ai/stt/v3)`.

 |
| **Triage Misclassification (GREEN instead of YELLOW)** | Keywords checked Romanized text (`bukhar`), whereas Prisma v2.5 transcribed in Devanagari (`बुखार`). | Enhanced the logic engine to perform dual-script matching across both Devanagari and Hinglish keyword arrays. |

---

## 6. Verification & Test Results

A full end-to-end live test was executed using a patient audio file (`audio1.wav`):

1. **Input Audio:** Patient describing symptoms out loud in Hindi.
2. **Prisma v2.5 STT Output:**

> *"दाहिनी आंख में जलन और दर्द है..."*

3. **Triage Classification Output:**

* **Triage Level:** `YELLOW (Moderate)`
* **Spoken Patient Advice:** *"आपको आँख में दर्द या समस्या है। अपनी आँख को बार-बार न छुएं और तुरंत नेत्र विशेषज्ञ से मिलें।"*
* **Actionable Steps for Health Worker:**

1. Wash eyes gently with clean water.
2. Avoid rubbing eyes.
3. Consult an ophthalmologist within 24 hours.
4. **Timbre v2.5 TTS Output:** Audio file (`response.wav`) generated successfully and played back via the web UI player with clear Hindi pronunciation.

---

## 7. Future Enhancements & Production Roadmap

* **LLM-Powered Clinical Parsing:** Replace rule-based keyword matching with a fine-tuned medical LLM (e.g., Med-PaLM / Llama-3-Medical) for complex multi-symptom diagnosis.
* **Offline Mobile Deployment:** Package the frontend as an Android APK (using Flutter or React Native) for offline edge execution in zero-connectivity rural zones.
* **Electronic Health Record (EHR) Integration:** Automatically push intake transcripts and triage logs directly to India's **ABDM (Ayushman Bharat Digital Mission)** health stack.
