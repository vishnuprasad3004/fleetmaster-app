# FleetMaster Project Structure

## Directory Organization

```
fleetmaster-app/
├── backend/                    # Backend services
│   ├── api/                    # API endpoints
│   │   ├── auth/              # Authentication endpoints
│   │   ├── vehicles/          # Vehicle endpoints
│   │   ├── drivers/           # Driver endpoints
│   │   └── tracking/          # Tracking endpoints
│   ├── models/                 # Database models
│   ├── services/               # Business logic
│   ├── middleware/             # Custom middleware
│   ├── utils/                  # Utility functions
│   ├── requirements.txt        # Python dependencies
│   ├── manage.py               # Django management
│   └── settings.py             # Configuration
│
├── frontend/                   # Flutter mobile app
│   ├── lib/
│   │   ├── screens/           # UI screens
│   │   ├── widgets/           # Reusable widgets
│   │   ├── models/            # Data models
│   │   ├── services/          # API services
│   │   ├── providers/         # State management
│   │   ├── utils/             # Utilities
│   │   └── main.dart          # Entry point
│   ├── test/                   # Tests
│   ├── pubspec.yaml            # Dependencies
│   └── README.md               # Frontend docs
│
├── web/                        # Web dashboard
│   ├── app/                    # Flask app
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS, JS, images
│   ├── routes/                 # Web routes
│   ├── requirements.txt        # Python dependencies
│   └── README.md               # Web docs
│
├── docker/                     # Docker configurations
│   ├── Dockerfile.backend      # Backend container
│   ├── Dockerfile.web          # Web container
│   └── docker-compose.yml      # Multi-container setup
│
├── .github/
│   ├── workflows/              # CI/CD pipelines
│   │   ├── backend-test.yml
│   │   ├── frontend-build.yml
│   │   └── deploy.yml
│   └── ISSUE_TEMPLATE/         # Issue templates
│
├── docs/                       # Documentation
│   ├── API.md                  # API documentation
│   ├── FRONTEND.md             # Frontend guide
│   ├── DATABASE.md             # Database schema
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── ARCHITECTURE.md         # System architecture
│   └── PROJECT_STRUCTURE.md    # This file
│
├── tests/                      # Integration tests
│   ├── api/
│   ├── e2e/
│   └── fixtures/
│
├── README.md                   # Project overview
├── CONTRIBUTING.md             # Contributing guidelines
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
└── .env.example                # Environment variables template
```

## Module Responsibilities

### Backend (`/backend`)
- **api/**: RESTful API endpoints
- **models/**: SQLAlchemy/Django ORM models
- **services/**: Core business logic
- **middleware/**: Authentication, logging, error handling
- **utils/**: Helper functions and utilities

### Frontend (`/frontend`)
- **screens/**: Full page views
- **widgets/**: Reusable UI components
- **models/**: Data classes and DTOs
- **services/**: API communication
- **providers/**: State management (Riverpod/Provider)
- **utils/**: Constants, helpers, extensions

### Web (`/web`)
- **app/**: Flask application factory
- **templates/**: Jinja2 HTML templates
- **static/**: CSS, JavaScript, images
- **routes/**: URL routing and views

## File Naming Conventions

### Python
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case()`
- Constants: `UPPER_CASE`

### Dart/Flutter
- Files: `snake_case.dart`
- Classes: `PascalCase`
- Functions: `camelCase()`
- Constants: `camelCase` or `UPPER_CASE`

### Configuration Files
- Environment: `.env`, `.env.local`
- Ignore: `.gitignore`
- Workflow: `.github/workflows/*.yml`

## Best Practices

1. **Keep modules focused**: Each module should have a single responsibility
2. **Reuse code**: Extract common logic into utils/services
3. **Document APIs**: Add docstrings and comments
4. **Test coverage**: Maintain >80% test coverage
5. **Consistent naming**: Follow naming conventions strictly
6. **Version control**: Use meaningful commit messages

## Getting Started

Refer to individual README files in each directory for setup and usage instructions:
- Backend: `backend/README.md`
- Frontend: `frontend/README.md`
- Web: `web/README.md`