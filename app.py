import os
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn

app = FastAPI()

API_KEY = os.getenv("GNANIAPIKEY")
BASE_URL = "https://api.vachana.ai"
HEADERS_KEY = {"X-API-Key-ID": API_KEY} if API_KEY else {}

# 1. STT Function (Prisma v2.5)
def transcribe_audio_file(file_path, language_code="hi-IN"):
    if not API_KEY:
        return "API Key not configured."
    url = f"{BASE_URL}/stt/v3"
    with open(file_path, "rb") as audio_file:
        files_payload = {"audio_file": (file_path, audio_file)}
        data_payload = {
            "language_code": language_code,
            "preferred_language": language_code,
            "format": "transcribe",
            "itn_native_numerals": "true"
        }
        response = requests.post(url, headers=HEADERS_KEY, data=data_payload, files=files_payload)
    if response.status_code == 200:
        result = response.json()
        return result.get("transcript") or result.get("text") or str(result)
    return f"STT Error: {response.text}"

# 2. Dynamic Triage & Solutions Engine
def evaluate_symptoms_and_solutions(transcript):
    if not transcript or "Error" in transcript:
        return "UNKNOWN", "विवरण नहीं मिला।", []
    t_lower = transcript.lower()
    
    if any(w in t_lower for w in ["chest pain", "breathlessness", "unconscious", "saans", "छाती में दर्द", "सांस फूलना"]):
        return "RED (Emergency)", "चेतावनी: गंभीर लक्षण पाए गए हैं। तुरंत नजदीकी अस्पताल जाएं।", ["Call 108 emergency ambulance immediately.", "Keep the patient calm and seated upright."]
    elif any(w in t_lower for w in ["eye", "आँख", "लेफ्ट आई", "right eye", "आंख"]):
        return "YELLOW (Moderate)", "आपको आँख में दर्द या समस्या है। अपनी आँख को बार-बार न छुएं और तुरंत नेत्र विशेषज्ञ से मिलें।", ["Wash eyes gently with clean water.", "Avoid rubbing eyes.", "Consult an ophthalmologist within 24 hours."]
    elif any(w in t_lower for w in ["hand", "हाथ", "arm", "उंगली"]):
        return "YELLOW (Moderate)", "आपको हाथ या बाजू में दर्द की शिकायत है। उस हाथ को आराम दें और ज्यादा वजन न उठाएं।", ["Rest the affected arm.", "Avoid lifting heavy objects.", "Consult a doctor if pain persists."]
    elif any(w in t_lower for w in ["sir dard", "headache", "sar dard", "सर दर्द", "सिर में दर्द"]):
        return "YELLOW (Moderate)", "आपको सिर दर्द की शिकायत है। शांत और अंधेरे कमरे में आराम करें।", ["Apply a cold compress on your forehead.", "Stay hydrated.", "Consult a doctor if headache persists."]
    elif any(w in t_lower for w in ["पैर में दर्द", "leg pain", "foot pain", "घुटना"]):
        return "YELLOW (Moderate)", "आपको पैर में दर्द है। पैर को ऊंचा रखकर आराम करें।", ["Rest the affected leg.", "Apply ice pack if there is swelling.", "Consult a physician if pain continues."]
    elif any(w in t_lower for w in ["bukhar", "fever", "बुखार"]):
        return "YELLOW (Moderate)", "आपके लक्षणों के अनुसार आपको बुखार है। पर्याप्त पानी पिएं और आराम करें।", ["Monitor body temperature every 4-6 hours.", "Stay hydrated with ORS.", "Consult a general physician within 24 hours."]
    elif any(w in t_lower for w in ["pet", "stomach", "vomit", "ulti", "पेट", "दस्त"]):
        return "YELLOW (Moderate)", "पेट की समस्या के लिए हल्का और ताजा भोजन लें तथा ओआरएस का घोल पिएं।", ["Consume light foods like khichdi.", "Avoid spicy or oily food.", "Maintain strict hydration."]
    else:
        return "GREEN (Mild)", "आपके लक्षण सामान्य प्रतीत होते हैं। पर्याप्त विश्राम करें और स्वास्थ्य केंद्र से परामर्श लें।", ["Get adequate rest for 1-2 days.", "Maintain proper hydration."]

# 3. TTS Function (Timbre v2.5)
def synthesize_voice(text, language_code="hi-IN", output_filename="response.wav"):
    if not API_KEY:
        return None
    url = f"{BASE_URL}/api/v1/tts/inference"
    payload = {
        "text": text, "voice": "Nalini", "model": "timbre-v2.5",
        "language": language_code, "speed": 1.0,
        "audio_config": {"sample_rate": 24000, "container": "wav"}
    }
    response = requests.post(url, headers={**HEADERS_KEY, "Content-Type": "application/json"}, json=payload)
    if response.status_code == 200:
        with open(output_filename, "wb") as f:
            f.write(response.content)
        return output_filename
    return None

# API Endpoints
@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...), language: str = Form("hi-IN")):
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        buffer.write(await file.read())
        
    transcript = transcribe_audio_file(temp_filename, language_code=language)
    triage_level, advice, solutions = evaluate_symptoms_and_solutions(transcript)
    audio_output_path = synthesize_voice(advice, language_code=language)
    
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        
    return JSONResponse({
        "transcript": transcript or "Transcription failed",
        "triage_level": triage_level,
        "advice": advice,
        "solutions": solutions,
        "audio_url": "/api/audio" if audio_output_path else ""
    })

@app.get("/api/audio")
async def get_audio():
    if os.path.exists("response.wav"):
        return FileResponse("response.wav", media_type="audio/wav")
    return JSONResponse({"error": "Audio not found"}, status_code=404)

