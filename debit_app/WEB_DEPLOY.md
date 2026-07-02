# Web Demo Deployment

This folder now contains a Streamlit web version of the cut-list app:

```text
streamlit_app.py
```

It reuses the same core files as the desktop application:

```text
core/parser.py
core/transformer.py
core/exporter.py
```

## Run Locally

From this folder:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The included `.streamlit/config.toml` binds Streamlit to all network
interfaces on port `8501`, so the app can be reached at:

```text
http://82.38.44.28:8501
```

If you use a different external port, update both `server.port` and
`browser.serverPort` in `.streamlit/config.toml`, then make sure that port is
allowed through the machine firewall and forwarded by the router if needed.

Streamlit's CORS and XSRF protections are left enabled by default; only change
those if you are deploying behind a proxy and see a specific browser-origin
error.

## Deploy On Streamlit Community Cloud

1. Push this project to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Set the main file path to:

```text
debit_app/streamlit_app.py
```

5. Streamlit will install dependencies from:

```text
debit_app/requirements.txt
```

6. Deploy and send the generated URL to the client.

## Desktop Build

The Windows desktop build still uses:

```text
requirements-desktop.txt
```

Run:

```powershell
.\build.bat
```

## Privacy Note

Uploaded CSV files are processed temporarily during the web request. The app does
not intentionally store client files, but the deployment host still receives the
uploaded data while processing it.
