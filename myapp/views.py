from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
import os
import numpy as np
from tensorflow.keras.models import load_model
import joblib

print("🚀 Starting Django app...")

# Load the Keras model
try:
    print("🧠 Loading Keras model...")
    model = load_model(os.path.join('ml_models', 'general_model.h5'))
    print("✅ Model loaded successfully!")
except Exception as e:
    print("❌ Error loading model:", e)
    model = None

# Load the label encoder
try:
    print("🎯 Loading label encoder...")
    label_encoder = joblib.load(os.path.join('ml_models', 'label_encoder.pkl'))
    print("✅ Label encoder loaded successfully!")
except Exception as e:
    print("⚠️ Could not load label encoder:", e)
    label_encoder = None

print("🔥 Views.py finished loading!")

# List of features required for prediction
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

# Regular web page prediction (for HTML form)
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


# 🔒 Protected API endpoint (requires valid Token Authentication)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_predict(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        # Validate required features
        missing_features = [key for key in FEATURES_NAME if key not in data]
        if missing_features:
            return JsonResponse({"error": f"Missing features: {', '.join(missing_features)}"}, status=400)

        # Validate age (first feature)
        first_feature = float(data.get(FEATURES_NAME[0]))
        if first_feature < 0:
            return JsonResponse({"error": "Age must be a non-negative value."}, status=400)

        # Validate other features (should be 0 or 1)
        invalid_features = {}
        for key in FEATURES_NAME[1:]:
            value = int(data.get(key))
            if value not in [0, 1]:
                invalid_features[key] = value
        if invalid_features:
            return JsonResponse({"error": f"Invalid feature values (should be 0 or 1): {invalid_features}"}, status=400)

        # Make prediction
        features = np.array([[int(data.get(key)) for key in FEATURES_NAME]])
        prediction = model.predict(features)
        predicted_disorder = label_encoder.inverse_transform([np.argmax(prediction)])[0]

        return JsonResponse({
            "predicted_disorder": predicted_disorder,
            "user": request.user.username  # optional: shows which user made the request
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

print("🚀 Checking for default user...")
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    token = Token.objects.create(user=user)
    print("✅ Created superuser: admin / admin123")
    print("🔑 Token:", token.key)
else:
    print("User already exists.")
    existing_user = User.objects.get(username='admin')
    token, _ = Token.objects.get_or_create(user=existing_user)
    print("🔑 Existing user token:", token.key)



@api_view(['GET'])
@permission_classes([AllowAny])
def get_general_test(request):
    """Return all general test questions."""
    questions = [
        {"id": 1, "question": "How old are you?"},
        {"id": 2, "question": "Do you sometimes feel nervous or on edge for no clear reason?"},
        {"id": 3, "question": "Have you ever had sudden moments where you felt scared or panicked out of nowhere?"},
        {"id": 4, "question": "Do you notice your breathing getting faster when you feel anxious or stressed?"},
        {"id": 5, "question": "Do you tend to sweat a lot when you’re worried or nervous?"},
        {"id": 6, "question": "Do you find it hard to focus on things, even when you try?"},
        {"id": 7, "question": "Do you often have trouble falling asleep or staying asleep through the night?"},
        {"id": 8, "question": "Has stress or your mood made it harder for you to focus on work or school lately?"},
        {"id": 9, "question": "Do you ever feel like things won’t get better, no matter what you do?"},
        {"id": 10, "question": "Do you get frustrated or angry more easily than you’d like to?"},
        {"id": 11, "question": "Do you feel like you sometimes overreact to small problems?"},
        {"id": 12, "question": "Have your eating habits changed recently like eating too much or too little?"},
        {"id": 13, "question": "Have you ever had thoughts about not wanting to be here anymore?"},
        {"id": 14, "question": "Do you often feel tired or drained, even when you haven’t done much?"},
        {"id": 15, "question": "Do you have someone you trust that you can talk to when you’re feeling low?"},
        {"id": 16, "question": "Do you ever feel like you spend too much time on social media or can’t put your phone down?"},
        {"id": 17, "question": "Have you noticed your weight changing recently without a clear reason?"},
        {"id": 18, "question": "Do you prefer spending time alone instead of being around people?"},
        {"id": 19, "question": "Do bad memories or stressful thoughts pop up suddenly in your mind?"},
        {"id": 20, "question": "Do you get nightmares that feel stressful or remind you of bad experiences?"},
        {"id": 21, "question": "Do you avoid certain people or activities because they make you uncomfortable or anxious?"},
        {"id": 22, "question": "Do you often catch yourself thinking negatively about yourself or life?"},
        {"id": 23, "question": "Do you struggle to stay focused on one thing for long?"},
        {"id": 24, "question": "Do you sometimes blame yourself for things that aren’t really your fault?"},
        {"id": 25, "question": "Have you ever seen or heard things that others couldn’t?"},
        {"id": 26, "question": "Do you find yourself repeating certain actions or routines over and over?"},
        {"id": 27, "question": "Do you notice your mood or energy changing depending on the season (like feeling low in winter)?"},
        {"id": 28, "question": "Do you sometimes feel full of energy or excitement for no clear reason?"}
    ]
    return JsonResponse({"questions": questions})

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_general_test(request):
    """Receive answers from Flutter, predict disorder, and return suggestions."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        answers = data.get('answers', [])

        # تأكيد وجود 28 إجابة
        if not answers or len(answers) != 28:
            return JsonResponse({"error": "28 answers are required"}, status=400)

        if model is None or label_encoder is None:
            return JsonResponse({"error": "Model or encoder not loaded"}, status=500)

        # تحويل الإجابات إلى الشكل المطلوب للموديل
        features = np.array([answers])
        prediction = model.predict(features)
        predicted_disorder = label_encoder.inverse_transform([np.argmax(prediction)])[0]

        # 🧠 تمارين مقترحة حسب النتيجة
        suggestions = {
            "Major Depressive Disorder (MDD)": ["Journaling", "Light exercise", "Daily routine"],
            "Autism Spectrum Disorder (ASD)": ["Structured activities", "Reduce screen time", "Positive reinforcement"],
            "Loneliness": ["Connect with people", "Volunteer", "Join social groups"],
            "Bipolar": ["Sleep schedule", "Mood tracking", "Avoid stress"],
            "Anxiety": ["Deep breathing", "Meditation", "Limit caffeine"],
            "Post-Traumatic Stress Disorder (PTSD)": ["Therapy", "Grounding exercises", "Mindfulness"],
            "Sleeping Disorder": ["Sleep hygiene", "Avoid screens before bed", "Consistent schedule"],
            "Psychotic Depression": ["Therapy support", "Regular sleep", "Avoid stressors"],
            "Eating Disorder": ["Balanced meals", "Avoid mirrors", "Support groups"],
            "Attention-Deficit/Hyperactivity Disorder (ADHD)": ["Task lists", "Short breaks", "Focus exercises"],
            "Persistent Depressive Disorder (PDD)": ["Therapy", "Routine planning", "Small goals"],
            "Obsessive-Compulsive Disorder (OCD)": ["CBT", "Avoid reassurance", "Routine stability"]
        }

        return JsonResponse({
            "predicted_disorder": predicted_disorder,
            "suggestions": suggestions.get(predicted_disorder, [])
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

