# Expense Management System

A full-stack expense management application built with Django REST Framework and React.

## Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Expense Submission**: Employees can submit expenses with receipt uploads
- **Approval Workflow**: Managers and admins can approve/reject expenses
- **OCR Processing**: Automatic text extraction from receipt images using Tesseract
- **Currency Conversion**: Support for multiple currencies with automatic conversion
- **Role-based Access**: Admin, Manager, and Employee roles with different permissions

## Tech Stack

### Backend
- Django 5.2.7
- Django REST Framework
- JWT Authentication
- SQLite Database
- Tesseract OCR
- Pillow for image processing

### Frontend
- React 19.2.0
- Material-UI
- Axios for API calls
- React Router for navigation

## Installation & Setup

### Prerequisites
- Python 3.12+
- Node.js 16+
- Tesseract OCR installed on your system

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Usage

### Getting Started

1. **Sign Up**: Create a new company account at `/signup`
   - This creates a company and makes you the admin
   - You can then create users and assign roles

2. **Login**: Use your credentials to log in at `/login`

### User Roles

#### Admin
- Can view all expenses in the company
- Can create and manage users
- Can approve/reject any expense
- Can set up approval rules

#### Manager
- Can view expenses that need their approval
- Can approve/reject expenses assigned to them
- Can view their own expenses

#### Employee
- Can submit new expenses
- Can view their own expense history
- Can upload receipt images

### Expense Submission

1. Navigate to "Add Expense" from the dashboard
2. Fill in the expense details:
   - Amount and currency
   - Category and description
   - Date
   - Upload receipt image (optional)
3. Submit the expense

### Approval Process

1. Managers/Admins can view pending approvals
2. They can approve or reject expenses with comments
3. The system automatically handles the approval workflow based on company rules

### OCR Feature

- Upload receipt images to automatically extract text
- The system will suggest amounts and other details
- Currently supports basic text extraction (can be enhanced)

### Currency Conversion

- The system supports multiple currencies
- Automatic conversion to company currency
- Uses free exchange rate API (exchangerate-api.com)

## API Endpoints

### Authentication
- `POST /api/signup/` - Create new company and admin user
- `POST /api/login/` - User login

### Expenses
- `GET /api/expenses/` - List expenses (role-based)
- `POST /api/expenses/` - Create new expense
- `GET /api/expenses/{id}/` - Get expense details
- `PUT /api/expenses/{id}/` - Update expense
- `DELETE /api/expenses/{id}/` - Delete expense

### Approvals
- `GET /api/approvals/` - List pending approvals
- `POST /api/approvals/{id}/approve/` - Approve expense
- `POST /api/approvals/{id}/reject/` - Reject expense

### Users (Admin only)
- `GET /api/users/` - List company users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Utilities
- `POST /api/ocr/` - OCR processing for receipt images
- `GET /api/currencies/` - List supported currencies
- `POST /api/convert-currency/` - Convert between currencies

## Test Users

The system comes with pre-created test users:

- **Admin**: username: `admin`, password: `admin123`
- **Employee**: username: `employee1`, password: `emp123`

## Development

### Adding New Features

1. **Backend**: Add new models, views, and serializers in the `expenses` app
2. **Frontend**: Create new components and update routing
3. **API**: Follow RESTful conventions for new endpoints

### Database

The system uses SQLite by default. For production, consider switching to PostgreSQL:

1. Update `DATABASES` in `settings.py`
2. Install `psycopg2-binary`
3. Update `docker-compose.yml` if using Docker

### Deployment

For production deployment:

1. Set `DEBUG = False` in settings
2. Configure proper database
3. Set up static file serving
4. Use environment variables for sensitive data
5. Set up proper CORS origins

## Troubleshooting

### Common Issues

1. **OCR not working**: Ensure Tesseract is installed on your system
2. **Currency conversion failing**: Check internet connection (uses external API)
3. **File upload issues**: Check MEDIA_ROOT and MEDIA_URL settings
4. **CORS errors**: Verify CORS_ALLOWED_ORIGINS in settings

### Logs

Check the Django console output for backend errors and browser console for frontend errors.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.
