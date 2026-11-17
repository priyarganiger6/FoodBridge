import streamlit as st
from email_service import send_welcome_email
from ngo import ngo_dashboard
from database import get_connection
from donar import donor_dashboard
from database import init_db, register_user, login_user

# Initialize database
init_db()

# =====================================
# FOODBRIDGE MAIN APPLICATION
# =====================================

st.set_page_config(
    page_title="FoodBridge",
    page_icon="🥗",
    layout="wide"
)

# =====================================
# LOAD CSS FILE
# =====================================

try:
    with open("style.css", "r", encoding="utf-8") as file:
        css = file.read()

    st.markdown(
        "<style>" + css + "</style>",
        unsafe_allow_html=True
    )

except FileNotFoundError:
    st.warning("CSS file not found. Please create style.css.")

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("🥗 FoodBridge")

st.sidebar.caption("Smart Food Donation Platform")

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Login",
        "Register",
        "Donor Dashboard",
        "NGO Dashboard",
        "About Us"
    ]
)
if "user" in st.session_state:
    st.sidebar.success(
        "Logged in as " + st.session_state["user"]["name"]
    )

    if st.sidebar.button("Logout"):
        del st.session_state["user"]
        st.rerun()
st.sidebar.divider()

st.sidebar.success("Don't Waste Food. Share Hope.")

# =====================================
# HOME PAGE
# =====================================

# =====================================
# HOME PAGE - MODERN FOODBRIDGE
# =====================================

