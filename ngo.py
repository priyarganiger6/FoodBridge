import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_connection


def ngo_dashboard():

    user = st.session_state.get("user")

    # LOGIN CHECK
    if not user:
        st.warning("Please login to access the NGO Dashboard.")
        return

    if user["role"] != "NGO":
        st.error("Only registered NGOs can access this dashboard.")
        return

    st.title("🤝 NGO Dashboard")
    st.write(f"Welcome, {user['name']}! Find food donations and help your community.")
    st.divider()

    # FETCH DONATIONS
    conn = get_connection()

    donations = conn.execute("""
        SELECT d.*, u.name AS donor_name
        FROM donations d
        JOIN users u ON d.donor_id = u.id
        WHERE d.status = 'Available'
        ORDER BY d.id DESC
    """).fetchall()

    # FETCH NGO REQUESTS
    requests = conn.execute("""
        SELECT COUNT(*) AS total
        FROM requests
        WHERE ngo_id = ?
    """, (user["id"],)).fetchone()

    pending = conn.execute("""
        SELECT COUNT(*) AS total
        FROM requests
        WHERE ngo_id = ? AND status = 'Pending'
    """, (user["id"],)).fetchone()

    conn.close()

    # DASHBOARD METRICS
    col1, col2, col3 = st.columns(3)

    col1.metric("Available Donations", len(donations))
    col2.metric("Total Requests", requests["total"])
    col3.metric("Pending Requests", pending["total"])

    st.divider()

    # AVAILABLE FOOD
    st.subheader("🥗 Available Food Donations")

    location = st.text_input(
        "🔍 Search by Location",
        placeholder="Enter location..."
    )

    filtered = [
        dict(donation) for donation in donations
    ]

    if location.strip():
        filtered = [
            d for d in filtered
            if location.lower() in d["location"].lower()
        ]

    if not filtered:
        st.info("No available food donations found.")

    else:

        st.dataframe(
            pd.DataFrame(filtered)[
                [
                    "id",
                    "food_name",
                    "quantity",
                    "location",
                    "pickup_deadline",
                    "donor_name"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("📝 Request Food")

        donation_options = {
            d["id"]: d for d in filtered
        }

        selected_id = st.selectbox(
            "Select Food Donation",
            list(donation_options.keys()),
            format_func=lambda x:
                f"{donation_options[x]['food_name']} - "
                f"{donation_options[x]['quantity']} kg "
                f"({donation_options[x]['location']})"
        )

        selected = donation_options[selected_id]

        st.write("**Food:**", selected["food_name"])
        st.write("**Donor:**", selected["donor_name"])
        st.write("**Location:**", selected["location"])
        st.write("**Pickup Deadline:**", selected["pickup_deadline"])

        with st.form("ngo_request_form"):

            quantity = st.number_input(
                "Required Quantity (kg)",
                min_value=0.1,
                max_value=float(selected["quantity"]),
                value=min(1.0, float(selected["quantity"])),
                step=0.1
            )

            submitted = st.form_submit_button(
                "🤝 Request Food",
                use_container_width=True
            )

            if submitted:

                conn = get_connection()

                try:
                    with conn:

                        result = conn.execute("""
                            UPDATE donations
                            SET status = 'Requested'
                            WHERE id = ? AND status = 'Available'
                        """, (selected_id,))

                        if result.rowcount == 0:
                            st.warning(
                                "This donation is no longer available."
                            )

                        else:
                            conn.execute("""
                                INSERT INTO requests
                                (donation_id, ngo_id,
                                 quantity_requested, requested_at, status)
                                VALUES (?, ?, ?, ?, 'Pending')
                            """, (
                                selected_id,
                                user["id"],
                                quantity,
                                datetime.now().strftime("%Y-%m-%d %H:%M")
                            ))

                            st.success(
                                "Food request submitted successfully! 🎉"
                            )

                            st.rerun()

                finally:
                    conn.close()

    # REQUEST HISTORY
    st.divider()

    st.subheader("📋 My Request History")

    conn = get_connection()

    history = conn.execute("""
        SELECT r.id, d.food_name, r.quantity_requested,
               r.requested_at, r.status, d.location
        FROM requests r
        JOIN donations d ON r.donation_id = d.id
        WHERE r.ngo_id = ?
        ORDER BY r.id DESC
    """, (user["id"],)).fetchall()

    conn.close()

    if history:

        st.dataframe(
            pd.DataFrame([dict(row) for row in history]),
            use_container_width=True,
            hide_index=True
        )

        for request in history:

            if request["status"] == "Pending":
                st.warning(
                    f"Request #{request['id']}: Waiting for approval"
                )

            elif request["status"] == "Approved":
                st.success(
                    f"Request #{request['id']}: Approved!"
                )

            elif request["status"] == "Rejected":
                st.error(
                    f"Request #{request['id']}: Rejected"
                )

    else:
        st.info("You haven't requested any food yet.")

    st.divider()

    st.caption("FoodBridge | Don't Waste Food. Share Hope. 💚")