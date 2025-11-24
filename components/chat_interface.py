import streamlit as st
from dotenv import load_dotenv
from utils.api_client import OpenAIClient
from config import DEFAULT_SETTINGS


load_dotenv()

class ChatInterface:
   
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
        
        # Estado para almacenar el esquema de la base de datos
        if 'database_schema' not in st.session_state:
            st.session_state.database_schema = ""
    
    def handle_user_input(self):
        """ Maneja la entrada del usuario y genera una respuesta SQL """
        if prompt := st.chat_input("Describe qué consulta SQL necesitas..."):
            # Mostramos el mensaje del usuario
            with st.chat_message("user"):
                st.markdown(prompt)

            # Añadir al historial
            self.add_message("user", prompt)

            temperature = st.session_state.temperature
            max_tokens = st.session_state.max_tokens

            # Generar respuesta
            if st.session_state.llm_client:
                with st.chat_message("assistant"):
                    st.caption(f"Usando: temperature={temperature} - max_tokens={max_tokens}")
                    with st.spinner("Generando query SQL..."):
                        # Crear el contexto del prompt SQL
                        context = self._create_sql_context(prompt)
                        response = st.session_state.llm_client.generate_response(
                            context,
                            st.session_state.messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        
                        full_response = ""
                        response_widget = st.empty()
                        for chunk in response:
                            if chunk:
                                full_response += chunk
                                response_widget.markdown(f"```sql\n{full_response}\n```")
                        
                        self.add_message("assistant", full_response)
            else:
                with st.chat_message("assistant"):
                    error_msg = "❌ No se pudo conectar con el servidor de IA. Verifica la configuración"
                    st.error(error_msg)
                    self.add_message("assistant", error_msg)
    
    def _create_sql_context(self, user_prompt: str) -> str:
        """
        Crea el contexto para generar queries SQL

        Args:
            user_prompt: La pregunta del usuario

        Returns:
            prompt completo con el contexto SQL
        """
        
        schema_info = ""
        if st.session_state.database_schema:
            schema_info = f"\n\nESQUEMA DE LA BASE DE DATOS:\n{st.session_state.database_schema}\n"

        context = f"""
            Eres SQL Query Assistant, un asistente especializado en generar consultas SQL.

            REGLAS IMPORTANTES:
            1. Responde ÚNICAMENTE con código SQL válido
            2. NO incluyas explicaciones en lenguaje natural
            3. NO uses prefijos como "Aquí está la query:" o similares
            4. Genera queries optimizadas y siguiendo mejores prácticas
            5. Si necesitas comentarios, usa sintaxis SQL (-- comentario)
            6. Usa nombres de tablas y columnas apropiados según el contexto
            7. Considera índices y rendimiento en queries complejas
            {schema_info}
            Solicitud del usuario: {user_prompt}

            Responde solo con la query SQL:
            las tablas y coumnas son:
            Tabla: authors
            au_id
            au_lname
            au_fname
            phone
            address
            city
            state
            zip
            contract,
            id:varchar(11)
            varchar(40)
            varchar(20)
            char(12)
            varchar(40)
            varchar(20)
            char(2)
            char(5)
            bit

            Tabla: employees
            emp_id
            fname
            minit
            lname
            job_id
            job_lvl
            pub_id
            hire_date,
            empid:char(9)
            varchar(20)
            char(1)
            varchar(30)
            smallint
            tinyint
            char(4)
            datetime

            tabla: jobs
            job_id
            job_desc
            min_lvl
            max_lvl,
            smallint
            varchar(50)
            tinyint
            tinyint

            tabla: pub_info
            pub_id
            logo
            pr_info,
            char(4)
            image
            text

            tabla: publishers
            pub_id
            pub_name
            city
            state
            country,
            char(4)
            varchar(40)
            varchar(20)
            char(2)
            varchar(30)

            tabla: roysched
            title_id
            lorange
            hirange
            royalty,
            tid:varchar(6)
            int
            int
            int

            tabla: sales
            stor_id
            ord_num
            ord_date
            qty
            payterms
            title_id,
            char(4)
            varchar(20)
            datetime
            smallint
            varchar(12)
            tid:varchar(6)

            tabla: stores
            stor_id
            stor_name
            stor_address
            city
            state
            zip,
            char(4)
            varchar(40)
            varchar(40)
            varchar(20)
            char(2)
            char(5)

            tabla: titleauthors
            au_id
            title_id
            au_ord
            royaltyper,
            id:varchar(11)
            tid:varchar(6)
            tinyint
            int

            tabla: titles
            title_id
            title
            type
            pub_id
            price
            advance
            royalty
            ytd_sales
            notes
            pubdate,
            tid:varchar(6)
            varchar(80)
            char(12)
            char(4)
            money
            money
            int
            int
            varchar(200)
            datetime

            """
        return context
    
    def add_message(self, role: str, msg: str):
        """ Añade el mensaje al historial """
        st.session_state.messages.append({
            "role": role,
            "message": msg
        })

    def display_messages(self):
        """ Muestra todos los mensajes del chat """
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    # Mostrar respuestas SQL con formato de código
                    st.markdown(f"```sql\n{message['message']}\n```")
                else:
                    st.markdown(message["message"])
    
    def display_chat_stats(self):
        """ Muestra estadísticas en la barra de estado """
        st.sidebar.markdown("### 📊 Estadísticas del chat")
        st.sidebar.metric("Mensajes Totales", len(st.session_state.messages))

        if st.session_state.messages:
            user_messages = len([m for m in st.session_state.messages if m['role'] == "user"])
            st.sidebar.metric("Consultas Realizadas", user_messages)
            
            sql_queries = len([m for m in st.session_state.messages if m['role'] == "assistant"])
            st.sidebar.metric("Queries SQL Generadas", sql_queries)

    def configure_database_schema(self):
        """ Permite configurar el esquema de la base de datos """
        with st.sidebar.expander("🗄️ Configurar Esquema de BD"):
            schema_input = st.text_area(
                "Define el esquema de tu base de datos",
                value=st.session_state.database_schema,
                placeholder="""Ejemplo:
            Tabla: usuarios (id, nombre, email, fecha_registro)
            Tabla: productos (id, nombre, precio, categoria_id)
            Tabla: categorias (id, nombre)""",
                height=150
            )
            
            if st.button("Guardar Esquema"):
                st.session_state.database_schema = schema_input
                st.success("✅ Esquema guardado correctamente")

    @staticmethod
    def export_chat():
        """
        Exporta el historial del chat como texto con queries SQL

        Returns:
            El historial del chat formateado
        """
        if not st.session_state.messages:
            return "No hay mensajes para exportar"
        
        export_text = "# Historial de Queries SQL - SQL Assistant\n\n"

        for i, message in enumerate(st.session_state.messages, 1):
            if message["role"] == "user":
                role = "👤 Usuario"
                export_text += f"## Consulta {i} - {role}\n\n"
                export_text += f"{message['message']}\n\n"
            else:
                role = "🤖 SQL Assistant"
                export_text += f"## Query {i} - {role}\n\n"
                export_text += f"```sql\n{message['message']}\n```\n\n"
            
            export_text += "---\n\n"
        
        return export_text
    
    @staticmethod
    def clear_chat():
        """ Limpia el historial del chat """
        st.session_state.messages = []
        st.rerun()
    
    def copy_last_query(self):
        """ Muestra botón para copiar la última query generada """
        if st.session_state.messages:
            last_assistant_msg = None
            for message in reversed(st.session_state.messages):
                if message["role"] == "assistant":
                    last_assistant_msg = message["message"]
                    break
            
            if last_assistant_msg:
                st.sidebar.markdown("### 📋 Última Query")
                st.sidebar.code(last_assistant_msg, language="sql")
                
                if st.sidebar.button("📄 Copiar al portapapeles"):
                    st.sidebar.info("Query lista para copiar desde el área de código")