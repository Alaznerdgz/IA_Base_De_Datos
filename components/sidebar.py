from datetime import datetime
import streamlit as st
from utils.api_client import OpenAIClient
from .chat_interface import ChatInterface
from config import DEFAULT_SETTINGS


def create_sidebar():
    """ Crea y configura el sidebar de la aplicación """

    with st.sidebar:
        st.title("🚀 MartAI")
        st.markdown("*Tu asistente de SQL*")
        st.divider()

        st.markdown("### ⚙️ Configuración")

        st.divider

        st.markdown("### 💬 Controles del Chat")

        if st.button("🗑️ Limpiar Chat", use_container_width=True):
            ChatInterface.clear_chat()

        # Exportar chat a texto
        if st.session_state.get('messages'):
            st.markdown("### 📋 Exportar Chat a Markdown")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            filename = st.text_input(
                "Nombre del archivo:",
                value= f"devmentor_chat_{timestamp}",
                help="Sin extensión",
            )

            if st.button(
                "💾 Descargar Chat",
                use_container_width=True,
                ):
                export_text = ChatInterface.export_chat()

                if not filename.endswith(".md"):
                    filename = f"{filename}.md"
                
                st.download_button(
                    "💾 Confirmar Descarga",
                    data=export_text,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
        
        st.divider()
        with st.expander("🔧 Configuración Avanzada"):
            temperature = st.slider(
                "Creatividad (Temperatura)",
                min_value = 0.0,
                max_value = 2.0,
                value=DEFAULT_SETTINGS["temperature"],
                help="Cuanto más alto, más creativo"
            )

            max_tokens = st.slider(
                "Máximo de Tokens",
                min_value = 100,
                max_value = 20000,
                value = DEFAULT_SETTINGS["max_tokens"],
                step = 100,
                help = "Longitud de la respuesta"
            )

            #Guardamos los parámetros en session_state (accesible desde ChatInterface también)
            st.session_state.temperature = temperature
            st.session_state.max_tokens = max_tokens