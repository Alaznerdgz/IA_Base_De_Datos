# Cliente para conectarse a Google Gemini
import google.generativeai as genai
from config import DEFAULT_SETTINGS
from typing import Generator, List, Optional, Dict, Any
import os


class GeminiClient:
    """Cliente para Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el cliente de Gemini

        Args:
            api_key: Clave de API de Google. 
                  Si no se proporciona, se busca en la variable de entorno GOOGLE_API_KEY
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere GOOGLE_API_KEY en las variables de entorno")
        
        genai.configure(api_key=self.api_key)
        self.model_name = DEFAULT_SETTINGS.get("model", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(self.model_name)

    def generate_response(self, prompt: str, messages: Optional[List[Dict[str, str]]] = None, **kwargs: Dict) -> Generator:
        """
        Genera una respuesta en streaming usando Gemini

        Args:
            prompt: El prompt del sistema/contexto
            messages: Historial de mensajes previos
            **kwargs: Parámetros adicionales (temperature, max_tokens)

        Returns:
            Generator con chunks de la respuesta
        """
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)
        
        # Construir el prompt completo con historial
        full_prompt = prompt + "\n\n"
        
        if messages:
            for message in messages:
                role = "Usuario" if message["role"] == "user" else "Asistente"
                full_prompt += f"{role}: {message['message']}\n\n"

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as ex:
            yield f"Error al generar respuesta: {str(ex)}"


# Alias para mantener compatibilidad con el código existente
OpenAIClient = GeminiClient


def create_llm_provider(provider: str = "gemini") -> Any:
    """
    Crea un cliente LLM basado en el proveedor especificado

    Args:
        provider: El proveedor ('gemini')

    Returns:
        Una instancia del cliente seleccionado
    """
    if provider.lower() == 'gemini':
        return GeminiClient()
    else:
        raise ValueError(f"Proveedor no soportado: {provider}. Usa 'gemini'")