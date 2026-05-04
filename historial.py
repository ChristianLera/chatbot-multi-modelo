# historial.py - Gestión de historial de conversaciones
import json
import os
from datetime import datetime
import csv

HISTORIAL_DIR = "historiales"
os.makedirs(HISTORIAL_DIR, exist_ok=True)

class HistorialManager:
    def __init__(self, modelo_actual):
        self.modelo_actual = modelo_actual
        self.archivo_modelo = os.path.join(HISTORIAL_DIR, f"{modelo_actual}.json")
        self.conversacion_actual_id = None
        self._cargar_historial()
    
    def _cargar_historial(self):
        """Carga el historial del modelo actual desde JSON"""
        if os.path.exists(self.archivo_modelo):
            try:
                with open(self.archivo_modelo, 'r', encoding='utf-8') as f:
                    self.historial = json.load(f)
            except:
                self.historial = {"conversaciones": [], "contador": 0}
        else:
            self.historial = {"conversaciones": [], "contador": 0}
    
    def _guardar_historial(self):
        """Guarda el historial en JSON"""
        with open(self.archivo_modelo, 'w', encoding='utf-8') as f:
            json.dump(self.historial, f, ensure_ascii=False, indent=2)
    
    def cambiar_modelo(self, nuevo_modelo):
        """Cambia al historial de otro modelo"""
        self.modelo_actual = nuevo_modelo
        self.archivo_modelo = os.path.join(HISTORIAL_DIR, f"{nuevo_modelo}.json")
        self._cargar_historial()
    
    def iniciar_nueva_conversacion(self):
        """Crea una nueva conversación y la establece como actual"""
        self.conversacion_actual_id = f"conv_{int(datetime.now().timestamp())}_{self.historial['contador']}"
        self.historial["contador"] += 1
        
        # Crear nueva conversación
        nueva_conv = {
            "id": self.conversacion_actual_id,
            "fecha_inicio": datetime.now().isoformat(),
            "fecha_ultimo_mensaje": datetime.now().isoformat(),
            "modelo": self.modelo_actual,
            "mensajes": [],
            "resumen": "Nueva conversación"
        }
        
        self.historial["conversaciones"].insert(0, nueva_conv)  # Al principio
        self._guardar_historial()
        return self.conversacion_actual_id
    
    def guardar_mensaje(self, user_message, bot_response):
        """Guarda un mensaje en la conversación actual"""
        if not self.conversacion_actual_id:
            self.iniciar_nueva_conversacion()
        
        for conv in self.historial["conversaciones"]:
            if conv["id"] == self.conversacion_actual_id:
                conv["mensajes"].append({
                    "usuario": user_message,
                    "bot": bot_response,
                    "timestamp": datetime.now().isoformat()
                })
                conv["fecha_ultimo_mensaje"] = datetime.now().isoformat()
                # Actualizar resumen con las primeras palabras
                if len(conv["mensajes"]) == 1:
                    preview = user_message[:50] + "..." if len(user_message) > 50 else user_message
                    conv["resumen"] = preview
                break
        
        self._guardar_historial()
    
    def cargar_conversacion(self, conv_id):
        """Carga una conversación específica para seguir hablando"""
        for conv in self.historial["conversaciones"]:
            if conv["id"] == conv_id:
                self.conversacion_actual_id = conv_id
                # Actualizar fecha (la convierto en la actual)
                conv["fecha_ultimo_mensaje"] = datetime.now().isoformat()
                self._guardar_historial()
                return conv["mensajes"]
        return None
    
    def eliminar_conversacion(self, conv_id):
        """Elimina una conversación específica"""
        self.historial["conversaciones"] = [c for c in self.historial["conversaciones"] if c["id"] != conv_id]
        if self.conversacion_actual_id == conv_id:
            self.conversacion_actual_id = None
        self._guardar_historial()
        return True
    
    def eliminar_todo_historial(self):
        """Elimina todo el historial del modelo actual"""
        self.historial = {"conversaciones": [], "contador": 0}
        self.conversacion_actual_id = None
        self._guardar_historial()
    
    def get_historial(self):
        """Devuelve el historial formateado para la interfaz"""
        conversaciones = []
        hoy = datetime.now().date()
        ayer = hoy.replace(day=hoy.day-1) if hoy.day > 1 else hoy
        
        for conv in self.historial["conversaciones"]:
            fecha_conv = datetime.fromisoformat(conv["fecha_inicio"]).date()
            if fecha_conv == hoy:
                categoria = "hoy"
            elif fecha_conv == ayer:
                categoria = "ayer"
            else:
                categoria = "semana_pasada"
            
            conversaciones.append({
                "id": conv["id"],
                "resumen": conv["resumen"],
                "fecha": conv["fecha_inicio"],
                "categoria": categoria,
                "modelo": conv["modelo"],
                "num_mensajes": len(conv["mensajes"])
            })
        
        return conversaciones
    
    def exportar_csv_finetune(self):
        """Exporta el historial a CSV para fine-tuning"""
        archivo_csv = os.path.join(HISTORIAL_DIR, f"{self.modelo_actual}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["prompt", "response", "model", "timestamp"])
            
            for conv in self.historial["conversaciones"]:
                for msg in conv["mensajes"]:
                    writer.writerow([
                        msg["usuario"],
                        msg["bot"],
                        conv["modelo"],
                        msg["timestamp"]
                    ])
        
        return archivo_csv
    
    def obtener_mensajes_actuales(self):
        """Obtiene los mensajes de la conversación actual"""
        if not self.conversacion_actual_id:
            return []
        
        for conv in self.historial["conversaciones"]:
            if conv["id"] == self.conversacion_actual_id:
                return conv["mensajes"]
        return []
