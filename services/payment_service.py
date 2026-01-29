import stripe
import streamlit as st
from config import STRIPE_PRICE_ID, BASE_URL

def create_checkout_session(user_email: str):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': STRIPE_PRICE_ID, 'quantity': 1}],
            mode='payment',
            customer_email=user_email,
            client_reference_id=user_email,
            success_url=f"{BASE_URL}/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/?session_id={{CHECKOUT_SESSION_ID}}&status=cancelled",
        )
        return checkout_session.url
    except Exception as e:
        st.error(f"Error creating stripe session: {str(e)}")
        return None

def verify_payment(session_id: str):
    """
    Retrieves session details from Stripe.
    Returns a tuple: (email, is_paid)
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        email = session.client_reference_id
        is_paid = (session.payment_status == 'paid')
        return email, is_paid
    except Exception as e:
        st.error(f"Error verifying payment: {str(e)}")
        return None, False