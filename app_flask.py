# app_flask.py - CHATBOT COMPLETO CORREGIDO (DialoGPT funciona)
from flask import Flask, render_template, request, jsonify, session
import requests
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from datetime import datetime
from dotenv import load_dotenv
from huggingface_hub import login
import psutil
import platform
from historial import HistorialManager

load_dotenv()

# Login a HuggingFace (necesario para Llama)
try:
    hf_token = os.getenv("HF_TOKEN", "")
    if hf_token:
        login(token=hf_token)
        print("✅ Login HuggingFace exitoso")
except:
    print("⚠️ No hay token de HuggingFace, algunos modelos no funcionarán")

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ============================================
# FUNCIÓN PARA DETECTAR HARDWARE DEL USUARIO
# ============================================

def get_system_info():
    """Detecta RAM y núcleos de CPU (funciona en Windows)"""
    
    ram = psutil.virtual_memory()
    ram_total_gb = round(ram.total / (1024**3), 1)
    ram_available_gb = round(ram.available / (1024**3), 1)
    ram_percent = ram.percent
    
    cpu_logicos = psutil.cpu_count(logical=True)
    cpu_fisicos = psutil.cpu_count(logical=False)
    
    try:
        frecuencia = psutil.cpu_freq()
        if frecuencia and frecuencia.current:
            velocidad_ghz = round(frecuencia.current / 1000, 1)
            velocidad_texto = f"{velocidad_ghz} GHz"
        else:
            velocidad_texto = "N/A"
    except:
        velocidad_texto = "N/A"
    
    cpu_porcentaje = psutil.cpu_percent(interval=0.5)
    
    if ram_available_gb < 4:
        recomendacion = "⚠️ RAM baja! Usa modelos ligeros"
    elif ram_available_gb < 8:
        recomendacion = "⚠️ RAM limitada. DialoGPT-medium recomendado"
    elif ram_available_gb < 16:
        recomendacion = "✅ RAM suficiente para Mistral 7B"
    else:
        recomendacion = "✅ RAM excelente! Puedes usar cualquier modelo"
    
    return {
        "ram_total": ram_total_gb,
        "ram_available": ram_available_gb,
        "ram_percent": ram_percent,
        "cpu_nucleos_fisicos": cpu_fisicos,
        "cpu_nucleos_logicos": cpu_logicos,
        "cpu_velocidad": velocidad_texto,
        "cpu_uso": cpu_porcentaje,
        "os": platform.system(),
        "os_version": platform.version().split('-')[0][:10] if platform.version() else "Unknown",
        "recomendacion": recomendacion
    }

# ============================================
# CONFIGURACIÓN DE MODELOS
# ============================================

