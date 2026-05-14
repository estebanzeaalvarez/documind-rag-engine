from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
import fitz  # PyMuPDF
from google import genai 
import time

# Configuración de la IA
client = genai.Client(api_key="AIzaSyCxecEPsKKoLi775K9StShWVCanwMPweQY")

app = FastAPI(title="DocuMind RAG Engine")

# Interfaz "Developer/Engineer Mode" mejorada con Prompt Editor
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocuMind Engine | 0→1 Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #09090b; color: #ededed; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        
        .prose pre { background-color: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1rem; color: #a1a1aa; }
        .prose code { color: #60a5fa; }
        .prose strong { color: #f4f4f5; }
        .prose h3 { color: #e4e4e7; font-weight: 600; margin-top: 1rem; border-bottom: 1px solid #27272a; padding-bottom: 0.5rem; }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #09090b; }
        ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }

        /* Estilo para el editor de prompt */
        #promptEditor {
            scrollbar-width: thin;
            scrollbar-color: #27272a #09090b;
        }
    </style>
</head>
<body class="min-h-screen">
    <!-- Navbar -->
    <nav class="border-b border-zinc-800 bg-zinc-950 px-6 py-4 flex justify-between items-center sticky top-0 z-10">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <i data-lucide="cpu" class="w-5 h-5 text-white"></i>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-tight">DocuMind <span class="text-zinc-500 font-normal">Extraction Engine</span></h1>
            </div>
        </div>
        <div class="flex items-center gap-4 text-xs font-mono text-zinc-400">
            <span class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-green-500"></div> System Online</span>
            <span class="bg-zinc-800 px-2 py-1 rounded">v1.1 (Dynamic Prompt)</span>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto py-8 px-4 grid lg:grid-cols-12 gap-6">
        
        <!-- COLUMNA IZQUIERDA: Inputs y Configuración -->
        <div class="lg:col-span-4 space-y-6">
            
            <!-- Upload Module -->
            <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-5 shadow-lg">
                <div class="flex items-center gap-2 mb-4">
                    <i data-lucide="file-json" class="w-4 h-4 text-blue-400"></i>
                    <h2 class="text-sm font-semibold text-zinc-200">1. Data Ingestion (PDF)</h2>
                </div>
                
                <form id="uploadForm" class="space-y-4">
                    <div id="dropZone" class="border-2 border-dashed border-zinc-700 bg-zinc-950/50 p-6 rounded-lg text-center hover:border-blue-500/50 hover:bg-blue-900/10 transition-all cursor-pointer group">
                        <i data-lucide="upload-cloud" class="w-8 h-8 mx-auto text-zinc-500 group-hover:text-blue-400 mb-2 transition-colors"></i>
                        <p id="dropText" class="text-xs text-zinc-400 font-medium">Arrastra un documento aquí</p>
                        <input type="file" id="fileInput" name="file" accept=".pdf" class="hidden">
                    </div>
                    
                    <button type="submit" id="submitBtn" class="w-full bg-white text-black hover:bg-zinc-200 font-semibold py-3 rounded-lg transition-all flex justify-center items-center gap-2 text-sm">
                        <span>Iniciar Pipeline de Extracción</span>
                        <i data-lucide="arrow-right" class="w-4 h-4"></i>
                    </button>
                </form>
            </div>

            <!-- Prompt Engineering Inspector (NOW EDITABLE) -->
            <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-5 shadow-lg flex flex-col h-[450px]">
                <div class="flex justify-between items-center mb-3">
                    <div class="flex items-center gap-2">
                        <i data-lucide="terminal" class="w-4 h-4 text-emerald-400"></i>
                        <h2 class="text-sm font-semibold text-zinc-200">2. Prompt Architecture</h2>
                    </div>
                    <span class="text-[10px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">Editable Mode</span>
                </div>
                <textarea id="promptEditor" class="bg-zinc-950 border border-zinc-800 rounded-lg p-4 flex-grow font-mono text-[11px] text-emerald-400/80 leading-relaxed resize-none focus:outline-none focus:border-emerald-500/50 transition-colors">Eres un motor de extracción de datos especializado en perfiles IT.
Tu trabajo es analizar el texto de un CV y devolver los datos organizados.
NO evalúes al candidato, solo extrae información.

DEVUELVE EL RESULTADO EN FORMATO MARKDOWN ESTRUCTURADO:

### ⚙️ Core Technical Stack
(Lenguajes y frameworks)

### ☁️ Cloud & Infrastructure
(Herramientas cloud y DevOps)

### 🚀 "0 to 1" / Build Experience
(Evidencias de construcción desde cero)

### 🧠 Seniority Signals
(Responsabilidades avanzadas y arquitectura)</textarea>
                <p class="mt-3 text-[10px] text-zinc-500 italic">
                    * El texto del CV se inyectará automáticamente al final de estas instrucciones.
                </p>
            </div>
        </div>

        <!-- COLUMNA DERECHA: Resultados y Logs -->
        <div class="lg:col-span-8 space-y-6">
            
            <!-- Output Console -->
            <div class="bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg overflow-hidden flex flex-col h-[calc(100vh-140px)]">
                
                <!-- Tabs -->
                <div class="flex border-b border-zinc-800 bg-zinc-950/50 px-4">
                    <button id="tabOutputBtn" class="px-4 py-3 text-sm font-medium text-blue-400 border-b-2 border-blue-500 transition-all">Structured Output</button>
                    <button id="tabLogsBtn" class="px-4 py-3 text-sm font-medium text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2 transition-all">
                        Engine Logs <span id="logCounter" class="bg-zinc-800 text-zinc-300 text-[10px] px-1.5 py-0.5 rounded-full">0</span>
                    </button>
                </div>

                <!-- Contenido Principal -->
                <div class="p-6 flex-grow overflow-y-auto relative bg-[#0c0c0e]">
                    
                    <div id="welcomeState" class="absolute inset-0 flex flex-col items-center justify-center text-center p-8">
                        <div class="w-16 h-16 bg-zinc-800/50 rounded-xl flex items-center justify-center mb-4 border border-zinc-700">
                            <i data-lucide="database-zap" class="w-8 h-8 text-zinc-500"></i>
                        </div>
                        <h3 class="text-lg font-bold text-zinc-300 mb-2">A la espera de datos</h3>
                        <p class="text-zinc-500 text-sm max-w-md">
                            Sube un PDF. Puedes modificar las instrucciones en el panel de la izquierda para cambiar cómo la IA extrae los datos.
                        </p>
                    </div>

                    <div id="logConsole" class="hidden absolute inset-0 bg-[#0c0c0e] p-6 font-mono text-[12px] text-zinc-400 overflow-y-auto space-y-2">
                        <div id="logContent"></div>
                        <div id="processingIndicator" class="flex items-center gap-2 text-blue-400 mt-2 animate-pulse">
                            <div class="w-2 h-4 bg-blue-500"></div> Procesando...
                        </div>
                    </div>

                    <div id="resultContainer" class="hidden">
                        <div class="flex justify-between items-center mb-6">
                            <h3 class="text-lg font-bold text-white flex items-center gap-2">
                                <i data-lucide="check-circle-2" class="w-5 h-5 text-green-500"></i> Extracción Exitosa
                            </h3>
                            <div class="flex gap-3 font-mono text-[11px]">
                                <span class="bg-zinc-800 text-zinc-300 px-2 py-1 rounded" id="metaTokens">Tokens: 0</span>
                                <span class="bg-blue-900/30 text-blue-400 border border-blue-800 px-2 py-1 rounded" id="metaTime">0ms</span>
                            </div>
                        </div>
                        <div id="aiResponse" class="prose prose-invert max-w-none text-sm text-zinc-300"></div>
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
        const promptEditor = document.getElementById('promptEditor');
        
        const welcomeState = document.getElementById('welcomeState');
        const logConsole = document.getElementById('logConsole');
        const logContent = document.getElementById('logContent');
        const resultContainer = document.getElementById('resultContainer');
        const aiResponse = document.getElementById('aiResponse');

        const tabOutputBtn = document.getElementById('tabOutputBtn');
        const tabLogsBtn = document.getElementById('tabLogsBtn');

        function setActiveTab(tab) {
            if (tab === 'output') {
                tabOutputBtn.className = "px-4 py-3 text-sm font-medium text-blue-400 border-b-2 border-blue-500 transition-all";
                tabLogsBtn.className = "px-4 py-3 text-sm font-medium text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2 transition-all";
                resultContainer.classList.remove('hidden');
                logConsole.classList.add('hidden');
            } else {
                tabLogsBtn.className = "px-4 py-3 text-sm font-medium text-blue-400 border-b-2 border-blue-500 transition-all";
                tabOutputBtn.className = "px-4 py-3 text-sm font-medium text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2 transition-all";
                logConsole.classList.remove('hidden');
                resultContainer.classList.add('hidden');
            }
        }

        tabOutputBtn.onclick = () => {
            if (welcomeState.classList.contains('hidden')) setActiveTab('output');
        };

        tabLogsBtn.onclick = () => {
            if (welcomeState.classList.contains('hidden')) setActiveTab('logs');
        };

        dropZone.onclick = () => fileInput.click();
        fileInput.onchange = () => { if(fileInput.files.length) dropText.innerText = fileInput.files[0].name; };
        
        dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('border-blue-500'); };
        dropZone.ondragleave = () => { dropZone.classList.remove('border-blue-500'); };
        dropZone.ondrop = (e) => {
            e.preventDefault();
            dropZone.classList.remove('border-blue-500');
            if (e.dataTransfer.files.length && e.dataTransfer.files[0].type === "application/pdf") {
                fileInput.files = e.dataTransfer.files;
                dropText.innerText = fileInput.files[0].name;
            }
        };

        const addLog = (text, color = "text-zinc-400") => {
            const time = new Date().toISOString().split('T')[1].substring(0, 8);
            logContent.innerHTML += `<div><span class="text-zinc-600">[${time}]</span> <span class="${color}">${text}</span></div>`;
        };

        form.onsubmit = async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) return;

            btn.disabled = true;
            btn.classList.add('opacity-50');
            welcomeState.classList.add('hidden');
            resultContainer.classList.add('hidden');
            logConsole.classList.remove('hidden');
            logContent.innerHTML = '';
            document.getElementById('logCounter').innerText = "Running";
            document.getElementById('processingIndicator').classList.remove('hidden');
            setActiveTab('logs');

            addLog("Iniciando POST /analyze/...", "text-blue-400");
            setTimeout(() => addLog("Archivo: " + fileInput.files[0].name), 400);
            setTimeout(() => addLog("Leyendo Prompt dinámico del editor...", "text-emerald-400"), 700);
            setTimeout(() => addLog("Ejecutando extracción de texto PDF..."), 1100);
            setTimeout(() => addLog("Llamando a Gemini 2.5 Flash...", "text-blue-400"), 1500);

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('custom_prompt', promptEditor.value);
            
            const startTime = Date.now();

            try {
                const response = await fetch('/analyze/', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (data.error) {
                    addLog("ERROR: " + data.detalles, "text-red-500");
                } else {
                    const elapsed = Date.now() - startTime;
                    addLog("Pipeline finalizado con éxito.", "text-green-400");
                    
                    setTimeout(() => {
                        document.getElementById('logCounter').innerText = "Logs OK";
                        document.getElementById('processingIndicator').classList.add('hidden');
                        
                        aiResponse.innerHTML = marked.parse(data.analisis_ia);
                        document.getElementById('metaTokens').innerText = `Context: ${data.info_tecnica.palabras_leidas} words`;
                        document.getElementById('metaTime').innerText = `${elapsed}ms`;
                        
                        setActiveTab('output');
                    }, 800);
                }
            } catch (err) {
                addLog("Error de conexión con el backend.", "text-red-500");
            } finally {
                btn.disabled = false;
                btn.classList.remove('opacity-50');
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
async def analyze_document(file: UploadFile = File(...), custom_prompt: str = Form(...)):
    try:
        # 1. Extracción de texto del PDF
        contenido = await file.read()
        doc = fitz.open(stream=contenido, filetype="pdf")
        texto_cv = "".join([pagina.get_text() for pagina in doc])
        doc.close()

        # 2. Uso del prompt dinámico enviado desde el frontend
        full_prompt = f"""
        {custom_prompt}

        ---
        TEXTO DEL DOCUMENTO A ANALIZAR:
        {texto_cv[:8000]}
        """
        
# Usamos el objeto 'model' definido arriba con la sintaxis correcta
        response = model.generate_content(full_prompt)
        
        return {
            "archivo": file.filename,
            "analisis_ia": response.text,
            "info_tecnica": {
                "modelo": "gemini-2.5-flash",
                "palabras_leidas": len(texto_cv.split())
            }
        }
    except Exception as e:
        return {"error": "Critical Failure", "detalles": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)