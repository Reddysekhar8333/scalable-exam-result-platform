# AWS Deployment Journey - Scalable Exam Result Delivery Platform

# Objective

After successfully containerizing the application locally using Docker Compose, the next goal was to deploy the complete platform on AWS and make it accessible to students over the internet.

The objective was:

* Deploy the application to AWS Cloud
* Run FastAPI, MySQL, and Redis using Docker Compose
* Make the application publicly accessible
* Validate the complete student result retrieval workflow

---

# Initial Architecture

Local Development Environment:

Student
↓
FastAPI Container
↓
Redis Container
↓
MySQL Container

Managed By:

Docker Compose

After validating the platform locally, the same architecture was migrated to AWS.

---

# AWS Infrastructure Selection

Chosen Components:

* AWS EC2
* Ubuntu Server
* Docker
* Docker Compose
* Git

Instance Configuration:

* Instance Type: t3.micro
* Storage: 20 GB gp3
* Operating System: Ubuntu 26.04 LTS

Reason:

* Free Tier Friendly
* Sufficient for current workload
* Suitable for learning cloud deployment

---

# Security Group Configuration

Inbound Rules:

| Type       | Port | Source   |
| ---------- | ---- | -------- |
| SSH        | 22   | My IP    |
| Custom TCP | 8000 | Anywhere |

Reasoning:

SSH access was restricted to my public IP to reduce the attack surface.

Application traffic was exposed through port 8000 because FastAPI was running on that port.

Important Learning:

Opening SSH access does not automatically expose the application.

Application ports must be explicitly allowed through Security Groups.

---

# EC2 Access

Connected to the server using:

```bash
ssh -i exam-results-server-key.pem ubuntu@<EC2_PUBLIC_IP>
```

Successfully established remote access to the server.

---

# Docker Installation

Updated package metadata:

```bash
sudo apt update
```

Installed Docker:

```bash
sudo apt install docker.io -y
```

Verified:

```bash
docker --version
```

Result:

Docker installed successfully.

---

# Docker Service Configuration

Started Docker:

```bash
sudo systemctl start docker
```

Enabled Docker on reboot:

```bash
sudo systemctl enable docker
```

Added current user to Docker group:

```bash
sudo usermod -aG docker $USER
```

Reconnected through SSH and verified:

```bash
docker ps
```

could be executed without sudo.

---

# Git Installation

Installed Git:

```bash
sudo apt install git -y
```

Verified:

```bash
git --version
```

---

# Docker Compose Installation

Installed Docker Compose:

```bash
sudo apt install docker-compose-plugin -y
```

Verified:

```bash
docker compose version
```

---

# Application Deployment

Cloned the repository:

```bash
git clone <repository_url>
```

Navigated to project directory:

```bash
cd scalable-exam-result-platform
```

Created required environment files:

Root .env

Backend .env

These files contained:

* Database Configuration
* Redis Configuration
* Application Configuration

---

# Container Deployment

Started the entire stack:

```bash
docker compose up -d --build
```

This automatically created:

* FastAPI Container
* MySQL Container
* Redis Container
* Docker Network
* Docker Volumes

Verified:

```bash
docker ps
```

Result:

All containers were running successfully.

---

# Issue 1 - MySQL Connection Error

Observed Error:

sqlalchemy.exc.OperationalError

Can't connect to MySQL server on 'mysql'

Investigation:

Checked container status:

```bash
docker ps
```

Checked MySQL logs:

```bash
docker logs exam-mysql
```

Observation:

MySQL became ready after FastAPI attempted its initial connection.

Root Cause:

Startup Race Condition

Sequence:

MySQL Starting
↓
FastAPI Starting
↓
FastAPI Attempting Connection
↓
Connection Refused
↓
MySQL Ready

Learning:

depends_on controls startup order but does not guarantee service readiness.

Future Improvement:

* Health Checks
* Retry Logic

---

# Issue 2 - Application Not Accessible From Laptop

Observed:

Inside EC2:

```bash
curl http://localhost:8000/docs
```

worked successfully.

Outside EC2:

http://<EC2_PUBLIC_IP>:8000/docs

failed.

Investigation:

Verified:

* FastAPI Running
* Docker Running
* Port Mapping Correct

Root Cause:

Port 8000 was not allowed in the Security Group.

Resolution:

