from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.db.models import Q
from django.http import JsonResponse
import requests
import pytesseract
from PIL import Image
import io
from .models import User, Company, Expense, ApprovalRule, ApprovalStep
from .serializers import (
    UserSerializer, SignupSerializer, LoginSerializer, ExpenseSerializer,
    ApprovalStepSerializer, CompanySerializer
)
from .utils import convert_currency

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.role == 'manager':
            return Expense.objects.filter(user__company=user.company)
        else:
            return Expense.objects.filter(user=user)

    def perform_create(self, serializer):
        expense = serializer.save(user=self.request.user)
        # Convert currency if needed
        if expense.currency != self.request.user.company.currency:
            converted_amount = convert_currency(
                expense.amount, 
                expense.currency, 
                self.request.user.company.currency
            )
            expense.converted_amount = converted_amount
            expense.save()
        
        # Create approval steps based on company rules
        self.create_approval_steps(expense)

    def create_approval_steps(self, expense):
        """Create approval steps based on company approval rules"""
        try:
            approval_rule = expense.user.company.approval_rule
            if approval_rule.rule_type == 'specific' and approval_rule.specific_user:
                ApprovalStep.objects.create(
                    expense=expense,
                    step_number=1,
                    approver=approval_rule.specific_user
                )
            elif approval_rule.rule_type == 'percentage':
                # For percentage-based rules, manager approval is required
                if expense.user.manager:
                    ApprovalStep.objects.create(
                        expense=expense,
                        step_number=1,
                        approver=expense.user.manager
                    )
                else:
                    # If no manager, assign to admin
                    admin = User.objects.filter(company=expense.user.company, role='admin').first()
                    if admin:
                        ApprovalStep.objects.create(
                            expense=expense,
                            step_number=1,
                            approver=admin
                        )
        except ApprovalRule.DoesNotExist:
            # Default: manager approval if user has a manager, else admin
            if expense.user.manager:
                ApprovalStep.objects.create(
                    expense=expense,
                    step_number=1,
                    approver=expense.user.manager
                )
            else:
                # Assign to admin
                admin = User.objects.filter(company=expense.user.company, role='admin').first()
                if admin:
                    ApprovalStep.objects.create(
                        expense=expense,
                        step_number=1,
                        approver=admin
                    )

class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.role == 'manager':
            return Expense.objects.filter(user__company=user.company)
        else:
            return Expense.objects.filter(user=user)

class ApprovalListView(generics.ListAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            # Admin and manager can see all pending expenses in their company
            return Expense.objects.filter(
                user__company=user.company,
                status='pending'
            )
        return Expense.objects.none()

class ApproveExpenseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)
            user = request.user

            if (user.role in ['admin', 'manager']) and expense.user.company == user.company and expense.status == 'pending':
                # Admin and manager can approve any pending expense in their company
                approval_step = ApprovalStep.objects.filter(
                    expense=expense,
                    status='pending'
                ).first()
                if approval_step:
                    approval_step.status = 'approved'
                    approval_step.comments = request.data.get('comments', '')
                    approval_step.save()
                else:
                    # If no step, create one and approve
                    ApprovalStep.objects.create(
                        expense=expense,
                        step_number=1,
                        approver=user,
                        status='approved',
                        comments=request.data.get('comments', '')
                    )
            else:
                return Response(
                    {'error': 'You are not authorized to approve this expense'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if all approval steps are completed
            remaining_steps = ApprovalStep.objects.filter(
                expense=expense,
                status='pending'
            ).count()

            if remaining_steps == 0:
                expense.status = 'approved'
                expense.save()

            return Response({'message': 'Expense approved successfully'})
        except Expense.DoesNotExist:
            return Response(
                {'error': 'Expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class RejectExpenseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)
            user = request.user

            if (user.role in ['admin', 'manager']) and expense.user.company == user.company and expense.status == 'pending':
                # Admin and manager can reject any pending expense in their company
                approval_step = ApprovalStep.objects.filter(
                    expense=expense,
                    status='pending'
                ).first()
                if approval_step:
                    approval_step.status = 'rejected'
                    approval_step.comments = request.data.get('comments', '')
                    approval_step.save()
                else:
                    # If no step, create one and reject
                    ApprovalStep.objects.create(
                        expense=expense,
                        step_number=1,
                        approver=user,
                        status='rejected',
                        comments=request.data.get('comments', '')
                    )
            else:
                return Response(
                    {'error': 'You are not authorized to reject this expense'},
                    status=status.HTTP_403_FORBIDDEN
                )

            expense.status = 'rejected'
            expense.save()

            return Response({'message': 'Expense rejected successfully'})
        except Expense.DoesNotExist:
            return Response(
                {'error': 'Expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class UserListView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.filter(company=user.company)
        return User.objects.none()

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.filter(company=user.company)
        return User.objects.none()

class OCRView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            image_file = request.FILES['image']
            image = Image.open(image_file)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)
            
            # Try to extract amount and other details from the text
            # This is a simple implementation - you might want to use more sophisticated parsing
            lines = extracted_text.split('\n')
            amount = None
            date = None
            
            for line in lines:
                # Look for amount patterns
                import re
                amount_match = re.search(r'[\$€£¥]?\s*(\d+\.?\d*)', line)
                if amount_match and not amount:
                    amount = float(amount_match.group(1))
            
            return Response({
                'extracted_text': extracted_text,
                'suggested_amount': amount,
                'suggested_date': date
            })
        except Exception as e:
            return Response(
                {'error': f'OCR processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CurrencyListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Return a list of common currencies
        currencies = [
            {'code': 'USD', 'name': 'US Dollar'},
            {'code': 'EUR', 'name': 'Euro'},
            {'code': 'GBP', 'name': 'British Pound'},
            {'code': 'JPY', 'name': 'Japanese Yen'},
            {'code': 'CAD', 'name': 'Canadian Dollar'},
            {'code': 'AUD', 'name': 'Australian Dollar'},
            {'code': 'CHF', 'name': 'Swiss Franc'},
            {'code': 'CNY', 'name': 'Chinese Yuan'},
            {'code': 'INR', 'name': 'Indian Rupee'},
            {'code': 'BRL', 'name': 'Brazilian Real'},
        ]
        return Response(currencies)

class CurrencyConversionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        from_currency = request.data.get('from_currency')
        to_currency = request.data.get('to_currency')
        
        if not all([amount, from_currency, to_currency]):
            return Response(
                {'error': 'Amount, from_currency, and to_currency are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            converted_amount = convert_currency(amount, from_currency, to_currency)
            return Response({
                'original_amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': converted_amount
            })
        except Exception as e:
            return Response(
                {'error': f'Currency conversion failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
