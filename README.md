<div align="center">

# 🏥🎙️ Rural Health Intake & Pre-Triage Voice Bot
### *Empowering Rural Healthcare Through Sovereign Conversational AI*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Gnani AI Artha Stack](https://img.shields.io/badge/Powered%20by-Gnani%20AI-orange.svg)](https://gnani.ai/)
[![Google Colab](https://img.shields.io/badge/Environment-Google%20Colab-yellow.svg)](https://colab.research.google.com/)
[![Hackathon Submission](https://img.shields.io/badge/Status-Submission%20Ready-success.svg)]()

*An end-to-end voice AI pipeline that bridges the literacy gap by allowing rural patients to speak symptoms in their native tongue, receive instant clinical triage, and hear actionable medical advice back in regional voice.*

</div>

---

## 🌟 Key Highlights & Features

*   🗣️ **Native Indic Voice Intake:** Translates spoken Hindi/Hinglish patient audio into structured data without requiring text literacy.
*   ⚡ **Lightning-Fast STT:** Powered by **Gnani AI Prisma v2.5** (`/stt/v3`) for high-accuracy regional transcription[cite: 2].
*   🏥 **Smart Triage Engine:** Automatically categorizes urgency into **RED (Emergency)**, **YELLOW (Moderate)**, and **GREEN (Mild)** with customized next steps.
*   🔊 **Natural Voice Synthesis:** Responds to patients using **Gnani AI Timbre v2.5** (`/api/v1/tts/inference`) for warm, localized audio guidance[cite: 2].

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
