# app.py - MÍNIMO ABSOLUTO (100% garantizado)
import gradio as gr
from chatbot import PersonalChatbot

bot = PersonalChatbot()

def chat(message, history):
    return bot.get_response(message)

demo = gr.ChatInterface(fn=chat)

demo.launch()