Added Inbound Rule:

Custom TCP
Port: 8000
Source: Anywhere (0.0.0.0/0)

Result:

Swagger UI became publicly accessible.

Learning:

Application health and network accessibility are separate concerns.

A healthy application can still be inaccessible if cloud networking is not configured correctly.

---

# Deployment Validation

Verified FastAPI:

```bash
curl http://localhost:8000/docs
```

Success

Verified Redis:

```bash
curl http://localhost:8000/redis-test
```

Response:

{
"message": "redis working"
}

Success

Verified Public Access:

http://<EC2_PUBLIC_IP>:8000/docs

Success

---

# Current AWS Architecture

Internet
↓
AWS Security Group
↓
EC2 Instance
↓
Docker Compose
├── FastAPI
├── MySQL
└── Redis

---

# Business Outcome

Students can now access examination results through a publicly hosted cloud application.

The platform supports:

* Result Retrieval
* CSV Result Upload
* Redis Caching
* Database Persistence
* Public Internet Access

---

# Skills Demonstrated

Cloud

* AWS EC2
* Security Groups
* SSH Access

Linux

* Package Management
* Service Management
* Remote Administration

Containers

* Docker
* Docker Compose
* Docker Networking
* Volume Management

Troubleshooting

* Startup Dependency Issues
* Database Connectivity Issues
* Cloud Networking Issues
* Public Access Validation

---

# Outcome

Successfully migrated the Scalable Exam Result Delivery Platform from a local Docker environment to AWS Cloud.

The platform is now publicly accessible and ready for the next phase:

* VPC Design
* Load Balancer
* Auto Scaling
* Terraform
* CI/CD Pipeline
* Monitoring


# Data Persistence and Storage Verification

After successfully deploying the application and uploading the examination results CSV file, an important question arose:

"Where is the uploaded student data actually stored?"

Initially, it might appear that the uploaded CSV file remains inside the FastAPI container. However, the actual data flow is:

exam_results.csv
↓
FastAPI Upload API
↓
SQLAlchemy ORM
↓
MySQL Database
↓
results Table

This means the CSV file is only used as a temporary ingestion source.

The student records are permanently stored inside the MySQL database.

---

## Docker Volume Persistence

The MySQL container was configured with a Docker volume:

```yaml
volumes:
  mysql_data:
```

and

```yaml
mysql:
  volumes:
    - mysql_data:/var/lib/mysql
```

Data flow:

MySQL Container
↓
/var/lib/mysql
↓
Docker Volume (mysql_data)

This ensures that database records remain available even if:

* The MySQL container is stopped
* The MySQL container is restarted
* The MySQL container is recreated

Without a Docker volume:

Delete Container
↓
Database Lost ❌

With a Docker volume:

Delete Container
↓
Create New Container
↓
Data Preserved ✅

---

## Storage Verification

Verified the uploaded student records by connecting directly to the MySQL container.

Access MySQL:

```bash
docker exec -it exam-mysql mysql -u root -p
```

Database verification:

```sql
SHOW DATABASES;

USE exam_results;

SHOW TABLES;

SELECT * FROM results;
```

Result:

All uploaded student records were successfully stored inside the MySQL database.

---

## Docker Volume Verification

Verified the persistent storage volume:

```bash
docker volume ls
```

Observed:

```text
scalable-exam-result-platform_mysql_data
```

Inspected volume details:

```bash
docker volume inspect scalable-exam-result-platform_mysql_data
```

This confirmed that the database files were stored outside the container filesystem and managed through Docker volumes.

---

## Learning Outcome

A key realization from this deployment was:

The CSV file is not the final storage location.

The CSV file acts only as an ingestion mechanism.

The actual source of truth is:

MySQL Database
↓
Docker Persistent Volume

This design ensures data durability and allows the application to survive container restarts without losing student records.


# Infrastructure Scaling Challenge
Issue:
EC2 Instance Reachability Check Failed

Investigation:
Reviewed EC2 system logs.

Root Cause:
Linux OOM Killer terminated MySQL because the
t3.micro instance (1 GB RAM) could not support
Ubuntu, Docker, MySQL, Redis, and FastAPI simultaneously.

Resolution:
Upgraded instance type from t3.micro to t3.small (2 GB RAM).

Outcome:
Instance became stable and all containers resumed normal operation.