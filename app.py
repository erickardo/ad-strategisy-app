import streamlit as st
import os
import time
from config import LOGO_FILE
from services.payment_service import create_checkout_session, verify_payment
from services.auth_service import update_credits, get_user_data, add_credits
from services.llm_service import call_strategy, call_writer
from ui.login import show_login_page

# 1. Page Config
st.set_page_config(page_title="Estratega de Anuncios", page_icon="📊", layout="wide")

#st.write("Params:", st.query_params)  # Debug line to see query params

# --- 2. HANDLE PAYMENT RETURN (Success OR Cancel) ---
if "session_id" in st.query_params:
    session_id = st.query_params["session_id"]
    status_param = st.query_params.get("status", "success")
    
    # Ask Stripe: "Who owns this session?"
    payer_email, is_paid = verify_payment(session_id)
    
    if payer_email:
        # 1. ALWAYS RESTORE SESSION (Auto-Login)
        st.session_state.authenticated = True
        st.session_state.user_email = payer_email
        
        # ⚠️ CRITICAL: We fetch data here, but it might still have the OLD balance (0)
        # because the update hasn't happened yet in the lines below.
        st.session_state.user_data = get_user_data(payer_email)
        
        # 2. HANDLE PAYMENT STATUS
        if is_paid:
            # We update the Database
            new_balance = add_credits(payer_email, 10)
            
            # ✅ THE FIX: We must ALSO update the Session State manually
            if new_balance is not None:
                st.session_state.user_data['credits_left'] = new_balance
            
            st.session_state.payment_success = True
            
        elif status_param == "cancelled":
            st.toast("Operación cancelada. No se realizaron cargos.", icon="ℹ️")
        
        # 3. Clean URL
        st.query_params.clear()
        
    else:
        st.error("Sesión inválida o expirada.")

# 2. Session State Initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'strategy' not in st.session_state:
    st.session_state.strategy = None
if 'ad_output' not in st.session_state:
    st.session_state.ad_output = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# 3. Auth Flow
if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# Recovery: If authenticated but user_data is missing, fetch it again.
if st.session_state.authenticated and st.session_state.user_data is None:
    # Try to fetch data using the email stored in session
    if 'user_email' in st.session_state:
        st.session_state.user_data = get_user_data(st.session_state.user_email)
    
    # If it is STILL missing, show an error instead of looping
    if st.session_state.user_data is None:
        st.error(f"⚠️ Error Crítico: No se encontraron datos para el usuario {st.session_state.get('user_email')}. Verifica que el correo exista EXACTAMENTE igual en la tabla 'Creditos' de Supabase.")
        if st.button("Volver al Login"):
            st.session_state.authenticated = False
            st.rerun()
        st.stop() # Stop execution here so we don't crash later