MODELOS = {
    "deepseek": {
        "nombre": "DeepSeek API",
        "tipo": "comercial",
        "categoria": "🌐 API",
        "descripcion": "Modelo chino, muy potente",
        "calidad": "⭐⭐⭐⭐⭐",
        "icono": "🐋",
        "ram_requerida": 0,
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "modelo_api": "deepseek-chat"
    },
    "chatgpt": {
        "nombre": "ChatGPT",
        "tipo": "comercial",
        "categoria": "🌐 API",
        "descripcion": "OpenAI GPT-3.5/4",
        "calidad": "⭐⭐⭐⭐⭐",
        "icono": "🤖",
        "ram_requerida": 0,
        "api_url": "https://api.openai.com/v1/chat/completions",
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "modelo_api": "gpt-3.5-turbo"
    },
    "gemini": {
        "nombre": "Gemini",
        "tipo": "comercial",
        "categoria": "🌐 API",
        "descripcion": "Google Gemini 2.0 Flash",
        "calidad": "⭐⭐⭐⭐",
        "icono": "🔵",
        "ram_requerida": 0,
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "api_key": os.getenv("GEMINI_API_KEY", "")
    },
    "dialoGPT_small": {
        "nombre": "DialoGPT-small",
        "tipo": "local",
        "categoria": "💻 Local",
        "descripcion": "Microsoft - 500MB - Ligero y conversacional",
        "calidad": "⭐⭐",
        "icono": "💬",
        "ram_requerida": 1,
        "modelo_id": "microsoft/DialoGPT-small",
        "arquitectura": "dialogpt"
    },
    "dialoGPT_medium": {
        "nombre": "DialoGPT-medium",
        "tipo": "local",
        "categoria": "💻 Local",
        "descripcion": "Microsoft - 1.5GB - Equilibrado",
        "calidad": "⭐⭐⭐",
        "icono": "💬",
        "ram_requerida": 2.5,
        "modelo_id": "microsoft/DialoGPT-medium",
        "arquitectura": "dialogpt"
    },
    "dialoGPT_large": {
        "nombre": "DialoGPT-large",
        "tipo": "local",
        "categoria": "💻 Local",
        "descripcion": "Microsoft - 3.5GB - Potente",
        "calidad": "⭐⭐⭐⭐",
        "icono": "💬",
        "ram_requerida": 5,
        "modelo_id": "microsoft/DialoGPT-large",
        "arquitectura": "dialogpt"
    },
    "gpt2_spanish": {
        "nombre": "GPT-2 Spanish",
        "tipo": "local",
        "categoria": "💻 Local",
        "descripcion": "datificate/gpt2-small-spanish - Español básico",
        "calidad": "⭐⭐",
        "icono": "🇪🇸",
        "ram_requerida": 1,
        "modelo_id": "datificate/gpt2-small-spanish",
        "arquitectura": "gpt2"
    },
    "llama3": {
        "nombre": "Llama 3 8B",
        "tipo": "local",
        "categoria": "💻 Local",
        "descripcion": "Meta - 8GB - Excelente calidad",
        "calidad": "⭐⭐⭐⭐⭐",
        "icono": "🦙",
        "ram_requerida": 10,
        "modelo_id": "meta-llama/Meta-Llama-3-8B-Instruct",
        "arquitectura": "llama"
    },
    "mistral": {
        "nombre": "Mistral 7B",
        "tipo": "local",
        "categoria": "💻 Local",
        "descripcion": "Mistral AI - 7GB - Rápido y preciso en español",
        "calidad": "⭐⭐⭐⭐⭐",
        "icono": "🎯",
        "ram_requerida": 8,
        "modelo_id": "mistralai/Mistral-7B-Instruct-v0.3",
        "arquitectura": "mistral",
        "seleccionado": True
    }
}

