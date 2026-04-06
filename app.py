import streamlit as st
from supabase import create_client
from datetime import date

SUPABASE_URL = "https://cxapnaocpincycjcjoap.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN4YXBuYW9jcGluY3ljamNqb2FwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODg4NTYsImV4cCI6MjA5MTA2NDg1Nn0.wO8Bg0S_o9oGvUwg0loMDGGpRpXZDE0BUEDw9kpx1VI"
OWNER_PASSWORD = "mehendi123"
WHATSAPP_NUMBER = "917041458383"

st.set_page_config(page_title="Vadodara Mehendi", page_icon="🌿", layout="centered")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if "role" not in st.session_state:
    st.session_state.role = None
if "artist_id" not in st.session_state:
    st.session_state.artist_id = None
if "artist_name" not in st.session_state:
    st.session_state.artist_name = None

def logout():
    st.session_state.role = None
    st.session_state.artist_id = None
    st.session_state.artist_name = None

# ── SIDEBAR ──────────────────────────────────────────
if st.session_state.role is None:
    page = st.sidebar.radio("Menu", ["Book Mehendi", "Artist Login", "Admin Login"])
elif st.session_state.role == "artist":
    page = "Artist Dashboard"
    st.sidebar.write(f"Hello, {st.session_state.artist_name}!")
    if st.sidebar.button("Logout"):
        logout(); st.rerun()
elif st.session_state.role == "admin":
    page = "Admin Panel"
    st.sidebar.write("Admin")
    if st.sidebar.button("Logout"):
        logout(); st.rerun()

# ── BOOKING PAGE ─────────────────────────────────────
if page == "Book Mehendi":
    st.title("🌿 Vadodara Mehendi")
    st.subheader("Ghar pe booking karein")

    artists_res = supabase.table("artists").select("id, name, specialty, rate").execute()
    artists = artists_res.data if artists_res.data else []

    if not artists:
        st.warning("Abhi koi artist available nahi hai.")
    else:
        with st.form("booking_form"):
            name = st.text_input("Aapka naam")
            phone = st.text_input("Phone number")
            address = st.text_area("Address")
            booking_date = st.date_input("Date", min_value=date.today())
            artist_options = {a["name"]: a for a in artists}
            selected_name = st.selectbox("Artist chunein",
                [f"{a['name']} — {a['specialty']} (₹{a['rate']})" for a in artists])
            selected_artist = artists[[f"{a['name']} — {a['specialty']} (₹{a['rate']})" for a in artists].index(selected_name)]
            design = st.selectbox("Design type", ["Bridal", "Arabic", "Indo-Arabic", "Simple"])
            submitted = st.form_submit_button("Book Karo")

            if submitted:
                if name and phone and address:
                    supabase.table("bookings").insert({
                        "customer_name": name,
                        "customer_phone": phone,
                        "address": address,
                        "booking_date": str(booking_date),
                        "artist_id": selected_artist["id"],
                        "artist_name": selected_artist["name"],
                        "design_type": design,
                        "status": "pending"
                    }).execute()
                    st.success(f"Booking confirmed! {selected_artist['name']} aayengi {booking_date} ko.")
                    wa_msg = f"Namaskar! Aapki mehendi booking confirm ho gayi.%0AArtist: {selected_artist['name']}%0ADate: {booking_date}%0ADesign: {design}%0AAddress: {address}"
                    wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={wa_msg}"
                    st.markdown(f'WhatsApp pe Confirm Karen', unsafe_allow_html=True)
                else:
                    st.error("Saari details bharein.")

# ── ARTIST LOGIN ──────────────────────────────────────
elif page == "Artist Login":
    st.title("Artist Login")
    with st.form("artist_login"):
        name_input = st.text_input("Aapka naam")
        pass_input = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            res = supabase.table("artists").select("*").eq("name", name_input).eq("password", pass_input).execute()
            if res.data:
                st.session_state.role = "artist"
                st.session_state.artist_id = res.data[0]["id"]
                st.session_state.artist_name = res.data[0]["name"]
                st.rerun()
            else:
                st.error("Galat naam ya password.")

