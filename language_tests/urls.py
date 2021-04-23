from django.urls import path

from language_tests import views


urlpatterns = [
    path('', views.language_test_type_list, name='language_test_type_list'),
    path('<int:pk>/', views.language_test, name='language_test'),
    path('result/', views.test_result, name='test_result'),
]
