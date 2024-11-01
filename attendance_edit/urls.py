from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register_attendance, name='register_attendance'),
    path('edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
