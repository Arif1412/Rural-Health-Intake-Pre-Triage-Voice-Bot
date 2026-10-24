# Rural Health Intake & Pre-Triage Voice Bot 🏥🎙️

An end-to-end sovereign voice AI application built using **Gnani AI's Artha Stack** for rural healthcare triage and patient intake. Designed for hackathons and internship challenges, this system transcribes spoken Indic symptoms, evaluates clinical urgency, provides structured medical advice, and speaks back in natural regional language.

---

## 🏗️ Architecture & Tech Stack

The application integrates three core pillars of conversational AI:
1. **Speech-to-Text (STT):** Gnani AI **Prisma v2.5** (`/stt/v3`) for accurate transcription of regional Indic languages (Hindi/Hinglish).
2. **Clinical Triage Logic Engine:** Rule-based medical parser that evaluates symptom severity (**RED**, **YELLOW**, **GREEN**) and outputs actionable next steps.
3. **Text-to-Speech (TTS):** Gnani AI **Timbre v2.5** (`/api/v1/tts/inference`) for warm, natural localized voice generation.

---

## 🔄 Workflow Pipeline
[Patient Voice Audio (.wav/.mp3)]
│
▼  (Prisma v2.5 STT)
[Transcribed Text in Devanagari]
│
▼  (Triage & Clinical Engine)
[Severity Assessment & Actionable Advice]
│
▼  (Timbre v2.5 TTS)
[Spoken Regional Audio Output & Playback]
