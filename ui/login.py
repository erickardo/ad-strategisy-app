import streamlit as st
from services.auth_service import send_otp_email, verify_otp, get_user_data

def show_login_page():
    st.title("🔐 Iniciar Sesión")
    
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False

    if not st.session_state.otp_sent:
        email = st.text_input("Email", placeholder="tu@email.com")
        if st.button("Enviar Código"):
            if get_user_data(email): 
                if send_otp_email(email):
                    st.session_state.otp_sent = True
                    st.session_state.login_email = email
                    st.rerun()
            else:
                st.error("Usuario no encontrado. Verifica que tu email esté en la tabla Creditos.")
    else:
        token = st.text_input("Código OTP", placeholder="123456")
        if st.button("Verificar Código"):
            # We use the email saved in session state from the previous step
            email = st.session_state.login_email
            
            if verify_otp(email, token):
                # 1. Set Authenticated to True
                st.session_state.authenticated = True
                
                # 2. SAVE THE EMAIL GLOBALLY (Crucial for app.py)
                st.session_state.user_email = email
                
                # 3. LOAD USER DATA IMMEDIATELY (Crucial to prevent the loop)
                user_info = get_user_data(email)
                st.session_state.user_data = user_info
                
                # 4. Clean up login variables
                st.session_state.otp_sent = False
                st.session_state.login_email = None
                
                st.success("Inicio de sesión exitoso")
                st.rerun()
            else:
                st.error("Código OTP inválido")