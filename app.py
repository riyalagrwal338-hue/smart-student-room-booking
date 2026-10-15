import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

st.set_page_config(page_title="Smart Campus Booking", page_icon="🏫", layout="wide")

def h(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

if "bookings" not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["id", "Student", "Email", "Room", "Date", "Start", "End", "Seats", "Status"])

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Room Details with Capacities, Facilities & Descriptions
ROOM_DETAILS = {
    "Classroom B": {
        "capacity": 50,
        "facilities": "Projector, AC, Smart Whiteboard, High-speed Wi-Fi",
        "description": "Ek spacious aur modern classroom jo lectures, workshops aur bade group study sessions ke liye best hai."
    },
    "Discussion Room": {
        "capacity": 10,
        "facilities": "Round Table, LED Display, AC, Whiteboard",
        "description": "Small team meetings, project discussions aur brainstorming sessions ke liye ek cozy aur quiet room."
    },
    "Auditorium": {
        "capacity": 150,
        "facilities": "Advanced Sound System, Stage, Projector, Central AC, Mic Setup",
        "description": "Bade events, seminars, cultural programs aur college functions ke liye bada hall."
    }
}

st.markdown("## 🏫 Smart Campus Reservation")
st.markdown("Find suitable rooms • prevent double bookings • manage approvals")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📖 Book a Room", "🏢 Room Directory & Preview", "📅 Bookings", "🔒 Admin"])

# --- TAB 1: BOOK A ROOM ---
with tab1:
    st.subheader("Book a Room on Campus")
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            room = st.selectbox("Select Room", list(ROOM_DETAILS.keys()))
            
            # Selected room ki live details dikhane ke liye
            st.info(f"💡 **Selected Room Info:**\n- **Capacity:** {ROOM_DETAILS[room]['capacity']} Seats\n- **Facilities:** {ROOM_DETAILS[room]['facilities']}\n- **Overview:** {ROOM_DETAILS[room]['description']}")
            
        with col2:
            date = st.date_input("Date", value=datetime.today())
            start = st.time_input("Start Time", value=datetime.strptime("10:00", "%H:%M").time())
            end = st.time_input("End Time", value=datetime.strptime("11:00", "%H:%M").time())
            seats = st.number_input("Seats Needed", min_value=1, value=5)
            
        submit_btn = st.form_submit_button("Submit Booking Request")
        
        if submit_btn:
            if not name or not email:
                st.error("Kripya apna naam aur email bharein!")
            elif start >= end:
                st.error("❌ Start time, End time se pehle honi chahiye!")
            elif seats > ROOM_DETAILS[room]["capacity"]:
                st.error(f"❌ Capacity limit exceeded! '{room}' ki maximum capacity sirf {ROOM_DETAILS[room]['capacity']} seats ki hai.")
            else:
                # Time strings ko pehle hi define kar liya gaya hai taaki NameError na aaye
                date_str = str(date)
                start_str = start.strftime("%H:%M")
                end_str = end.strftime("%H:%M")
                
                df = st.session_state.bookings
                overlap_found = False
                
                # Double Booking & Time Overlap Prevention Check
                if not df.empty:
                    for _, r in df.iterrows():
                        if r["Room"] == room and str(r["Date"]) == date_str:
                            if r["Status"] in ["Approved", "None"]:
                                existing_start = r["Start"]
                                existing_end = r["End"]
                                
                                # Time overlap condition check
                                if not (end_str <= existing_start or start_str >= existing_end):
                                    overlap_found = True
                                    break
                
                if overlap_found:
                    st.error(f"❌ Double Booking Error: '{room}' is selected date aur time slot ke liye pehle se booked ya pending hai! Kripya doosra time ya room chunein.")
                else:
                    new_id = int(df["id"].max() + 1) if not df.empty else 1
                    new_row = {
                        "id": new_id, 
                        "Student": name, 
                        "Email": email, 
                        "Room": room, 
                        "Date": date_str, 
                        "Start": start_str, 
                        "End": end_str, 
                        "Seats": seats, 
                        "Status": "None"
                    }
                    st.session_state.bookings = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("✅ Booking request successfully submit ho gayi hai! Admin approval ka intezaar karein.")

# --- TAB 2: ROOM DIRECTORY & PREVIEW ---
with tab2:
    st.subheader("🏢 Campus Rooms Directory & Facilities Preview")
    st.markdown("Yahan aap dekh sakte hain ki har room kaisa hai aur kya suvidhayein milti hain:")
    
    for r_name, details in ROOM_DETAILS.items():
        with st.expander(f"📌 {r_name} (Capacity: {details['capacity']} Seats)"):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(f"**Description:** {details['description']}")
                st.markdown(f"**Available Facilities:** {details['facilities']}")
            with col_b:
                st.markdown(f"**Max Seats:** {details['capacity']}")
                st.markdown("Status: 🟢 Available for Booking")
        st.markdown("")

# --- TAB 3: MY BOOKINGS ---
with tab3:
    st.subheader("📅 All Bookings Status")
    if not st.session_state.bookings.empty:
        st.dataframe(st.session_state.bookings, use_container_width=True)
    else:
        st.info("Abhi tak koi bookings nahi hain.")

# --- TAB 4: ADMIN PANEL ---
with tab4:
    st.subheader("🔒 Administrator Panel")
    if not st.session_state.admin_logged_in:
        with st.form("login"):
            pwd = st.text_input("Admin password", type="password")
            if st.form_submit_button("Login"):
                try: 
                    secret = st.secrets["ADMIN_PASSWORD_HASH"]
                except: 
                    secret = "admin123"
                
                if h(pwd) == secret or pwd == secret:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else: 
                    st.error("Incorrect password.")
                    st.caption("Default password: admin123")
    else:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.markdown("---")
        df = st.session_state.bookings
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            bid = st.selectbox("Select Booking ID to manage", options=df["id"].tolist())
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("✅ Approve", use_container_width=True):
                    st.session_state.bookings.loc[df["id"] == bid, "Status"] = "Approved"
                    st.rerun()
            with c2:
                if st.button("❌ Reject", use_container_width=True):
                    st.session_state.bookings.loc[df["id"] == bid, "Status"] = "Rejected"
                    st.rerun()
            with c3:
                if st.button("🗑️ Delete History", use_container_width=True):
                    st.session_state.bookings = df[df["id"] != bid]
                    st.rerun()
        else:
            st.info("Manage karne ke liye koi bookings nahi hain.")