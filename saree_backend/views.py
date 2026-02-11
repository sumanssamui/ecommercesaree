from django.http import JsonResponse

def root_api(request):
    response = JsonResponse({"message": "API is working"})
    return response