# Sleek Dark HTML Frontend Served at Root
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rural Health Intake & Pre-Triage Voice Assistant</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased flex flex-col items-center py-10 px-4">
        <div class="max-w-3xl w-full bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-8">
            <header class="mb-8 text-center">
                <span class="bg-cyan-500/10 text-cyan-400 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider border border-cyan-500/20">Gnani AI Artha Stack</span>
                <h1 class="text-3xl font-extrabold mt-3 tracking-tight text-white">Rural Health Intake & Pre-Triage Bot</h1>
                <p class="text-slate-400 text-sm mt-1">Sovereign Voice AI Assistant for Frontline Healthcare Workers</p>
            </header>

            <!-- Upload Card -->
            <div class="border-2 border-dashed border-slate-700 hover:border-cyan-500 transition rounded-xl p-8 text-center bg-slate-950/50 cursor-pointer mb-6" onclick="document.getElementById('audioFile').click()">
                <input type="file" id="audioFile" accept="audio/*" class="hidden" onchange="handleFileSelect(event)">
                <div id="uploadPrompt">
                    <svg class="mx-auto h-12 w-12 text-slate-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    <p class="text-sm font-medium text-slate-200">Click to upload or drag & drop patient audio (.wav, .mp3)</p>
                    <p class="text-xs text-slate-500 mt-1">Supports Hindi, Hinglish & Regional Dialects</p>
                </div>
                <div id="fileInfo" class="hidden text-cyan-400 font-medium text-sm"></div>
            </div>

            <button onclick="analyzeAudio()" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-3 px-6 rounded-xl shadow-lg transition duration-200 flex items-center justify-center space-x-2">
                <span>🚀 Run Clinical Pre-Triage Analysis</span>
            </button>

            <!-- Loading Spinner -->
            <div id="loader" class="hidden text-center my-6">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-cyan-500 border-t-transparent"></div>
                <p class="text-sm text-slate-400 mt-2">Processing with Prisma v2.5 & Timbre v2.5...</p>
            </div>

            <!-- Results Section -->
            <div id="results" class="hidden mt-8 space-y-6 border-t border-slate-800 pt-6">
                <div>
                    <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">🗣️ Transcribed Speech (Prisma v2.5)</h3>
                    <div id="transcriptBox" class="bg-slate-950 p-4 rounded-xl border border-slate-800 text-slate-200 text-sm"></div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">🏥 Triage Level</h3>
                        <div id="triageBadge" class="inline-block px-4 py-2 rounded-xl font-bold text-sm"></div>
                    </div>
                    <div>
                        <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">🔊 Spoken Voice Guidance (Timbre v2.5)</h3>
                        <audio id="audioPlayer" controls class="w-full h-10"></audio>
                    </div>
                </div>

                <div>
                    <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">💬 Patient Advice (Hindi)</h3>
                    <div id="adviceBox" class="bg-slate-950 p-4 rounded-xl border border-slate-800 text-slate-200 text-sm"></div>
                </div>

                <div>
                    <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">📋 Actionable Steps for Health Worker</h3>
                    <ul id="solutionsList" class="bg-slate-950 p-4 rounded-xl border border-slate-800 text-slate-300 text-sm space-y-2 list-disc list-inside"></ul>
                </div>
            </div>
        </div>

        <script>
            let selectedFile = null;
            function handleFileSelect(event) {
                selectedFile = event.target.files[0];
                if (selectedFile) {
                    document.getElementById('uploadPrompt').classList.add('hidden');
                    const info = document.getElementById('fileInfo');
                    info.classList.remove('hidden');
                    info.innerText = `Selected File: ${selectedFile.name} (${(selectedFile.size/1024/1024).toFixed(2)} MB)`;
                }
            }

            async function analyzeAudio() {
                if (!selectedFile) {
                    alert("Please select or upload an audio file first!");
                    return;
                }
                const formData = new FormData();
                formData.append("file", selectedFile);
                formData.append("language", "hi-IN");

                document.getElementById('loader').classList.remove('hidden');
                document.getElementById('results').classList.add('hidden');

                try {
                    const response = await fetch("/api/analyze", { method: "POST", body: formData });
                    const result = await response.json();
                    
                    document.getElementById('transcriptBox').innerText = result.transcript;
                    
                    const badge = document.getElementById('triageBadge');
                    badge.innerText = result.triage_level;
                    if (result.triage_level.includes("RED")) {
                        badge.className = "px-4 py-2 rounded-xl font-bold text-sm bg-red-500/20 text-red-400 border border-red-500/30";
                    } else if (result.triage_level.includes("YELLOW")) {
                        badge.className = "px-4 py-2 rounded-xl font-bold text-sm bg-amber-500/20 text-amber-400 border border-amber-500/30";
                    } else {
                        badge.className = "px-4 py-2 rounded-xl font-bold text-sm bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
                    }

                    document.getElementById('adviceBox').innerText = result.advice;
                    
                    const list = document.getElementById('solutionsList');
                    list.innerHTML = "";
                    result.solutions.forEach(sol => {
                        const li = document.createElement('li');
                        li.innerText = sol;
                        list.appendChild(li);
                    });

                    if (result.audio_url) {
                        const player = document.getElementById('audioPlayer');
                        player.src = result.audio_url + "?t=" + new Date().getTime();
                        player.play().catch(e => console.log("Autoplay blocked by browser policy"));
                    }

                    document.getElementById('results').classList.remove('hidden');
                } catch (err) {
                    alert("Error processing request: " + err);
                } finally {
                    document.getElementById('loader').classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
