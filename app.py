import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Vadodara Mehendi", page_icon="🌿", layout="centered")

if "bookings" not in st.session_state:
    st.session_state.bookings = []

ARTISTS = [
    {"name": "Aamena", "specialty": "Bridal / Arabic", "rate": 700},
    {"name": "Fatima", "specialty": "Indo-Arabic", "rate": 600},
    {"name": "Zoya", "specialty": "Arabic / Glitter", "rate": 650},
]

page = st.sidebar.radio("Menu", ["Book Mehendi", "Artist List", "Admin Panel"])

if page == "Book Mehendi":
    st.title("🌿 Vadodara Mehendi")
    st.subheader("Ghar pe booking karein")

    with st.form("booking_form"):
        name = st.text_input("Aapka naam")
        phone = st.text_input("Phone number")
        address = st.text_area("Address")
        booking_date = st.date_input("Date", min_value=date.today())
        artist_names = [a["name"] for a in ARTISTS]
        selected = st.selectbox("Artist chunein", artist_names)
        design = st.selectbox("Design type", ["Bridal", "Arabic", "Indo-Arabic", "Simple"])
        submitted = st.form_submit_button("Book Karo")

        if submitted:
            if name and phone and address:
                booking = {
                    "naam": name, "phone": phone,
                    "address": address, "date": str(booking_date),
                    "artist": selected, "design": design
                }
                st.session_state.bookings.append(booking)
                st.success(f"Booking confirmed! {selected} aayengi {booking_date} ko.")
                st.info("Confirmation ke liye 07041458383 par WhatsApp karein.")
            else:
                st.error("Saari details bharein.")

elif page == "Artist List":
    st.title("Hamare Artists")
    for a in ARTISTS:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{a['name']}**")
                st.caption(a["specialty"])
            with col2:
                st.markdown(f"₹{a['rate']}/visit")
            st.divider()

elif page == "Admin Panel":
    st.title("Admin Panel")
    password = st.text_input("Password", type="password")
    if password == "mehendi123":
        st.success("Welcome!")
        if st.session_state.bookings:
            df = pd.DataFrame(st.session_state.bookings)
            st.dataframe(df, use_container_width=True)
            st.metric("Total Bookings", len(st.session_state.bookings))
        else:
            st.info("Abhi koi booking nahi hai.")
    elif password:
        st.error("Wrong password")
