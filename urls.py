from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings            # ✅ Import settings
from django.conf.urls.static import static  # ✅ Import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.donor_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('donate/', views.donate, name='donate'),
    path('donation_dashboard/', views.donation_dashboard, name='donation_dashboard'),
    path('donation_success/<int:id>/', views.donation_success, name='donation_success'),
    path('request_medicine/', views.request_medicine, name='request_medicine'),
    path('all_prescriptions/', views.all_prescriptions, name='all_prescriptions'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('unread_notifications/', views.unread_notifications, name='unread_notifications'),
    path('predict_donation_status/', views.predict_donation_status, name='predict_donation_status'),
    path('nlp_results/', views.nlp_results_view, name='nlp_results'),
    
]

# ✅ Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
