import os
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn

app = FastAPI(title="AarogyaVoice")

API_KEY = os.getenv("GNANIAPIKEY")
BASE_URL = "https://api.vachana.ai"
HEADERS_KEY = {"X-API-Key-ID": API_KEY} if API_KEY else {}

# Voice Mapping for Timbre v2.5 TTS
VOICE_MAP = {
    "hi-IN": "Nalini",   # Hindi
    "bn-IN": "Srabani",  # Bengali
    "ta-IN": "Kavitha",  # Tamil
    "te-IN": "Padma",    # Telugu
    "mr-IN": "Pooja",    # Marathi
    "en-IN": "Nalini"    # English
}

# 1. STT Function with Auto-Detection Configuration
def transcribe_audio_file(file_path):
    if not API_KEY:
        return "API Key not configured."
    url = f"{BASE_URL}/stt/v3"
    with open(file_path, "rb") as audio_file:
        files_payload = {"audio_file": (file_path, audio_file)}
        data_payload = {
            "format": "transcribe",
            "itn_native_numerals": "true"
        }
        response = requests.post(url, headers=HEADERS_KEY, data=data_payload, files=files_payload)
    if response.status_code == 200:
        result = response.json()
        return result.get("transcript") or result.get("text") or str(result)
    return f"STT Error: {response.text}"

# 2. Intelligent Script-Based Language Detector & Triage Engine
def evaluate_symptoms_and_solutions(transcript):
    if not transcript or "Error" in transcript:
        return "UNKNOWN", "en-IN", "Details not found.", []
    
    t_lower = transcript.lower()

    # Detect language based on script characters or specific keywords
    # Bengali Script Check
    if any('\u0980' <= c <= '\u09FF' for c in transcript) or any(w in t_lower for w in ["বুক", "চোখ", "জ্বর", "পায়খানা"]):
        lang_code = "bn-IN"
    # Tamil Script Check
    elif any('\u0B80' <= c <= '\u0BFF' for c in transcript):
        lang_code = "ta-IN"
    # Telugu Script Check
    elif any('\u0C00' <= c <= '\u0C7F' for c in transcript):
        lang_code = "te-IN"
    # Marathi / Hindi Devanagari Script Check
    elif any('\u0900' <= c <= '\u097F' for c in transcript):
        # Differentiate Marathi specific words if needed, otherwise default to Hindi
        if any(w in t_lower for w in ["दुखणे", "पाय", "डोळा"]):
            lang_code = "mr-IN"
        else:
            lang_code = "hi-IN"
    else:
        lang_code = "en-IN"

    # Multilingual Keyword Matching & Responses
    red_keywords = ["chest pain", "breathlessness", "unconscious", "saans", "छाती में दर्द", "सांस फूलना", "বুক ব্যথা", "শ্বাসকষ্ট", "மார்பக வலி", "ఛాతీ నొప్పి"]
    eye_keywords = ["eye", "आँख", "लेफ्ट आई", "right eye", "left eye", "आंख", "চোখ", "கண்", "కన్ను", "डोळा"]
    fever_keywords = ["bukhar", "fever", "बुखार", "ज্বর", "காய்ச்சல்", "జ్వరం", "ताप"]
    stomach_keywords = ["pet", "stomach", "vomit", "ulti", "पेट", "পেট", "வயிறு", "కడుపు", "पोट"]

    if any(w in t_lower for w in red_keywords):
        tier = "RED (Emergency)"
        if lang_code == "bn-IN":
            advice = "সতর্কতা: মারাত্মক লক্ষণ দেখা গেছে। অবিলম্বে নিকটস্থ হাসপাতালে যান।"
            solutions = ["অবিলম্বে ১০৮ এ্যাম্বুলেন্সে কল করুন।", "রোগীকে শান্ত রাখুন।"]
        elif lang_code == "ta-IN":
            advice = "எச்சரிக்கை: தீவிர அறிகுறிகள். உடனடியாக மருத்துவமனைக்குச் செல்லவும்."
            solutions = ["உடனடியாக 108 அழைக்கவும்.", "நோயாளியை அமைதியாக வைக்கவும்."]
        elif lang_code == "te-IN":
            advice = "హెచ్చరిక: తీవ్రమైన లక్షణాలు. వెంటనే ఆసుపత్రికి వెళ్లండి."
            solutions = ["వెంటనే 108 కి కాల్ చేయండి.", "రోగిని ప్రశాంతంగా ఉంచండి."]
        elif lang_code == "en-IN":
            advice = "Warning: Severe symptoms detected. Proceed to the nearest hospital immediately."
            solutions = ["Call 108 emergency ambulance immediately.", "Keep patient calm."]
        else:
            advice = "चेतावनी: गंभीर लक्षण पाए गए हैं। तुरंत नजदीकी अस्पताल जाएं।"
            solutions = ["Call 108 emergency ambulance immediately.", "Keep patient calm."]

    elif any(w in t_lower for w in eye_keywords):
        tier = "YELLOW (Moderate - Eye)"
        if lang_code == "bn-IN":
            advice = "আপনার চোখে সমস্যা রয়েছে। চোখ ঘষবেন না এবং চক্ষু বিশেষজ্ঞের পরামর্শ নিন।"
            solutions = ["পরিষ্কার জল দিয়ে চোখ ধুয়ে নিন.", "চোখ ঘষবেন না."]
        elif lang_code == "en-IN":
            advice = "You have an eye issue. Avoid touching your eye and consult an ophthalmologist."
            solutions = ["Wash eyes with clean water.", "Avoid rubbing eyes."]
        else:
            advice = "आपको आँख में समस्या है। अपनी आँख को न छुएं और नेत्र विशेषज्ञ से मिलें।"
            solutions = ["Wash eyes with clean water.", "Avoid rubbing eyes."]

    elif any(w in t_lower for w in fever_keywords):
        tier = "YELLOW (Moderate - Fever)"
        if lang_code == "bn-IN":
            advice = "আপনার জ্বর রয়েছে। পর্যাপ্ত জল বা ওআরএস পান করুন।"
            solutions = ["তাপমাত্রা মাপুন।", "পর্যাপ্ত জল পান করুন।"]
        elif lang_code == "en-IN":
            advice = "You have a fever. Stay hydrated with ORS and rest."
            solutions = ["Monitor temperature.", "Stay hydrated."]
        else:
            advice = "आपको बुखार है। ओआरएस का घोल पिएं और आराम करें।"
            solutions = ["Monitor temperature.", "Stay hydrated with ORS."]

    else:
        tier = "GREEN (Mild)"
        if lang_code == "bn-IN":
            advice = "আপনার লক্ষণগুলি সাধারণ। পর্যাপ্ত বিশ্রাম নিন।"
            solutions = ["পর্যাপ্ত বিশ্রাম নিন।"]
        elif lang_code == "en-IN":
            advice = "Your symptoms appear mild. Get adequate rest."
            solutions = ["Get adequate rest."]
        else:
            advice = "आपके लक्षण सामान्य प्रतीत होते हैं। पर्याप्त विश्राम करें।"
            solutions = ["Get adequate rest."]

    return tier, lang_code, advice, solutions

