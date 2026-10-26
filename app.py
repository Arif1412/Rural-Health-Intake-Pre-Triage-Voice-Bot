import os
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn

app = FastAPI(title="AarogyaVoice")

API_KEY = os.getenv("GNANIAPIKEY")
BASE_URL = "https://api.vachana.ai"
HEADERS_KEY = {"X-API-Key-ID": API_KEY} if API_KEY else {}

# Voice Mapping for Timbre v2.5 TTS across Indian Languages
VOICE_MAP = {
    "hi-IN": "Nalini",   # Hindi
    "bn-IN": "Srabani",  # Bengali
    "ta-IN": "Kavitha",  # Tamil
    "te-IN": "Padma",    # Telugu
    "mr-IN": "Pooja",    # Marathi
    "en-IN": "Nalini"    # English (Indian Accent)
}

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

# 2. Fully Localized Multilingual Triage & Solutions Engine (Expanded Bengali Support)
def evaluate_symptoms_and_solutions(transcript, language_code="hi-IN"):
    if not transcript or "Error" in transcript:
        return "UNKNOWN", "विवरण नहीं मिला / Details not found.", []
    
    t_lower = transcript.lower()

    # Multilingual Keyword Arrays (Expanded with variations like पेটে ব্যথা / পেটে ব্যাথা)
    red_keywords = [
        "chest pain", "breathlessness", "unconscious", "saans", "छाती में दर्द", "सांस फूलना",
        "বুক ব্যথা", "বুকে ব্যথা", "বুকের ব্যাথা", "শ্বাসকষ্ট", "অজ্ঞান",
        "மார்பக வலி", "மூச்சு திணறல்", "மயக்கம்",
        "ఛాతీ నొప్పి", "శ్వాస తీసుకోవడంలో ఇబ్బంది", "స్పృహ కోల్పోవడం",
        "छातीत दुखणे", "श्वास घेण्यास त्रास", "बेसुध"
    ]

    eye_keywords = [
        "eye", "आँख", "लेफ्ट आई", "right eye", "left eye", "आंख", "চোখ", "চোখে ব্যথা",
        "கண்", "கண் வலி", "కన్ను", "डोळा"
    ]

    arm_keywords = [
        "hand", "हाथ", "arm", "उंगली", "হাত", "হাতে ব্যথা",
        "கை", "చేతి", "हात"
    ]

    headache_keywords = [
        "sir dard", "headache", "sar dard", "सर दर्द", "सिर में दर्द", "মাথা ব্যথা", "মাথাব্যথা", "মাথা ধরা",
        "தலைவலி", "తలనొప్పి", "डोकेदुखी"
    ]

    leg_keywords = [
        "প্যার মে दर्द", "leg pain", "foot pain", "घुटना", "পা ব্যথা", "পায়ে ব্যথা",
        "கால் வலி", "ಕಾಲು ನೋವು", "కాలు నొప్పి", "पाय दुखणे"
    ]

    fever_keywords = [
        "bukhar", "fever", "बुखार", "ज্বর", "গা গরম", "গরম",
        "காய்ச்சல்", "జ్వరం", "ताप"
    ]

    stomach_keywords = [
        "pet", "stomach", "vomit", "ulti", "पेट", "दस्त", "পেট", "পেটে ব্যথা", "পেটে ব্যাথা", "বমি", "পাতলা পায়খানা", "ব্যথা করছে",
        "வயிறு வலி", "வாந்தி", "కడుపు నొప్పి", "వాంతి", "पोटदुखी", "उल्टी"
    ]

    # ---- 1. RED (Emergency) ----
    if any(w in t_lower for w in red_keywords):
        tier = "RED (Emergency)"
        if language_code == "bn-IN":
            advice = "সতর্কতা: মারাত্মক লক্ষণ দেখা গেছে। অবিলম্বে নিকটস্থ হাসপাতালে যান।"
            solutions = ["অবিলম্বে ১০৮ এ্যাম্বুলেন্সে কল করুন।", "রোগীকে শান্ত রাখুন এবং সোজা বসিয়ে রাখুন।"]
        elif language_code == "ta-IN":
            advice = "எச்சரிக்கை: தீவிர அறிகுறிகள் கண்டறியப்பட்டுள்ளன. உடனடியாக அருகில் உள்ள மருத்துவமனைக்குச் செல்லவும்."
            solutions = ["உடனடியாக 108 அவசர ஊர்தியை அழைக்கவும்.", "நோயாளி அமைதியாக நிமிர்ந்து அமர்ந்திருக்கச் செய்யவும்."]
        elif language_code == "te-IN":
            advice = "హెచ్చరిక: తీవ్రమైన లక్షణాలు గుర్తించబడ్డాయి. వెంటనే సమీప ఆసుపత్రికి వెళ్లండి."
            solutions = ["వెంటనే 108 అంబులెన్స్‌కు కాల్ చేయండి.", "రోగిని ప్రశాంతంగా నిటారుగా కూర్చోబెట్టండి."]
        elif language_code == "mr-IN":
            advice = "चेतावणी: गंभीर लक्षणे आढळली आहेत. त्वरित जवळच्या रुग्णालयात जा."
            solutions = ["त्वरित १०८ रुग्णवाहिकेला कॉल करा.", "रुग्णाला शांत ठेवा आणि सरळ बसवा."]
        elif language_code == "en-IN":
            advice = "Warning: Severe symptoms detected. Please proceed to the nearest emergency hospital immediately."
            solutions = ["Call 108 emergency ambulance immediately.", "Keep the patient calm and seated upright."]
        else:
            advice = "चेतावनी: गंभीर लक्षण पाए गए हैं। तुरंत नजदीकी अस्पताल जाएं।"
            solutions = ["Call 108 emergency ambulance immediately.", "Keep the patient calm and seated upright."]

    # ---- 2. YELLOW (Moderate - Stomach / पेट / পেটে ব্যথা) ----
    elif any(w in t_lower for w in stomach_keywords):
        tier = "YELLOW (Moderate - Stomach)"
        if language_code == "bn-IN":
            advice = "পেটের সমস্যার জন্য হালকা ও তাজা খাবার খান এবং ওআরএস পান করুন।"
            solutions = ["খিচুড়ির মতো হালকা খাবার খান।", "ঝাল বা তেলযুক্ত খাবার এড়িয়ে চলুন।", "পর্যাপ্ত জল ও ওআরএস পান করুন।"]
        elif language_code == "ta-IN":
            advice = "வயிறு தொந்தரவுக்கு எளிதில் செரிமானமாகும் உணவை உட்கொள்ளவும் மற்றும் ஓஆர்எஸ் குடிக்கவும்."
            solutions = ["கஞ்சி அல்லது எளிமையான உணவுகளை உண்ணவும்.", "காரமான மற்றும் எண்ணெய் உணவுகளை தவிர்க்கவும்.", "ஓஆர்எஸ் மற்றும் நீர் அருந்தவும்."]
        elif language_code == "te-IN":
            advice = "కడుపు సమస్య కోసం తేలికపాటి ఆహారం తీసుకోండి మరియు ఓఆర్ఎస్ త్రాగండి."
            solutions = ["ఖిచ్డీ వంటి తేలికపాటి ఆహారం తినండి.", "కారంగా లేదా నూనెతో కూడిన ఆహారాన్ని నివారించండి.", "ORS మరియు నీరు త్రాగండి."]
        elif language_code == "mr-IN":
            advice = "पोटाच्या समस्येसाठी हलके अन्न खा आणि ओआरएसचे सेवन करा."
            solutions = ["खिचडीसारखे हलके अन्न खा.", "तिखट किंवा तेलकट पदार्थ टाळा.", "भरपूर पाणी आणि ओआरएस प्या."]
        elif language_code == "en-IN":
            advice = "For stomach discomfort, consume light foods and maintain strict hydration with ORS."
            solutions = ["Consume light foods like khichdi.", "Avoid spicy or oily food.", "Maintain strict hydration."]
        else:
            advice = "पेट की समस्या के लिए हल्का भोजन लें और ओआरएस का घोल पिएं।"
            solutions = ["Consume light foods like khichdi.", "Avoid spicy or oily food.", "Maintain strict hydration."]

    # ---- 3. YELLOW (Moderate - Eye) ----
    elif any(w in t_lower for w in eye_keywords):
        tier = "YELLOW (Moderate - Eye)"
        if language_code == "bn-IN":
            advice = "আপনার চোখে সমস্যা বা ব্যথা রয়েছে। চোখ ঘষবেন না এবং চক্ষু বিশেষজ্ঞের পরামর্শ নিন।"
            solutions = ["পরিষ্কার জল দিয়ে চোখ ধুয়ে নিন।", "চোখ ঘষা থেকে বিরত থাকুন।", "২৪ ঘণ্টার মধ্যে চক্ষু বিশেষজ্ঞের পরামর্শ নিন।"]
        elif language_code == "en-IN":
            advice = "You have an eye issue or pain. Avoid touching your eye and consult an ophthalmologist promptly."
            solutions = ["Wash eyes gently with clean water.", "Avoid rubbing eyes.", "Consult an ophthalmologist within 24 hours."]
        else:
            advice = "आपको आँख में दर्द या समस्या है। अपनी आँख को बार-बार न छुएं और तुरंत नेत्र विशेषज्ञ से मिलें।"
            solutions = ["Wash eyes gently with clean water.", "Avoid rubbing eyes.", "Consult an ophthalmologist within 24 hours."]

    # ---- 4. YELLOW (Moderate - Fever) ----
    elif any(w in t_lower for w in fever_keywords):
        tier = "YELLOW (Moderate - Fever)"
        if language_code == "bn-IN":
            advice = "আপনার লক্ষণ অনুযায়ী জ্বর রয়েছে। পর্যাপ্ত জল বা ওআরএস পান করুন।"
            solutions = ["প্রতি ৪-৬ ঘণ্টা পর পর তাপমাত্রা মাপুন।", "ওআরএস বা জল খেয়ে হাইড্রেটেড থাকুন।", "২৪ ঘণ্টার মধ্যে চিকিৎসকের পরামর্শ নিন।"]
        elif language_code == "en-IN":
            advice = "According to your symptoms, you have a fever. Stay hydrated with ORS and rest."
            solutions = ["Monitor body temperature every 4-6 hours.", "Stay hydrated with ORS.", "Consult a general physician within 24 hours."]
        else:
            advice = "आपके लक्षणों के अनुसार आपको बुखार है। ओआरएस का घोल पिएं और आराम करें।"
            solutions = ["Monitor body temperature every 4-6 hours.", "Stay hydrated with ORS.", "Consult a general physician within 24 hours."]

    # ---- 5. GREEN (Mild) ----
    else:
        tier = "GREEN (Mild)"
        if language_code == "bn-IN":
            advice = "আপনার লক্ষণগুলি সাধারণ বলে মনে হচ্ছে। পর্যাপ্ত বিশ্রাম নিন।"
            solutions = ["১-২ দিন পর্যাপ্ত বিশ্রাম নিন।", "পর্যাপ্ত জল পান করুন।"]
        elif language_code == "en-IN":
            advice = "Your symptoms appear mild. Get adequate rest and monitor your health."
            solutions = ["Get adequate rest for 1-2 days.", "Maintain proper hydration."]
        else:
            advice = "आपके लक्षण सामान्य प्रतीत होते हैं। पर्याप्त विश्राम करें।"
            solutions = ["Get adequate rest for 1-2 days.", "Maintain proper hydration."]

    return tier, advice, solutions

