# Medicine recognizer prototype

This small prototype in `core/nlp.py` recognizes medicines from free text using a small alias dictionary and optional fuzzy matching (via `rapidfuzz`). It flags high-cost oncology injections by a `cost_tag` field.

How to run

1. (Optional) Create and activate a virtualenv.
2. Install dependencies (optional fuzzy matching):

```powershell
pip install -r requirements.txt
```

3. Run the prototype:

```powershell
python core/nlp.py
```

Extending the medicine list

- Edit `core/nlp.py` and update the `MEDICINES` dict. Use `aliases` for alternate spellings.
- Add `cost_tag` (low/medium/high/very_high) and `category` (e.g., oncology) to mark expensive drugs.

Improvements

- Use spaCy or scispaCy with a custom NER model for better recall in messy clinical text.
- Integrate an external medicines database or pricing API to get real cost data.
- Add unit tests and integrate into your project's test suite.

# HealBridge (Django + djongo) - Ready-to-run (Day 1)

This is a minimal Django project preconfigured to use **local MongoDB** via **djongo**.
It includes a small `core` app with a `Medicine` model, simple donation form, and templates.

---

## What's included
- Django project `medibridge/`
- App `core/` with models, forms, views and templates
- `requirements.txt` with exact versions
- Media folder configured for uploaded images

> This project uses **Django 3.2.18** and **djongo 1.5.1** (recommended pairing for local MongoDB compatibility).

---

## Steps to run (detailed) — AFTER you download & unzip the project

### 1) Install MongoDB (local)
You must have MongoDB Community edition installed and running on your machine.
- **Linux (Ubuntu example)**:
  ```bash
  sudo apt update
  sudo apt install -y mongodb
  # Start the service (if not started)
  sudo systemctl start mongodb
  sudo systemctl enable mongodb
  ```
- **Windows / Mac**: download MongoDB Community Server from https://www.mongodb.com/try/download/community and follow installer instructions. After install, ensure the `mongod` service is running.
- You can verify with:
  ```bash
  # using mongosh (if installed):
  mongosh --eval "db.adminCommand({ping:1})"
  ```
If your MongoDB runs on a different port or host, edit `DATABASES` in `medibridge/settings.py` (the `host` value).

### 2) Open project in VS Code
Unzip the downloaded `medibridge_djongo.zip` and open the folder in VS Code or your editor.

### 3) Create & activate virtual environment
Linux / Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```
Windows (PowerShell):
```powershell
py -3 -m venv venv
.env\Scripts\Activate.ps1
```

### 4) Install Python requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5) Run Django migrations & create superuser
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
# follow prompts to set username & password
```

> If `makemigrations` or `migrate` fails with djongo errors, ensure MongoDB server is running and that djongo version is 1.5.1 with Django 3.2.18. Sometimes djongo needs additional packages; see Troubleshooting below.

### 6) Run development server
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser. Click **Donate Medicine** to submit a donation. Uploaded images are saved under the `media/` folder.

### 7) View data in Django admin
Open http://127.0.0.1:8000/admin/ and login with the superuser you created. You will find the **Medicines** listed there.

---

## Troubleshooting (common issues)
- **Cannot connect to MongoDB / server selection timeout**: ensure `mongod` is running and accessible at `mongodb://127.0.0.1:27017` (default). If you changed the host/port, update `medibridge/settings.py` DATABASES CLIENT host.
- **`djongo` migration errors**: djongo has limited compatibility; this project pins versions (Django 3.2.18 + djongo 1.5.1). If you get errors, try reinstalling the exact versions in `requirements.txt` or restart MongoDB.
- **Image not showing**: ensure DEBUG=True and `MEDIA_URL` is being served (the development server serves media automatically as configured in urls). Check the `media/` folder for uploaded files.
- If you prefer not to use djongo later, we can provide a PyMongo-based version (different project) that writes directly to MongoDB without Django ORM.

---

If anything fails, copy the terminal output and paste it to me. I'll debug step-by-step with you.
