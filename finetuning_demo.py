# finetuning_demo.py - Versión ultra simple para demostración
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset

print("🚀 FINE-TUNING DEMO - Versión Simplificada")

# Datos mínimos para demostrar que sé fine-tuning
datos = [
    {"text": "Usuario: Hola\nAsistente: ¡Hola! ¿Cómo estás?\n"},
    {"text": "Usuario: Bien, ¿y tú?\nAsistente: Muy bien, gracias por preguntar.\n"},
]

dataset = Dataset.from_list(datos)

# Cargar modelo pequeño
model_name = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def tokenize(examples):
    tokens = tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized_dataset = dataset.map(tokenize, batched=True)

# Entrenamiento rápido (solo 1 época para demostración)
training_args = TrainingArguments(
    output_dir="./demo-finetuning",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    logging_steps=1,
    save_steps=50,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

print("🎯 Iniciando fine-tuning de demostración...")
trainer.train()

# Guardar
model.save_pretrained("./mi-modelo-finetuned")
tokenizer.save_pretrained("./mi-modelo-finetuned")

print("✅ Fine-tuning completado. Modelo guardado en ./mi-modelo-finetuned")
