from django.shortcuts import render
from .models import GeneralTestResult
from .utils import FEATURES_NAME, predict_disorder

def general_test_view(request):
    result_text = ""
    error_message = ""
    result = None
    if request.method == "POST":
        answers_numeric = []
        for i, feature in enumerate(FEATURES_NAME):
            val = request.POST.get(feature, 0)
            if i == 0:
                try:
                    age_value = float(val)
                    if age_value < 0 or age_value > 100:
                        error_message = "please enter a valid age between 0 and 100."
                        break  # نوقف المعالجة
                except ValueError:
                    error_message = "please enter a numeric value for age."
                    break

                answers_numeric.append(age_value)
            else:
                try:
                    v = int(val)
                    answers_numeric.append(1 if v == 1 else 0)
                except:
                    answers_numeric.append(
                        1 if str(val).lower() in ["yes", "true", "1"] else 0
                    )
        if not error_message:
            result = predict_disorder(answers_numeric)
            predicted = result.get("predicted_disorder", "Unknown")
            description = result.get("description", "")
            suggestions = result.get("suggestions", [])
            video = result.get("video", "")

            result_text = f"Predicted Disorder: {predicted}"

            if request.user.is_authenticated and result is not None:
                GeneralTestResult.objects.create(
                    user=request.user,
                    predicted_disorder=predicted,
                    description=description,
                    suggestions=suggestions,
                    video_url=video,
                    answers=answers_numeric
                )

    return render(request, "general_test.html", {"result": result_text, "features": FEATURES_NAME, "error_message":error_message})
