from django.shortcuts import render
from .models import GeneralTestResult
from .utils import FEATURES_NAME, predict_disorder

def general_test_view(request):
    result_text = ""
    if request.method == "POST":
        answers_numeric = []
        for i, feature in enumerate(FEATURES_NAME):
            val = request.POST.get(feature, 0)
            if i == 0:
                try:
                    age_value = float(val)
                    answers_numeric.append(age_value if age_value >= 0 else 0)
                except:
                    answers_numeric.append(0)
            else:
                answers_numeric.append(1 if str(val).lower() in ["yes", "true", "1"] else 0)

        result = predict_disorder(answers_numeric)

        if request.user.is_authenticated:
            GeneralTestResult.objects.create(
                user=request.user,
                predicted_disorder=result["predicted_disorder"],
                description=result["description"],
                suggestions=result["suggestions"],
                video_url=result["video"],
                answers=answers_numeric
            )

        result_text = f"Predicted Disorder: {result['predicted_disorder']}"

    return render(request, "general_test.html", {"result": result_text, "features": FEATURES_NAME})
