import smtplib
import streamlit as st
from email.message import EmailMessage


def send_welcome_email(receiver_email, name, role):

    try:
        sender_email = st.secrets["email"]["sender"]
        app_password = st.secrets["email"]["password"]

        msg = EmailMessage()

        msg["Subject"] = "Welcome to FoodBridge! 🌱"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        msg.set_content(f"""
Dear {name},

Welcome to FoodBridge! 💚

Thank you for registering as a {role}.

We are happy to have you as part of our mission
to reduce food waste and help communities in need.

With FoodBridge, you can:
- Share surplus food.
- Connect with NGOs.
- Help reduce food waste.
- Make a positive social impact.

Together, let's make every meal count!

Warm regards,
Team FoodBridge
Don't Waste Food. Share Hope. 💚
""")

        # Use secure SMTP connection on port 465
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=20
        ) as server:

            server.login(
                sender_email,
                app_password.replace(" ", "")
            )

            server.send_message(msg)

        return True, "Welcome email sent successfully!"

    except Exception as e:
        return False, f"{type(e).__name__}: {e}"