if page == "Home":

    st.markdown("""
    <h1>👋 Welcome to FoodBridge!</h1>
    <p style="font-size:18px;">
    Connect, Share and Make a Difference 💚
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # IMPACT STATISTICS

    st.markdown("## 🌍 Our Impact")

    col1, col2, col3, col4 = st.columns(4)

    # GET LIVE STATISTICS FROM DATABASE

    conn = get_connection()

    total_food = conn.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM donations
        WHERE status != 'Cancelled'
    """).fetchone()[0]

    total_donations = conn.execute("""
        SELECT COUNT(*)
        FROM donations
        WHERE status != 'Cancelled'
    """).fetchone()[0]

    total_ngos = conn.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'NGO'
    """).fetchone()[0]

    conn.close()

    stats = [
        ("🍱", f"{total_food:g} kg", "Food Donated", "#e4f6df"),
        ("👥", str(total_donations), "Total Donations", "#e2efff"),
        ("🌿", "Coming Soon", "CO₂ Reduced", "#fff0dc"),
        ("🤝", str(total_ngos), "Partner NGOs", "#f0e6ff")
    ]
    

    for col, item in zip(
        [col1, col2, col3, col4], stats
    ):
        with col:
            st.markdown(f"""
            <div class="stat-card"
                 style="background:{item[3]};">
                <div style="font-size:30px;">
                    {item[0]}
                </div>
                <h2>{item[1]}</h2>
                <p>{item[2]}</p>
            </div>
            """, unsafe_allow_html=True)

    # HERO BANNER

    st.markdown("""
    <div class="hero-banner">
        <h1>Every Meal Matters! 🌱</h1>
        <h3>Share Food, Spread Happiness.</h3>
        <p style="font-size:17px;">
        Join FoodBridge and help surplus food reach
        people who need it.
        </p>
        <h3>♻️ Reduce Waste | ❤️ Share Hope</h3>
    </div>
    """, unsafe_allow_html=True)

    # RECENT ACTIVITY AND QUICK ACTIONS

    col1, col2 = st.columns([1.2, 1])

    with col1:

        st.markdown("""
        <div class="dashboard-panel">
            <h2>⚡ Recent Activity</h2>
            <hr>
            <p>🍱 Food donations will appear here.</p>
            <hr>
            <p>🤝 NGO connections will appear here.</p>
            <hr>
            <p>❤️ Community impact will appear here.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="dashboard-panel">
            <h2>🚀 Quick Actions</h2>
            <hr>
            <div class="action-card">
                🍱 Donate Food
            </div>
            <div class="action-card">
                🔍 Find Available Food
            </div>
            <div class="action-card">
                🤝 Connect with NGOs
            </div>
            <div class="action-card">
                📊 Track Your Impact
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # HOW IT WORKS

    st.markdown("## 💚 How FoodBridge Works")

    col1, col2, col3 = st.columns(3)

    features = [
        ("🍱", "Donate Food",
         "Restaurants share their surplus food."),
        ("🤝", "Connect with NGOs",
         "NGOs discover available food donations."),
        ("❤️", "Make an Impact",
         "Food reaches people who need it.")
    ]

    for col, feature in zip(
        [col1, col2, col3], features
    ):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <h2>{feature[0]}</h2>
                <h3>{feature[1]}</h3>
                <p>{feature[2]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    st.success(
        "🌍 Together, We Can Make Every Meal Count!"
    )

    st.markdown("""
    <div style="text-align:center; padding:15px;">
        <p>FoodBridge | Don't Waste Food. Share Hope. 💚</p>
    </div>
    """, unsafe_allow_html=True)
# =====================================
# LOGIN PAGE
# =====================================

elif page == "Login":

    st.title("Welcome Back!")
    st.subheader("Login to FoodBridge")

    with st.form("login_form"):

        email = st.text_input("Email Address")

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button("Login")

        if submitted:

            user = login_user(email, password)

            if user:

                st.session_state["user"] = user

                st.success(
                    "Welcome " + user["name"] + "!"
                )

                st.write("Account Type:", user["role"])

            else:
                st.error("Invalid email or password.")
# =====================================
# REGISTRATION PAGE
# =====================================

# =====================================
# REGISTRATION PAGE
# =====================================

elif page == "Register":

    st.title("Join FoodBridge 💚")
    st.subheader("Create Your Account")

    with st.form("register_form"):

        name = st.text_input("Full Name")

        email = st.text_input("Email Address")

        role = st.selectbox(
            "Select Account Type",
            ["Food Donor", "NGO"]
        )

        location = st.text_input("Location")

        password = st.text_input(
            "Create Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Register",
            use_container_width=True
        )

        if submitted:

            if not name or not email or not location or not password:
                st.error("Please fill in all the fields.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            else:

                success, message = register_user(
                    name,
                    email,
                    password,
                    role,
                    location
                )

                if success:

                    st.success(message)

                    # SEND WELCOME EMAIL

                    email_sent, email_message = send_welcome_email(
                        email,
                        name,
                        role
                    )

                    if email_sent:

                        st.success(
                            "📧 Welcome email sent successfully to "
                            + email
                        )

                    else:

                        st.warning(
                            "Account created, but email could not be sent: "
                            + email_message
                        )

                else:

                    st.error(message)


# =====================================
# DONOR DASHBOARD
# =====================================

elif page == "Donor Dashboard":

    donor_dashboard()


# =====================================
# NGO DASHBOARD
# =====================================

elif page == "NGO Dashboard":

    ngo_dashboard()

# =====================================
# ABOUT US PAGE
# =====================================

# =====================================
# ABOUT US PAGE
# =====================================

elif page == "About Us":

    st.title("About FoodBridge 💚")

    st.subheader("Turning Surplus Food into Hope")

    st.write(
        "FoodBridge is a smart food donation platform "
        "that connects hotels, restaurants and catering "
        "services with NGOs."
    )

    st.write(
        "Our objective is to reduce avoidable food waste "
        "and help surplus edible food reach communities in need."
    )

    st.divider()

    st.header("🎯 Our Mission")

    st.success(
        "To reduce food waste and connect food donors "
        "with charitable organisations."
    )

    st.header("🌍 Our Vision")

    st.info(
        "A world where surplus edible food is shared "
        "instead of wasted."
    )

    st.header("💚 Our Core Values")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ♻️ Sustainability")
        st.write("Reducing food waste.")

    with col2:
        st.markdown("### ❤️ Compassion")
        st.write("Helping communities.")

    with col3:
        st.markdown("### 🤝 Collaboration")
        st.write("Connecting donors and NGOs.")

    st.divider()

    st.caption(
        "FoodBridge | Don't Waste Food. Share Hope. 💚"
    )