# one-off script to delete all Notification rows
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medibridge.settings')
django.setup()
from core.models import Notification
count = Notification.objects.count()
Notification.objects.all().delete()
print(f"Deleted {count} Notification rows.")
