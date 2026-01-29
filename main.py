import streamlit as st
import requests
from pydantic import BaseModel, ValidationError
from typing import List
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LOGO_FILE = "logo.png"

# Pydantic models for structured output
class AdVariation(BaseModel):
    title: str
    body: str
    type: str

class AdOutput(BaseModel):
    ad_variations: List[AdVariation]
    creative_concepts: List[str]

# Mock data for testing without API keys
MOCK_STRATEGY = """
**Análisis de la Ecuación de Valor:**

• Resultado Deseado: El usuario quiere reducir el tiempo dedicado a redactar copys publicitarios en un 80% mientras mantiene las tasas de conversión
• Probabilidad de Éxito: Alta - respaldado por marcos probados (Ecuación de Valor de Hormozi)
• Retraso de Tiempo: Inmediato - genera copy en menos de 2 minutos vs. 2+ horas de escritura manual
• Esfuerzo y Sacrificio: Mínimo - entrada de formulario simple vs. investigación extensa y pruebas A/B

**Ángulos Estratégicos:**
1. Eficiencia de tiempo (ROI cuantificable en horas ahorradas)
2. Metodología respaldada por marcos (reduce el riesgo percibido)
3. Diferenciador de tono neutral (destaca en un mercado saturado de hype)
4. Salida multiformato (cubre diferentes necesidades de campaña)
"""

MOCK_AD_OUTPUT = {
    "ad_variations": [
        {
            "title": "Generador de Copy Publicitario Reduce el Tiempo de Escritura en 80%",
            "body": "Esta herramienta aplica el marco de la Ecuación de Valor para generar copy publicitario. Los usuarios ingresan detalles del producto y reciben tres variaciones de copy en menos de dos minutos. El sistema usa procesamiento de IA en dos pasos para separar el análisis estratégico de la generación de contenido. No se requiere experiencia en marketing.",
            "type": "Direct"
        },
        {
            "title": "La Mayoría de Equipos de Marketing Gastan 12 Horas Por Semana Escribiendo Copy",
            "body": "El copywriter promedio produce tres variaciones de anuncios en 90 minutos. Esta aplicación genera el mismo resultado en menos de dos minutos automatizando la fase de análisis estratégico. La herramienta separa la aplicación del framework de la ejecución de escritura. El resultado mantiene principios de conversión sin lenguaje promocional.",
            "type": "Problem/Solution"
        },
        {
            "title": "Usado Por Equipos en 47 Empresas Durante el Primer Mes",
            "body": "Este sistema de generación de anuncios procesó 1,840 solicitudes en sus primeros 30 días. Los usuarios reportan un ahorro promedio de 78 minutos por campaña. La herramienta aplica frameworks de conversión establecidos para crear tres enfoques publicitarios distintos. Todo el copy se adhiere a estándares de tono neutral y objetivo.",
            "type": "Social Proof"
        }
    ],
    "creative_concepts": [
        "Visual de pantalla dividida: Lado izquierdo muestra escritorio desordenado con papeles arrugados y tazas de café (copywriting tradicional). Lado derecho muestra escritorio limpio con una laptop mostrando la interfaz de la herramienta. Reloj en el fondo muestra la diferencia de tiempo.",
        "Diseño estilo infografía: Diagrama de Ecuación de Valor con cuatro cuadrantes (Resultado Soñado, Probabilidad, Retraso de Tiempo, Esfuerzo). Cada cuadrante contiene iconos minimalistas y puntos de datos. Paleta de colores neutral: grises, blancos, un color de acento.",
        "Línea de tiempo antes/después: Barra superior muestra proceso tradicional de 90 minutos dividido en fases de investigación, redacción y edición. Barra inferior muestra proceso automatizado de 2 minutos. Tipografía limpia, diseño minimalista, sin rostros humanos.",
        "Comparación en cuadrícula: Cuadrícula 2x3 mostrando anuncios llenos de hype en columna izquierda vs. anuncios neutrales en columna derecha. Marcas X rojas en la izquierda, marcas de verificación verdes en la derecha. Leyenda: 'Mismas métricas de conversión. Enfoque diferente.'"
    ]
}

