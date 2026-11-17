import streamlit as st
import sqlite3
from datetime import date, datetime, time
from database import get_connection


def donor_dashboard():

    st.title("🍱 Food Donor Dashboard")
    st.write("Share surplus food and help someone in need.")

    st.divider()

    st.subheader("➕ Add a Food Donation")

    # Get logged-in donor ID
    user = st.session_state.get("user")

    if not user:
        st.warning("Please login first to donate food.")
        return

    with st.form("donation_form"):

        food_name = st.text_input("Food Name")

        quantity = st.number_input(
            "Quantity (kg)",
            min_value=0.1,
            step=0.5
        )

        location = st.text_input("Pickup Location")

        pickup_date = st.date_input(
            "Pickup Deadline Date",
            min_value=date.today()
        )

        pickup_time = st.time_input(
            "Pickup Deadline Time",
            value=time(18, 0)
        )

        submitted = st.form_submit_button(
            "Submit Donation",
            use_container_width=True
        )

        if submitted:

            if not food_name.strip() or not location.strip():
                st.warning("Please enter food name and location.")

            else:

                deadline = datetime.combine(
                    pickup_date, pickup_time
                ).isoformat(timespec="minutes")

                try:
                    conn = get_connection()

                    conn.execute("""
                        INSERT INTO donations
                        (donor_id, food_name, quantity,
                         location, pickup_deadline)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        user["id"],
                        food_name.strip(),
                        quantity,
                        location.strip(),
                        deadline
                    ))

                    conn.commit()
                    conn.close()

                    st.success("Food donation added successfully! 🎉")
                    st.rerun()

                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")

    st.divider()

    # DISPLAY DONATIONS

    st.subheader("📦 Your Food Donations")

    try:
        conn = get_connection()

        donations = conn.execute("""
            SELECT * FROM donations
            WHERE donor_id = ?
            ORDER BY id DESC
        """, (user["id"],)).fetchall()

        conn.close()

        if donations:

            for donation in donations:

                with st.container(border=True):

                    st.markdown(
                        f"### 🍱 {donation['food_name']}"
                    )

                    col1, col2 = st.columns(2)

                    col1.write(
                        f"**Quantity:** {donation['quantity']} kg"
                    )

                    col2.write(
                        f"**Status:** {donation['status']}"
                    )

                    st.write(
                        f"📍 Location: {donation['location']}"
                    )

                    st.write(
                        f"⏰ Pickup Deadline: "
                        f"{donation['pickup_deadline']}"
                    )

        else:
            st.info("No donations added yet.")

    except sqlite3.Error as e:
        st.error(f"Could not load donations: {e}")

    st.divider()

    st.subheader("📊 Donation Summary")

    try:
        conn = get_connection()

        summary = conn.execute("""
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(quantity), 0) AS quantity
            FROM donations
            WHERE donor_id = ?
        """, (user["id"],)).fetchone()

        conn.close()

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Donations",
            summary["total"]
        )

        col2.metric(
            "Food Donated",
            f"{summary['quantity']:.1f} kg"
        )

    except sqlite3.Error as e:
        st.error(f"Could not load summary: {e}")