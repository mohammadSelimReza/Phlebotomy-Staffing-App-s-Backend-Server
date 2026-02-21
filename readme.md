

# Phlebotomy Staffing App Backend

A robust, highly scalable, RESTful backend designed to power the Phlebotomy Staffing App platform. Built heavily inspired by **cross-border rental and marketplace** logic, it efficiently handles the matching, scheduling, and payment orchestration between clinical businesses and independent phlebotomists.

## 🚀 Key Features & Architecture

- 💳 **Stripe Subscription Integration**  
  Fully integrated Stripe billing cycles, handling multi-tier subscriptions, customer invoice cycles, and split payments seamlessly.

- 🏗️ **Micro-service & MERN Inspired API**  
  Although written in Django, the application adopts a modular, **Micro-service** approach, mimicking the decoupled and highly scalable nature of MERN stacks. The frontend API consumption is thoroughly optimized via clear, JSON RESTful endpoints.

- ☁️ **AWS & CI/CD Deployment**  
  Containerization via Docker and structured CI/CD pipelines allows independent scaling of endpoints to cloud providers (e.g., AWS EBS, Lightsail, or ECS).

## 🧑‍⚕️ User Modularity (Roles)

### 1. Phlebotomist Profile
- **Personal**: Name, Email, Phone, Gender, DOB
- **Professional Credentials**: License No., Expiry Date, Experience, Speciality
- **Onboarding Documents**: File uploads for License & Identification
- **Availability Matrix**: Work preference (part_time/full_time), Service Area, Weekly Scheduling logic

### 2. Business Profile
- **Company Info**: Name, Type, Address, Contact Person
- **Legal Compliance**: Business License, Legal Document Uploads
- **Job Posting Params**: Hourly rates, Job configurations, Shift requirements
- **Contracts**: Digital Signature processing & Compliance enforcement

*Note: Profiles map 1-to-1 with core User instances ensuring clear separation of domain concerns.*

## 💻 Tech Stack
- **API Engine**: Python / Django REST Framework
- **Databases**: PostgreSQL (Core), Redis (Cache/Broker)
- **Billing**: Stripe API
- **DevOps**: Docker, Docker Compose, CI/CD automated test-runners

## 🛠 Getting Started

### Prerequisites
- Docker & Docker-Compose
- PostgreSQL 

### Installation via Docker (Best Practice)
Launch the application and database containers quickly:
```bash
docker-compose up --build
```
This handles DB migrations implicitly and runs the project on port `8500`.

### Local Development Setup
1. Virtual environment setup:
   ```bash
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment:
   Copy `.env.example` to `.env` and fill the Stripe & DB credentials.
3. Apply schema & run:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver 8500
   ```
 