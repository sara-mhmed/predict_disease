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
            "user": request.user.username  # optional
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# Create default admin if not exist
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

# 🧮 Receive answers and return prediction
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_general_test(request):
    """Receive answers from Flutter, predict disorder, and return suggestions."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        answers = data.get('answers', [])

        # check if user answer 28 question or not
        if not answers or len(answers) != 28:
            return JsonResponse({"error": "28 answers are required"}, status=400)

        if model is None or label_encoder is None:
            return JsonResponse({"error": "Model or encoder not loaded"}, status=500)

        # check the age for first question , other questions
        answers_numeric = []
        for i, ans in enumerate(answers):
            if i == 0:
                try:
                    age_value = float(ans)
                    if age_value < 0:
                        return JsonResponse({"error": "Age must be a positive number"}, status=400)
                    answers_numeric.append(age_value)
                except:
                    return JsonResponse({"error": "Invalid age format"}, status=400)
            else:
                answers_numeric.append(1 if str(ans).lower() in ["yes", "true", "1"] else 0)

        # change them to numbers
        features = np.array([answers_numeric], dtype= float)

        prediction = model.predict(features)
        predicted_disorder = label_encoder.inverse_transform([np.argmax(prediction)])[0]

        info = {
                "Major Depressive Disorder (MDD)": {
                    "description": "You may be showing signs of depression such as low mood and loss of interest.",
                    "suggestions": ["Try journaling", "Do light exercise", "Follow a daily routine"],
                    "video": "https://www.youtube.com/watch?v=inpok4MKVLM"
                },
                "Autism Spectrum Disorder (ASD)": {
                    "description": "You may have challenges in social communication or interaction patterns.",
                    "suggestions": ["Follow structured activities", "Reduce screen time", "Use positive reinforcement"],
                    "video": "https://www.youtube.com/watch?v=wklfY1n7tNg"
                },
                "Loneliness": {
                    "description": "You may be experiencing loneliness or social disconnection.",
                    "suggestions": ["Reach out to old friends", "Join a community", "Volunteer regularly"],
                    "video": "https://www.youtube.com/watch?v=kF8YzICpKaU"
                },
                "Bipolar": {
                    "description": "You may experience mood swings between high energy and sadness.",
                    "suggestions": ["Keep a sleep routine", "Track your moods", "Avoid stress triggers"],
                    "video": "https://www.youtube.com/watch?v=U5m0pH6A0l8"
                },
                "Anxiety": {
                    "description": "You may be showing symptoms of anxiety such as restlessness or overthinking.",
                    "suggestions": ["Try deep breathing", "Practice mindfulness", "Limit caffeine intake"],
                    "video": "https://www.youtube.com/watch?v=aNXKjGFUlMs"
                },
                "Post-Traumatic Stress Disorder (PTSD)": {
                    "description": "You may experience flashbacks, nightmares, or anxiety from past trauma.",
                    "suggestions": ["Try grounding techniques", "Seek therapy", "Practice mindfulness"],
                    "video": "https://www.youtube.com/watch?v=8qW7xrW7g1Y"
                },
                "Sleeping Disorder": {
                    "description": "You may have difficulty sleeping or maintaining sleep quality.",
                    "suggestions": ["Keep consistent sleep hours", "Avoid screens before bed", "Create a calm bedtime routine"],
                    "video": "https://www.youtube.com/watch?v=ZPZsK_Fc3X4"
                },
                "Psychotic Depression": {
                    "description": "You may experience depressive thoughts with delusional ideas.",
                    "suggestions": ["Seek professional therapy", "Follow a stable routine", "Reduce stress exposure"],
                    "video": "https://www.youtube.com/watch?v=wGPJpG6XwRg"
                },
                "Eating Disorder": {
                    "description": "You may have an unhealthy relationship with food or body image.",
                    "suggestions": ["Eat balanced meals", "Avoid comparison", "Talk to a counselor"],
                    "video": "https://www.youtube.com/watch?v=UYLa9D8pKSM"
                },
                "Attention-Deficit/Hyperactivity Disorder (ADHD)": {
                    "description": "You may have trouble focusing or staying still for long periods.",
                    "suggestions": ["Break tasks into parts", "Take short breaks", "Use focus exercises"],
                    "video": "https://www.youtube.com/watch?v=5U3Vfu4g8kI"
                },
                "Persistent Depressive Disorder (PDD)": {
                    "description": "You may experience long-term mild depression with low energy or motivation.",
                    "suggestions": ["Follow a daily plan", "Set small goals", "Engage in enjoyable activities"],
                    "video": "https://www.youtube.com/watch?v=z7I2h8s4p9E"
                },
                "Obsessive-Compulsive Disorder (OCD)": {
                    "description": "You may experience repetitive thoughts or actions you feel forced to do.",
                    "suggestions": ["Practice CBT techniques", "Avoid seeking reassurance", "Stick to a routine"],
                    "video": "https://www.youtube.com/watch?v=Dp7LJXZVmsA"
                }
            }

        result = info.get(predicted_disorder, {
                "description": "No clear match found.",
                "suggestions": [],
                "video": ""
            })

        return JsonResponse({
                "predicted_disorder": predicted_disorder,
                "description": result["description"],
                "suggestions": result["suggestions"],
                "video": result["video"]
            })

    except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
