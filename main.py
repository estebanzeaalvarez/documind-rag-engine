from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
import fitz  # PyMuPDF
from google import genai 

# Configuración de la IA con el nuevo cliente oficial
client = genai.Client(api_key="AIzaSyCxecEPsKKoLi775K9StShWVCanwMPweQY")

app = FastAPI(title="DocuMind AI - G2i Edition")

# Interfaz Premium: Dark Mode, Dashboard Style y análisis enfocado en G2i
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuMind AI | Engine Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .prose h1, .prose h2, .prose h3 { color: #60a5fa; font-weight: 700; margin-top: 1.5rem; }
        .prose strong { color: #f8fafc; }
        .prose p { color: #cbd5e1; margin-bottom: 1rem; }
        .prose ul { list-style-type: disc; padding-left: 1.5rem; color: #cbd5e1; }
    </style>
</head>
<body class="bg-[#0f172a] text-slate-200 min-h-screen">
    <div class="max-w-6xl mx-auto py-10 px-4">
        
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-12 gap-4">
            <div>
                <h1 class="text-3xl font-black tracking-tighter text-white">DOCUMIND <span class="text-blue-500">PRO</span></h1>
                <p class="text-slate-400 mt-1">Intelligent Document Processing & Talent Matching</p>
            </div>
            <div class="flex items-center gap-3 bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-full">
                <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span class="text-blue-400 text-xs font-bold tracking-widest uppercase">Target: G2i AI Startup Role</span>
            </div>
        </div>

        <div class="grid lg:grid-cols-12 gap-8">
            
            <!-- Panel Lateral: Control y Status -->
            <div class="lg:col-span-4 space-y-6">
                <div class="bg-[#1e293b] p-6 rounded-2xl border border-slate-700/50 shadow-2xl">
                    <h2 class="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wider flex items-center gap-2">
                        <i data-lucide="binary" class="w-4 h-4"></i> Data Input
                    </h2>
                    <form id="uploadForm" class="space-y-4">
                        <div id="dropZone" class="border-2 border-dashed border-slate-700 p-8 rounded-xl text-center hover:border-blue-500/50 transition-all cursor-pointer bg-slate-900/50 group">
                            <i data-lucide="file-up" class="w-10 h-10 mx-auto text-slate-600 group-hover:text-blue-500 mb-2 transition-colors"></i>
                            <p id="dropText" class="text-sm text-slate-500 font-medium">Drop candidate PDF</p>
                            <input type="file" id="fileInput" name="file" accept=".pdf" class="hidden">
                        </div>
                        
                        <button type="submit" id="submitBtn" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl transition-all flex justify-center items-center gap-3 shadow-lg shadow-blue-900/20 group">
                            <span>RUN AI ANALYSIS</span>
                            <i data-lucide="play" class="w-4 h-4 fill-current group-hover:scale-110 transition-transform"></i>
                        </button>
                    </form>

                    <div id="loading" class="hidden mt-6">
                        <div class="flex items-center justify-center gap-3 text-blue-400">
                            <div class="inline-block animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                            <span class="text-xs font-bold uppercase tracking-wider">Processing Neural Engine...</span>
                        </div>
                    </div>
                </div>

                <div class="bg-[#1e293b]/50 p-6 rounded-2xl border border-slate-700/50">
                    <h2 class="text-xs font-bold text-slate-500 uppercase mb-4 tracking-wider flex items-center gap-2">
                        <i data-lucide="activity" class="w-4 h-4"></i> System Specs
                    </h2>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-500">Core LLM:</span>
                            <span class="text-xs font-mono text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded">gemini-2.5-flash</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-500">Context Window:</span>
                            <span class="text-xs font-mono text-slate-300">1M Tokens</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-500">Architecture:</span>
                            <span class="text-xs font-mono text-slate-300">0 &rarr; 1 Ready</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Panel Principal: Reporte -->
            <div class="lg:col-span-8">
                <!-- Estado Inicial -->
                <div id="welcomeState" class="bg-[#1e293b]/30 h-full min-h-[500px] rounded-3xl border border-dashed border-slate-700 flex flex-col items-center justify-center text-center p-12">
                    <div class="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6 border border-slate-700">
                        <i data-lucide="brain-circuit" class="w-10 h-10 text-slate-600"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-white mb-3">AI Matching Engine</h3>
                    <p class="text-slate-500 max-w-sm mx-auto leading-relaxed italic">
                        "Designed to evaluate Senior Python & LLM Engineers for high-impact startup roles."
                    </p>
                </div>

                <!-- Resultado -->
                <div id="resultContainer" class="hidden space-y-6">
                    <div class="bg-[#1e293b] p-10 rounded-3xl border border-slate-700/50 shadow-2xl relative overflow-hidden">
                        <div class="absolute top-0 right-0 p-6">
                             <div class="bg-green-500/10 border border-green-500/20 text-green-400 px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-xl">
                                AI Verified Match
                            </div>
                        </div>
                        
                        <div class="flex items-center gap-4 mb-10 pb-6 border-b border-slate-700/50">
                            <div class="bg-blue-600 p-3 rounded-2xl shadow-lg shadow-blue-900/40">
                                <i data-lucide="scroll-text" class="w-7 h-7 text-white"></i>
                            </div>
                            <div>
                                <h2 class="text-2xl font-black text-white tracking-tight">Strategic Hiring Report</h2>
                                <p id="fileName" class="text-blue-400 text-xs font-medium"></p>
                            </div>
                        </div>
                        
                        <div id="aiResponse" class="prose prose-invert max-w-none">
                            <!-- Inyectado por JS -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const dropText = document.getElementById('dropText');
        const form = document.getElementById('uploadForm');
        const btn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading');
        const welcomeState = document.getElementById('welcomeState');
        const resultContainer = document.getElementById('resultContainer');
        const aiResponse = document.getElementById('aiResponse');

        dropZone.onclick = () => fileInput.click();
        fileInput.onchange = () => { if(fileInput.files.length) dropText.innerText = fileInput.files[0].name; };

        form.onsubmit = async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) return;

            btn.disabled = true;
            btn.classList.add('opacity-50');
            loading.classList.remove('hidden');
            welcomeState.classList.add('hidden');
            resultContainer.classList.add('hidden');

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            try {
                const response = await fetch('/analyze/', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (data.error) {
                    alert("Error: " + data.detalles);
                } else {
                    aiResponse.innerHTML = marked.parse(data.analisis_ia);
                    document.getElementById('fileName').innerText = data.archivo.toUpperCase();
                    resultContainer.classList.remove('hidden');
                    resultContainer.scrollIntoView({ behavior: 'smooth' });
                }
            } catch (err) {
                alert("Motor de IA fuera de línea");
            } finally {
                btn.disabled = false;
                btn.classList.remove('opacity-50');
                loading.classList.add('hidden');
            }
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return html_content

@app.post("/analyze/")
async def analyze_document(file: UploadFile = File(...)):
    try:
        # 1. Extracción Técnica
        contenido = await file.read()
        doc = fitz.open(stream=contenido, filetype="pdf")
        texto_cv = "".join([pagina.get_text() for pagina in doc])
        doc.close()

        # 2. Prompt Estratégico Optimizado para balancear rigor y potencial
        prompt = f"""
        Actúa como el CTO de G2i evaluando a un candidato Senior para un startup de IA.
        La vacante es para un Senior Fullstack/Backend (Python + LLM). Buscamos mentalidad "0 a 1".

        CV A EVALUAR:
        {texto_cv[:8000]}

        GENERA UN INFORME DE CONTRATACIÓN EN MARKDOWN:

        # 🎯 Match Estratégico: [X/10]
        (Puntuación basada en Seniority técnico y capacidad de ejecución en startups. Sé objetivo pero busca el potencial oculto).

        ## 🚀 Ejecución y Propiedad (Mentalidad Startup)
        (Analiza su autonomía. ¿Muestra signos de haber tomado decisiones difíciles o liderado iniciativas técnicas?).

        ## 🐍 Stack Tecnológico (Python & Systems)
        (Evalúa su maestría en Python y su capacidad para diseñar sistemas escalables).

        ## 🧠 IA Contextual & LLMs
        (Analiza su curiosidad técnica o proyectos relacionados con IA. Si no tiene proyectos directos de IA, evalúa su capacidad de aprendizaje rápido basado en su trayectoria técnica).

        ## 💡 Recomendación para Juliana
        (Un veredicto final: ¿Es el perfil 'grit' que G2i necesita? Sugiere 2 temas técnicos profundos para la entrevista inicial).
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        return {
            "archivo": file.filename,
            "analisis_ia": response.text,
            "info_tecnica": {"modelo": "gemini-2.5-flash"}
        }
    except Exception as e:
        return {"error": "Critical Failure", "detalles": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)