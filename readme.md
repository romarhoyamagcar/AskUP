📘 AskUP – Student Q&A Platform

AskUP is a Django-based Question-and-Answer (Q&A) platform designed for students and administrators. It provides a secure and structured environment where students can ask questions, get answers, and engage with academic discussions, while administrators can manage content, users, and the overall platform experience.

🚀 Project Overview

AskUP is built to empower collaborative learning within an academic environment. The platform ensures that:

Students have a safe space to ask questions.

Admins can moderate, organize, and manage the discussions.

Authentication (login/signup) is required to access student or admin features.

A clean and responsive UI is maintained with static assets (CSS, JS, images).

🎯 Goals and Expectations
✅ Core Expectations

User Authentication

Secure Login & Signup system (required for both students and admins).

Passwords stored safely using Django’s built-in authentication.

Role-based access control:

Students: Can ask questions and view answers.

Admins: Can manage users, questions, and content.

Q&A System

Students can submit questions.

Answers can be posted by admins or instructors.

Question filtering & organization (by category, recent, unanswered).

Admin Panel

Access to Django Admin for user & content management.

Ability to approve/remove questions if needed.

Frontend (Static Files)

Centralized static/ directory for CSS, JS, and images.

Modern and responsive design for all devices.

💡 Future Enhancements (Expected Features)

Voting system for best answers.

Search functionality to quickly find questions.

Student profiles with activity history.

Email verification for signup.

API support for mobile integration.

Gamification (badges, points for active participation).

⚙️ Installation & Setup

Clone repository:

git clone https://github.com/your-username/askup.git
cd askup


Create virtual environment & install dependencies:

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt


Run migrations:

python manage.py migrate


Create superuser (for admin access):

python manage.py createsuperuser


Start server:

python manage.py runserver


Access the app:

Student Portal: http://127.0.0.1:8000/

Admin Panel: http://127.0.0.1:8000/admin/

📂 Project Structure
AskUP/
├── askup/                # Main Django project folder
│   ├── settings.py       # Configurations (with STATIC files setup)
│   ├── urls.py           # URL routing
│   └── wsgi.py
├── qna/                   # Q&A App (students’ questions)
│   ├── templates/qa/     # HTML templates
│   ├── static/qa/        # CSS, JS, Images
│   ├── models.py         # Question models
│   ├── views.py          # Business logic
│   └── urls.py
├── users/                # User Management App (Login/Signup)
│   ├── templates/users/  # Auth templates
│   ├── models.py         # Custom User model (if needed)
│   ├── views.py
│   └── urls.py
├── manage.py
└── README.md

🔐 Authentication Workflow

New users must sign up before accessing the platform.

Returning users log in to access Q&A features.

Admins can log in separately via Django Admin.

Unauthorized users are redirected to login/signup pages.

👥 Roles
🧑‍🎓 Student

Sign up & log in.

Post questions.

View answers.

Edit/Delete own questions.

🛠️ Admin

Full access via Admin Panel.

Manage questions, users, and site settings.

Moderate content and approve flagged questions.

📝 License

MIT License – free to use, modify, and distribute.

# AskUP - Student Q&A Platform

A Django-based academic Q&A platform where students can ask questions, get answers, and learn together with comprehensive admin management system.

## 📁 Project Structure

```
AskUP/
├── askup/                          # Main Django project folder
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # Updated with users app and templates config
│   ├── urls.py                     # Routes to both qna and users apps
│   └── wsgi.py
├── qna/                            # Q&A App (questions & answers)
│   ├── migrations/
│   ├── templates/qna/
│   │   ├── ask_question.html       # Question posting form
│   │   ├── home.html               # Main homepage with questions list
│   │   └── question_detail.html    # Question detail with answers
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # Question and Answer models
│   ├── tests.py
│   ├── urls.py                     # Q&A routes only
│   └── views.py                    # Q&A business logic
├── users/                          # User Management App (Authentication)
│   ├── migrations/
│   ├── templates/users/
│   │   ├── admin_dashboard.html    # Admin dashboard with statistics
│   │   ├── admin_login.html        # Secret admin login
│   │   ├── admin_signup.html       # Secret admin registration
│   │   ├── login.html              # Student login
│   │   └── signup.html             # Student registration
│   ├── __init__.py
│   ├── admin.py                    # UserProfile admin registration
│   ├── apps.py
│   ├── models.py                   # UserProfile model
│   ├── tests.py
│   ├── urls.py                     # Authentication routes
│   └── views.py                    # Authentication logic
├── templates/                      # Shared templates
│   └── base.html                   # Base template with navigation
├── static/
│   ├── css/
│   │   └── style.css               # Enhanced global styles with logo styling
│   ├── images/
│   │   └── logo.png                # AskUP logo (circular with border)
│   └── js/
├── db.sqlite3
├── manage.py
└── readme.md                       # This file
```

## 🚀 Features Implemented

### Student Features
- **User Registration**: Custom signup form with email, first_name, last_name
- **User Login/Logout**: Secure authentication system
- **Ask Questions**: Protected question posting (login required)
- **View Questions**: Browse all questions and answers
- **Answer Questions**: Post answers to existing questions (login required)
- **Role Badges**: Visual indicators for Student vs Admin users

