# Dockerization Journey - Scalable Exam Result Delivery Platform

## Objective

After successfully building and testing the FastAPI application locally with MySQL and Redis, the next goal was to containerize the entire platform and prepare it for cloud deployment.

The objective was:

* Eliminate machine-specific dependencies
* Create a reproducible deployment process
* Prepare the application for AWS deployment
* Run the complete stack using a single command

---

## Initial Architecture

Before Dockerization:

Student
↓
FastAPI (Local Python Environment)
↓
Redis (Docker Container)
↓
MySQL (Local Installation)

Although functional, this setup was difficult to replicate across environments.

---

## FastAPI Containerization

Created:

* Dockerfile
* .dockerignore

The FastAPI application was packaged into a Docker image.

Build Process:

Application Code
↓
Dockerfile
↓
Docker Image
↓
Docker Container

Successfully built:

exam-result-api

---

## Environment Variable Refactoring

Removed hardcoded configuration values and introduced:

* backend/.env
* root .env

Configuration such as:

* Database Host
* Database Password
* Redis Host

became environment driven.

### Challenge

The database password contained:

@

which caused SQLAlchemy connection string parsing issues.

### Solution

Used:

quote_plus()

to safely encode special characters inside the database URL.

---

## Docker Compose Implementation

Created:

docker-compose.yml

to orchestrate:

* FastAPI Container
* MySQL Container
* Redis Container

The platform could now be started using:

docker compose up -d --build

---

## Security Improvement

Initially, MySQL credentials were hardcoded inside docker-compose.yml.

This was identified and improved by moving credentials into environment variables using:

${DB_PASSWORD}

and

${DB_NAME}

This made the configuration cleaner and closer to production practices.

---

## Container Networking

A major change during Dockerization was replacing:

localhost

with Docker service names:

DB_HOST=mysql

REDIS_HOST=redis

This allowed containers to communicate through Docker's internal network.

### Lesson Learned

Inside a container:

localhost refers to the container itself, not the host machine.

---

## MySQL Containerization

Replaced the local MySQL installation with a MySQL Docker container.

Implemented:

* Persistent Docker Volume
* Dedicated MySQL Service
* Automatic Database Creation

Benefits:

* Consistent environment
* Portable deployment
* Simplified cloud migration

---

## Startup Issue Encountered

After deploying with Docker Compose, FastAPI initially failed to connect to MySQL.

Error:

Can't connect to MySQL server on 'mysql'

### Investigation

Verified:

docker ps

Confirmed all containers were running.

Checked:

docker logs exam-mysql

and observed MySQL becoming ready after FastAPI attempted the connection.

### Root Cause

Startup race condition.

FastAPI started before MySQL finished initialization.

### Learning

depends_on controls startup order but does not guarantee service readiness.

Future improvements:

* Health Checks
* Retry Logic
* Wait-for-It Scripts

---

## End-to-End Validation

Verified:

### FastAPI

Swagger UI loaded successfully.

### Redis

/redis-test

returned:

{
"message": "redis working"
}

### MySQL

Database connectivity verified through API requests.

---

## Data Seeding

Used the examination board CSV file as seed data.

Endpoint:

POST /admin/upload-results

Results:

* Inserted Records: 7
* Updated Records: 0
* Invalid Records: 0

---

## Cache Validation

First Request:

GET /results/HT12346

Response Source:

mysql

Second Request:

GET /results/HT12346

Response Source:

redis

Successfully validated the Cache-Aside caching pattern.

---

## Final Dockerized Architecture

Student
↓
FastAPI Container
↓
Redis Container
↓
MySQL Container

Managed By:

Docker Compose

Configuration:

Environment Variables

Storage:

Docker Volumes

Networking:

Docker Internal Network

---

## Key Skills Demonstrated

* Docker
* Docker Compose
* Container Networking
* Environment Variables
* Volume Management
* FastAPI Containerization
* MySQL Containerization
* Redis Integration
* Cache Aside Pattern
* Container Debugging
* Service Dependency Troubleshooting

---

## Outcome

The application evolved from a partially local setup into a fully containerized platform.

Current Deployment:

docker compose up -d --build

starts:

* FastAPI
* MySQL
* Redis

and the platform is now ready for the next phase:

AWS Cloud Deployment and VPC Architecture.
