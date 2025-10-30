from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
import os
import numpy as np
from tensorflow.keras.models import load_model
import joblib
from django.db import connection

print("🚀 Starting Django app...")

# تحميل الموديل
try:
    print("🧠 Loading Keras model...")
    model = load_model(os.path.join('ml_models', 'general_model.h5'))
    print("✅ Model loaded successfully!")
except Exception as e:
    print("❌ Error loading model:", e)
    model = None

# تحميل الـ label encoder
try:
    print("🎯 Loading label encoder...")
    label_encoder = joblib.load(os.path.join('ml_models', 'label_encoder.pkl'))
    print("✅ Label encoder loaded successfully!")
except Exception as e:
    print("⚠️ Could not load label encoder:", e)
    label_encoder = None

print("🔥 Views.py finished loading!")

# قائمة الخصائص المطلوبة للتنبؤ
FEATURES_NAME = [
    'ag+1:629e', 'feeling.nervous', 'panic', 'breathing.rapidly', 'sweating',
    'trouble.in.concentration', 'having.trouble.in.sleeping', 'having.trouble.with.work',
    'hopelessness', 'anger', 'over.react', 'change.in.eating', 'suicidal.thought',
    'feeling.tired', 'close.friend', 'social.media.addiction', 'weight.gain',
    'introvert', 'popping.up.stressful.memory', 'having.nightmares',
    'avoids.people.or.activities', 'feeling.negative', 'trouble.concentrating',
    'blamming.yourself', 'hallucinations', 'repetitive.behaviour',
    'seasonally', 'increased.energy'
]

# جلب التوكن من Environment Variable
SUPERUSER_TOKEN = os.getenv("SUPERUSER_TOKEN")

# صفحة التنبؤ العادية
def predict(request):
    if request.method == 'POST':
        try:
            features = [int(request.POST.get(feature, 0)) for feature in FEATURES_NAME]
            prediction = model.predict(np.array([features]))
            predicted_disorder = label_encoder.inverse_transform([np.argmax(prediction)])[0]
            result = f"The predicted mental health condition is: {predicted_disorder}"
            return render(request, 'predict.html', {"result": result})
        except Exception as e:
            return render(request, 'predict.html', {"error": str(e)})
    return render(request, 'predict.html')

# API التنبؤ المحمي بالتوكن
@api_view(['POST'])
def api_predict(request):
    # التحقق من التوكن قبل أي عملية
    token = request.headers.get('Authorization')  # في Postman: "Token <توكن>"
    if token != f"Token {SUPERUSER_TOKEN}":
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))

        # التحقق من وجود كل الخصائص المطلوبة
        missing_features = [key for key in FEATURES_NAME if key not in data]
        if missing_features:
            return JsonResponse({"error": f"Missing features: {', '.join(missing_features)}"}, status=400)

        # تحقق من أن العمر غير سالب
        first_feature = float(data.get(FEATURES_NAME[0]))
        if first_feature < 0:
            return JsonResponse({"error": "Age must be a non-negative value."}, status=400)

        # تحقق أن كل الخصائص الأخرى 0 أو 1
        invalid_features = {}
        for key in FEATURES_NAME[1:]:
            value = int(data.get(key))
            if value not in [0, 1]:
                invalid_features[key] = value
        if invalid_features:
            return JsonResponse({"error": f"Invalid feature values (should be 0 or 1): {invalid_features}"}, status=400)

        # التنبؤ بالمرض
        features = np.array([[int(data.get(key)) for key in FEATURES_NAME]])
        prediction = model.predict(features)
        predicted_disorder = label_encoder.inverse_transform([np.argmax(prediction)])[0]
        return JsonResponse({"predicted_disorder": predicted_disorder})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# endpoint لعرض الجداول (اختياري، للتأكد من قاعدة البيانات)
def list_tables(request):
    """Show all tables in current DB, works with SQLite or Postgres."""
    with connection.cursor() as cursor:
        vendor = connection.vendor  # 'sqlite', 'postgresql', 'mysql', ...
        if vendor == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        elif vendor == 'postgresql':
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
        else:
            return JsonResponse({"error": f"Unsupported DB: {vendor}"}, status=500)
        tables = [row[0] for row in cursor.fetchall()]
    return JsonResponse({"tables": tables})
