from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('expenses/', views.ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('approvals/', views.ApprovalListView.as_view(), name='approval-list'),
    path('approvals/<int:pk>/approve/', views.ApproveExpenseView.as_view(), name='approve-expense'),
    path('approvals/<int:pk>/reject/', views.RejectExpenseView.as_view(), name='reject-expense'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('ocr/', views.OCRView.as_view(), name='ocr'),
    path('currencies/', views.CurrencyListView.as_view(), name='currency-list'),
    path('convert-currency/', views.CurrencyConversionView.as_view(), name='currency-conversion'),
]
