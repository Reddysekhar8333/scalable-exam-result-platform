# Scalable Exam Result Platform - Complete Infrastructure Journey

## Project Overview

The Scalable Exam Result Platform is a cloud-native web application built to provide highly available, secure, scalable, and fault-tolerant access to student examination results.

The project started as a simple FastAPI application running on a single EC2 instance with a MySQL Docker container. Over time, the architecture evolved into a production-style platform using AWS services such as Amazon RDS, AWS Secrets Manager, Application Load Balancer, Auto Scaling Groups, IAM Roles, Launch Templates, and Self-Healing Infrastructure.

---

# 1. Amazon RDS Migration

## Problem

Initially, MySQL was running inside a Docker container on the application server.

Architecture:

Application Server
→ FastAPI Container
→ MySQL Container

Challenges:

* Database and application tightly coupled
* Risk of data loss if server fails
* Difficult backup management
* No database scalability

## Implementation

* Created a DB Subnet Group using private subnets across multiple Availability Zones.
* Created an Amazon RDS MySQL instance.
* Configured a dedicated RDS Security Group.
* Allowed MySQL access only from application servers.
* Exported existing MySQL data from the Docker container.
* Migrated the data into Amazon RDS.

## Challenges Faced

* RDS creation options were initially unavailable.
* Database Subnet Group configuration required troubleshooting.
* Existing EC2 instance outside the VPC could not directly access RDS.

## Solution

* Created proper DB Subnet Group.
* Used S3 as an intermediary during migration.
* Imported backup successfully into RDS.

## Outcome

* Managed MySQL database.
* Independent database lifecycle.
* Improved reliability and maintainability.

---

# 2. AWS Secrets Manager Integration

## Problem

Database credentials were stored inside environment files.

Challenges:

* Hardcoded credentials
* Security risks
* Difficult credential rotation

## Implementation

Created AWS Secrets Manager secret:

exam-result-platform/rds

Stored:

* DB_USER
* DB_PASSWORD
* DB_HOST
* DB_PORT
* DB_NAME

Modified FastAPI application to retrieve credentials dynamically using boto3.

## Challenges Faced

Application instances required AWS permissions.

## Solution

Created IAM Role:

exam-app-role

Attached Secrets Manager permissions and assigned role to EC2 instances.

## Outcome

* No database credentials stored in GitHub.
* Centralized secret management.
* Improved application security.

---

# 3. Application Load Balancer (ALB)

## Problem

Single EC2 deployment created a single point of failure.

If the server failed, the entire application became unavailable.

## Implementation

Created:

* Application Load Balancer
* Target Group
* Listener Rules

Traffic Flow:

Student Browser
→ ALB
→ Application Servers

## Challenges Faced

Initial Target Group used:

Port 80

FastAPI application was running on:

Port 8000

Result:

* 404 Errors
* Failed routing

## Solution

Created new Target Group:

Port 8000

Updated ALB listener rules.

## Outcome

Traffic successfully distributed across multiple application servers.

---

# 4. Auto Scaling Group (ASG)

## Problem

Manual scaling was not possible for production workloads.

## Implementation

Created Auto Scaling Group:

* Minimum Capacity = 2
* Desired Capacity = 2
* Maximum Capacity = 4

Configured CPU-based scaling policy.

## Outcome

Infrastructure can automatically increase or decrease capacity based on demand.

---

# 5. Launch Templates

## Problem

New EC2 instances launched by ASG were empty servers.

Manual setup was required.

## Implementation

Created Launch Template:

exam-app-template

Included:

* AMI
* Instance Type
* Security Groups
* User Data

## Challenges Faced

Initial Launch Template versions lacked:

* IAM Role
* Docker Compose installation

## Solution

Created improved Launch Template versions and validated deployments.

## Outcome

New EC2 instances launch with standardized configuration.

---

# 6. User Data Automation

## Problem

Every new EC2 instance required manual setup.

Manual tasks included:

* Docker installation
* Git installation
* Repository cloning
* Environment configuration
* Container startup

## Implementation

Added User Data bootstrap script.

Automated:

* Docker installation
* Docker Compose installation
* Git installation
* Repository cloning
* Environment file creation
* Container startup

## Outcome

Fully automated application deployment.

---

# 7. IAM Roles

## Problem

Application instances needed secure access to AWS services.

## Implementation

Created:

exam-app-role

Attached permissions for:

* AWS Secrets Manager

Configured Launch Template to automatically attach IAM Role.

## Challenges Faced

New instances initially launched without the IAM Role.

Application failed to retrieve secrets.

## Solution

Updated Launch Template Version 3.

## Outcome

All Auto Scaling instances automatically receive required AWS permissions.

---

# 8. Production Security Groups

## Problem

Initially the same Security Group was attached to:

* Application Load Balancer
* EC2 Instances

This was not production-grade.

## Implementation

Created separate Security Groups.

### ALB Security Group

Inbound:

* HTTP 80 from Internet

### Application Security Group

Inbound:

* Port 8000 from ALB Security Group
* SSH from Administrator IP

### RDS Security Group

Inbound:

* MySQL 3306 from Application Security Group

## Outcome

Improved network isolation and security.

---

# 9. Self-Healing Infrastructure

## Objective

Ensure application automatically recovers from server failures.

## Testing Procedure

* Terminated running application instances manually.
* Observed Auto Scaling Group behavior.

## Automated Recovery Process

Instance Terminated
→ ASG Detects Capacity Loss
→ New EC2 Created
→ Launch Template Executes
→ User Data Runs
→ Docker Installed
→ Application Deployed
→ Secrets Retrieved
→ RDS Connected
→ Target Group Healthy
→ ALB Routes Traffic

## Challenges Faced

New instances initially became unhealthy.

Root Cause:

Docker Compose was not installed automatically.

## Solution

Created Launch Template Version 4 with Docker Compose installation.

## Outcome

New instances became healthy automatically.

No manual intervention required.

---

# 10. Load Balancing Validation Across 4 Servers

Created endpoint:

GET /server-info

Used container hostname to identify responding server.

Observed responses:

* 05f43d0379b3
* ef432d9cbb3c
* dea93594c23d
* 51e6de8b7d28

The Application Load Balancer distributed requests across all healthy instances.

## Validation Result

Load Balancing = Successful

Traffic Distribution = Successful

Auto Scaling Deployment = Successful

Self-Healing Infrastructure = Successful

---

# Final Architecture

Internet
→ Application Load Balancer
→ Auto Scaling Group
→ FastAPI Containers
→ Redis Containers
→ Amazon RDS MySQL

Supporting Services:

* AWS Secrets Manager
* IAM Roles
* Launch Templates
* Security Groups

---

# Key Achievements

✅ Amazon RDS Migration

✅ AWS Secrets Manager Integration

✅ Application Load Balancer

✅ Auto Scaling Group

✅ Launch Templates

✅ User Data Automation

✅ IAM Roles

✅ Production Security Groups

✅ Self-Healing Infrastructure

✅ Load Balancing Across 4 Servers

The project successfully evolved from a single-server deployment into a highly available, scalable, secure, and self-healing cloud-native platform using AWS best practices.
