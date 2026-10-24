# 🩺 AarogyaVoice: Sovereign Rural Health Intake & Pre-Triage Voice Assistant

> *Empowering frontline healthcare workers in rural India with sovereign, localized conversational AI.*

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-005571?logo=fastapi)
![Gnani AI Artha Stack](https://img.shields.io/badge/Powered%20by-Gnani%20AI%20Artha%20Stack-purple)
![Deployment](https://img.shields.io/badge/Status-Live%20on%20Render-success)

---

## 🚀 Live Demo & Submission Links
* **Live Web Application:** [https://aarogyavoice.onrender.com](https://aarogyavoice.onrender.com/)
* **Challenge:** Great Indian AI Internship Challenge

---

## 💡 Overview
In rural and remote parts of India, frontline health workers (ASHA/ANM workers) often face language barriers, heavy patient queues, and the challenge of rapid symptom triage. **AarogyaVoice** bridges this gap by offering a fully functional, sleek, dark-themed voice intake web application. 

By capturing spoken patient descriptions in Indian languages and dialects, AarogyaVoice transcribes the audio, runs a dynamic clinical triage evaluation, categorizes urgency (Red/Yellow/Green), and provides immediate localized voice-synthesized medical guidance.

---

## 🛠️ Tech Stack & Architecture
Built entirely on sovereign Indian AI infrastructure:
* **Backend:** FastAPI (Python) serving REST endpoints and managing asset lifecycles.
* **Speech-to-Text (STT):** **Gnani AI Prisma v2.5** (`/stt/v3`) for accurate vernacular transcription and native numeral processing.
* **Triage Engine:** Custom rule-based medical pre-triage logic engine parsing specific organ and symptom keywords (fever, respiratory distress, head/eye/hand/leg pain).
* **Text-to-Speech (TTS):** **Gnani AI Timbre v2.5** (`/api/v1/tts/inference`) using the `Nalini` voice model at 24kHz to synthesize natural-sounding Hindi voice responses.
* **Frontend:** Responsive, modern single-page dashboard built with Tailwind CSS.
* **Deployment:** Containerized and hosted permanently via Render.

---

## 🔍 How It Works (The Clinical Workflow)
1. **Audio Intake:** The health worker uploads or records a patient audio sample (`.wav` or `.mp3`).
2. **Vernacular Transcription:** Prisma v2.5 accurately transcribes the spoken speech text.
3. **Smart Triage & Actionable Steps:** The backend evaluates symptoms dynamically, outputting an urgent triage level (`RED`, `YELLOW`, or `GREEN`) alongside clear steps for healthcare workers.
4. **Voice Guidance:** Timbre v2.5 generates a spoken audio response advising the patient on immediate next steps.

---

## 🏗️ Architecture & Pipeline Flow

```text
 ┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
 │ Patient Audio (.wav)   │ ───> │ Prisma v2.5 (STT)      │ ───> │ Triage Logic Engine    │
 └────────────────────────┘      └────────────────────────┘      └────────────────────────┘
                                                                              │
                                                                              ▼
 ┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
 │ Audio Playback in Colab│ <─── │ Timbre v2.5 (TTS)      │ <─── │ Symptom & Solutions    │
 └────────────────────────┘      └────────────────────────┘      └────────────────────────┘



