import os
import numpy as np
from tensorflow.keras.models import load_model
import joblib

MODEL_PATH = os.path.join('ml_models', 'general_model.h5')
ENCODER_PATH = os.path.join('ml_models', 'label_encoder.pkl')

try:
    model = load_model(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
except Exception as e:
    print("Error loading model or encoder:", e)
    model = None
    label_encoder = None

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

INFO = {
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

def predict_disorder(answers_numeric):
    if model is None or label_encoder is None:
        return {
            "predicted_disorder": "Unknown",
            "description": "Model not loaded",
            "suggestions": [],
            "video": ""
        }
    features = np.array([answers_numeric], dtype=float)
    prediction = model.predict(features)
    predicted_disorder = label_encoder.inverse_transform([np.argmax(prediction)])[0]
    result = INFO.get(predicted_disorder, {"description": "No clear match found.", "suggestions": [], "video": ""})
    return {
        "predicted_disorder": predicted_disorder,
        "description": result["description"],
        "suggestions": result["suggestions"],
        "video": result["video"]
    }
