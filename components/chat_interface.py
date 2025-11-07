#Maneja toda la lógica del chat (mensajes, respuestas, historial)
import streamlit as st
from utils import OpenAIClient
from dotenv import load_dotenv


load_dotenv()

class ChatInterface:
    """ Gestiona la interfaz del chat """

    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """ Inicializar el estado de sesión """
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'llm_client' not in st.session_state:
            try:
                st.session_state.llm_client = OpenAIClient()
            except ValueError:
                st.session_state.llm_client = None
    
    def handle_user_input(self):
        """ Maneja la entrada del usuario y genera una respuesta """
        if prompt := st.chat_input("Escribe tu consulta sobre desarrollo..."):
            # Mostramos el mensaje del usuario
            #st.markdown(prompt)
            with st.chat_message("user"):
                st.markdown(prompt)

            # Añadir al historial
            self.add_message("user",prompt)

            temperature = st.session_state.temperature
            max_tokens = st.session_state.max_tokens

            # Generar respuesta
            if st.session_state.llm_client:
                    with st.chat_message("assistant"):
                        st.caption(f"Usando: temperature={temperature} - max_tokens={max_tokens}")
                        with st.spinner("Pensando..."):
                            # Crear el contexto del prompt
                            context = self._create_context(prompt)
                            response = st.session_state.llm_client.generate_response(
                                context,
                                st.session_state.messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            )
                            #st.write_stream(response)
                            full_response = ""
                            response_widget = st.empty()
                            for chunk in response:
                                if chunk:
                                    full_response += chunk
                                    response_widget.markdown(full_response)
                            self.add_message("assistant", full_response)
            else:
                with st.chat_message("assistant"):
                    error_msg="❌ No se pudo conectar con el servidor de IA. Verifica la configuración"
                    st.error(error_msg)
                    self.add_message("assistant", error_msg)
    

    def _create_context(self, user_prompt: str) -> str:
        """
        Crea el contexto para traducir preguntas en lenguaje natural a SQL sobre la base de datos Pubs.

        Args:
            user_prompt: La pregunta del usuario

        Returns:
            Prompt completo con el contexto
        """

        context = f"""
        Eres MartAI, un asistente experto en bases de datos SQL Server.
        Tu tarea es traducir preguntas en lenguaje natural a consultas SQL válidas y precisas
        sobre la base de datos "Pubs", sin ejecutar el código.

        Esquema de la base de datos Pubs:
        - publishers(pub_id, pub_name, city, state, country)
        - authors(au_id, au_lname, au_fname, phone, address, city, state, zip, contract)
        - titles(title_id, title, type, pub_id, price, advance, royalty, ytd_sales, notes, pubdate)
        - titleauthor(au_id, title_id, au_ord, royaltyper)
        - stores(stor_id, stor_name, stor_address, city, state, zip)
        - sales(stor_id, ord_num, ord_date, qty, payterms, title_id)

        Reglas:
        - Devuelve solo consultas SQL en formato texto.
        - No ejecutes el SQL.
        - Usa SELECT únicamente.
        - Si no se especifica límite, aplica TOP 100 por defecto.
        - No incluyas instrucciones peligrosas como DROP, DELETE, UPDATE, INSERT, ALTER, EXEC.

        Pregunta del usuario: {user_prompt}

        Devuelve solo la consulta SQL correspondiente, sin explicaciones adicionales.
        """
        return context
    
    def add_message(self, role:str, msg:str):
        """ Añade el mensaje al historial """
        st.session_state.messages.append({
            "role":role,
            "message":msg
        })


    def display_messages(self):
        """ Muestra todos los mensajes del chat """
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["message"])

    
    def display_chat_stats(self):
        """ Muestra estadísticas en la barra de estado """
        st.sidebar.markdown("### 📊 Estadísticas del chat")
        st.sidebar.metric("Mensajes Totales", len(st.session_state.messages))

        if st.session_state.messages:
            user_messages = len([m for m in st.session_state.messages if m['role'] == "user"])
            st.sidebar.metric("Preguntas Realizadas", user_messages)

    @staticmethod
    def export_chat():
        """

        Exporta el historial del chat como texto
        
        Returns:
            El historial ddel chat formateado

        """

        if not st.session_state.messages:
            return "No hay mensajes para exportar"
        
        export_text = "# Historial de Chat - MartAI\n\n"

        for i, message in enumerate(st.session_state.messages):
            role = "👤 Usuario" if message["role"] == "user" else " 🕵️‍♀️ MartAI"
            export_text += f"## Mensaje {i} - {role}\n\n"
            export_text += f"{message['message']}\n\n"
            export_text += f"---\n\n"
        
        return export_text
    
    @staticmethod
    def clear_chat():
        st.session_state.messages = []
        st.rerun()

