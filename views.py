from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from PIL import Image
import pytesseract
from textblob import TextBlob
import os
import pandas as pd
import joblib
import json

from .forms import MedicineForm, PrescriptionForm
from django import forms as django_forms
from .models import Medicine, PrescriptionRequest, Donation, Notification
from .ml_model import train_medicine_model



# Train and test accuracy
model = train_medicine_model()

# -------------------- CONFIG --------------------
import os
import pandas as pd
import pytesseract

# Build the absolute path dynamically (safe for any system)
csv_path = os.path.join(os.path.dirname(__file__), 'data', 'healbridge_final_dataset.csv')

# Try loading the dataset safely
if os.path.exists(csv_path):
    medicine_df = pd.read_csv(csv_path)
    print(f"✅ Dataset loaded successfully from: {csv_path}")
    print(f"📊 Total records: {len(medicine_df)}")
else:
    medicine_df = None
    print(f"⚠️ Dataset not found at: {csv_path}")

# Path for Tesseract OCR (adjust if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------- LOGIN --------------------
def donor_login(request):
    """Custom login view for donors"""
    if request.user.is_authenticated:
        # Already logged in, redirect to next or donate
        next_url = request.GET.get('next', '/donate/')
        return redirect(next_url)
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to "next" page if available, else donate
            next_url = request.GET.get('next', '/donate/')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

# -------------------- HOME --------------------
def home(request):
    return render(request, "home.html")

