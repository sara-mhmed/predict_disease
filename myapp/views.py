from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib
from .models import GeneralTestResult

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

# ---- Depression Model ----
try:
    
    print("🧠 Loading Depression model...")
    depression_model = joblib.load(os.path.join('ml_models', 'depression_model.pkl'))
    scaler = joblib.load(os.path.join('ml_models', 'scaler.pkl'))
    print("✅ Depression model and scaler loaded successfully!")
except Exception as e:
    print("❌ Error loading depression model or scaler:", e)
    depression_model = None
    scaler = None

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
            "user": request.user.username  
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# Receive answers and return prediction
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
                    "video": "https://youtu.be/4Talws29mys?si=Ec6dniPHrLkXwwkK"
                },
                "Loneliness": {
                    "description": "You may be experiencing loneliness or social disconnection.",
                    "suggestions": ["Reach out to old friends", "Join a community", "Volunteer regularly"],
                    "video":"https://youtu.be/GckT5n9Ik1s"
                },
                "Bipolar": {
                    "description": "You may experience mood swings between high energy and sadness.",
                    "suggestions": ["Keep a sleep routine", "Track your moods", "Avoid stress triggers"],
                    "video": "https://www.youtube.com/watch?v=inpok4MKVLM"
                },
                "Anxiety": {
                    "description": "You may be showing symptoms of anxiety such as restlessness or overthinking.",
                    "suggestions": ["Try deep breathing", "Practice mindfulness", "Limit caffeine intake"],
                    "video": "https://youtu.be/SNqYG95j_UQ"
                },
                "Post-Traumatic Stress Disorder (PTSD)": {
                    "description": "You may experience flashbacks, nightmares, or anxiety from past trauma.",
                    "suggestions": ["Try grounding techniques", "Seek therapy", "Practice mindfulness"],
                    "video": "https://youtu.be/LiUnFJ8P4gM?si=1p_ivB984-f8CWAF"
                },
                "Sleeping Disorder": {
                    "description": "You may have difficulty sleeping or maintaining sleep quality.",
                    "suggestions": ["Keep consistent sleep hours", "Avoid screens before bed", "Create a calm bedtime routine"],
                    "video": "https://youtu.be/ywTaRqSbQpw"
                },
                "Psychotic Depression": {
                    "description": "You may experience depressive thoughts with delusional ideas.",
                    "suggestions": ["Seek professional therapy", "Follow a stable routine", "Reduce stress exposure"],
                    "video": "https://youtu.be/LiUnFJ8P4gM"
                },
                "Eating Disorder": {
                    "description": "You may have an unhealthy relationship with food or body image.",
                    "suggestions": ["Eat balanced meals", "Avoid comparison", "Talk to a counselor"],
                    "video": "https://youtu.be/LiUnFJ8P4gM?si=1p_ivB984-f8CWAF"
                },
                "Attention-Deficit/Hyperactivity Disorder (ADHD)": {
                    "description": "You may have trouble focusing or staying still for long periods.",
                    "suggestions": ["Break tasks into parts", "Take short breaks", "Use focus exercises"],
                    "video": "https://youtu.be/rTIv5X8Bo1w"
                },
                "Persistent Depressive Disorder (PDD)": {
                    "description": "You may experience long-term mild depression with low energy or motivation.",
                    "suggestions": ["Follow a daily plan", "Set small goals", "Engage in enjoyable activities"],
                    "video": "https://youtu.be/sFtP0HWvu0k?si=ejxXUWJJPgLXc0QU"
                },
                "Obsessive-Compulsive Disorder (OCD)": {
                    "description": "You may experience repetitive thoughts or actions you feel forced to do.",
                    "suggestions": ["Practice CBT techniques", "Avoid seeking reassurance", "Stick to a routine"],
                    "video": "https://youtu.be/SNqYG95j_UQ?si=NH_kSHp3Mbf7ZYeS"
                    
                }
            }

        result = info.get(predicted_disorder, {
                "description": "No clear match found.",
                "suggestions": [],
                "video": ""
            })
       # Save only for authenticated users
        if request.user.is_authenticated:
            GeneralTestResult.objects.create(
                user=request.user,
                predicted_disorder=predicted_disorder,
                description=result["description"],
                suggestions=result["suggestions"],
                video_url=result["video"],
                answers=answers_numeric
            )

        return JsonResponse({
            "predicted_disorder": predicted_disorder,
            "description": result["description"],
            "suggestions": result["suggestions"],
            "video": result["video"]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    # Retrieve all test results #
@api_view(['GET'])
@permission_classes([AllowAny])
def test_results(request):
    try:
        if request.user.is_authenticated:
            results = GeneralTestResult.objects.filter(user=request.user).order_by('-created_at')
        else:
            results = []

        results_data = [{
            "id": result.id,
            "predicted_disorder": result.predicted_disorder,
            "description": result.description,
            "suggestions": result.suggestions,
            "video_url": result.video_url,
            "answers": result.answers,
            "created_at": result.created_at
        } for result in results]

        return JsonResponse({"results": results_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# depression questionnaire page

def predict_depression(request):
    result = None 

    if request.method == 'POST':
        #Read data from the form html 
        try:
            gender = request.POST['gender']
            age = float(request.POST['age'])
            work_pressure = float(request.POST['pressure'])
            job_satisfaction = float(request.POST['satisfaction'])
            sleep_duration = request.POST['sleep']
            dietary = request.POST['diet']
            suicidal = request.POST['suicidal']
            work_hours = float(request.POST['study_hours'])
            financial_stress = float(request.POST['financial'])
            family_history = request.POST['family']
            
            # change value to numeric like in the model training
            gender = 1 if gender == 'Female' else 0
            suicidal = 1 if suicidal == 'Yes' else 0
            family_history = 1 if family_history == 'Yes' else 0

            sleep_map = {
                'Less than 5 hours': 3,
                '5-6 hours': 5.5,
                '7-8 hours': 7.5,
                'More than 8 hours': 10
            }
            sleep_duration = sleep_map.get(sleep_duration, 7.5)

            diet_map = {
                'Unhealthy': 0,
                'Moderate': 2.5,
                'Healthy': 5
            }
            dietary = diet_map.get(dietary, 2.5)
            # prepare the features for prediction from dataset
            input_data = pd.DataFrame([[
                gender, age, work_pressure, job_satisfaction, sleep_duration,
                dietary, suicidal, work_hours, financial_stress, family_history
            ]], columns=[
                'Gender', 'Age', 'Work Pressure', 'Job Satisfaction', 
                'Sleep Duration', 'Dietary Habits', 
                'Have you ever had suicidal thoughts ?', 
                'Work Hours', 'Financial Stress', 'Family History of Mental Illness'
            ])

            numeric_cols = ['Age', 'Work Pressure', 'Job Satisfaction', 'Work Hours', 'Financial Stress']
            input_data [numeric_cols] = scaler.transform(input_data[numeric_cols])

            prediction = depression_model.predict(input_data)[0]

            print("🧠 Prediction:", prediction)
            if int(prediction) == 1:
                result = " You may be showing significant signs of depression. 😔"
            else:
                result = " You are unlikely to be experiencing depression. 🙂"

        except Exception as e:
            result = f" Error: {e}"
    return render(request, 'depression.html', {'result': result})


