from django.urls import path

from language_tests import views


urlpatterns = [
    path('', views.language_test_type_list, name='language_test_type_list'),
    path('<int:pk>/', views.language_test, name='language_test'),
    path('add/answer/', views.answer, name='create_answer'),
    path('add/question/', views.question, name='create_question'),
    path('add/test-type/', views.language_test_type, name='create_language_test_type'),
    path('result/', views.test_result, name='test_result'),
]
