# chatbot.py - COMPATIBLE CON LOS MEJORES MODELOS GRATUITOS
from huggingface_hub import login
import os

# Cargar token desde variable de entorno
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    login(token=hf_token)

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ============================================
# 👇 CAMBIA AQUÍ EL MODELO QUE QUIERES PROBAR
# ============================================

# OPCIÓN 1 - MISTRAL (recomendado, muy conversacional)
MODELO = "mistralai/Mistral-7B-Instruct-v0.3"

# OPCIÓN 2 - QWEN (mejor español)
# MODELO = "Qwen/Qwen2.5-7B-Instruct"

# OPCIÓN 3 - LLAMA 3.1 (el más potente)
# MODELO = "meta-llama/Llama-3.1-8B-Instruct"

# ============================================

class PersonalChatbot:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🚀 Cargando {MODELO}")
        print(f"💾 Memoria disponible: 64GB RAM")
        
        self.tokenizer = AutoTokenizer.from_pretrained(MODELO)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODELO,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.memoria = []
        print(f"✅ Modelo listo. ¡A conversar!")

    def get_response(self, user_message):
        if not user_message.strip():
            return "Por favor, escribe algo."
        
        # Prompt adaptado para conversación natural
        if "mistral" in MODELO.lower():
            # Formato Mistral (el más natural)
            prompt = f"<s>[INST] Eres un asistente conversacional amigable. Responde en español de forma natural y útil.\n\nUsuario: {user_message} [/INST]"
        
        elif "qwen" in MODELO.lower():
            # Formato Qwen (excelente español)
            prompt = f"<|im_start|>system\nEres un asistente conversacional amigable. Responde en español de forma natural y útil.<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"
        
        elif "llama" in MODELO.lower():
            # Formato Llama
            prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nEres un asistente conversacional amigable. Responde en español de forma natural y útil.<|eot_id|>\n<|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        else:
            prompt = f"Usuario: {user_message}\nAsistente:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=250,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        response = response.strip()
        
        if not response:
            response = "No entendí bien. ¿Puedes reformular?"
        
        self.memoria.append(user_message)
        self.memoria.append(response)
        
        return response

    def reset_conversation(self):
        self.memoria = []
        return "🗑️ Memoria borrada. Empezamos de nuevo."


if __name__ == "__main__":
    # Prueba rápida
    bot = PersonalChatbot()
    print("\n🧪 Prueba de conversación:")
    print(f"Usuario: Hola ¿cómo estás?")
    print(f"Asistente: {bot.get_response('Hola ¿cómo estás?')}")
