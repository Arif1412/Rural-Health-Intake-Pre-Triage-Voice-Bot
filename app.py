import os
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn

app = FastAPI(title="AarogyaVoice")

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

# Frontend Dashboard
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en" class="scroll-smooth">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AarogyaVoice — Sovereign AI Pre-Triage Assistant</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #050505; }
            .font-mono-code { font-family: 'JetBrains Mono', monospace; }
        </style>
    </head>
    <body class="text-neutral-200 min-h-screen flex flex-col items-center selection:bg-neutral-800 selection:text-white">

        <!-- Top Navigation Bar -->
        <nav class="w-full max-w-5xl px-6 py-4 mt-4 flex items-center justify-between border border-neutral-800/80 bg-neutral-950/80 backdrop-blur-md rounded-2xl sticky top-4 z-50">
            <a href="#top" class="flex items-center space-x-3 group cursor-pointer">
                <span class="bg-neutral-900 border border-neutral-800 text-white font-bold text-xs px-2.5 py-1 rounded-md tracking-wide uppercase group-hover:border-neutral-600 transition">AV</span>
                <span class="font-bold text-white text-base tracking-tight group-hover:text-neutral-300 transition">AarogyaVoice</span>
            </a>
            <div class="hidden md:flex items-center space-x-6 text-xs font-medium text-neutral-400">
                <a href="#intake" class="hover:text-white transition">Voice Intake</a>
                <a href="#system" class="hover:text-white transition">System Architecture</a>
                <a href="#about" class="hover:text-white transition">About Project</a>
            </div>
            <a href="https://github.com/Arif1412/Rural-Health-Intake-Pre-Triage-Voice-Bot" target="_blank" class="bg-white text-black hover:bg-neutral-200 text-xs font-semibold px-4 py-2 rounded-lg transition flex items-center space-x-2">
                <span>GitHub Repo</span>
            </a>
        </nav>

        <main id="top" class="w-full max-w-5xl px-6 py-10 space-y-12">

            <!-- Hero Section -->
            <section class="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
                <div class="md:col-span-7 bg-neutral-900/40 border border-neutral-800/90 hover:border-neutral-700 transition duration-300 rounded-2xl p-8 flex flex-col justify-between">
                    <div>
                        <div class="inline-flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full text-emerald-400 text-xs font-medium mb-6">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                            <span>Sovereign Voice AI Active</span>
                        </div>
                        <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
                            Frontline Healthcare Intake & Pre-Triage Engine
                        </h1>
                        <p class="text-neutral-400 text-sm mt-4 leading-relaxed">
                            AarogyaVoice empowers community health workers (ASHA/ANM) in rural India to capture patient speech in sovereign vernacular dialects, process clinical pre-triage assessment and return instant spoken guidance.
                        </p>
                    </div>

                    <div class="mt-8 pt-6 border-t border-neutral-800/80 flex flex-wrap gap-2">
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">Gnani Prisma v2.5 STT</span>
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">Gnani Timbre v2.5 TTS</span>
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">FastAPI</span>
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">Render Deployment</span>
                    </div>
                </div>

                <div class="md:col-span-5 bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition duration-300 rounded-2xl p-6 font-mono-code text-xs text-neutral-300 flex flex-col justify-between shadow-2xl relative overflow-hidden">
                    <div class="flex items-center justify-between pb-3 border-b border-neutral-800 text-neutral-500 text-[11px]">
                        <span>system_config.json</span>
                        <span class="text-emerald-400">● active</span>
                    </div>
                    <pre class="py-4 text-neutral-400 overflow-x-auto space-y-1">
<span class="text-purple-400">const</span> <span class="text-blue-400">AarogyaVoice</span> = {
  <span class="text-neutral-500">model_stt</span>: <span class="text-emerald-300">"Prisma v2.5"</span>,
  <span class="text-neutral-500">model_tts</span>: <span class="text-emerald-300">"Timbre v2.5"</span>,
  <span class="text-neutral-500">dialect</span>: <span class="text-amber-300">"hi-IN (Hindi)"</span>,
  <span class="text-neutral-500">triage_tiers</span>: [<span class="text-red-400">"RED"</span>, <span class="text-amber-400">"YELLOW"</span>, <span class="text-emerald-400">"GREEN"</span>],
  <span class="text-neutral-500">target_users</span>: <span class="text-emerald-300">"ASHA / ANM Workers"</span>
};