### Admin Features
- **Secret Admin Registration**: Hidden registration system with secret key
- **Separate Admin Login**: Independent admin authentication
- **Admin Dashboard**: Comprehensive overview with statistics and management
- **User Management**: View recent users and their roles
- **Question Oversight**: Monitor recent questions and answers
- **System Information**: Access to registration URLs and secret keys

## 🔐 Authentication System

### Student Authentication
- **Login URL**: `/login/`
- **Registration URL**: `/signup/`
- **Logout URL**: `/logout/`

### Admin Authentication (Secret System)
- **Admin Login URL**: `/panel/login/`
- **Admin Registration URL**: `/panel/signup/?secret=admin_registration_2024`
- **Admin Dashboard URL**: `/panel/dashboard/`
- **Secret Key**: `ASKUP_ADMIN_2024`

### Security Features
- Secret URL parameter prevents unauthorized admin registration access
- Secret key validation in admin registration form
- Role-based access control using `is_staff` flag
- Separate authentication workflow for admins vs students
- Protected views with `@login_required` and `@user_passes_test` decorators

## 🎨 UI/UX Features

### Design Elements
- **Bootstrap 5**: Modern responsive framework
- **Font Awesome**: Professional icons throughout
- **Gradient Backgrounds**: Modern visual appeal
- **Circular Logo**: Professional branding with hover effects
- **Role Badges**: Visual user role identification
- **Message System**: User feedback for all actions

### Logo Implementation
- Circular logo with white border in navigation
- Hover effects with scaling and shadow
- Consistent branding across all admin templates
- External CSS styling for maintainability

## 📊 Database Models

### QnA App Models
```python
# Question Model
class Question(models.Model):
    title = models.CharField(max_length=200)
    details = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# Answer Model
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Users App Models
```python
# UserProfile Model (for future enhancements)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
```

## 🛠 Technical Implementation

### URL Configuration
```python
# Main URLs (askup/urls.py)
urlpatterns = [
    path('admin/', admin.site.urls),        # Django Admin
    path('', include('qna.urls')),          # Q&A functionality
    path('', include('users.urls')),        # Authentication functionality
]

# Users URLs (users/urls.py)
urlpatterns = [
    # Student Authentication
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    
    # Admin Authentication (Secret URLs)
    path('panel/login/', views.admin_login, name='admin_login'),
    path('panel/signup/', views.admin_signup, name='admin_signup'),
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

# QnA URLs (qna/urls.py)
urlpatterns = [
    path('', views.home, name='home'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('ask/', views.ask_question, name='ask_question'),
]
```

### Settings Configuration
```python
# Added to INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'qna',
    'users',  # Added for authentication system
]

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Added for shared templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Authentication settings
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'
```

## 🎯 Key Changes Made

### 1. Project Restructuring
- Separated authentication logic into dedicated `users/` app
- Moved authentication views and templates from `qna/` to `users/`
- Created shared `templates/` directory for consistent layouts
- Updated main URL configuration to include both apps

### 2. Authentication System Enhancement
- Implemented custom `SignUpForm` with additional fields
- Created separate admin authentication workflow
- Added secret key validation for admin registration
- Implemented role-based access control

### 3. Template System Overhaul
- Created shared `base.html` template for consistent navigation
- Updated all QnA templates to extend shared base
- Designed admin-specific templates with security themes
- Added responsive design with Bootstrap 5

### 4. Security Implementation
- Secret URL parameters for admin registration
- Secret key validation in forms
- Protected views with decorators
- Separate admin and student authentication flows

### 5. UI/UX Improvements
- Added circular logo with professional styling
- Implemented role badges for user identification
- Enhanced CSS with modern gradients and animations
- Added message system for user feedback

## 🚦 How to Run

1. **Install Dependencies**:
   ```bash
   pip install django
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py makemigrations users
   python manage.py migrate
   ```

3. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

4. **Access the Application**:
   - **Homepage**: `http://127.0.0.1:8000/`
   - **Student Login**: `http://127.0.0.1:8000/login/`
   - **Admin Login**: `http://127.0.0.1:8000/panel/login/`

## 🔑 Admin Access

### Creating First Admin
1. Visit: `http://127.0.0.1:8000/panel/signup/?secret=admin_registration_2024`
2. Enter the secret key: `ASKUP_ADMIN_2024`
3. Complete the registration form
4. Login at: `http://127.0.0.1:8000/panel/login/`

### Admin Dashboard Features
- View total questions, answers, students, and admins
- Monitor recent questions and new user registrations
- Quick access to Django admin panel
- System information with registration URLs and secret keys
- User management and oversight capabilities

## 📝 Notes

- The system maintains separation between Django's built-in admin (`/admin/`) and the custom admin panel (`/panel/`)
- All authentication views include proper error handling and user feedback
- The logo system uses external CSS for maintainability
- Role-based UI elements provide clear user experience differentiation
- The secret admin system ensures only authorized personnel can create admin accounts

## 🔒 Security Considerations

- Secret keys should be changed in production environments
- Admin registration URLs should be shared only with trusted personnel
- The system uses Django's built-in authentication for secure password storage
- CSRF protection is enabled on all forms
- Role validation prevents unauthorized access to admin features