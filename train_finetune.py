# train_finetune.py - Fine-tuning para Llama 3
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
import json

class FineTuneLlama3:
    def __init__(self, model_name="meta-llama/Meta-Llama-3-8B"):
        print("🚀 Preparando fine-tuning para Llama 3...")
        
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Configurar token de padding
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
    def preparar_dataset(self, conversations_file="conversations.json"):
        """
        Prepara tus datos para fine-tuning
        Formato esperado del JSON:
        [
            {
                "messages": [
                    {"role": "user", "content": "Hola"},
                    {"role": "assistant", "content": "¡Hola! ¿Cómo estás?"}
                ]
            }
        ]
        """
        with open(conversations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Formatear conversaciones para entrenamiento
        formatted_texts = []
        for conv in data:
            formatted = self.tokenizer.apply_chat_template(
                conv["messages"],
                tokenize=False,
                add_generation_prompt=False
            )
            formatted_texts.append({"text": formatted})
        
        dataset = Dataset.from_list(formatted_texts)
        
        # Tokenizar dataset
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=512
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset
    
    def entrenar(self, dataset, output_dir="./llama3-finetuned", epochs=3):
        """Ejecuta el fine-tuning"""
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=1,  # Batch pequeño por RAM
            gradient_accumulation_steps=4,
            warmup_steps=100,
            logging_steps=10,
            save_steps=100,
            evaluation_strategy="no",
            save_strategy="steps",
            learning_rate=2e-5,
            fp16=True,
            push_to_hub=False,
            report_to="none"
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            tokenizer=self.tokenizer,
        )
        
        print("🎯 Comenzando fine-tuning...")
        trainer.train()
        
        # Guardar modelo fine-tuneado
        model_path = "./llama3-custom"
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        print(f"✅ Modelo guardado en {model_path}")
        
        return model_path

# Ejemplo de uso
if __name__ == "__main__":
    # Crear dataset de ejemplo (especializado en tu dominio)
    ejemplo_dataset = [
        {
            "messages": [
                {"role": "user", "content": "¿Qué es Python?"},
                {"role": "assistant", "content": "Python es un lenguaje de programación de alto nivel, interpretado y de código abierto. Es conocido por su sintaxis clara y legible, lo que lo hace ideal para principiantes y expertos."}
            ]
        },
        {
            "messages": [
                {"role": "user", "content": "¿Cómo crear un chatbot?"},
                {"role": "assistant", "content": "Para crear un chatbot, necesitas: 1) Un modelo preentrenado como Llama 3, 2) Transformers de Hugging Face, 3) Una interfaz como Gradio. El proceso incluye cargar el modelo, implementar historial de conversación y desplegar la aplicación."}
            ]
        }
    ]
    
    with open("conversations.json", "w", encoding='utf-8') as f:
        json.dump(ejemplo_dataset, f, ensure_ascii=False, indent=2)
    
    # Ejecutar fine-tuning
    finetuner = FineTuneLlama3()
    dataset = finetuner.preparar_dataset("conversations.json")
    finetuner.entrenar(dataset, epochs=3)
