# SmallHolder Carbon Assessment Platform (SHCAP)

## Project Overview

SHCAP is a web-based platform designed to democratize access to carbon markets for smallholder farmers in East Africa through affordable, above-ground biomass (AGB) estimation. The system uses machine learning models trained on multi-source remote sensing data to provide accurate carbon stock assessments and carbon market eligibility evaluations.

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
source agb_env/bin/activate  # On Windows: agb_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4. Create Directory Structure

```bash
mkdir -p backend/app/{models,auth,main}
mkdir -p frontend/{static/{css,js},templates/auth}
mkdir -p scripts data/{raw,processed,sample_regions} ml_models docs tests
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

## Database Setup

### Initialize Database Tables

```bash
# Test connection and create tables
python setup_supabase.py
```

Expected output:
```
✅ Connected to Supabase PostgreSQL successfully
✅ Database tables created successfully
✅ Supabase setup completed successfully!
```

### Create Demo Users (Optional)

```bash
python create_demo_users.py
```

This creates three demo accounts:

- **Researcher**: researcher@demo.com / Demo123!
- **Project Developer**: developer@demo.com / Demo123!
- **Administrator**: admin@demo.com / Demo123!

## Running the Application

### Development Server

```bash
python run_development.py
```

The application will be available at:

- Main site: http://localhost:5000
- Demo page: http://localhost:5000/demo
- Login: http://localhost:5000/auth/login
- Register: http://localhost:5000/auth/register

### Production Server

For production deployment, use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## Development Workflow

### Branch Structure

This project uses feature branches for different issues:

```
main (production-ready code)
├── develop (integration branch)
├── feature/auth-foundation (#2)
├── feature/password-reset (#3)
├── feature/2fa-implementation (#4)
└── feature/role-validation (#5)
```

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

For questions or support, please open an issue on GitHub.

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/inoLPW_E)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=20099699&assignment_repo_type=AssignmentRepo)
