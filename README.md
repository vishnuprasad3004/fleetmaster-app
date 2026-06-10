# FleetMaster App

> A comprehensive fleet management system for real-time vehicle tracking, driver management, and earnings monitoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Dart](https://img.shields.io/badge/Dart-3.0%2B-blue)](https://dart.dev/)
[![Flutter](https://img.shields.io/badge/Flutter-3.0%2B-blue)](https://flutter.dev/)

## 📱 Features

- **Real-time Fleet Tracking**: Monitor vehicle locations on interactive maps
- **Live Dashboard**: View fleet status with running, idle, and alert states
- **Driver Management**: Track driver information and performance metrics
- **Earnings Dashboard**: Monitor driver earnings and trip statistics
- **Route Optimization**: Plan efficient routes between destinations
- **Alert System**: Instant notifications for vehicle anomalies
- **Multi-platform Support**: Native mobile app (iOS/Android) and web application

## 🏗️ Architecture

```
fleetmaster-app/
├── backend/              # Python Django/FastAPI backend
├── frontend/             # Flutter mobile application
├── web/                  # Web dashboard (Python/HTML)
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
└── docker/               # Docker configurations
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Flutter 3.0+
- Dart 3.0+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
flutter pub get
flutter run
```

### Web Setup

```bash
cd web
pip install -r requirements.txt
python app.py
```

## 📁 Project Structure

### Backend (`/backend`)
- REST API for fleet operations
- Database models for vehicles, drivers, routes
- Real-time tracking services
- Authentication and authorization
- Admin dashboard

### Frontend (`/frontend`)
- Flutter mobile application
- State management
- UI components
- Real-time map integration
- Push notifications

### Web (`/web`)
- Django/Flask web dashboard
- Admin panel
- Analytics and reporting
- User management

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python (Django/FastAPI) |
| Frontend | Flutter/Dart |
| Web | Python (Flask/Django) |
| Database | PostgreSQL |
| Real-time | WebSockets |
| Maps | Google Maps API |
| Storage | AWS S3 / Local Storage |

## 📖 Documentation

- [Backend API Documentation](./docs/API.md)
- [Frontend Development Guide](./docs/FRONTEND.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Database Schema](./docs/DATABASE.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 👨‍💻 Author

**Vishnu Prasad**
- GitHub: [@vishnuprasad3004](https://github.com/vishnuprasad3004)

## 📧 Support

For support, email support@fleetmaster.app or open an issue on GitHub.

## 🗺️ Project Timeline

- **Year 1**: Initial development and MVP launch
- **Current**: Beta version with core features
- **Roadmap**: Enhanced analytics, AI-driven insights, advanced route optimization

---

**Last Updated**: June 2026