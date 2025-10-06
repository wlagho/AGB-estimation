# SmallHolder Carbon Assessment Platform (SHCAP)

## Project Overview

SHCAP is a web-based platform designed to democratize access to carbon markets for smallholder farmers in East Africa through affordable, satellite-based above-ground biomass (AGB) estimation. The system uses machine learning models trained on multi-source remote sensing data to provide accurate carbon stock assessments and carbon market eligibility evaluations.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Sprint Structure](#sprint-structure)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

### Core Functionality

- **AGB Estimation**: Satellite-based above-ground biomass estimation using Random Forest models
- **Carbon Market Assessment**: Eligibility scoring and revenue potential analysis
- **Multi-source Data Integration**: Combines Sentinel-2, ALOS-2 PALSAR-2, GEDI L4A, and environmental data
- **Role-based Access Control**: Different access levels for Researchers, Project Developers, and Administrators

### Authentication & Security

- User registration with email verification
- Secure password hashing with bcrypt
- Two-factor authentication (2FA) via SMS and email
- Password reset functionality
- Session management with CSRF protection

### User Roles

1. **Researcher**: Basic AGB analysis and carbon stock calculations
2. **Project Developer**: Full carbon market assessment and detailed reporting
3. **Administrator**: User management and system analytics

## Technology Stack

### Backend

- **Framework**: Flask 2.3.3
- **Database**: PostgreSQL (via Supabase)
- **ORM**: Flask-SQLAlchemy 3.0.5
- **Authentication**: Flask-WTF, bcrypt
- **ML Libraries**: scikit-learn, pandas, numpy
- **Geospatial**: geopandas, rasterio

### Frontend

- **HTML/CSS/JavaScript**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Maps**: Leaflet.js
- **Charts**: Chart.js

### Data Sources

- **Satellite Data**: Sentinel-2, ALOS-2 PALSAR-2
- **LiDAR**: GEDI L4A (via HuggingFace)
- **Environmental**: DEM, Land Cover, Canopy Height

## Project Structure

```
AGB-estimation/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask application factory
│   │   ├── config.py                # Configuration settings
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py              # User model
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py            # Authentication routes
│   │   │   ├── forms.py             # WTForms definitions
│   │   │   └── utils.py             # Auth utilities
│   │   └── main/
│   │       ├── __init__.py
│   │       └── routes.py            # Main application routes
│   ├── app.py                       # Main application entry
│   ├── run_development.py           # Development server
│   └── requirements.txt             # Python dependencies
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── auth.css
│   │   └── js/
│   │       └── auth.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── demo.html
│       └── auth/
│           ├── login.html
│           ├── register.html
│           └── dashboard.html
├── scripts/
│   ├── agbd_data_processor.py       # Data processing pipeline
│   └── data_exploration.py          # Dataset exploration
├── data/
│   ├── raw/                         # Raw data files
│   ├── processed/                   # Processed datasets
│   └── sample_regions/              # Sample regions for demo
├── ml_models/                       # Trained ML models
├── docs/                            # Documentation
├── tests/                           # Test files
├── setup_supabase.py                # Database setup script
├── create_demo_users.py             # Demo user creation
├── .env.example                     # Environment variables template
├── .gitignore
└── README.md
```

## Prerequisites

- **Operating System**: Ubuntu 20.04+ (or similar Linux distribution)
- **Python**: 3.8 or higher
- **PostgreSQL**: 12+ (via Supabase)
- **Node.js**: 14+ (optional, for frontend tooling)
- **Git**: For version control
- **Supabase Account**: For database hosting

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/wlagho/AGB-estimation.git
cd AGB-estimation
```

### 2. Create Virtual Environment

```bash
python3 -m venv agb_env
```

```bash
source agb_env/bin/activate  
On Windows: agb_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
```

```bash
pip install -r backend/requirements.txt
```

## Configuration

### 1. Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Required environment variables:

```bash
# Flask Configuration
SECRET_KEY=your-very-secure-secret-key-change-this
FLASK_ENV=development
FLASK_DEBUG=1

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Database Configuration
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Email Configuration (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Twilio Configuration (for 2FA)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
```

### 2. Supabase Setup

1. Create a Supabase account at https://supabase.com
2. Create a new project
3. Navigate to Settings → Database
4. Copy your connection string
5. Update DATABASE_URL in .env

## Running the Application

### Development Server

```bash
python app.py
```

The application will be available at:

- Main site: http://localhost:5000
- Demo page: http://localhost:5000/demo
- Login: http://localhost:5000/auth/login
- Register: http://localhost:5000/auth/register

### Working on Issues

1. **Create feature branch**:

   ```bash
   git checkout -b feature/issue-name
   ```

2. **Implement feature**:
   - Write code
   - Test functionality
   - Update documentation

3. **Commit changes**:

   ```bash
   git add .
   git commit -m "Implement [feature description]"
   ```

4. **Push to remote**:

   ```bash
   git push origin feature/issue-name
   ```

5. **Create pull request** on GitHub

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Comment complex logic
- Keep functions focused and concise

## Sprint Structure

### Sprint 1: Authentication Foundation

- Login/Signup forms for all user types
- Password reset via email
- 2FA using SMS/email
- Role validation on login

**Deliverables**:

- Working authentication system
- User registration and login
- Role-based access control
- Password reset functionality
- Two-factor authentication

### Sprint 2: ML Pipeline & Data Processing

- AGBD dataset integration
- Random Forest model training
- Feature extraction pipeline
- Model validation and testing
- Sample region data preparation

**Deliverables**:

- Trained ML ensemble models
- Data processing pipeline
- Model performance metrics
- Sample regions for demo

### Sprint 3: Core AGB Functionality

- Interactive map interface
- Region selection functionality
- AGB estimation service
- Results visualization
- Carbon assessment logic

**Deliverables**:

- Working AGB estimation interface
- Carbon market assessment
- Results dashboard
- Export functionality

### Sprint 4: Integration & Polish

- Full system integration
- User testing and feedback
- Performance optimization
- Documentation completion
- Deployment preparation

**Deliverables**:

- Complete integrated system
- User documentation
- Deployment guide
- Final thesis documentation

<!-- ## Testing

### Manual Testing Checklist

#### Authentication (Issue #2)
- [ ] User can register with valid email/password
- [ ] Password strength validation works
- [ ] Login with correct credentials succeeds
- [ ] Login with incorrect credentials fails
- [ ] Logout clears session
- [ ] Role-based dashboard displays correctly
- [ ] Demo page accessible without login -->

<!-- #### Password Reset (Issue #3)
- [ ] Password reset email sent successfully
- [ ] Reset link works within expiry time
- [ ] Password successfully changed
- [ ] Old password no longer works
- [ ] New password works for login

#### Two-Factor Authentication (Issue #4)
- [ ] 2FA setup interface works
- [ ] SMS/Email codes received
- [ ] Valid codes accepted
- [ ] Invalid codes rejected
- [ ] Backup codes function correctly

#### Role Validation (Issue #5)
- [ ] Researcher access restricted appropriately
- [ ] Project Developer has full access
- [ ] Admin can manage users
- [ ] Unauthorized access blocked
- [ ] Role changes apply immediately

### Automated Testing

Run unit tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=backend tests/
```

## API Documentation

### Authentication Endpoints

#### Register User
```
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "researcher"
}

Response: 201 Created
{
  "message": "Registration successful",
  "user_id": 123
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "message": "Login successful",
  "user": {
    "id": 123,
    "email": "user@example.com",
    "role": "researcher"
  }
}
```

#### Logout
```
GET /auth/logout

Response: 302 Redirect to /
```

### AGB Estimation Endpoints (Sprint 2+)

Documentation will be updated after Sprint 2 implementation. -->

<!-- ## Deployment

### Heroku Deployment

1. **Install Heroku CLI**:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Heroku app**:
   ```bash
   heroku create shcap-app
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DATABASE_URL=your-database-url
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

### Docker Deployment

```bash
# Build image
docker build -t shcap .

# Run container
docker run -p 5000:5000 --env-file .env shcap
``` -->

## Contributing

### For Team Members

1. Fork the repository
2. Create feature branch
3. Make changes
4. Write/update tests
5. Submit pull request

<!-- ## Troubleshooting

### Common Issues

#### Database Connection Failed
```
Error: could not connect to server
```
**Solution**: Check DATABASE_URL in .env, verify Supabase project is active

#### Import Errors
```
ModuleNotFoundError: No module named 'backend'
```
**Solution**: Ensure virtual environment is activated and you're in project root

#### Port Already in Use
```
OSError: [Errno 98] Address already in use
```
**Solution**: Kill process using port 5000:
```bash
lsof -ti:5000 | xargs kill -9
```

#### CSS/JS Not Loading
```
404 Not Found: static files
```
**Solution**: Check Flask static file configuration, ensure files are in correct directory

#### Session Not Persisting
```
User logged out unexpectedly
```
**Solution**: Check SECRET_KEY is set, verify session configuration

### Getting Help

- Check existing GitHub issues
- Review documentation in /docs
- Contact project supervisor
- Email: your-email@university.edu -->

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- AGBD Dataset: Sialelli et al. (2025)
- GEDI Mission: NASA
- Sentinel-2 Data: European Space Agency
- Supabase: Database infrastructure
- Flask Framework: Web development

<!-- ## Project Metadata

- **Author**: Wendy Lagho
- **Institution**: strathmore university
- **Supervisor**: Dr. Joseph Orero
- **GitHub**: https://github.com/wlagho/AGB-estimation -->

<!-- **Last Updated**: December 2024 -->

For questions or support, please open an issue on GitHub or contact the project maintainer.