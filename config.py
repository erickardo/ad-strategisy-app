import streamlit as st
from supabase import create_client, Client
import stripe


# Constants
LOGO_FILE = "logo.png"
OPENROUTER_API_KEY = st.secrets["OPEN_ROUTER_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
STRIPE_API_KEY = st.secrets["STRIPE_API_KEY"]
STRIPE_PRICE_ID = st.secrets["STRIPE_PRICE_ID"]
BASE_URL = st.secrets["BASE_URL"]

# Initialize Supabase (Singleton pattern)
def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials missing in .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

#Initialize Stripe
stripe.api_key = STRIPE_API_KEY