# 3. TTS Function (Timbre v2.5 with Fallback Check)
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
    if response.status_code == 200 and len(response.content) > 100:
        with open(output_filename, "wb") as f:
            f.write(response.content)
        return output_filename
    print(f"TTS Error Response: {response.text}")
    return None

# API Endpoints
@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...), language: str = Form("hi-IN")):
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        buffer.write(await file.read())
        
    transcript = transcribe_audio_file(temp_filename, language_code=language)
    triage_level, advice, solutions = evaluate_symptoms_and_solutions(transcript, language_code=language)
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
        <title>AarogyaVoice — Multi-Indic Sovereign AI Pre-Triage Assistant</title>
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

        <!-- Top Navigation Bar with Glassy Effect -->
        <nav class="w-full max-w-5xl px-6 py-4 mt-4 flex items-center justify-between border border-neutral-700/50 bg-neutral-950/40 backdrop-blur-xl rounded-2xl sticky top-4 z-50 shadow-2xl transition-all duration-300">
            <a href="#top" class="flex items-center space-x-3 group cursor-pointer">
                <span class="bg-neutral-900 border border-neutral-800 text-white font-bold text-xs px-2.5 py-1 rounded-md tracking-wide uppercase group-hover:border-neutral-500 group-hover:bg-neutral-800 transition-all duration-300">AV</span>
                <span class="font-bold text-white text-base tracking-tight group-hover:text-neutral-300 transition-colors duration-300">AarogyaVoice</span>
            </a>
            <div class="hidden md:flex items-center space-x-6 text-xs font-medium text-neutral-400">
                <a href="#intake" class="hover:text-white hover:translate-y-[-1px] transition-all duration-200">Voice Intake</a>
                <a href="#system" class="hover:text-white hover:translate-y-[-1px] transition-all duration-200">System Architecture</a>
                <a href="#about" class="hover:text-white hover:translate-y-[-1px] transition-all duration-200">About Project</a>
            </div>
            <a href="https://github.com/Arif1412/Rural-Health-Intake-Pre-Triage-Voice-Bot" target="_blank" class="bg-white text-black hover:bg-neutral-200 hover:scale-[1.02] active:scale-[0.98] text-xs font-semibold px-4 py-2 rounded-lg transition-all duration-200 flex items-center space-x-2 shadow-md">
                <span>GitHub Repo</span>
            </a>
        </nav>

        <main id="top" class="w-full max-w-5xl px-6 py-10 space-y-12">

            <!-- Hero Section -->
            <section class="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
                <div class="md:col-span-7 bg-neutral-900/40 border border-neutral-800/90 hover:border-neutral-600 hover:bg-neutral-900/60 transition-all duration-300 rounded-2xl p-8 flex flex-col justify-between shadow-xl">
                    <div>
                        <div class="inline-flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full text-emerald-400 text-xs font-medium mb-6">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                            <span>Sovereign AI Active</span>
                        </div>
                        <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
                            Frontline Healthcare Intake & Pre-Triage Engine
                        </h1>
                        <p class="text-neutral-400 text-sm mt-4 leading-relaxed">
                            AarogyaVoice empowers community health workers (ASHA/ANM) across India to capture patient speech in 6 major Indic dialects, process clinical pre-triage assessment and return instant spoken guidance.
                        </p>
                    </div>

                    <div class="mt-8 pt-6 border-t border-neutral-800/80 flex flex-wrap gap-2">
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">Prisma v2.5 STT</span>
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">Timbre v2.5 TTS</span>
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">6 Indic Languages</span>
                        <span class="bg-neutral-900 text-neutral-300 border border-neutral-800 text-xs px-3 py-1 rounded-md font-mono-code">FastAPI</span>
                    </div>
                </div>

                <div class="md:col-span-5 bg-neutral-950 border border-neutral-800 hover:border-neutral-600 transition-all duration-300 rounded-2xl p-6 font-mono-code text-xs text-neutral-300 flex flex-col justify-between shadow-2xl relative overflow-hidden">
                    <div class="flex items-center justify-between pb-3 border-b border-neutral-800 text-neutral-500 text-[11px]">
                        <span>system_config.json</span>
                        <span class="text-emerald-400">● active</span>
                    </div>
                    <pre class="py-4 text-neutral-400 overflow-x-auto space-y-1">