# 3. TTS Function
def synthesize_voice(text, language_code="hi-IN", output_filename="response.wav"):
    if not API_KEY:
        return None
    url = f"{BASE_URL}/api/v1/tts/inference"
    voice_name = VOICE_MAP.get(language_code, "Nalini")
    payload = {
        "text": text, "voice": voice_name, "model": "timbre-v2.5",
        "language": language_code, "speed": 1.0,
        "audio_config": {"sample_rate": 24000, "container": "wav"}
    }
    response = requests.post(url, headers={**HEADERS_KEY, "Content-Type": "application/json"}, json=payload)
    if response.status_code == 200:
        with open(output_filename, "wb") as f:
            f.write(response.content)
        return output_filename
    return None

# API Endpoints (No Language Form Input Needed)
@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        buffer.write(await file.read())
        
    transcript = transcribe_audio_file(temp_filename)
    triage_level, detected_lang, advice, solutions = evaluate_symptoms_and_solutions(transcript)
    audio_output_path = synthesize_voice(advice, language_code=detected_lang)
    
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        
    return JSONResponse({
        "transcript": transcript or "Transcription failed",
        "triage_level": triage_level,
        "detected_language": detected_lang,
        "advice": advice,
        "solutions": solutions,
        "audio_url": "/api/audio" if audio_output_path else ""
    })

@app.get("/api/audio")
async def get_audio():
    if os.path.exists("response.wav"):
        return FileResponse("response.wav", media_type="audio/wav")
    return JSONResponse({"error": "Audio not found"}, status_code=404)

