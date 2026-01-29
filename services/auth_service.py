import streamlit as st
from config import supabase

def send_otp_email(email: str) -> bool:
    try:
        supabase.auth.sign_in_with_otp({
            "email": email,
            ##"options": {"should_create_user": False}
        })
        return True
    except Exception as e:
        st.error(f"Error sending OTP: {str(e)}")
        return False

def verify_otp(email: str, token: str) -> bool:
    try:
        response = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "email"
        })
        if response.user:
            st.session_state.user_id = response.user.id
            st.session_state.user_email = email
            return True
        return False
    except Exception as e:
        st.error(f"Error verifying OTP: {str(e)}")
        return False

def get_user_data(email: str):
    try:
        # Check if table is 'users' or 'Creditos' (based on your code snippet)
        response = supabase.table("Creditos").select("*").eq("email", email).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching user data: {str(e)}")
        return None

def update_credits(email: str, current_credits: int):
    try:
        new_credits = max(0, current_credits - 1)
        supabase.table("Creditos").update({"credits_left": new_credits}).eq("email", email).execute()
        return new_credits
    except Exception as e:
        st.error(f"Error updating credits: {str(e)}")
        return current_credits
    
def add_credits(email: str, amount: int):
    """Adds credits to the existing balance"""
    try:
        # 1. Get current credits
        current_data = get_user_data(email)
        if not current_data:
            return False
            
        current_balance = current_data['credits_left']
        new_balance = current_balance + amount
        
        # 2. Update database
        supabase.table("Creditos").update({"credits_left": new_balance}).eq("email", email).execute()
        return new_balance
    except Exception as e:
        st.error(f"Error adding credits: {str(e)}")
        return None