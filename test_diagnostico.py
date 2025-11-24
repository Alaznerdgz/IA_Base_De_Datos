"""
Script de diagnóstico para detectar problemas con la configuración
"""
import os
import sys

print("="*60)
print("DIAGNÓSTICO DE CONFIGURACIÓN")
print("="*60)

# 1. Verificar archivos
print("\n1. VERIFICANDO ARCHIVOS:")
print(f"   Directorio actual: {os.getcwd()}")
print(f"   ¿Existe .env? {os.path.exists('.env')}")
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        content = f.read()
        print(f"   Contenido del .env (primeras líneas):")
        for line in content.split('\n')[:5]:
            if 'API_KEY' in line:
                # Ocultar la key
                parts = line.split('=')
                if len(parts) == 2:
                    print(f"   {parts[0]}={parts[1][:10]}...")
            else:
                print(f"   {line}")

# 2. Cargar dotenv
print("\n2. CARGANDO VARIABLES DE ENTORNO:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✅ dotenv cargado correctamente")
except ImportError:
    print("   ❌ python-dotenv no instalado. Ejecuta: pip install python-dotenv")
    sys.exit(1)

# 3. Verificar API Key
print("\n3. VERIFICANDO API KEY:")
google_key = os.getenv("GOOGLE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if google_key:
    print(f"   ✅ GOOGLE_API_KEY encontrada: {google_key[:15]}...{google_key[-4:]}")
    print(f"   Longitud: {len(google_key)} caracteres")
    if not google_key.startswith('AIza'):
        print("   ⚠️  ADVERTENCIA: Las keys de Google suelen empezar con 'AIza'")
else:
    print("   ❌ GOOGLE_API_KEY no encontrada")

if openai_key:
    print(f"   ℹ️  OPENAI_API_KEY también encontrada (no la necesitas para Gemini)")

# 4. Verificar instalación de google-generativeai
print("\n4. VERIFICANDO PAQUETE GOOGLE:")
try:
    import google.generativeai as genai
    print("   ✅ google-generativeai instalado")
    print(f"   Versión: {genai.__version__ if hasattr(genai, '__version__') else 'desconocida'}")
except ImportError:
    print("   ❌ google-generativeai NO instalado")
    print("   Ejecuta: pip install google-generativeai")
    sys.exit(1)

# 5. Probar conexión con Gemini
print("\n5. PROBANDO CONEXIÓN CON GEMINI:")
if google_key:
    try:
        genai.configure(api_key=google_key)
        print("   ✅ API configurada")
        
        # Listar modelos disponibles
        print("   Probando listar modelos...")
        models = genai.list_models()
        print(f"   ✅ Conexión exitosa. Modelos disponibles:")
        for model in models:
            if 'gemini' in model.name.lower():
                print(f"      - {model.name}")
        
        # Probar generación
        print("\n   Probando generación de contenido...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Di solo 'Hola'")
        print(f"   ✅ Respuesta recibida: {response.text}")
        
    except Exception as e:
        print(f"   ❌ Error al conectar con Gemini:")
        print(f"   {type(e).__name__}: {str(e)}")
        if "API_KEY" in str(e).upper() or "401" in str(e) or "403" in str(e):
            print("\n   💡 La API key parece inválida. Verifica:")
            print("   1. Crea una nueva en: https://aistudio.google.com/app/apikey")
            print("   2. Copia EXACTAMENTE la key (sin espacios)")
            print("   3. Pégala en el .env como: GOOGLE_API_KEY=tu_key_aqui")
else:
    print("   ⏭️  Saltando prueba (no hay API key)")

# 6. Verificar config.py
print("\n6. VERIFICANDO CONFIG.PY:")
try:
    from config import DEFAULT_SETTINGS
    print(f"   ✅ config.py cargado")
    print(f"   Configuración:")
    for key, value in DEFAULT_SETTINGS.items():
        print(f"      {key}: {value}")
except Exception as e:
    print(f"   ❌ Error cargando config.py: {e}")

# 7. Probar utils.api_client
print("\n7. PROBANDO utils/api_client.py:")
try:
    from utils.api_client import OpenAIClient
    print("   ✅ Módulo importado correctamente")
    
    print("   Intentando crear cliente...")
    client = OpenAIClient()
    print("   ✅ Cliente creado exitosamente")
    
    print("   Probando generate_response...")
    response = client.generate_response(
        "Di solo 'test'", 
        [], 
        temperature=0.7, 
        max_tokens=100
    )
    result = ""
    for chunk in response:
        result += chunk
    print(f"   ✅ Respuesta: {result[:50]}...")
    
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    print("\n   Stack trace completo:")
    traceback.print_exc()

print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETADO")
print("="*60)