<span class="text-neutral-500">// Sovereign pipeline ready</span>
<span class="text-blue-400">console</span>.log(<span class="text-emerald-300">"Pipeline initialized."</span>);</pre>
                    <div class="pt-3 border-t border-neutral-800/80 text-[11px] text-neutral-500 flex justify-between">
                        <span>Status: 200 OK</span>
                        <span>Latency: &lt; 680ms</span>
                    </div>
                </div>
            </section>

            <!-- Voice Intake Console Section -->
            <section id="intake" class="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-8">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h2 class="text-xl font-bold text-white tracking-tight">Clinical Voice Intake Console</h2>
                        <p class="text-xs text-neutral-400 mt-1">Upload patient audio recording (.wav or .mp3) for instant analysis</p>
                    </div>
                    <span class="bg-neutral-900 text-neutral-400 border border-neutral-800 text-xs px-3 py-1 rounded-lg font-mono-code">Step 01 / 02</span>
                </div>

                <!-- Dropzone Card -->
                <div class="border border-dashed border-neutral-800 hover:border-neutral-600 transition rounded-xl p-8 text-center bg-neutral-950/60 cursor-pointer mb-6" onclick="document.getElementById('audioFile').click()">
                    <input type="file" id="audioFile" accept="audio/*" class="hidden" onchange="handleFileSelect(event)">
                    <div id="uploadPrompt" class="space-y-3">
                        <div class="w-10 h-10 mx-auto rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center text-neutral-400">
                            📁
                        </div>
                        <p class="text-sm font-semibold text-neutral-200">Click or drop audio file here</p>
                        <p class="text-xs text-neutral-500">Supports Hindi, Hinglish & Regional Accents (.wav, .mp3)</p>
                    </div>
                </div>

                <!-- Audio Preview Panel (Appears after selecting file) -->
                <div id="previewContainer" class="hidden bg-neutral-950 border border-neutral-800 rounded-xl p-5 mb-6 space-y-3">
                    <div class="flex items-center justify-between">
                        <span id="fileInfo" class="text-emerald-400 font-mono-code text-xs"></span>
                        <span class="text-[10px] uppercase font-mono-code bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">Ready to Analyze</span>
                    </div>
                    <div>
                        <audio id="previewAudioPlayer" controls class="w-full h-8 mt-2"></audio>
                    </div>
                </div>

                <button onclick="analyzeAudio()" class="w-full bg-white hover:bg-neutral-200 text-black font-semibold py-3 px-6 rounded-xl transition duration-200 text-sm flex items-center justify-center space-x-2">
                    <span>Execute</span>
                </button>

                <!-- Loading Spinner -->
                <div id="loader" class="hidden text-center my-8">
                    <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                    <p class="text-xs font-mono-code text-neutral-400 mt-3">Transcribing with Prisma v2.5 & synthesizing voice response...</p>
                </div>

                <!-- Results Output Grid -->
                <div id="results" class="hidden mt-10 space-y-6 pt-6 border-t border-neutral-800">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                            <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Triage Urgency Assessment</span>
                            <div id="triageBadge" class="inline-block px-3 py-1.5 rounded-lg font-bold text-xs"></div>
                        </div>

                        <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                            <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Voice Guidance (Timbre v2.5)</span>
                            <audio id="audioPlayer" controls class="w-full h-8 mt-1"></audio>
                        </div>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Vernacular Transcript (Prisma v2.5 STT)</span>
                        <p id="transcriptBox" class="text-sm text-neutral-200 leading-relaxed font-mono-code"></p>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Localized Verbal Advice</span>
                        <p id="adviceBox" class="text-sm text-neutral-200 leading-relaxed"></p>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-3">Action Plan for Health Worker</span>
                        <ul id="solutionsList" class="text-xs text-neutral-300 space-y-2 list-disc list-inside font-mono-code"></ul>
                    </div>
                </div>
            </section>

            <!-- System Architecture Section -->
            <section id="system" class="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-8 space-y-6">
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">System Architecture</h2>
                    <p class="text-xs text-neutral-400 mt-1">End-to-end processing pipeline powered by Gnani AI Artha Stack</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono-code text-xs">
                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl hover:border-neutral-700 transition">
                        <span class="text-neutral-500 text-[10px]">01 / STT PIPELINE</span>
                        <h3 class="text-sm font-bold text-white mt-1 mb-2">Gnani Prisma v2.5</h3>
                        <p class="text-neutral-400 text-[11px] leading-relaxed">Transcribes spoken patient complaints from Indian languages into accurate text with native numeral normalization.</p>
                    </div>
                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl hover:border-neutral-700 transition">
                        <span class="text-neutral-500 text-[10px]">02 / CLINICAL LOGIC</span>
                        <h3 class="text-sm font-bold text-white mt-1 mb-2">Pre-Triage Engine</h3>
                        <p class="text-neutral-400 text-[11px] leading-relaxed">Evaluates symptoms severely based on body organ & critical markers (chest pain, fever, eye, arm/leg pain) into Red, Yellow or Green urgency levels.</p>
                    </div>
                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl hover:border-neutral-700 transition">
                        <span class="text-neutral-500 text-[10px]">03 / VOICE SYNTHESIS</span>
                        <h3 class="text-sm font-bold text-white mt-1 mb-2">Gnani Timbre v2.5</h3>
                        <p class="text-neutral-400 text-[11px] leading-relaxed">Synthesizes natural, localized voice instructions ('Nalini' voice model at 24kHz) to guide health workers and patients immediately.</p>
                    </div>
                </div>
            </section>

            <!-- About Project Section -->
            <section id="about" class="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-8 space-y-6">
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">About Project</h2>
                    <p class="text-xs text-neutral-400 mt-1">Addressing healthcare delivery challenges across rural India</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-neutral-300 leading-relaxed">
                    <div class="bg-neutral-950 border border-neutral-800 p-6 rounded-xl space-y-2">
                        <h3 class="text-sm font-bold text-white">The Problem Statement</h3>
                        <p class="text-neutral-400">Rural primary health centers and frontline community health workers (ASHA / ANMs) often struggle with language barriers, heavy patient queues and rapid symptom categorization, leading to delayed emergency triage.</p>
                    </div>
                    <div class="bg-neutral-950 border border-neutral-800 p-6 rounded-xl space-y-2">
                        <h3 class="text-sm font-bold text-white">Sovereign AI Solution</h3>
                        <p class="text-neutral-400">AarogyaVoice leverages indigenous voice technology built specifically for Indian languages. It bridges the gap between patient speech intake and immediate clinical triage advice without requiring complex text interfaces.</p>
                    </div>
                </div>
            </section>

        </main>

        <footer class="w-full border-t border-neutral-900 py-6 mt-12 text-center text-xs text-neutral-600 font-mono-code">
            <p>AarogyaVoice © 2026 — Built for Great Indian AI Internship Challenge</p>
        </footer>

        <script>
            let selectedFile = null;

            // Handle Audio Upload File Selection & Show Audio Preview
            function handleFileSelect(e) {
                selectedFile = e.target.files[0];
                if(selectedFile) {
                    const info = document.getElementById('fileInfo');
                    const container = document.getElementById('previewContainer');
                    const previewPlayer = document.getElementById('previewAudioPlayer');
                    const uploadPrompt = document.getElementById('uploadPrompt');

                    info.innerText = `Selected File: ${selectedFile.name} (${(selectedFile.size/1024/1024).toFixed(2)} MB)`;
                    
                    // Create local object URL for instant preview playback
                    previewPlayer.src = URL.createObjectURL(selectedFile);
                    container.classList.remove('hidden');
                    uploadPrompt.innerHTML = `<div class="w-10 h-10 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-2">✅</div><p class="text-sm font-semibold text-emerald-400">Audio File Loaded Successfully</p><p class="text-xs text-neutral-500">Click or drop another file to replace</p>`;
                }
            }

            // Execute Triage Analysis API Request
            async function analyzeAudio() {
                if(!selectedFile) return alert("Please select an audio file first!");
                const formData = new FormData();
                formData.append("file", selectedFile);
                formData.append("language", "hi-IN");

                document.getElementById('loader').classList.remove('hidden');
                document.getElementById('results').classList.add('hidden');

                try {
                    const res = await fetch("/api/analyze", { method: "POST", body: formData });
                    const result = await res.json();

                    document.getElementById('transcriptBox').innerText = result.transcript;
                    const badge = document.getElementById('triageBadge');
                    badge.innerText = result.triage_level;
                    if(result.triage_level.includes("RED")) {
                        badge.className = "px-3 py-1.5 rounded-lg font-bold text-xs bg-red-500/10 text-red-400 border border-red-500/20";
                    } else if(result.triage_level.includes("YELLOW")) {
                        badge.className = "px-3 py-1.5 rounded-lg font-bold text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20";
                    } else {
                        badge.className = "px-3 py-1.5 rounded-lg font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                    }

                    document.getElementById('adviceBox').innerText = result.advice;
                    const list = document.getElementById('solutionsList');
                    list.innerHTML = "";
                    result.solutions.forEach(s => {
                        const li = document.createElement('li');
                        li.innerText = s;
                        list.appendChild(li);
                    });

                    if(result.audio_url) {
                        const player = document.getElementById('audioPlayer');
                        player.src = result.audio_url + "?t=" + new Date().getTime();
                        player.play().catch(e => console.log(e));
                    }
                    document.getElementById('results').classList.remove('hidden');
                } catch(e) {
                    alert("Error processing audio: " + e);
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
