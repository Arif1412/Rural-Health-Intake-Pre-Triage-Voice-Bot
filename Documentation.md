# 📄 Technical Development & System Architecture Documentation

**Project Name:** Rural Health Intake & Pre-Triage Voice Assistant

**Developer:** Md. Golam Morshed

**Platform Stack:** Gnani AI Artha Stack (Prisma v2.5 STT, Timbre v2.5 TTS)

**Environment:** Google Colab / Python 3.10+ / Gradio

---

## 1. Executive Summary & Problem Statement

In rural and semi-urban Indian healthcare settings, frontline health workers (ASHA/ANM workers) face significant challenges during initial patient intake:

* **Literacy & Language Barriers:** Patients often cannot read or fill out written health forms and articulate symptoms exclusively in spoken regional Indic dialects (Hindi, Hinglish).
* **Triage Bottlenecks:** Primary Health Centers (PHCs) are frequently overcrowded, leading to delays in identifying life-threatening emergency cases versus routine outpatient consultations.

**Solution:** An end-to-end sovereign voice AI application built on **Gnani AI’s Artha Stack**. The system ingests patient voice recordings, transcribes Indic speech with high precision using **Prisma v2.5**, classifies clinical risk using a multi-keyword Triage Logic Engine, and generates natural spoken audio advice in Hindi via **Timbre v2.5**.

---

## 2. Technical Stack & API Specs

| Component | Technology / Service | Endpoint / Library | Purpose |
| --- | --- | --- | --- |
| **Speech Recognition (STT)** | Gnani AI Prisma v2.5 | `POST [https://api.vachana.ai/stt/v3](https://api.vachana.ai/stt/v3)` | High-accuracy transcription of Hindi/Hinglish audio files. |
| **Clinical Triage Engine** | Custom Python Engine | Rule-Based Parser (Devanagari + Hinglish) | Risk stratification (**RED**, **YELLOW**, **GREEN**) & action plan synthesis. |
| **Speech Synthesis (TTS)** | Gnani AI Timbre v2.5 | `POST [https://api.vachana.ai/api/v1/tts/inference](https://api.vachana.ai/api/v1/tts/inference)` | Generates 24kHz localized Hindi audio advice (`Nalini` voice). |
| **Execution Environment** | Google Colab | `google.colab.userdata` | Secure API key storage and notebook runtime execution. |
| **Web Interface** | Gradio UI | `gradio.Interface` | Interactive web frontend supporting live mic recording and audio playback. |

---

## 3. End-to-End System Architecture

```text
               ┌─────────────────────────────────────────────────────────┐
               │              Patient Voice Input (.wav / .mp3)          │
               └────────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
 ┌───────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 1: SPEECH-TO-TEXT TRANSCRIPTION                                                  │
 │ API Endpoint: POST https://api.vachana.ai/stt/v3                                      │
 │ Model: prisma-v2.5 | Language: hi-IN                                                 │
 │ Output: Transcribed Devanagari / Hinglish Text                                        │
 └──────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
 ┌───────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 2: CLINICAL PRE-TRIAGE LOGIC ENGINE                                              │
 │ Multi-Keyword Evaluation (Devanagari + Romanized Hinglish Matching)                  │
 │ • RED (Emergency): Critical signs (chest pain, breathlessness / सांस / दर्द)         │
 │ • YELLOW (Moderate): Fever, stomach issues (bukhar / बुखार / पेट)                    │
 │ • GREEN (Mild): Routine self-care / observation                                       │
 │ Output: Risk Categorization + Actionable Medical Solutions                            │
 └──────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
 ┌───────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 3: TEXT-TO-SPEECH VOICE SYNTHESIS                                                │
 │ API Endpoint: POST https://api.vachana.ai/api/v1/tts/inference                        │
 │ Model: timbre-v2.5 | Voice: Nalini | Container: wav (24kHz)                           │
 │ Output: Generated Audio Response File (response.wav)                                 │
 └──────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
               ┌─────────────────────────────────────────────────────────┐
               │           Spoken Audio Output & Action Plan UI          │
               └─────────────────────────────────────────────────────────┘

```

---

## 4. Step-by-Step Development Roadmap

### Phase 1: Authentication & Environment Setup

1. **API Key Provisioning:** Created and verified developer API credentials on the Gnani AI platform.
2. **Secure Secret Management:** Configured Google Colab Secrets (`userdata.get('GNANI_API_KEY')`) to prevent hardcoding credentials in public source files.
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
3. **In-Notebook Playback:** Rendered HTML5 audio players in Colab using `IPython.display.Audio`.

### Phase 5: Interactive Web UI (Gradio Integration)

1. Wrapped the entire pipeline into a single execution function (`process_patient_audio`).
2. Deployed a web UI using Gradio, supporting live microphone recording, transcript display, triage level alerts, and automatic voice playback.

---

## 5. Key Challenges & Technical Solutions

| Challenge Experienced | Root Cause | Technical Fix Applied |
| --- | --- | --- |
| **`401 Unauthorized`** | Missing or uninitialized API key variable. | Switched to Colab Secrets (`userdata.get('GNANI_API_KEY')`) for secure runtime injection. |
| **`404 Not Found` on STT** | Invalid legacy REST endpoint route (`/stt/transcribe`). | Updated STT request routing to Gnani AI's official REST path: `[https://api.vachana.ai/stt/v3](https://api.vachana.ai/stt/v3)`. |
| **Triage Misclassification (GREEN instead of YELLOW)** | Keywords checked Romanized text (`bukhar`), whereas Prisma v2.5 transcribed in Devanagari (`बुखार`). | Enhanced the logic engine to perform dual-script matching across both Devanagari and Hinglish keyword arrays. |

---

## 6. Verification & Test Results

A full end-to-end live test was executed using a recorded patient audio file (`voicetest.wav`):

1. **Input Audio:** Patient describing symptoms out loud in Hindi.
2. **Prisma v2.5 STT Output:**
> *"हेलो मेरा नाम मोहम्मद गुलाम मुर्शिद है... मुझे २ दिन से बुखार है और मेरा पेट में भी थोड़ा थोड़ा प्रॉब्लम हो रहा है..."*


3. **Triage Classification Output:**
* **Triage Level:** `YELLOW (Moderate - Outpatient Consultation)`
* **Spoken Patient Advice:** *"आपके लक्षणों के अनुसार आपको बुखार है। कृपया पर्याप्त मात्रा में पानी पिएं, आराम करें और डॉक्टर से सलाह लें।"*
* **Actionable Steps for Health Worker:**
1. Monitor body temperature every 4–6 hours.
2. Stay hydrated with oral rehydration salts (ORS) or water.
3. Consult a general physician within 24 hours for proper medication.




4. **Timbre v2.5 TTS Output:** Audio file (`response.wav`) generated in 6 seconds and played back successfully with clear Hindi pronunciation.

---

## 7. Future Enhancements & Production Roadmap

* **LLM-Powered Clinical Parsing:** Replace rule-based keyword matching with a fine-tuned medical LLM (e.g., Med-PaLM / Llama-3-Medical) for complex multi-symptom diagnosis.
* **Offline Mobile Deployment:** Package the frontend as an Android APK (using Flutter or React Native) for offline edge execution in zero-connectivity rural zones.
* **Electronic Health Record (EHR) Integration:** Automatically push intake transcripts and triage logs directly to India's **ABDM (Ayushman Bharat Digital Mission)** health stack.
