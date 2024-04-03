from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler400 = lambda request, exception=None: JsonResponse({'error': 'Bad Request (400)'}, status=400)
handler404 = lambda request, exception=None: JsonResponse({'error': 'Not Found (404)'}, status=404)
handler500 = lambda request, exception=None: JsonResponse({'error': 'Server Error (500)'}, status=500)
