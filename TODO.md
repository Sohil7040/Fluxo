# Expense Management System TODO

## Project Setup
- [x] Create project directories: backend/, frontend/
- [x] Set up docker-compose.yml for PostgreSQL
- [x] Initialize Django project in backend/
- [x] Create Django app 'expenses'
- [x] Install backend dependencies (Django, DRF, JWT, pytesseract, etc.)
- [x] Configure settings.py for PostgreSQL, JWT, CORS

## Database Models
- [x] Define Custom User model with roles (Admin, Manager, Employee)
- [x] Company model
- [x] Expense model (amount, category, description, date, currency, status)
- [x] ApprovalRule model (percentage, specific approver, hybrid)
- [x] ApprovalStep model (sequence, approver)
- [x] ExpenseApproval model (links expense to approvers, status, comments)

## Authentication & User Management
- [ ] Implement JWT authentication
- [ ] Signup view: auto-create company and admin user
- [ ] Admin views: create users, assign roles, set manager relationships
- [ ] Role-based permissions

## Expense Submission
- [ ] Employee API: submit expense (convert currency if needed)
- [ ] View own expense history

## Approval Workflow
- [ ] Manager/Admin APIs: view pending approvals, approve/reject with comments
- [ ] Logic for sequential approvals
- [ ] Conditional approval logic (percentage, specific approver)

## Additional Features
- [ ] OCR endpoint: upload receipt, extract data using pytesseract
- [ ] Currency API integration: fetch countries/currencies, exchange rates
- [ ] Utility functions for currency conversion

## Frontend Setup
- [x] Initialize React app in frontend/
- [x] Install dependencies (axios, react-router, Material-UI, etc.)
- [x] Set up routing

## Frontend Components
- [x] Login/Signup component
- [x] Dashboard (role-based)
- [x] Expense submission form (with receipt upload)
- [x] Expense history view
- [x] Approval list and actions
- [ ] Admin user management interface

## Integration & Testing
- [ ] Connect React to Django APIs
- [ ] Run migrations, start servers
- [ ] Test authentication, expense submission, approvals
- [ ] Test OCR and currency features