# -------------------- DONATE MEDICINE --------------------
@login_required(login_url='login')
def donate(request):
    # Build company choices from dataset (if available)
    choices = [("", "Select Company")]
    try:
        if medicine_df is not None and 'company' in medicine_df.columns:
            comps = medicine_df['company'].dropna().astype(str).map(lambda s: s.strip()).unique().tolist()
            comps = sorted([c for c in set(comps) if c])
            choices = [("", "Select Company")] + [(c, c) for c in comps]
    except Exception:
        # fallback to model default
        choices = [("", "Unknown Company"), ("Unknown Company", "Unknown Company")]

    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES)
        # replace company field with ChoiceField so validation matches the dropdown
        form.fields['company'] = django_forms.ChoiceField(choices=choices, required=False)
        if form.is_valid():
            # If company not provided, try to infer it from dataset using medicine name
            name_val = form.cleaned_data.get('name', '')
            company_val = form.cleaned_data.get('company') or ''
            try:
                if (not company_val) and medicine_df is not None and 'name' in medicine_df.columns and 'company' in medicine_df.columns:
                    # try exact match (case-insensitive)
                    df = medicine_df
                    mask_exact = df['name'].astype(str).str.strip().str.lower() == str(name_val).strip().lower()
                    candidates = df.loc[mask_exact, 'company'].dropna().astype(str).map(lambda s: s.strip())
                    if candidates.empty:
                        # try contains match
                        mask_contains = df['name'].astype(str).str.strip().str.lower().str.contains(str(name_val).strip().lower(), na=False)
                        candidates = df.loc[mask_contains, 'company'].dropna().astype(str).map(lambda s: s.strip())
                    if not candidates.empty:
                        # choose the most common company among candidates
                        inferred_company = candidates.mode().iloc[0]
                        form.instance.company = inferred_company
            except Exception:
                # any failure, fall back to whatever the form has
                pass

            # Save medicine first
            medicine = form.save()

            # Create Donation linking medicine to current user
            Donation.objects.create(
                donor=request.user,
                medicine=medicine,
                quantity=form.cleaned_data.get('stock', 1),
                verified=False
            )

            messages.success(request, "Donation submitted! Pending verification.")
            # Redirect to success page (which auto-redirects to donate form after 5 seconds)
            return redirect("donation_success", id=medicine.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MedicineForm()
        form.fields['company'] = django_forms.ChoiceField(choices=choices, required=False)

    return render(request, 'donate.html', {'form': form})


# Donation dashboard view
@login_required(login_url='login')
def donation_dashboard(request):
    # Get donations of current user
    donations = Donation.objects.filter(donor=request.user).order_by('-donated_at')
    return render(request, 'donation_dashboard.html', {'donations': donations})



# -------------------- DONATION SUCCESS --------------------
@login_required
def donation_success(request, id):
    medicine = Medicine.objects.get(id=id)
    # Get the latest donation for this medicine (or find by user+medicine)
    donation = Donation.objects.filter(medicine=medicine, donor=request.user).order_by('-donated_at').first()
    return render(request, "donation_success.html", {"medicine": medicine, "donation": donation})


@login_required
def request_medicine(request):
    result = None
    nlp_result = None

    if request.method == "POST":
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            pres = form.save()
            messages.success(request, "Prescription uploaded successfully!")

            # 🧾 Extract text from prescription using OCR
            image_path = pres.prescription.path
            extracted_text = pytesseract.image_to_string(Image.open(image_path))

            # ✅ Normalize text (for matching)
            def _normalize(s):
                return ''.join(ch for ch in (s or '').lower() if ch.isalnum())

            text_norm = _normalize(extracted_text)
            extracted_text_lower = extracted_text.lower()

            # ✅ Extended list of known medicines (you can add more here)
            known_medicines = [
                "Humalog", "Ozempic", "Jardiance", "Crestor", "Xarelto",
                "Dexilant", "Myoril", "Panadol Extra", "Insulin",
                "Metformin", "Losartan", "Atorvastatin", "Paracetamol",
                "Amoxicillin", "Omeprazole", "Levothyroxine", "Gabapentin",
                "Amlodipine", "Lisinopril", "Simvastatin", "Prednisone",
                "Azithromycin", "Clopidogrel", "Hydrochlorothiazide",
                "Vitamin D", "Montelukast", "Cetirizine", "Ranitidine",
                "Ibuprofen", "Aspirin", "Fluoxetine", "Salbutamol",
                "Insulin Glargine", "Trulicity", "Farxiga", "Empagliflozin"
            ]

            # ✅ Determine available and unavailable medicines
            available = [m for m in known_medicines if m.lower() in extracted_text_lower]
            unavailable = [m for m in known_medicines if m.lower() not in extracted_text_lower]

            # 🧠 NLP analysis
            blob = TextBlob(extracted_text)
            nlp_result = {
                "sentiment": {
                    "polarity": blob.sentiment.polarity,
                    "subjectivity": blob.sentiment.subjectivity
                },
                "noun_phrases": list(blob.noun_phrases)
            }

            # ✅ Store results properly as lists (not joined strings)
            result = {
                "available": available,
                "unavailable": unavailable,
                "price": request.POST.get("price")
            }

            # Save result in model (optional)
            pres.result = result
            pres.processed = True
            pres.save()

            # Render template with results
            return render(
                request,
                "request_medicine.html",
                {
                    "form": PrescriptionForm(),
                    "result": result,
                    "nlp_result": nlp_result,
                    "extracted_text": extracted_text
                }
            )

    else:
        form = PrescriptionForm()

    return render(request, "request_medicine.html", {"form": form, "result": result, "nlp_result": nlp_result})
# -------------------- ALL PRESCRIPTIONS --------------------
@login_required
def all_prescriptions(request):
    prescriptions = PrescriptionRequest.objects.all().order_by('-id')
    return render(request, "all_prescriptions.html", {"prescriptions": prescriptions})

# -------------------- NOTIFICATIONS --------------------
@login_required
def notifications_view(request):
    user_notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, "notifications.html", {"notifications": user_notifications})

@login_required
def unread_notifications(request):
    notifications_qs = Notification.objects.filter(user=request.user)
    data = [{"id": n.id, "message": n.message, "created_at": n.created_at} for n in notifications_qs]
    notifications_qs.delete()
    return JsonResponse({"notifications": data})

# -------------------- ML PREDICTION --------------------
@csrf_exempt
def predict_donation_status(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)
    try:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'model.pkl')
        model = joblib.load(model_path)

        data = json.loads(request.body.decode('utf-8'))
        quantity = float(data.get('quantity', 1))
        condition = 1 if data.get('condition', 'Sealed') == 'Sealed' else 0

        X = [[quantity, condition]]
        prediction = model.predict(X)[0]

        return JsonResponse({'prediction': str(prediction)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# -------------------- NLP RESULTS --------------------
def nlp_results_view(request):
    json_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'data', 'nlp_results.json')
    csv_path = os.path.join(os.path.dirname(__file__), 'all_patient_data.csv')

    data = []
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        data = df.to_dict(orient='records')

    return render(request, "nlp_results.html", {"results": data})
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # ✅ Add these 2 lines exactly here:
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            # Else go to default dashboard
            return redirect('donor_dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")