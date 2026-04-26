from django import forms
from .models import Medicine, Donation, PrescriptionRequest

# -------------------- MEDICINE DONATION FORM --------------------
class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ["name", "company", "price", "expiry_date", "medicine_image"]

# -------------------- DONATION FORM --------------------
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["medicine", "quantity", "is_good"]
        labels = {
            "medicine": "Medicine",
            "donor_name": "Donor Name (optional)",
            "quantity": "Quantity Donated",
        }

# -------------------- PRESCRIPTION UPLOAD FORM --------------------
class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = PrescriptionRequest
        fields = ["prescription"]
        labels = {
            "prescription": "Upload Prescription Image",
        }
