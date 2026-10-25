import streamlit as st
import urllib.parse
from datetime import datetime
import random

try:
    from streamlit_geolocation import streamlit_geolocation
    GEO_AVAILABLE = True
except Exception:
    GEO_AVAILABLE = False

st.set_page_config(page_title="Women Safety | SafeBand", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.stApp {background:linear-gradient(180deg,#fff7f8,#f8fafc 55%,#f4f7fb);}
.hero {padding:1.2rem 1.4rem;border-radius:18px;background:linear-gradient(120deg,#7f1d3a,#be123c);color:white;}
.hero h1 {color:white;margin:0}.hero p {color:#ffe4e6;margin-bottom:0}
.demo {padding:.8rem 1rem;border-radius:12px;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412}
</style>
""", unsafe_allow_html=True)

# Data below is temporary and held only in the current Streamlit session.
for key, default in {
    "contacts": [], "alerts": [], "location": None, "sos_armed": False,
    "fall_events": [], "health_demo": {"heart_rate": 78, "spo2": 98, "steps": 6250}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.markdown("## 🛡️ SafeBand")
    st.caption("Women Safety Project")
    page = st.radio("Navigation", [
        "Home & SOS", "Emergency Contacts", "Location", "Health Monitoring",
        "Band Connection", "Alert History", "About & Safety"
    ])
    st.divider()
    st.caption("Prototype: SMS/calls, sensors and ESP32 actions require setup.")

st.markdown("""
<div class="hero">
<h1>🛡️ Women Safety System</h1>
<p>Safety dashboard • SOS • Location • Health monitoring • Smart band prototype</p>
</div>
""", unsafe_allow_html=True)

def location_text():
    loc = st.session_state.location
    return f"{loc['lat']}, {loc['lon']}" if loc else "Location not added"

def make_message():
    return f"EMERGENCY ALERT: I may need help. Last location: {location_text()}. Please contact me and check my safety."

def add_alert(source="Web SOS", status="Test alert recorded locally"):
    st.session_state.alerts.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source, "location": location_text(), "status": status
    })

if page == "Home & SOS":
    a, b, c = st.columns(3)
    a.metric("Safety Status", "🟢 Ready")
    b.metric("Trusted Contacts", len(st.session_state.contacts))
    c.metric("Location", "Available" if st.session_state.location else "Not set")
    st.markdown("### Emergency SOS")
    st.warning("This demo records a test alert only. It does not automatically contact emergency services.")
    confirm = st.checkbox("I understand this is a prototype and want to activate a test SOS.")
    if st.button("🚨 ACTIVATE SOS", type="primary", width="stretch", disabled=not confirm):
        add_alert("Web SOS", "SOS test alert recorded locally")
        st.session_state.sos_armed = True
        st.error("Test alert recorded. No SMS was sent and no call was made.")
    if st.session_state.sos_armed:
        st.markdown("#### Contact actions")
        st.code(make_message())
        if st.session_state.contacts:
            for contact in st.session_state.contacts:
                phone = "".join(ch for ch in contact["phone"] if ch.isdigit() or ch == "+")
                sms = "sms:" + phone + "?body=" + urllib.parse.quote(make_message())
                st.markdown(f"**{contact['name']}** — {contact['phone']}  ·  [📞 Call](tel:{phone}) · [✉️ Open SMS draft]({sms})")
        else:
            st.info("Add a trusted contact on the Emergency Contacts page.")
    st.info("A browser-based Streamlit page cannot guarantee background alerts.")

elif page == "Emergency Contacts":
    st.subheader("Trusted Emergency Contacts")
    with st.form("add_contact", clear_on_submit=True):
        name = st.text_input("Contact name")
        phone = st.text_input("Phone number (include country code, e.g. +91...)")
        relation = st.selectbox("Relationship", ["Family", "Friend", "Guardian", "Other"])
        submitted = st.form_submit_button("Add contact")
    if submitted:
        if not name.strip() or not phone.strip():
            st.warning("Please enter both a name and phone number.")
        else:
            st.session_state.contacts.append({"name": name.strip(), "phone": phone.strip(), "relation": relation})
            st.success(f"Added {name.strip()}.")
    if st.session_state.contacts:
        for i, contact in enumerate(st.session_state.contacts):
            left, middle, right = st.columns([3, 3, 1])
            left.write(f"**{contact['name']}**")
            middle.write(f"{contact['phone']} · {contact['relation']}")
            if right.button("Remove", key=f"remove_{i}"):
                st.session_state.contacts.pop(i)
                st.rerun()
    else:
        st.caption("No contacts added yet.")
    st.caption("Contacts are stored only in this session; they are not saved to a permanent database.")

elif page == "Location":
    st.subheader("📍 Location")
    st.write("Browser location requires permission and works best on HTTPS hosting.")
    if GEO_AVAILABLE:
        try:
            loc = streamlit_geolocation()
            if loc and loc.get("latitude") is not None and loc.get("longitude") is not None:
                st.session_state.location = {"lat": round(float(loc["latitude"]), 6), "lon": round(float(loc["longitude"]), 6)}
                st.success("Location received from browser.")
        except Exception:
            st.warning("Could not read browser location; enter coordinates manually.")
    else:
        st.info("Location component unavailable; enter coordinates manually.")
    with st.form("manual_location"):
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=float(st.session_state.location["lat"]) if st.session_state.location else 26.7606, format="%.6f")
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=float(st.session_state.location["lon"]) if st.session_state.location else 83.3732, format="%.6f")
        save_loc = st.form_submit_button("Save location")
    if save_loc:
        st.session_state.location = {"lat": round(lat, 6), "lon": round(lon, 6)}
        st.success("Location saved for this session.")
    if st.session_state.location:
        loc = st.session_state.location
        url = f"https://www.openstreetmap.org/?mlat={loc['lat']}&mlon={loc['lon']}#map=16/{loc['lat']}/{loc['lon']}"
        st.write(f"Saved coordinates: {loc['lat']}, {loc['lon']}")
        st.markdown(f"[Open location on OpenStreetMap]({url})")
        st.map([{"lat": loc["lat"], "lon": loc["lon"]}])
    st.caption("Manually entered coordinates are demo data until verified against the phone's actual location.")

elif page == "Health Monitoring":
    st.subheader("❤️ Health & Activity Monitoring")
    st.markdown('<div class="demo"><b>DEMO MODE:</b> These are sample values, not measurements from your body. No sensors are connected.</div>', unsafe_allow_html=True)
    readings = st.session_state.health_demo
    x, y, z = st.columns(3)
    x.metric("Heart Rate", f"{readings['heart_rate']} BPM", help="Demo value only.")
    y.metric("SpO₂", f"{readings['spo2']}%", help="Demo value only.")
    z.metric("Steps", f"{readings['steps']:,}", help="Demo value only.")
    if st.button("🔄 Generate new DEMO readings", width="stretch"):
        st.session_state.health_demo = {
            "heart_rate": random.randint(65, 100),
            "spo2": random.randint(95, 99),
            "steps": random.randint(500, 10000)
        }
        st.rerun()
    st.markdown("### Fall Detection")
    st.write("Real fall detection needs a movement sensor such as MPU6050 connected to an ESP32 and a tested algorithm.")
    st.warning("This button simulates a fall event for demonstration only. It does not detect an actual fall or contact anyone.")
    if st.button("🧪 Simulate a possible fall", type="primary", width="stretch"):
        event = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Simulated possible fall",
            "status": "Demo event only — no physical sensor checked"
        }
        st.session_state.fall_events.insert(0, event)
        add_alert("Fall Detection Demo", "Simulated fall event — demo only")
        st.error("Demo fall event recorded. No actual fall was detected and no alert was sent.")
    if st.session_state.fall_events:
        st.markdown("#### Demo fall-event history")
        st.dataframe(st.session_state.fall_events, width="stretch", hide_index=True)
    st.caption("Heart rate and SpO₂ demo values are not medical measurements. Do not use this prototype for diagnosis or medical decisions.")

elif page == "Band Connection":
    st.subheader("⌚ ESP32 Smart Band")
    st.write("This is a setup placeholder. The online website cannot automatically read an ESP32 on your local Wi-Fi without a secure backend/device connection.")
    mode = st.radio("Connection method", ["Local Wi-Fi (same network)", "Cloud webhook (for remote dashboard)"])
    if mode == "Local Wi-Fi (same network)":
        st.write("Local testing may be blocked by network and browser security restrictions.")
        st.code("Example concept only: http://ESP32_LOCAL_IP/sos")
    else:
        st.write("For remote use, ESP32 should send authenticated events to a backend API.")
        st.code("ESP32 → HTTPS backend endpoint → database → Streamlit dashboard")
    st.warning("No physical ESP32 or sensor readings are connected yet.")
    if st.button("⌚ Simulate band SOS", width="stretch"):
        add_alert("Simulated ESP32 Band", "Demo event only — no physical device contacted")
        st.success("Simulated event added. No physical device was contacted.")

elif page == "Alert History":
    st.subheader("Alert History")
    if not st.session_state.alerts:
        st.info("No alerts recorded in this session.")
    else:
        st.dataframe(st.session_state.alerts, width="stretch", hide_index=True)
        if st.button("Clear session history"):
            st.session_state.alerts = []
            st.session_state.fall_events = []
            st.rerun()
    st.caption("History is temporary and clears when the session resets. Persistent logs need a database.")

else:
    st.subheader("About this project")
    st.markdown("""
**SafeBand** is an educational Women Safety System prototype.

**Included:** SOS test-event recording, emergency contact entry, SMS draft/call links, browser/manual location, map preview, simulated ESP32 alert, health monitoring demo, and simulated fall event.

**Not yet enabled:** automatic SMS/calling, permanent database, live ESP32-to-cloud communication, real heart-rate/SpO₂ readings, sensor-based fall detection, or guaranteed background alerts.

Never rely on an untested prototype as your only emergency plan. In India, the national emergency response number is **112**; do not use test alerts to contact emergency services.
""")
