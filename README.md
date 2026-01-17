# Fan Control

This repository is a simple Flask app to control a fan over serial.

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run with Waitress (production):

```bash
python serve.py
```

Run in development (Flask builtin server):

```bash
python app.py
```