def call_openrouter_strategy(product: str, audience: str, value_prop: str, api_key: str) -> str:
    """Step 1: Strategic analysis using OpenRouter"""
    try:
        system_prompt = """Eres un estratega de conversión especializado en el marco de la Ecuación de Valor de Alex Hormozi.

Analiza la oferta del usuario usando estos cuatro componentes:
1. Resultado Soñado (lo que quieren)
2. Probabilidad Percibida de Logro (confianza/prueba)
3. Retraso de Tiempo (qué tan rápido obtienen resultados)
4. Esfuerzo y Sacrificio (qué tan fácil es)

Genera un análisis estratégico con viñetas. Enfócate en ángulos de conversión y oportunidades de posicionamiento.
NO escribas copy publicitario. Solo analiza y sugiere ángulos estratégicos."""

        user_prompt = f"""Producto: {product}
Audiencia Objetivo: {audience}
Propuesta de Valor: {value_prop}

Analiza esta oferta usando la Ecuación de Valor. Identifica los ángulos de conversión más fuertes."""

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "openai/gpt-5-nano",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7
            })
        )
        
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        st.error(f"Error de API de OpenRouter: {str(e)}")
        return None

def call_openrouter_writer(product: str, audience: str, value_prop: str, strategy: str, api_key: str) -> AdOutput:
    """Step 2: Content generation using OpenRouter"""
    try:
        system_prompt = """Eres un copywriter especializado en "Copy Invisible" - publicidad que convierte sin hype.

REGLAS DE TONO (OBLIGATORIAS):
- Lenguaje clínico, objetivo, estilo reportero
- SIN signos de exclamación
- SIN palabras hype: "revolucionario," "transforma," "desata," "cambia el juego," "innovador"
- Usa oraciones simples Sujeto-Verbo-Objeto
- Declara hechos y características directamente
- Resalta el resultado deseado mediante la propuesta de valor
- Nunca menciones a Alex Hormozi
- Prefiere voz activa y números concretos
- Evita usar palabras en inglés
- Utiliza palabras que hasta un niño de 15 años pueda entender

Recibirás ángulos estratégicos. Úsalos para escribir tres variaciones de anuncios:
1. Directo (declaración de valor directa con lenguaje que hasta un niño de 15 años pueda entender)
2. Problema/Solución (identifica punto de dolor, presenta solución con lenguaje que hasta un niño de 15 años pueda entender)
3. Prueba Social (usa datos, testimonios o métricas de adopción con lenguaje que hasta un niño de 15 años pueda entender)

También crea 4 conceptos visuales/creativos para diseñadores.

Genera solo JSON válido."""

        user_prompt = f"""ANÁLISIS ESTRATÉGICO:
{strategy}

ENTRADAS DEL USUARIO:
Producto: {product}
Audiencia: {audience}
Propuesta de Valor: {value_prop}

Genera conceptos de anuncios en este formato JSON exacto:
{{
  "ad_variations": [
    {{"title": "...", "body": "...", "type": "Direct"}},
    {{"title": "...", "body": "...", "type": "Problem/Solution"}},
    {{"title": "...", "body": "...", "type": "Social Proof"}}
  ],
  "creative_concepts": [
    "Concepto visual 1...",
    "Concepto visual 2...",
    "Concepto visual 3...",
    "Concepto visual 4..."
  ]
}}"""

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "anthropic/claude-3.7-sonnet",
                "messages": [
                    {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                ],
                "temperature": 0.8
            })
        )
        
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Try to find JSON in the response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        # Parse and validate with Pydantic
        data = json.loads(json_str)
        return AdOutput(**data)
        
    except ValidationError as e:
        st.error(f"Error de validación de salida: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error de API de OpenRouter: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Estratega de Anuncios",
        page_icon="📊",
        layout="wide"
    )
    
    # Get environment variables
    OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Check authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Acceso Requerido")
        st.markdown("Por favor ingresa la clave secreta para acceder a la aplicación.")
        
        user_secret = st.text_input("Clave Secreta", type="password")
        
        if st.button("Acceder", type="primary"):
            if user_secret == SECRET_KEY:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Clave secreta incorrecta")
        
        st.stop()
    
    if os.path.exists(LOGO_FILE):
        st.sidebar.image(LOGO_FILE, width=220)

    # Custom CSS for blue button
    st.markdown("""
        <style>
        .stButton > button[kind="primary"] {
            background-color: #b4bfa5;
            color: white;
            border: 2px solid #b4bfa5;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #8a9470;
            color: white;
            border: 2px solid #8a9470;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'strategy' not in st.session_state:
        st.session_state.strategy = None
    if 'ad_output' not in st.session_state:
        st.session_state.ad_output = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Header with logo
    st.title("Estratega de Anuncios por Estudios E")
    st.markdown("*Copy publicitario de alta conversión usando frameworks de valor. Cero hype.*")
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        
        st.subheader("Llena la información:")
        product = st.text_input("Nombre del Producto", placeholder="ej., Herramienta de Analítica SaaS")
        audience = st.text_area("Audiencia Objetivo", placeholder="ej., Fundadores de SaaS B2B con 10-50 empleados...", height=100)
        value_prop = st.text_area("Propuesta de Valor", placeholder="ej., Reduce la rotación en 30% usando analítica predictiva...", height=100)
        
        st.divider()
        
        generate_button = st.button("🚀 Generar Conceptos de Anuncios", type="primary", use_container_width=True, disabled=st.session_state.processing)
    
    # Main content area
    # Status placeholder in main area
    status_placeholder = st.empty()
    
    if generate_button:
        if not product or not audience or not value_prop:
            status_placeholder.error("Por favor completa todos los detalles del producto")
        elif not OPENROUTER_API_KEY:
            status_placeholder.error("La clave API de OpenRouter no está configurada en el archivo .env")
        else:
            st.session_state.processing = True
            
            status_placeholder.info("⏳ Procesando... Paso 1/2: Analizando estrategia")
            
            strategy = call_openrouter_strategy(product, audience, value_prop, OPENROUTER_API_KEY)
            
            if strategy:
                st.session_state.strategy = strategy
                
                status_placeholder.info("⏳ Procesando... Paso 2/2: Generando copy")
                
                ad_output = call_openrouter_writer(product, audience, value_prop, strategy, OPENROUTER_API_KEY)
                
                if ad_output:
                    st.session_state.ad_output = ad_output
                    status_placeholder.success("✅ Generación completa")
                    import time
                    time.sleep(2)
                    status_placeholder.empty()
                    st.rerun()
                else:
                    status_placeholder.error("Error al generar el copy publicitario")
            else:
                status_placeholder.error("Error al generar la estrategia")
            
            st.session_state.processing = False
    
    if st.session_state.strategy and st.session_state.ad_output:
        
        # Section 1: Strategy (Expander)
        with st.expander("🧠 Detrás de la Lógica (Análisis)", expanded=False):
            st.markdown(st.session_state.strategy)
        
        st.divider()
        
        # Section 2: Ad Copy (Tabs)
        st.subheader("✍️ Variaciones de Anuncios")
        
        ad_data = st.session_state.ad_output
        tabs = st.tabs(["📢 Directo", "🔧 Problema/Solución", "⭐ Prueba Social"])
        
        for idx, (tab, ad) in enumerate(zip(tabs, ad_data.ad_variations)):
            with tab:
                st.markdown(f"**{ad.title}**")
                st.write(ad.body)
                
                # Copy to clipboard using code block trick
                st.code(f"{ad.title}\n\n{ad.body}", language=None)
                st.caption("↑ Selecciona y copia el texto de arriba")
        
        st.divider()
        
        # Section 3: Visual Concepts
        st.subheader("🎨 Conceptos Creativos")
        
        cols = st.columns(2)
        for idx, concept in enumerate(ad_data.creative_concepts):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"**Concepto {idx + 1}**")
                    st.write(concept)
    
    else:
        # Empty state
        if not st.session_state.processing:
            st.info("👈 Configura los detalles de tu producto en la barra lateral y haz clic en 'Generar Conceptos de Anuncios' para comenzar.")
            
            st.markdown("### Cómo Funciona")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
            **Paso 1: Análisis Estratégico**
            - Aplica la Ecuación de Valor
            - Identifica ángulos de conversión
            - Sin copywriting, solo lógica
            """)
            
            with col2:
                st.markdown("""
            **Paso 2: Copy Neutral**
            - Escribe en tono objetivo, estilo limpio
            - Cero hype, cero signos de exclamación
            - Tres variaciones + conceptos visuales
            """)

if __name__ == "__main__":
    main()