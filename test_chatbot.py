import pytest
from chatbot import PersonalChatbot

@pytest.fixture
def chatbot():
    return PersonalChatbot()

def test_inicializacion(chatbot):
    assert chatbot.model is not None
    assert chatbot.tokenizer is not None
    assert chatbot.prompt_inicial.startswith("Eres un asistente")

def test_respuesta_no_vacia(chatbot):
    respuesta = chatbot.get_response("Hola")
    assert isinstance(respuesta, str)
    assert len(respuesta) > 0

def test_respuesta_a_mensaje_vacio(chatbot):
    respuesta = chatbot.get_response("")
    assert respuesta == "Por favor, escribe algo."

def test_historial_se_actualiza(chatbot):
    chatbot.get_response("Hola")
    assert len(chatbot.history) == 2
    chatbot.get_response("¿Cómo estás?")
    assert len(chatbot.history) == 4

def test_reset_conversacion(chatbot):
    chatbot.get_response("Test")
    chatbot.reset_conversation()
    assert len(chatbot.history) == 0