# ── ARTIST DASHBOARD ──────────────────────────────────
elif page == "Artist Dashboard":
    st.title(f"Welcome, {st.session_state.artist_name}!")
    bookings_res = supabase.table("bookings").select("*").eq("artist_id", st.session_state.artist_id).order("booking_date", desc=True).execute()
    bookings = bookings_res.data if bookings_res.data else []

    total = len(bookings)
    pending = len([b for b in bookings if b["status"] == "pending"])
    done = len([b for b in bookings if b["status"] == "done"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total", total)
    col2.metric("Pending", pending)
    col3.metric("Done", done)

    st.divider()
    if not bookings:
        st.info("Abhi koi booking nahi hai.")
    for b in bookings:
        with st.expander(f"{b['booking_date']} — {b['customer_name']} ({b['status'].upper()})"):
            st.write(f"Phone: {b['customer_phone']}")
            st.write(f"Address: {b['address']}")
            st.write(f"Design: {b['design_type']}")
            wa = f"https://wa.me/91{b['customer_phone']}?text=Namaskar+{b['customer_name']}!+Main+{st.session_state.artist_name}+hoon.+Aapki+booking+confirm+hai."
            st.markdown(f'WhatsApp karo', unsafe_allow_html=True)
            if b["status"] == "pending":
                if st.button("Mark as Done", key=b["id"]):
                    supabase.table("bookings").update({"status": "done"}).eq("id", b["id"]).execute()
                    st.rerun()

# ── ADMIN LOGIN ───────────────────────────────────────
elif page == "Admin Login":
    st.title("Admin Login")
    with st.form("admin_login"):
        pwd = st.text_input("Password", type="password")
        btn = st.form_submit_button("Login")
        if btn:
            if pwd == OWNER_PASSWORD:
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("Wrong password.")

# ── ADMIN PANEL ───────────────────────────────────────
elif page == "Admin Panel":
    st.title("Admin Panel")
    tab1, tab2 = st.tabs(["Bookings", "Artists"])

    with tab1:
        all_bookings = supabase.table("bookings").select("*").order("booking_date", desc=True).execute()
        bookings = all_bookings.data if all_bookings.data else []
        total = len(bookings)
        pending = len([b for b in bookings if b["status"] == "pending"])
        done = len([b for b in bookings if b["status"] == "done"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total)
        col2.metric("Pending", pending)
        col3.metric("Done", done)
        st.divider()
        for b in bookings:
            with st.expander(f"{b['booking_date']} — {b['customer_name']} → {b['artist_name']} ({b['status'].upper()})"):
                st.write(f"Phone: {b['customer_phone']}")
                st.write(f"Address: {b['address']}")
                st.write(f"Design: {b['design_type']}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if b["status"] == "pending":
                        if st.button("Mark Done", key=f"done_{b['id']}"):
                            supabase.table("bookings").update({"status": "done"}).eq("id", b["id"]).execute()
                            st.rerun()
                with col_b:
                    if st.button("Delete", key=f"del_{b['id']}"):
                        supabase.table("bookings").delete().eq("id", b["id"]).execute()
                        st.rerun()

    with tab2:
        all_artists = supabase.table("artists").select("*").execute()
        artists = all_artists.data if all_artists.data else []
        for a in artists:
            with st.expander(f"{a['name']} — {a['specialty']} (₹{a['rate']})"):
                st.write(f"Phone: {a['phone']}")
        st.divider()
        st.subheader("Naya artist add karo")
        with st.form("add_artist"):
            n = st.text_input("Naam")
            p = st.text_input("Phone")
            s = st.text_input("Specialty")
            r = st.number_input("Rate (₹)", value=700)
            pw = st.text_input("Password")
            if st.form_submit_button("Add Artist"):
                if n and pw:
                    supabase.table("artists").insert({"name": n, "phone": p, "specialty": s, "rate": int(r), "password": pw}).execute()
                    st.success(f"{n} add ho gaya!")
                    st.rerun()
