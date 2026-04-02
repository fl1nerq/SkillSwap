# SkillSwap API

SkillSwap is an asynchronous RESTful API designed for skill exchange between users. The project implements a clean architecture and is fully containerized for seamless deployment.

## Tech Stack
* Backend: Python, FastAPI
* Database: PostgreSQL, SQLAlchemy (ORM), Alembic (Migrations)
* Testing: Pytest
* Containerization: Docker, Docker Compose

## Key Features
* User registration and JWT-based authentication
* Asynchronous CRUD operations for users and skills
* Relational database design with strict data validation
* Automated unit testing for critical endpoints

## Local Setup

1. Clone the repository:
   git clone [https://github.com/yourusername/skillswap.git](https://github.com/yourusername/skillswap.git)
   cd skillswap

2. Create an environment variables file based on the provided example:
cp .env.example .env

3. Build and start the services using Docker Compose:
docker-compose up --build

The API will be available at http://localhost:8000. You can access the interactive Swagger UI documentation at http://localhost:8000/docs.

4.Running Tests
To execute the test suite within the isolated Docker environment:
docker-compose exec web pytest