# Frontend Dashboard (Dropdown Removed)
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en" class="scroll-smooth">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AarogyaVoice — Auto-Detect Sovereign AI Pre-Triage Assistant</title>
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

        <nav class="w-full max-w-5xl px-6 py-4 mt-4 flex items-center justify-between border border-neutral-800/80 bg-neutral-950/80 backdrop-blur-md rounded-2xl sticky top-4 z-50 shadow-lg">
            <a href="#top" class="flex items-center space-x-3 group cursor-pointer">
                <span class="bg-neutral-900 border border-neutral-800 text-white font-bold text-xs px-2.5 py-1 rounded-md uppercase">AV</span>
                <span class="font-bold text-white text-base tracking-tight">AarogyaVoice</span>
            </a>
            <a href="https://github.com/Arif1412/Rural-Health-Intake-Pre-Triage-Voice-Bot" target="_blank" class="bg-white text-black hover:bg-neutral-200 text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-md">
                <span>GitHub Repo</span>
            </a>
        </nav>

        <main class="w-full max-w-5xl px-6 py-10 space-y-12">
            <section class="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-8 shadow-xl text-center space-y-4">
                <div class="inline-flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full text-emerald-400 text-xs font-medium">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span>Automatic Language Identification Active</span>
                </div>
                <h1 class="text-3xl font-extrabold text-white tracking-tight">Sovereign Multilingual Voice AI</h1>
                <p class="text-neutral-400 text-sm max-w-2xl mx-auto">Upload any patient audio file in Hindi, Bengali, Tamil, Telugu, Marathi, or English. The system will automatically detect the language, analyze symptoms, and reply in the same language.</p>
            </section>

            <section class="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-8 shadow-xl">
                <div class="border border-dashed border-neutral-800 hover:border-neutral-500 transition-all rounded-xl p-8 text-center bg-neutral-950/60 cursor-pointer mb-6 group" onclick="document.getElementById('audioFile').click()">
                    <input type="file" id="audioFile" accept="audio/*" class="hidden" onchange="handleFileSelect(event)">
                    <div id="uploadPrompt" class="space-y-3">
                        <div class="w-10 h-10 mx-auto rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center text-neutral-400">📁</div>
                        <p class="text-sm font-semibold text-neutral-200">Click or drop patient audio file here</p>
                        <p class="text-xs text-neutral-500">Auto-detects language dialect (.wav, .mp3)</p>
                    </div>
                </div>

                <div id="previewContainer" class="hidden bg-neutral-950 border border-neutral-800 rounded-xl p-5 mb-6 space-y-3">
                    <div class="flex items-center justify-between">
                        <span id="fileInfo" class="text-emerald-400 font-mono-code text-xs"></span>
                        <span class="text-[10px] uppercase font-mono-code bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">Ready</span>
                    </div>
                    <audio id="previewAudioPlayer" controls class="w-full h-8 mt-2"></audio>
                </div>

                <button onclick="analyzeAudio()" class="w-full bg-white hover:bg-neutral-200 text-black font-semibold py-3 px-6 rounded-xl transition-all text-sm shadow-lg">
                    <span>Execute</span>
                </button>

                <div id="loader" class="hidden text-center my-8">
                    <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                    <p class="text-xs font-mono-code text-neutral-400 mt-3">Detecting language, transcribing & synthesizing voice...</p>
                </div>

                <div id="results" class="hidden mt-10 space-y-6 pt-6 border-t border-neutral-800">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                            <span class="text-[11px] font-mono-code text-neutral-500 uppercase block mb-2">Triage & Detected Language</span>
                            <div class="flex items-center space-x-2">
                                <div id="triageBadge" class="px-3 py-1.5 rounded-lg font-bold text-xs"></div>
                                <span id="langBadge" class="bg-neutral-900 border border-neutral-800 text-neutral-300 font-mono-code text-xs px-2.5 py-1 rounded-md"></span>
                            </div>
                        </div>

                        <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                            <span class="text-[11px] font-mono-code text-neutral-500 uppercase block mb-2">Voice Guidance (Timbre v2.5)</span>
                            <audio id="audioPlayer" controls class="w-full h-8 mt-1"></audio>
                        </div>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase block mb-2">Vernacular Transcript (Prisma v2.5 STT)</span>
                        <p id="transcriptBox" class="text-sm text-neutral-200 font-mono-code"></p>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase block mb-2">Localized Verbal Advice</span>
                        <p id="adviceBox" class="text-sm text-neutral-200"></p>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 p-5 rounded-xl">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase block mb-3">Action Plan for Health Worker</span>
                        <ul id="solutionsList" class="text-xs text-neutral-300 space-y-2 list-disc list-inside font-mono-code"></ul>
                    </div>
                </div>
            </section>
        </main>

        <script>
            let selectedFile = null;

            function handleFileSelect(e) {
                selectedFile = e.target.files[0];
                if(selectedFile) {
                    document.getElementById('fileInfo').innerText = `Selected: ${selectedFile.name}`;
                    document.getElementById('previewAudioPlayer').src = URL.createObjectURL(selectedFile);
                    document.getElementById('previewContainer').classList.remove('hidden');
                }
            }

            async function analyzeAudio() {
                if(!selectedFile) return alert("Please select an audio file first!");
                const formData = new FormData();
                formData.append("file", selectedFile);

                document.getElementById('loader').classList.remove('hidden');
                document.getElementById('results').classList.add('hidden');

                try {
                    const res = await fetch("/api/analyze", { method: "POST", body: formData });
                    const result = await res.json();

                    document.getElementById('transcriptBox').innerText = result.transcript;
                    document.getElementById('langBadge').innerText = `Lang: ${result.detected_language}`;
                    
                    const badge = document.getElementById('triageBadge');
                    badge.innerText = result.triage_level;
                    badge.className = result.triage_level.includes("RED") ? "px-3 py-1.5 rounded-lg font-bold text-xs bg-red-500/10 text-red-400 border border-red-500/20" : "px-3 py-1.5 rounded-lg font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";

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
                    alert("Error: " + e);
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
