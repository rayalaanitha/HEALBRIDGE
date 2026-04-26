from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Donation flow
    path('donate/', views.donate, name='donate'),
    path('donation-success/<int:id>/', views.donation_success, name='donation_success'),
    path('donation_dashboard/', views.donation_dashboard, name='donation_dashboard'),

    # Prescription / request
    path('request_medicine/', views.request_medicine, name='request_medicine'),
    path('all_prescriptions/', views.all_prescriptions, name='all_prescriptions'),

    # Notifications - include the polling path expected by frontend
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/unread/', views.unread_notifications, name='notifications_unread'),

    # ML / NLP
    path('predict/', views.predict_donation_status, name='predict_donation_status'),
    path('nlp-results/', views.nlp_results_view, name='nlp_results'),

    # Auth (use DonorLoginView defined in views.py)
    # Auth
    path('login/', views.donor_login, name='login'),
    
]

