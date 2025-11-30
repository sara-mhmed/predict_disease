from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models import GeneralTestResult
from .serializers import GeneralTestResultSerializer
from ..utils import FEATURES_NAME, predict_disorder

class GeneralTestApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        answers = request.data.get("answers", [])
        if len(answers) != 28:
            return Response({"error": "28 answers required"}, status=400)

        answers_numeric = []
        for i, val in enumerate(answers):
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

        return Response(result)

class TestResultsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = GeneralTestResult.objects.filter(user=request.user).order_by('-created_at')
        serializer = GeneralTestResultSerializer(results, many=True)
        return Response(serializer.data)
