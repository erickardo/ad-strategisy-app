import requests
import json
import streamlit as st
from pydantic import ValidationError
from models import AdOutput
from config import OPENROUTER_API_KEY

api_key = OPENROUTER_API_KEY

def call_strategy(product: str, audience: str, value_prop: str) -> str:
    """Step 1: Strategic analysis using OpenRouter"""
    try:
        system_prompt = """Eres un estratega de conversión especializado en el marco de la Ecuación de Valor de Alex Hormozi.

Analiza la oferta del usuario usando estos cuatro componentes:
1. Resultado Soñado (lo que quieren)
2. Probabilidad Percibida de Logro (confianza/prueba)
3. Retraso de Tiempo (qué tan rápido obtienen resultados)
4. Esfuerzo y Sacrificio (qué tan fácil es)
5. Nunca menciones a Alex Hormozi en la respuesta.

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


def call_writer(product: str, audience: str, value_prop: str, strategy: str) -> AdOutput:
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
- Nunca menciones a Alex Hormozi en la respuesta.
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
