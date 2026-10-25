# Women Safety Streamlit Project — SafeBand

## Run locally (Windows)

1. Install Python 3.11 or 3.12 from https://www.python.org/downloads/
2. Open this folder in VS Code.
3. Open Terminal and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, run the app with:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py` and `requirements.txt`.
2. Visit https://share.streamlit.io/
3. Connect GitHub, choose your repository, branch, and `app.py`.
4. Deploy.

## Important limitations

This is an educational prototype. The SOS button records a local session event; it does not automatically send SMS or call emergency services. The SMS/call links open the phone's messaging/dialer app when supported. Browser GPS requires permission and HTTPS. Contacts and alerts are temporary in session state, not securely persisted. ESP32 connection is currently simulated and requires a secure backend/device integration for real operation.

Do not store real passwords, API keys, or Wi-Fi credentials in source code or a public repository.
