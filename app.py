import streamlit as st
import urllib.parse
from datetime import datetime
import json
import os

try:
    from streamlit_geolocation import streamlit_geolocation
    GEO_AVAILABLE = True
except Exception:
    GEO_AVAILABLE = False

st.set_page_config(
    page_title="Women Safety | SafeBand",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #fff7f8 0%, #f8fafc 45%, #f4f7fb 100%); }
.hero { padding: 1.2rem 1.4rem; border-radius: 18px; background: linear-gradient(120deg,#7f1d3a,#be123c); color: white; }
.hero h1 { color: white; margin: 0; }
.hero p { color: #ffe4e6; margin-bottom: 0; }
.metric-card { background: white; padding: 1rem; border-radius: 14px; border: 1px solid #f1cbd4; }
.sos-note { padding: .8rem 1rem; border-radius: 12px; background: #fff1f2; border: 1px solid #fecdd3; color: #881337; }
.small-muted { color: #64748b; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

if "contacts" not in st.session_state:
    st.session_state.contacts = []
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "location" not in st.session_state:
    st.session_state.location = None
if "sos_armed" not in st.session_state:
    st.session_state.sos_armed = False

with st.sidebar:
    st.markdown("## 🛡️ SafeBand")
    st.caption("Women Safety Project")
    page = st.radio("Navigation", ["Home & SOS", "Emergency Contacts", "Location", "Band Connection", "Alert History", "About & Safety"])
    st.divider()
    st.caption("Prototype mode: SMS/calls and ESP32 actions require device/service setup.")

st.markdown("""
<div class="hero">
  <h1>🛡️ Women Safety System</h1>
  <p>Mobile-friendly safety dashboard • SOS • Location • Trusted contacts • Smart band prototype</p>
</div>
""", unsafe_allow_html=True)
st.write("")

def get_location_text():
    loc = st.session_state.location
    if not loc:
        return "Location not added"
    return f"{loc['lat']}, {loc['lon']}"

def make_message():
    return (
        "EMERGENCY ALERT: I may need help. "
        f"Last location: {get_location_text()}. "
        "Please contact me and check my safety."
    )

def add_alert(source="Web SOS"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item = {"time": now, "source": source, "location": get_location_text(), "status": "SOS activated locally"}
    st.session_state.alerts.insert(0, item)

if page == "Home & SOS":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card"><b>Safety Status</b><h3>🟢 Ready</h3><span class="small-muted">Prototype running</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><b>Trusted Contacts</b><h3>{len(st.session_state.contacts)}</h3><span class="small-muted">Saved in this session</span></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><b>Location</b><h3>{"📍 Available" if st.session_state.location else "Not set"}</h3><span class="small-muted">{get_location_text()}</span></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("### Emergency SOS")
    st.markdown('<div class="sos-note">Press SOS only when you need assistance. This demo records an alert in the dashboard; it does not silently contact emergency services.</div>', unsafe_allow_html=True)
    confirm = st.checkbox("I understand this is a prototype and want to activate a test SOS.")
    if st.button("🚨 ACTIVATE SOS", type="primary", use_container_width=True, disabled=not confirm):
        add_alert("Web SOS")
        st.session_state.sos_armed = True
        st.error("SOS TEST ALERT RECORDED. Use the contact links below to call or prepare an SMS; this website has not sent an SMS or called anyone.")
    if st.session_state.sos_armed:
        st.markdown("#### Contact actions")
        st.code(make_message())
        if st.session_state.contacts:
            for i, contact in enumerate(st.session_state.contacts):
                phone = "".join(ch for ch in contact["phone"] if ch.isdigit() or ch == "+")
                sms_url = "sms:" + phone + "?body=" + urllib.parse.quote(make_message())
                call_url = "tel:" + phone
                st.markdown(f"**{contact['name']}** — {contact['phone']}  \n[📞 Call contact]({call_url}) · [✉️ Open SMS draft]({sms_url})")
        else:
            st.info("Add at least one trusted contact on the Emergency Contacts page.")
    st.write("")
    st.markdown("### Quick actions")
    st.info("For reliable emergency use, configure and test a real SMS/call provider or a native Android app. A browser-based Streamlit page cannot guarantee background alerts.")

elif page == "Emergency Contacts":
    st.subheader("Trusted Emergency Contacts")
    st.write("Add family members or friends who have agreed to be emergency contacts.")
    with st.form("add_contact", clear_on_submit=True):
        name = st.text_input("Contact name")
        phone = st.text_input("Phone number (include country code, e.g. +91...)")
        relation = st.selectbox("Relationship", ["Family", "Friend", "Guardian", "Other"])
        submitted = st.form_submit_button("Add contact")
    if submitted:
        if not name.strip() or not phone.strip():
            st.warning("Please enter both a name and a phone number.")
        else:
            st.session_state.contacts.append({"name": name.strip(), "phone": phone.strip(), "relation": relation})
            st.success(f"Added {name.strip()}.")
    if st.session_state.contacts:
        st.markdown("#### Saved contacts")
        for i, c in enumerate(st.session_state.contacts):
            left, mid, right = st.columns([3, 3, 1])
            left.write(f"**{c['name']}**")
            mid.write(f"{c['phone']} · {c['relation']}")
            if right.button("Remove", key=f"remove_{i}"):
                st.session_state.contacts.pop(i)
                st.rerun()
    else:
        st.caption("No contacts added yet.")
    st.caption("Prototype note: contacts are stored only in the current Streamlit session. Persistent private storage needs a database and authentication.")

elif page == "Location":
    st.subheader("📍 Location")
    st.write("Location access depends on browser permission and secure hosting (HTTPS).")
    if GEO_AVAILABLE:
        st.markdown("Click the location control below and allow location access in your browser.")
        try:
            loc = streamlit_geolocation()
            if loc and loc.get("latitude") is not None and loc.get("longitude") is not None:
                st.session_state.location = {"lat": round(float(loc["latitude"]), 6), "lon": round(float(loc["longitude"]), 6)}
                st.success("Location received from browser.")
        except Exception as e:
            st.warning("Browser location could not be read. You can enter coordinates manually below.")
    else:
        st.info("Automatic browser GPS component is not installed in this environment. You can enter coordinates manually; after deployment, the optional geolocation component can request browser permission.")
    with st.form("manual_location"):
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=float(st.session_state.location["lat"]) if st.session_state.location else 26.7606, format="%.6f")
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=float(st.session_state.location["lon"]) if st.session_state.location else 83.3732, format="%.6f")
        save_loc = st.form_submit_button("Save location")
    if save_loc:
        st.session_state.location = {"lat": round(lat, 6), "lon": round(lon, 6)}
        st.success("Location saved for this session.")
    if st.session_state.location:
        loc = st.session_state.location
        map_url = f"https://www.openstreetmap.org/?mlat={loc['lat']}&mlon={loc['lon']}#map=16/{loc['lat']}/{loc['lon']}"
        st.markdown(f"**Saved coordinates:** `{loc['lat']}, {loc['lon']}`")
        st.markdown(f"[Open location on OpenStreetMap]({map_url})")
        st.map([{"lat": loc["lat"], "lon": loc["lon"]}])
    st.caption("Coordinates entered manually are only a demo until verified against the phone's actual GPS.")

elif page == "Band Connection":
    st.subheader("⌚ ESP32 Smart Band")
    st.write("This page is a setup placeholder for an ESP32 band. A deployed Streamlit website cannot directly connect to an ESP32 that is only on your home Wi-Fi unless a reachable backend or a secure device-to-cloud connection is configured.")
    st.markdown("#### Choose the connection method")
    mode = st.radio("Connection method", ["Local Wi-Fi (same network)", "Cloud webhook (recommended for remote dashboard)"])
    if mode == "Local Wi-Fi (same network)":
        st.write("For local testing, the ESP32 can host an HTTP endpoint on the same Wi-Fi network. The browser/cloud server may not be able to reach it due to network and security restrictions.")
        st.code("Example concept only: http://ESP32_LOCAL_IP/sos")
    else:
        st.write("For remote use, ESP32 should send an authenticated SOS event to a backend API. Do not expose an unauthenticated device endpoint publicly.")
        st.code("ESP32 button → HTTPS backend endpoint → database → Streamlit dashboard")
    st.warning("No real ESP32 commands are being sent from this prototype. Next stage requires your ESP32 board, Wi-Fi credentials kept private, and backend endpoint.")
    st.markdown("#### Test a simulated band alert")
    if st.button("⌚ Simulate band SOS", use_container_width=True):
        add_alert("Simulated ESP32 Band")
        st.success("Simulated band event added to alert history. No physical device was contacted.")

elif page == "Alert History":
    st.subheader("Alert History")
    if not st.session_state.alerts:
        st.info("No alerts recorded in this session.")
    else:
        st.dataframe(st.session_state.alerts, use_container_width=True, hide_index=True)
        if st.button("Clear session history"):
            st.session_state.alerts = []
            st.rerun()
    st.caption("History is temporary and clears when the session resets. Persistent logs need a database.")

else:
    st.subheader("About this project")
    st.markdown("""
**SafeBand** is an educational prototype for a Women Safety System.

**Included in this starter**
- Responsive Streamlit dashboard
- SOS test-event recording
- Emergency contact entry
- SMS draft and call links
- Location capture component (when available) plus manual coordinates
- OpenStreetMap link and map preview
- Simulated ESP32 alert and integration guidance

**Not yet enabled**
- Automatic SMS delivery from the server
- Automatic calling / emergency-services integration
- Persistent user accounts and database
- Live ESP32-to-cloud communication
- Guaranteed background alerts

Never rely on an untested prototype as your only emergency plan. Keep your phone charged and use local emergency services when needed.
""")
    st.markdown("For India, the national emergency response number is **112**. Verify local emergency guidance and do not use test alerts to contact emergency services.")