<span class="text-purple-400">const</span> <span class="text-blue-400">AarogyaVoice</span> = {
  <span class="text-neutral-500">model_stt</span>: <span class="text-emerald-300">"Prisma v2.5"</span>,
  <span class="text-neutral-500">model_tts</span>: <span class="text-emerald-300">"Timbre v2.5"</span>,
  <span class="text-neutral-500">languages</span>: [<span class="text-amber-300">"Hindi, Bengali, Tamil"</span>, <span class="text-amber-300">"Telugu, Marathi, English"</span>],
  <span class="text-neutral-500">triage_tiers</span>: [<span class="text-red-400">"RED"</span>, <span class="text-amber-400">"YELLOW"</span>, <span class="text-emerald-400">"GREEN"</span>]
};</pre>
                    <div class="pt-3 border-t border-neutral-800/80 text-[11px] text-neutral-500 flex justify-between">
                        <span>Status: 200 OK</span>
                        <span>Multi-Dialect Ready</span>
                    </div>
                </div>
            </section>

            <!-- Voice Intake Console Section -->
            <section id="intake" class="bg-neutral-900/30 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 rounded-2xl p-8 shadow-xl">
                <div class="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
                    <div>
                        <h2 class="text-xl font-bold text-white tracking-tight">Clinical Voice Intake Console</h2>
                        <p class="text-xs text-neutral-400 mt-1">Select language dialect and upload patient audio recording (.wav, .mp3)</p>
                    </div>

                    <!-- Language Selection Dropdown -->
                    <div class="flex items-center space-x-3">
                        <label for="languageSelect" class="text-xs font-mono-code text-neutral-400">Dialect:</label>
                        <select id="languageSelect" class="bg-neutral-900 text-white border border-neutral-700 text-xs px-3 py-2 rounded-xl focus:outline-none focus:border-emerald-500 font-mono-code">
                            <option value="hi-IN">🇮🇳 Hindi (हिन्दी)</option>
                            <option value="bn-IN" selected>🇮🇳 Bengali (বাংলা)</option>
                            <option value="ta-IN">🇮🇳 Tamil (தமிழ்)</option>
                            <option value="te-IN">🇮🇳 Telugu (తెలుగు)</option>
                            <option value="mr-IN">🇮🇳 Marathi (मराठी)</option>
                            <option value="en-IN">🇮🇳 English (Indian Accent)</option>
                        </select>
                    </div>
                </div>

                <!-- Dropzone Card -->
                <div class="border border-dashed border-neutral-800 hover:border-neutral-500 hover:bg-neutral-950/90 transition-all duration-300 rounded-xl p-8 text-center bg-neutral-950/60 cursor-pointer mb-6 shadow-inner group" onclick="document.getElementById('audioFile').click()">
                    <input type="file" id="audioFile" accept="audio/*" class="hidden" onchange="handleFileSelect(event)">
                    <div id="uploadPrompt" class="space-y-3">
                        <div class="w-10 h-10 mx-auto rounded-full bg-neutral-900 border border-neutral-800 group-hover:border-neutral-500 group-hover:scale-110 transition-all duration-300 flex items-center justify-center text-neutral-400">
                            📁
                        </div>
                        <p class="text-sm font-semibold text-neutral-200 group-hover:text-white transition-colors duration-200">Click or drop audio file here</p>
                        <p class="text-xs text-neutral-500">Supports Hindi, Bengali, Tamil, Telugu, Marathi & English (.wav, .mp3)</p>
                    </div>
                </div>

                <!-- Audio Preview Panel -->
                <div id="previewContainer" class="hidden bg-neutral-950 border border-neutral-800 rounded-xl p-5 mb-6 space-y-3 shadow-lg">
                    <div class="flex items-center justify-between">
                        <span id="fileInfo" class="text-emerald-400 font-mono-code text-xs"></span>
                        <span class="text-[10px] uppercase font-mono-code bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">Ready to Analyze</span>
                    </div>
                    <div>
                        <audio id="previewAudioPlayer" controls class="w-full h-8 mt-2"></audio>
                    </div>
                </div>

                <button onclick="analyzeAudio()" class="w-full bg-white hover:bg-neutral-200 hover:scale-[1.01] active:scale-[0.99] text-black font-semibold py-3 px-6 rounded-xl transition-all duration-200 text-sm flex items-center justify-center space-x-2 shadow-lg">
                    <span>Execute</span>
                </button>

                <!-- Loading Spinner -->
                <div id="loader" class="hidden text-center my-8">
                    <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent"></div>
                    <p class="text-xs font-mono-code text-neutral-400 mt-3">Transcribing speech & synthesizing regional voice response...</p>
                </div>

                <!-- Results Output Grid -->
                <div id="results" class="hidden mt-10 space-y-6 pt-6 border-t border-neutral-800">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 p-5 rounded-xl shadow-md">
                            <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Triage Urgency Assessment</span>
                            <div id="triageBadge" class="inline-block px-3 py-1.5 rounded-lg font-bold text-xs"></div>
                        </div>

                        <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 p-5 rounded-xl shadow-md">
                            <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Voice Guidance (Timbre v2.5)</span>
                            <audio id="audioPlayer" controls class="w-full h-8 mt-1"></audio>
                        </div>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 p-5 rounded-xl shadow-md">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Vernacular Transcript (Prisma v2.5 STT)</span>
                        <p id="transcriptBox" class="text-sm text-neutral-200 leading-relaxed font-mono-code"></p>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 p-5 rounded-xl shadow-md">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-2">Localized Verbal Advice</span>
                        <p id="adviceBox" class="text-sm text-neutral-200 leading-relaxed"></p>
                    </div>

                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 p-5 rounded-xl shadow-md">
                        <span class="text-[11px] font-mono-code text-neutral-500 uppercase tracking-wider block mb-3">Action Plan for Health Worker</span>
                        <ul id="solutionsList" class="text-xs text-neutral-300 space-y-2 list-disc list-inside font-mono-code"></ul>
                    </div>
                </div>
            </section>

            <!-- System Architecture Section -->
            <section id="system" class="bg-neutral-900/30 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 rounded-2xl p-8 space-y-6 shadow-xl">
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">System Architecture</h2>
                    <p class="text-xs text-neutral-400 mt-1">End-to-end processing pipeline powered by Gnani AI Artha Stack</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono-code text-xs">
                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-500 hover:-translate-y-1 transition-all duration-300 p-5 rounded-xl shadow-lg">
                        <span class="text-neutral-500 text-[10px]">01 / STT PIPELINE</span>
                        <h3 class="text-sm font-bold text-white mt-1 mb-2">Gnani Prisma v2.5</h3>
                        <p class="text-neutral-400 text-[11px] leading-relaxed">Transcribes spoken patient complaints from multi-Indic languages into accurate text with native numeral normalization.</p>
                    </div>
                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-500 hover:-translate-y-1 transition-all duration-300 p-5 rounded-xl shadow-lg">
                        <span class="text-neutral-500 text-[10px]">02 / CLINICAL LOGIC</span>
                        <h3 class="text-sm font-bold text-white mt-1 mb-2">Pre-Triage Engine</h3>
                        <p class="text-neutral-400 text-[11px] leading-relaxed">Evaluates symptoms across multiple dialects into Red, Yellow or Green urgency levels with structured worker checklists.</p>
                    </div>
                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-500 hover:-translate-y-1 transition-all duration-300 p-5 rounded-xl shadow-lg">
                        <span class="text-neutral-500 text-[10px]">03 / VOICE SYNTHESIS</span>
                        <h3 class="text-sm font-bold text-white mt-1 mb-2">Gnani Timbre v2.5</h3>
                        <p class="text-neutral-400 text-[11px] leading-relaxed">Synthesizes natural, localized voice instructions using regional models (Nalini, Srabani, Padma, etc. at 24kHz).</p>
                    </div>
                </div>
            </section>

            <!-- About Project Section -->
            <section id="about" class="bg-neutral-900/30 border border-neutral-800 hover:border-neutral-700 transition-all duration-300 rounded-2xl p-8 space-y-6 shadow-xl">
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">About Project</h2>
                    <p class="text-xs text-neutral-400 mt-1">Addressing healthcare delivery challenges across rural India</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs text-neutral-300 leading-relaxed">
                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-600 hover:-translate-y-1 transition-all duration-300 p-6 rounded-xl space-y-2 shadow-lg">
                        <h3 class="text-sm font-bold text-white">The Problem Statement</h3>
                        <p class="text-neutral-400">Rural primary health centers and frontline community health workers (ASHA / ANMs) struggle with diverse regional language barriers, heavy queues, and rapid symptom categorization.</p>
                    </div>
                    <div class="bg-neutral-950 border border-neutral-800 hover:border-neutral-600 hover:-translate-y-1 transition-all duration-300 p-6 rounded-xl space-y-2 shadow-lg">
                        <h3 class="text-sm font-bold text-white">Sovereign Multi-Indic AI Solution</h3>
                        <p class="text-neutral-400">AarogyaVoice leverages indigenous voice technology built specifically for Indian regional dialects, bridging patient intake and immediate clinical guidance seamlessly.</p>
                    </div>
                </div>
            </section>

        </main>

        <footer class="w-full border-t border-neutral-900 py-6 mt-12 text-center text-xs text-neutral-600 font-mono-code">
            <p>AarogyaVoice © 2026 — Built for Great Indian AI Internship Challenge</p>
        </footer>

        <script>
            let selectedFile = null;

            function handleFileSelect(e) {
                selectedFile = e.target.files[0];
                if(selectedFile) {
                    const info = document.getElementById('fileInfo');
                    const container = document.getElementById('previewContainer');
                    const previewPlayer = document.getElementById('previewAudioPlayer');
                    const uploadPrompt = document.getElementById('uploadPrompt');

                    info.innerText = `Selected File: ${selectedFile.name} (${(selectedFile.size/1024/1024).toFixed(2)} MB)`;
                    previewPlayer.src = URL.createObjectURL(selectedFile);
                    container.classList.remove('hidden');
                    uploadPrompt.innerHTML = `<div class="w-10 h-10 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-2">✅</div><p class="text-sm font-semibold text-emerald-400">Audio File Loaded Successfully</p><p class="text-xs text-neutral-500">Click or drop another file to replace</p>`;
                }
            }

            async function analyzeAudio() {
                if(!selectedFile) return alert("Please select an audio file first!");
                const lang = document.getElementById('languageSelect').value;

                const formData = new FormData();
                formData.append("file", selectedFile);
                formData.append("language", lang);

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
