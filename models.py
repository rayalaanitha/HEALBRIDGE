from django.db import models
from django.contrib.auth.models import User

# -------------------- MEDICINE MASTER --------------------
class Medicine(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, default="Unknown Company")
    certified_doctor = models.CharField(max_length=150, default="Not Assigned")
    expiry_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=10)
    medicine_image = models.ImageField(upload_to='medicines/', null=True, blank=True)

    def __str__(self):
        return self.name


# -------------------- DONATION --------------------
class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    remaining_quantity = models.PositiveIntegerField(default=1)
    is_good = models.BooleanField(default=True)
    donated_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.donor.username} -> {self.medicine.name} x{self.quantity}"


# -------------------- PRESCRIPTION REQUEST --------------------
class PrescriptionRequest(models.Model):
    prescription = models.ImageField(upload_to="prescriptions/", null=True, blank=True)
    result = models.JSONField(null=True, blank=True)  # {"available": [], "unavailable": []}
    processed = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription {self.id}"

    def get_available(self):
        if self.result and "available" in self.result:
            return self.result["available"]
        return []

    def get_unavailable(self):
        if self.result and "unavailable" in self.result:
            return self.result["unavailable"]
        return []


# -------------------- NOTIFICATION --------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    related_donation = models.ForeignKey(Donation, on_delete=models.SET_NULL, null=True, blank=True)
    related_request = models.ForeignKey(PrescriptionRequest, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}"


# -------------------- USER PROFILE --------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"
