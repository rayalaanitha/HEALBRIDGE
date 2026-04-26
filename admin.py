from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from .models import Medicine, PrescriptionRequest, Donation, Notification, Profile

# =======================
# 🧾 MEDICINE ADMIN
# =======================
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'price', 'expiry_date', 'medicine_image')
    search_fields = ('name', 'company')
    list_filter = ('expiry_date',)
    actions = ['dummy_action']

    def dummy_action(self, request, queryset):
        # placeholder if you want to add actions later
        pass
    dummy_action.short_description = "No actions currently"


# =======================
# 🧾 PRESCRIPTION REQUEST ADMIN
# =======================
@admin.register(PrescriptionRequest)
class PrescriptionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "prescription", "processed", "created_at")
    list_filter = ("processed",)
    search_fields = ("id", "prescription")


# =======================
# 🎁 DONATION ADMIN
# =======================
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'donor', 'quantity', 'remaining_quantity', 'is_good', 'verified', 'donated_at')
    list_editable = ('verified',)
    list_filter = ('is_good', 'verified', 'donated_at')
    search_fields = ('donor__username', 'medicine__name')
    actions = ['mark_as_good']

    def mark_as_good(self, request, queryset):
        """Mark selected donations as good and notify users."""
        count = 0
        for donation in queryset:
            if not donation.is_good:
                donation.is_good = True
                donation.save()
                count += 1

                # ✅ Notify donor (in-app)
                Notification.objects.create(
                    user=donation.donor,
                    message=f"✅ Your donation '{donation.medicine.name}' has been approved as safe."
                )

                # ✅ Optional: Email donor
                if donation.donor.email:
                    send_mail(
                        subject='✅ Your Donation Approved',
                        message=(
                            f"Dear {donation.donor.username},\n\n"
                            f"Your donation '{donation.medicine.name}' has been marked as safe and approved.\n"
                            f"Thank you for your contribution 💚!"
                        ),
                        from_email='healbridge.team@example.com',
                        recipient_list=[donation.donor.email],
                        fail_silently=True,
                    )

                # ✅ Notify all receivers (in-app)
                receiver_group = Group.objects.filter(name="receiver").first()
                if receiver_group:
                    for receiver in receiver_group.user_set.all():
                        Notification.objects.create(
                            user=receiver,
                            message=f"💊 A verified medicine '{donation.medicine.name}' is now available!"
                        )

        self.message_user(
            request,
            f"✅ {count} donation(s) marked as good and notifications sent successfully."
        )

    mark_as_good.short_description = "✅ Mark as Good & Notify Donors/Receivers"


# =======================
# 🏛️ ADMIN BRANDING
# =======================
admin.site.site_header = "HealBridge Admin"
admin.site.site_title = "HealBridge Admin Portal"
admin.site.index_title = "Welcome to HealBridge Dashboard"


# =======================
# 🔔 NOTIFICATION ADMIN
# =======================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)


# =======================
# 👤 PROFILE ADMIN
# =======================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'phone')
