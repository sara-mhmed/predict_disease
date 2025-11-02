import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'predict_disorder.settings')
django.setup()

print("🚀 Running migrations on Railway...")
try:
    call_command('migrate', interactive=False)
    print("✅ Migrations completed successfully!")
except Exception as e:
    print("❌ Error running migrations:", e)