class ChatbotManager:
    def __init__(self):
        self.modelo_actual = "mistral"
        self.modelo_info = MODELOS[self.modelo_actual]
        self.modelo_cargado = None
        self.tokenizer = None
        self.memoria = []
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.system_info = get_system_info()
        
        # Inicializar historial
        self.historial = HistorialManager(self.modelo_actual)
        self.historial.iniciar_nueva_conversacion()
        
        print("="*50)
        print("🤖 SISTEMA DE CHATBOT MULTI-MODELO")
        print("="*50)
        print(f"💻 Hardware: {self.device.upper()}")
        print(f"🧠 RAM Total: {self.system_info['ram_total']} GB")
        print(f"⚡ RAM Disponible: {self.system_info['ram_available']} GB")
        print("="*50)
        
        if self.modelo_info["tipo"] == "local":
            self._cargar_modelo_local()
    
    def _cargar_modelo_local(self):
        modelo_id = self.modelo_info["modelo_id"]
        arquitectura = self.modelo_info.get("arquitectura", "default")
        
        ram_necesaria = self.modelo_info.get("ram_requerida", 4)
        if self.system_info["ram_available"] < ram_necesaria:
            return False, f"⚠️ RAM insuficiente! Necesitas {ram_necesaria} GB"
        
        print(f"\n🚀 Cargando: {self.modelo_info['nombre']}")
        print(f"📦 ID: {modelo_id}")
        
        try:
            if arquitectura == "dialogpt":
                # DialoGPT - Usar AutoModelForCausalLM directamente (más fiable)
                self.tokenizer = AutoTokenizer.from_pretrained(modelo_id)
                self.modelo_cargado = AutoModelForCausalLM.from_pretrained(
                    modelo_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                # Configurar token de padding
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                print(f"✅ {self.modelo_info['nombre']} cargado (AutoModel)")
                
            elif arquitectura in ["mistral", "llama"]:
                self.tokenizer = AutoTokenizer.from_pretrained(modelo_id)
                self.modelo_cargado = AutoModelForCausalLM.from_pretrained(
                    modelo_id,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    low_cpu_mem_usage=True
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                print(f"✅ {self.modelo_info['nombre']} cargado")
                
            elif arquitectura == "gpt2":
                self.tokenizer = AutoTokenizer.from_pretrained(modelo_id)
                self.modelo_cargado = AutoModelForCausalLM.from_pretrained(
                    modelo_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                print(f"✅ {self.modelo_info['nombre']} cargado")
                
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(modelo_id)
                self.modelo_cargado = AutoModelForCausalLM.from_pretrained(
                    modelo_id,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                print(f"✅ {self.modelo_info['nombre']} cargado")
            
            return True, "OK"
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, str(e)
    
    def _generar_respuesta_local(self, user_message):
        arquitectura = self.modelo_info.get("arquitectura", "default")
        
        try:
            if arquitectura == "dialogpt":
                # Formato específico para DialoGPT
                prompt = f"User: {user_message}\nBot:"
                inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
                with torch.no_grad():
                    outputs = self.modelo_cargado.generate(
                        inputs.input_ids,
                        max_new_tokens=150,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                response = response.strip()
                if not response or len(response) < 2:
                    response = "No entendí bien, ¿puedes reformular?"
                return response
                
            elif arquitectura in ["mistral", "llama"]:
                prompt = f"<s>[INST] {user_message} [/INST]"
                inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
                with torch.no_grad():
                    outputs = self.modelo_cargado.generate(
                        inputs.input_ids,
                        max_new_tokens=250,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
                response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                return response.strip() if response else "No pude generar una respuesta."
                
            elif arquitectura == "gpt2":
                prompt = f"Usuario: {user_message}\nAsistente:"
                inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
                with torch.no_grad():
                    outputs = self.modelo_cargado.generate(
                        inputs.input_ids,
                        max_new_tokens=150,
                        temperature=0.8,
                        do_sample=True,
                        pad_token_id=self.tokenizer.pad_token_id
                    )
                response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                return response.strip() if response else "No pude generar una respuesta."
                
            else:
                return f"Usando {self.modelo_info['nombre']}. Procesando..."
                
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"
    
    def _consultar_api_deepseek(self, user_message):
        if not self.modelo_info["api_key"]:
            return "⚠️ API Key de DeepSeek no configurada"
        headers = {"Authorization": f"Bearer {self.modelo_info['api_key']}", "Content-Type": "application/json"}
        data = {"model": self.modelo_info["modelo_api"], "messages": [{"role": "user", "content": user_message}], "temperature": 0.7}
        try:
            response = requests.post(self.modelo_info["api_url"], headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"Error API: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def _consultar_api_chatgpt(self, user_message):
        if not self.modelo_info["api_key"]:
            return "⚠️ API Key de OpenAI no configurada"
        headers = {"Authorization": f"Bearer {self.modelo_info['api_key']}", "Content-Type": "application/json"}
        data = {"model": self.modelo_info["modelo_api"], "messages": [{"role": "user", "content": user_message}], "temperature": 0.7}
        try:
            response = requests.post(self.modelo_info["api_url"], headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"Error API: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def _consultar_api_gemini(self, user_message):
        if not self.modelo_info["api_key"]:
            return "⚠️ API Key de Gemini no configurada"
        url = f"{self.modelo_info['api_url']}?key={self.modelo_info['api_key']}"
        data = {"contents": [{"parts": [{"text": user_message}]}]}
        try:
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return f"Error API: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def get_response(self, user_message):
        if not user_message.strip():
            return "Por favor, escribe algo."
        
        if self.modelo_info["tipo"] == "comercial":
            if self.modelo_actual == "deepseek":
                response = self._consultar_api_deepseek(user_message)
            elif self.modelo_actual == "chatgpt":
                response = self._consultar_api_chatgpt(user_message)
            elif self.modelo_actual == "gemini":
                response = self._consultar_api_gemini(user_message)
            else:
                response = "Modelo no implementado"
        else:
            if self.modelo_cargado is None:
                success, msg = self._cargar_modelo_local()
                if not success:
                    return f"❌ {msg}"
            response = self._generar_respuesta_local(user_message)
        
        self.memoria.append({"role": "user", "content": user_message})
        self.memoria.append({"role": "assistant", "content": response})
        if len(self.memoria) > 40:
            self.memoria = self.memoria[-40:]
        
        # Guardar en historial
        self.historial.guardar_mensaje(user_message, response)
        
        return response
    
    def cambiar_modelo(self, nuevo_modelo_key):
        if nuevo_modelo_key not in MODELOS:
            return False, "Modelo no disponible"
        if nuevo_modelo_key == self.modelo_actual:
            return False, "Ya estás usando este modelo"
        
        modelo_info = MODELOS[nuevo_modelo_key]
        
        if modelo_info["tipo"] == "local":
            ram_necesaria = modelo_info.get("ram_requerida", 4)
            if self.system_info["ram_available"] < ram_necesaria:
                return False, f"⚠️ RAM insuficiente para {modelo_info['nombre']}!"
            
            modelo_anterior = self.modelo_actual
            modelo_anterior_cargado = self.modelo_cargado
            
            try:
                self.modelo_actual = nuevo_modelo_key
                self.modelo_info = modelo_info
                
                success, msg = self._cargar_modelo_local()
                if success:
                    self.reset_conversation()
                    self.historial.cambiar_modelo(nuevo_modelo_key)
                    self.historial.iniciar_nueva_conversacion()
                    return True, f"✅ Cambiado a {modelo_info['nombre']}\n{modelo_info['descripcion']}"
                else:
                    self.modelo_actual = modelo_anterior
                    self.modelo_info = MODELOS[modelo_anterior]
                    self.modelo_cargado = modelo_anterior_cargado
                    return False, f"❌ {msg}"
            except Exception as e:
                return False, f"❌ Error: {str(e)}"
        else:
            self.modelo_actual = nuevo_modelo_key
            self.modelo_info = modelo_info
            self.reset_conversation()
            self.historial.cambiar_modelo(nuevo_modelo_key)
            self.historial.iniciar_nueva_conversacion()
            return True, f"✅ Cambiado a {modelo_info['nombre']}"
    
    def reset_conversation(self):
        self.memoria = []
        self.historial.iniciar_nueva_conversacion()
        return "🧹 Conversación reiniciada."
    
    def cargar_conversacion(self, conv_id):
        mensajes = self.historial.cargar_conversacion(conv_id)
        if mensajes:
            self.memoria = []
            for msg in mensajes:
                self.memoria.append({"role": "user", "content": msg["usuario"]})
                self.memoria.append({"role": "assistant", "content": msg["bot"]})
            return mensajes
        return None
    
    def get_info_sistema(self):
        return {
            "modelo_actual": self.modelo_info["nombre"],
            "tipo_modelo": self.modelo_info["tipo"],
            "hardware": self.device.upper(),
            "mensajes_totales": len(self.memoria) // 2,
            "modelos_disponibles": len(MODELOS),
            "fecha": "Mayo 2026"
        }

# Inicializar chatbot
chatbot = ChatbotManager()

# ============================================
# RUTAS DE FLASK
# ============================================

@app.route('/')
def index():
    return render_template('chat_completo.html', 
                         modelos=MODELOS,
                         modelo_actual=chatbot.modelo_actual,
                         info_sistema=chatbot.get_info_sistema())

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        response = chatbot.get_response(user_message)
        return jsonify({'response': response, 'status': 'success', 'modelo': chatbot.modelo_info['nombre']})
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/reset', methods=['POST'])
def reset():
    message = chatbot.reset_conversation()
    return jsonify({'message': message, 'status': 'success'})

@app.route('/cambiar_modelo', methods=['POST'])
def cambiar_modelo():
    try:
        data = request.get_json()
        nuevo_modelo = data.get('modelo', '')
        success, message = chatbot.cambiar_modelo(nuevo_modelo)
        if success:
            return jsonify({
                'status': 'success', 
                'message': message, 
                'modelo_info': MODELOS[nuevo_modelo]
            })
        else:
            return jsonify({'status': 'error', 'message': message}), 400
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/estado', methods=['GET'])
def estado():
    info_sistema = chatbot.get_info_sistema()
    info_hardware = get_system_info()
    
    return jsonify({
        **info_sistema,
        "hardware_real": info_hardware
    })

# ============================================
# RUTAS PARA EL HISTORIAL
# ============================================

@app.route('/historial/get', methods=['GET'])
def get_historial():
    conversaciones = chatbot.historial.get_historial()
    return jsonify({
        "status": "success",
        "conversaciones": conversaciones,
        "modelo_actual": chatbot.modelo_actual
    })

@app.route('/historial/cargar', methods=['POST'])
def cargar_conversacion():
    data = request.get_json()
    conv_id = data.get('conv_id', '')
    mensajes = chatbot.cargar_conversacion(conv_id)
    if mensajes:
        return jsonify({"status": "success", "mensajes": mensajes})
    return jsonify({"status": "error", "message": "No encontrada"}), 404

@app.route('/historial/eliminar', methods=['POST'])
def eliminar_conversacion():
    data = request.get_json()
    conv_id = data.get('conv_id', '')
    success = chatbot.historial.eliminar_conversacion(conv_id)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404

@app.route('/historial/eliminar_todo', methods=['POST'])
def eliminar_todo_historial():
    chatbot.historial.eliminar_todo_historial()
    chatbot.historial.iniciar_nueva_conversacion()
    chatbot.memoria = []
    return jsonify({"status": "success"})

@app.route('/historial/exportar', methods=['POST'])
def exportar_historial():
    archivo = chatbot.historial.exportar_csv_finetune()
    return jsonify({
        "status": "success",
        "archivo": archivo,
        "mensaje": f"Exportado a {archivo}"
    })

if __name__ == '__main__':
    import webbrowser
    import threading
    
    def abrir_navegador():
        webbrowser.open('http://localhost:5000')
    
    print("\n" + "="*60)
    print("🤖 CHATBOT FUNCIONANDO - DialoGPT CORREGIDO")
    print("="*60)
    print(f"📍 Abriendo: http://localhost:5000")
    print(f"🎯 Modelo: {chatbot.modelo_info['nombre']}")
    print(f"💻 Hardware: {chatbot.device.upper()}")
    print(f"🧠 RAM Total: {chatbot.system_info['ram_total']} GB")
    print(f"⚡ RAM Disponible: {chatbot.system_info['ram_available']} GB")
    print("="*60)
    print("📜 HISTORIAL: Haz clic en el nombre del modelo para verlo")
    print("="*60 + "\n")
    
    threading.Timer(1.5, abrir_navegador).start()
    app.run(debug=True, port=5000, use_reloader=False)
