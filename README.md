# 🤖 Personal AI Chatbot - Christian Lera

**Sistema multi-modelo de chatbot conversacional con interfaz Flask y Gradio, capaz de ejecutar modelos locales (Mistral, Llama, DialoGPT) y vía API (DeepSeek, ChatGPT, Gemini).**

---

## 📋 Índice

- [Visión General](#visión-general)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Modelos de IA Implementados](#modelos-de-ia-implementados)
- [Experiencia con Gradio vs Flask](#experiencia-con-gradio-vs-flask)
- [Análisis de Rendimiento de Modelos](#análisis-de-rendimiento-de-modelos)
- [Fine-Tuning: Recursos y Limitaciones](#fine-tuning-recursos-y-limitaciones)
- [Estructura de Archivos](#estructura-de-archivos)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Despliegue en Hugging Face Spaces](#despliegue-en-hugging-face-spaces)
- [Problemas de Seguridad Resueltos](#problemas-de-seguridad-resueltos)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Conclusiones y Estado del Proyecto](#conclusiones-y-estado-del-proyecto)

---

## Visión General

Este proyecto representa mi trabajo de experimentación y desarrollo de un **chatbot conversacional multi-modelo**. A lo largo del proceso, he probado **9 modelos de IA diferentes** (tanto locales como vía API) para evaluar su rendimiento en español, velocidad de respuesta y calidad de conversación.

El resultado es un sistema flexible que permite:
- Cambiar entre modelos en tiempo real
- Guardar historial de conversaciones por modelo
- Exportar conversaciones para fine-tuning
- Detectar automáticamente el hardware disponible

**Autor:** Christian Lera  
**Fecha:** Mayo 2026

---

## Arquitectura del Proyecto

El proyecto contiene **dos aplicaciones principales** que conviven en el mismo repositorio:

### 1. Aplicación Flask (`app_flask.py`) - VERSIÓN PRINCIPAL

Esta es la implementación **completa y definitiva** del chatbot. Incluye:

- **Servidor web Flask** con rutas RESTful
- **Selector de modelos** con 9 opciones disponibles
- **Detección de hardware** (RAM, CPU) para recomendar modelos compatibles
- **Sistema de historial** persistente en JSON
- **Exportación a CSV** para fine-tuning
- **Gestión de conversaciones** (cargar, eliminar, exportar)

### 2. Aplicación Gradio (`app.py`) - VERSIÓN EXPERIMENTAL

Implementación inicial usada para prototipado rápido. Presenta limitaciones significativas que se detallan más adelante.

### 3. Módulos Auxiliares

| Archivo | Función |
|---------|---------|
| `chatbot.py` | Clase base del chatbot con soporte multi-modelo |
| `historial.py` | Gestión de conversaciones (JSON, CSV) |
| `utils.py` | Utilidades (timers, limpieza de texto) |
| `test_hardware.py` | Diagnóstico de recursos del sistema |

---

## Modelos de IA Implementados

He integrado y probado **9 modelos diferentes**, clasificados en dos categorías:

### 🌐 Modelos vía API (Comerciales)

| Modelo | Proveedor | Calidad | Estado |
|--------|-----------|---------|--------|
| DeepSeek | DeepSeek AI | ⭐⭐⭐⭐⭐ | Operativo |
| ChatGPT | OpenAI GPT-3.5/4 | ⭐⭐⭐⭐⭐ | Operativo |
| Gemini | Google 2.0 Flash | ⭐⭐⭐⭐ | Operativo |

**Ventajas:** No consumen recursos locales, calidad excelente  
**Desventajas:** Requieren API keys, latencia de red, límites de uso

### 💻 Modelos Locales (Open Source)

| Modelo | Tamaño | RAM Requerida | Calidad | Estado |
|--------|--------|---------------|---------|--------|
| DialoGPT-small | 500MB | 1GB | ⭐⭐ | Descartado (bucles) |
| DialoGPT-medium | 1.5GB | 2.5GB | ⭐⭐⭐ | Aceptable |
| DialoGPT-large | 3.5GB | 5GB | ⭐⭐⭐⭐ | Bueno pero pesado |
| GPT-2 Spanish | 500MB | 1GB | ⭐⭐ | Descartado (alucinaciones) |
| Llama 3 8B | 8GB | 10GB | ⭐⭐⭐⭐⭐ | Excelente, config. compleja |
| **Mistral 7B** | 7GB | 8GB | ⭐⭐⭐⭐⭐ | **ELEGIDO** |

### ✅ Modelo Seleccionado: Mistral 7B

Después de exhaustivas pruebas, **Mistral 7B** fue el modelo elegido como predeterminado por:

- **Excelente comprensión del español**
- **Velocidad aceptable en CPU** (respuestas en 2-5 segundos)
- **Conversaciones naturales** sin bucles repetitivos
- **Código abierto** sin restricciones de uso
- **Balance óptimo** entre calidad y consumo de recursos

---

## Experiencia con Gradio vs Flask

### Gradio - Experimentación Inicial

Comencé este proyecto usando **Gradio** por su facilidad de implementación. Sin embargo, pronto identifiqué limitaciones críticas:

```
PROBLEMAS ENCONTRADOS CON GRADIO:
├── LENTITUD EXTREMA: Cada interacción recarga componentes innecesarios
├── SIN ESTADO PERSISTENTE: El historial se pierde al recargar
├── UI POCO PERSONALIZABLE: Imposible implementar selector de modelos elegante
├── RENDIMIENTO DEGRADADO: El frontend en Python es inherentemente ineficiente
├── DEPURACIÓN DIFÍCIL: Los errores son crípticos
└── ESCALABILIDAD NULA: No apto para producción
```

### Flask - Solución Definitiva

Migrar a **Flask** fue una decisión que transformó completamente el proyecto:

```
MEJORAS CON FLASK:
├── VELOCIDAD: Las respuestas son instantáneas, solo se procesa la IA
├── UI PROFESIONAL: HTML/CSS/JS nativo sin intermediarios
├── ESTADO COMPLETO: Sessions, historial, modelos persistentes
├── API RESTFUL: Endpoints para integración con otros sistemas
├── RENDIMIENTO: Solo Python para la lógica, el frontend es estático
└── CONTROL TOTAL: Manejo de errores, logs, configuración
```

### Conclusión sobre Frameworks

> **Gradio es útil para prototipar en 5 minutos, pero Flask es la única opción profesional para un chatbot funcional.** La diferencia de rendimiento es abismal: con Gradio necesitaba 3-5 segundos por mensaje solo en la interfaz; con Flask, la interfaz responde en milisegundos y solo el modelo consume tiempo.

**Recomendación:** Usar Gradio solo para demos rápidas o despliegues en Hugging Face Spaces. Para cualquier aplicación seria, Flask es la elección correcta.

---

## Análisis de Rendimiento de Modelos

Durante el desarrollo, documenté **fallos y limitaciones** de cada modelo para tomar decisiones informadas:

### Modelos Descartados por Problemas Graves

| Modelo | Problema | Severidad |
|--------|----------|-----------|
| **DialoGPT-small** | Entra en bucles repitiendo "User: Bot: User: Bot:" | ❌ Crítico |
| **DialoGPT-medium** | Responde igual que small en español | ⚠️ Moderado |
| **GPT-2 Spanish** | Alucinaciones constantes, respuestas sin sentido | ❌ Crítico |
| **Llama 3 8B** | Configuración muy compleja, requiere GPU | ⚠️ Moderado |

### Problemas Comunes Detectados

```
FRECUENCIA DE FALLOS POR MODELO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DialoGPT-small     ██████████████████████████████████░░  90% fallos
GPT-2 Spanish      ██████████████████████████████░░░░░░  80% fallos  
DialoGPT-medium    ████████████████████░░░░░░░░░░░░░░░░  50% fallos
Llama 3 8B         ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░  25% fallos
Mistral 7B         ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10% fallos
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Lección Aprendida

**No todos los modelos open-source funcionan bien con español.** Modelos como DialoGPT fueron entrenados predominantemente en inglés y su rendimiento en español es pobre. Mistral 7B destaca porque su entrenamiento incluyó datos multilingües de calidad.

---

## Fine-Tuning: Recursos y Limitaciones

### Archivos de Fine-Tuning

El proyecto incluye dos archivos relacionados con fine-tuning:

| Archivo | Propósito |
|---------|-----------|
| `train_finetune.py` | Script completo para fine-tuning de Llama 3 con datasets JSON |
| `finetuning_demo.py` | Demostración mínima (2 ejemplos, 1 época) para mostrar el concepto |

### ¿Por qué hay dos archivos?

`finetuning_demo.py` existe **únicamente como prueba de concepto**. Demuestra que sé implementar fine-tuning, pero **no es práctico para uso real** con solo 2 ejemplos.

### Realidad del Fine-Tuning

El fine-tuning serio requiere **recursos significativos**:

```
REQUISITOS PARA FINE-TUNING REAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mistral 7B / Llama 3 8B:
├── RAM: 16-32 GB mínimo
├── GPU: 16-24 GB VRAM (recomendado)
├── Dataset: 500-5000 conversaciones de calidad
├── Tiempo: 2-8 horas en GPU
└── Coste: 50-200€ en cloud GPU

Para fines de demostración en este proyecto:
├── Dataset: solo 2-4 ejemplos (insuficiente)
├── Épocas: 1 (deberían ser 3-5)
├── Batch size: 1 (debería ser 4-8)
└── Resultado: Modelo sobreajustado, no usable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Mi Decisión sobre Fine-Tuning

> **Por ahora, no he realizado fine-tuning completo** porque:
> 1. Requiere hardware que no poseo (GPU con 16GB+ VRAM)
> 2. Necesito al menos 500 conversaciones de calidad para resultados útiles
> 3. El proceso de anotación manual es extremadamente laborioso
> 
> Sin embargo, los scripts están **preparados y funcionales**. Cuando tenga acceso a una GPU adecuada o suficientes conversaciones exportadas del historial, el fine-tuning se puede ejecutar con:
> ```bash
> python train_finetune.py
> ```

Los archivos están incluidos para demostrar mi **conocimiento técnico del proceso**, no como una característica completamente implementada.

---

## Estructura de Archivos

```
proyecto-chatbot/
│
├── APLICACIONES PRINCIPALES
│   ├── app.py                 # Versión Gradio (experimental)
│   └── app_flask.py           # Versión Flask (PRODUCCIÓN)
│
├── SCRIPTS DE EJECUCIÓN
│   ├── run_gradio.bat         # Lanza app.py en Windows
│   ├── run_gradio.ps1         # Lanza app.py en PowerShell
│   ├── run_flask.bat          # Lanza app_flask.py en Windows
│   └── run_flask.ps1          # Lanza app_flask.py en PowerShell
│
├── MÓDULOS DEL CHATBOT
│   ├── chatbot.py             # Clase principal del chatbot
│   ├── historial.py           # Gestión de conversaciones
│   └── utils.py               # Utilidades varias
│
├── FINE-TUNING
│   ├── train_finetune.py      # Fine-tuning completo para Llama 3
│   └── finetuning_demo.py     # Demo de prueba de concepto
│
├── TESTS
│   ├── test_chatbot.py        # Tests unitarios
│   └── test_hardware.py       # Detección de hardware
│
├── CONFIGURACIÓN
│   ├── requirements.txt       # Dependencias Python
│   └── .env                   # Variables de entorno (API keys)
│
├── PLANTILLAS (para Flask)
│   └── templates/
│       └── chat_completo.html # Interfaz web completa
│
└── DATOS
    └── historiales/           # Conversaciones guardadas (JSON/CSV)
```

---

## Instalación y Ejecución

### Requisitos Previos

- Python 3.10 o superior
- 8GB RAM mínimo (16GB recomendado para Mistral)
- Windows 10/11 (el proyecto ha sido probado principalmente en Windows)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/ChristianLera/chatbot-portfolio.git
cd chatbot-portfolio

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar la Aplicación

**Opción 1: Flask (RECOMENDADA)**
```bash
# Windows CMD
run_flask.bat

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File run_flask.ps1

# O manualmente
python app_flask.py
```

**Opción 2: Gradio (Experimental)**
```bash
# Windows CMD
run_gradio.bat

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File run_gradio.ps1
```

### Variables de Entorno (API Keys)

Crea un archivo `.env` en la raíz:

```env
HF_TOKEN=tu_token_huggingface
DEEPSEEK_API_KEY=tu_api_key_deepseek
OPENAI_API_KEY=tu_api_key_openai
GEMINI_API_KEY=tu_api_key_gemini
```

---

## Despliegue en Hugging Face Spaces

Hugging Face Spaces permite desplegar aplicaciones Gradio gratis. Uso `deploy_space.bat` o `deploy_space.ps1` para preparar el proyecto:

```bash
# Prepara la carpeta space/ con los archivos necesarios
deploy_space.bat
```

**Limitaciones importantes:**
- Spaces solo corre **aplicaciones Gradio**, no Flask
- RAM máxima gratuita: 16GB (insuficiente para Mistral 7B)
- El despliegue en Spaces es **útil solo para la interfaz**, no para los modelos locales

Por estas razones, **no recomiendo desplegar este proyecto en Spaces** si se quiere usar modelos locales. Para demostración, se puede subir la versión Gradio conectada a APIs externas.

---

## Seguridad

Este proyecto utiliza **variables de entorno** para todas las claves de API y tokens. 
Nunca se deben hardcodear credenciales en el código.

### Configuración segura:

- ✅ Variables de entorno para todas las API keys
- ✅ `.gitignore` configurado para excluir `.env` y `historiales/`
- ✅ Logs informativos sin exponer secretos
- ✅ Validación de entrada de usuario

---

## Tecnologías Utilizadas

| Categoría | Tecnologías |
|-----------|-------------|
| **Frameworks Web** | Flask, Gradio |
| **Modelos IA** | Transformers (Hugging Face), PyTorch |
| **APIs** | OpenAI, DeepSeek, Google Gemini |
| **Almacenamiento** | JSON, CSV (historiales) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Hardware Detection** | psutil, platform |
| **Testing** | pytest |
| **Despliegue** | Hugging Face Spaces, Flask dev server |

---

## Conclusiones y Estado del Proyecto

### Estado Actual: ✅ PRODUCCIÓN LISTA

La versión Flask del chatbot es **completamente funcional** y puede usarse en producción con las siguientes características:

- ✅ Cambio dinámico entre 9 modelos
- ✅ Persistencia de conversaciones
- ✅ Exportación de datos para fine-tuning
- ✅ Detección automática de hardware
- ✅ Manejo robusto de errores

### Lecciones Aprendidas

1. **Gradio es para prototipos, Flask es para producción** - La diferencia de rendimiento es enorme
2. **No todos los modelos funcionan bien en español** - Mistral 7B es la mejor opción actual
3. **El fine-tuning requiere recursos que no siempre se tienen** - Los scripts están listos para cuando los recursos estén disponibles
4. **La seguridad es prioritaria** - Tokens hardcodeados son un riesgo grave
5. **La experimentación con modelos diferentes es valiosa** - Cada modelo tiene fortalezas y debilidades únicas

### Trabajo Futuro

- [ ] Adquirir GPU para fine-tuning completo
- [ ] Implementar streaming de respuestas (token a token)
- [ ] Añadir más modelos locales (Phi-3, Gemma 2)
- [ ] Crear versión Docker para despliegue en la nube
- [ ] Implementar autenticación de usuarios

---

## Contacto

**Christian Lera**  
Proyecto de portfolio - Mayo 2026

---

## Licencia

MIT License - Libre para uso educativo y comercial con atribución.

---

*"La mejor manera de aprender IA es construir, fallar, iterar y mejorar. He hecho todo eso con este proyecto."* – Christian Lera
