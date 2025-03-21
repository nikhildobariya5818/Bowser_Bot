from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import run_bot
import threading

@csrf_exempt
def start_bot(request):
    """API endpoint to start the bot."""
    if request.method == "POST":
        thread = threading.Thread(target=run_bot)
        thread.start()
        return JsonResponse({"message": "Bot started"}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=400)