# 4. Custom CSS
st.markdown("""
    <style>
    /* Target regular buttons (Generar Conceptos) */
    .stButton > button[kind="primary"] {
        background-color: #b4bfa5 !important;
        color: white !important;
        border: 2px solid #b4bfa5 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #8a9470 !important;
        color: white !important;
        border: 2px solid #8a9470 !important;
    }

    /* Target LINK buttons (The new Stripe button) */
    .stLinkButton > a[kind="primary"] {
        background-color: #b4bfa5 !important;
        color: white !important;
        border: 2px solid #b4bfa5 !important;
    }
    .stLinkButton > a[kind="primary"]:hover {
        background-color: #8a9470 !important;
        color: white !important;
        border: 2px solid #8a9470 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 5. Sidebar Layout
if os.path.exists(LOGO_FILE):
    st.sidebar.image(LOGO_FILE, width=220)

credits_left = st.session_state.user_data['credits_left']
st.sidebar.metric("Créditos", credits_left)


if st.sidebar.button("💳 Añadir 10 Créditos", type="secondary"):
    with st.sidebar.status("Conectando con Stripe...", expanded=True) as status:
        checkout_url = create_checkout_session(st.session_state.user_email)
        if checkout_url:
            status.update(label="✅ ¡Listo!", state="complete", expanded=True)
            # Instead of auto-redirecting (which freezes), show a clear link
            st.sidebar.link_button("👉 Adquirir ahora en Stripe", checkout_url, type="primary")
        else:
            status.update(label="❌ Error", state="error")
            st.sidebar.error("Revisa los logs para comprobar error.")

st.sidebar.subheader("Llena la información:")
product = st.sidebar.text_input("Nombre del Producto", placeholder="ej., Herramienta de Analítica SaaS")
audience = st.sidebar.text_area("Audiencia Objetivo", placeholder="ej., Fundadores de SaaS...", height=100)
value_prop = st.sidebar.text_area("Propuesta de Valor", placeholder="ej., Reduce la rotación...", height=100)

st.sidebar.divider()

# We initialize the variable to False so the app logic later knows nothing was clicked
generate_button = False 

if credits_left > 0:
    # Only show the button if they have credits
    generate_button = st.sidebar.button(
        "🚀 Generar Conceptos", 
        type="primary", 
        use_container_width=True,
        disabled=st.session_state.processing
    )
else:
    # Optional: Show a message telling them why the button is gone
    st.sidebar.warning("⚠️ Saldo agotado. Añade créditos arriba para continuar.")

# 6. Main Logic (Button Click)
status_placeholder = st.empty()

if generate_button:
    if not product or not audience or not value_prop:
        status_placeholder.error("Por favor completa todos los detalles.")
    else:
        st.session_state.processing = True
        status_placeholder.info("⏳ Procesando... Paso 1/2: Analizando estrategia")
        
        # 1. Call Strategy Service
        strategy = call_strategy(product, audience, value_prop)
        
        if strategy:
            st.session_state.strategy = strategy
            status_placeholder.info("⏳ Procesando... Paso 2/2: Generando copy")
            
            # 2. Call Writer Service
            ad_output = call_writer(product, audience, value_prop, strategy)
            
            if ad_output:
                st.session_state.ad_output = ad_output
                
                # 3. Update Credits in Database
                new_credits = update_credits(st.session_state.user_email, st.session_state.user_data['credits_left'])
                st.session_state.user_data['credits_left'] = new_credits
                
                status_placeholder.success("✅ Generación completa")
                time.sleep(1)
                status_placeholder.empty()
                st.rerun() # Rerun to refresh the UI with new data
            else:
                status_placeholder.error("Error al generar el copy.")
        else:
            status_placeholder.error("Error al generar la estrategia.")
        
        st.session_state.processing = False

# 7. Main Content Display
st.title("Estratega de Anuncios")
st.markdown("*Copy publicitario de alta conversión usando frameworks de valor. Cero hype.*")
st.divider()

if st.session_state.get('payment_success', False):
    st.balloons()
    st.toast("¡10 créditos agregados exitosamente!", icon="💰")
    st.session_state.payment_success = False # Reset flag so it doesn't show again on refresh

if st.session_state.strategy and st.session_state.ad_output:
    
    # --- A. Strategy Section (Expander) ---
    with st.expander("🧠 Detrás de la Lógica (Análisis)", expanded=False):
        st.markdown(st.session_state.strategy)
    
    st.divider()
    
    # --- B. Ad Copy Section (Tabs) ---
    st.subheader("✍️ Variaciones de Anuncios")
    
    ad_data = st.session_state.ad_output
    tabs = st.tabs(["📢 Directo", "🔧 Problema/Solución", "⭐ Prueba Social"])
    
    # We iterate through tabs and data simultaneously
    for idx, (tab, ad) in enumerate(zip(tabs, ad_data.ad_variations)):
        with tab:
            st.markdown(f"**{ad.title}**")
            st.write(ad.body)
            
            # Code block for easy copying
            st.code(f"{ad.title}\n\n{ad.body}", language=None)
            st.caption("↑ Selecciona y copia el texto de arriba")
    
    st.divider()
    
    # --- C. Creative Concepts (2 Column Grid) ---
    st.subheader("🎨 Conceptos Creativos")
    
    cols = st.columns(2)
    for idx, concept in enumerate(ad_data.creative_concepts):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"**Concepto {idx + 1}**")
                st.write(concept)

else:
    # --- D. Empty State / Instructions ---
    if not st.session_state.processing:
        st.info("👈 Configura los detalles de tu producto en la barra lateral y haz clic en 'Generar' para comenzar.")
        
        st.markdown("### Cómo Funciona")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
        **Paso 1: Análisis Estratégico**
        - Aplica la Ecuación de Valor
        - Identifica ángulos de conversión
        - Solo analiza tu oferta
        """)
        
        with col2:
            st.markdown("""
        **Paso 2: Copy Objetivo**
        - Escribe anuncios objetivamente, estilo limpio
        - Cero hype, cero signos de exclamación
        - Tres variaciones + conceptos visuales
        """)
