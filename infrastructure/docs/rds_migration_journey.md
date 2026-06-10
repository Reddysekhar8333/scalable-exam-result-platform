# Database Migration Journey: Docker MySQL to Amazon RDS

## Overview

As part of the Scalable Exam Result Platform, the initial application architecture stored student result data inside a MySQL Docker container running on an EC2 instance. While this approach worked for development and initial testing, it introduced a major architectural limitation: the database was tightly coupled to a single server.

To build a production-ready cloud architecture capable of supporting Auto Scaling and high availability, the database layer was migrated from a containerized MySQL instance to Amazon RDS MySQL.

This document captures the complete migration journey, including challenges encountered, troubleshooting steps performed, lessons learned, and the final successful migration process.

---

## Initial Architecture

The application initially operated using the following setup:

```text
Student
   ↓
FastAPI
   ↓
Docker MySQL Container
   ↓
EC2 Instance
```

The database was hosted inside a Docker container named:

```text
exam-mysql
```

All student examination records were stored in this containerized MySQL database.

Although suitable for development, this design had a critical limitation:

* Database availability depended on a single EC2 instance.
* Auto Scaling application servers could not share the same database.
* Failure of the EC2 instance could result in application downtime.
* Database backups and maintenance had to be managed manually.

---

## Goal of Migration

The objective was to move the database into Amazon RDS to achieve:

* Managed MySQL service
* Centralized database access
* Improved reliability
* Better scalability
* Easier backup management
* Production-grade cloud architecture

Target architecture:

```text
Internet
   ↓
Application Load Balancer
   ↓
Auto Scaling Group
   ↓
FastAPI Application
   ↓
Amazon RDS MySQL
```

---

## Step 1: Creating Private Database Subnets

To secure the database, dedicated private subnets were created across two Availability Zones.

Database Subnets:

```text
private-db-subnet-a
private-db-subnet-b
```

A DB Subnet Group was created:

```text
exam-db-subnet-group
```

This allowed RDS to be deployed inside private networking boundaries rather than being exposed to the internet.

---

## Step 2: Creating Amazon RDS

An Amazon RDS MySQL instance was provisioned with the following configuration:

```text
Engine: MySQL 8.0
Instance Type: db.t3.micro
Storage: 20 GB gp3
Public Access: Disabled
Database Name: exam_results
```

Key design decision:

```text
Public Access = No
```

This ensured the database could only be accessed from resources inside the VPC.

---

## Challenge 1: RDS Console Configuration Issues

During creation of the RDS instance, the AWS Console behaved unexpectedly:

Observed issues:

* Storage Type dropdown was empty
* Instance Type dropdown was empty
* VPC selection was unavailable

Troubleshooting performed:

* Verified DB Subnet Group configuration
* Confirmed subnet group status was Complete
* Verified VPC association
* Attempted browser refreshes and configuration changes

Resolution:

Instead of relying on the console, the database was successfully created using AWS CloudShell and AWS CLI commands.

Lesson learned:

```text
Infrastructure can always be provisioned using CLI even when the UI behaves unexpectedly.
```

---

## Step 3: Securing Database Access

A dedicated security group was created:

```text
rds-mysql-sg
```

Only application servers were allowed to access MySQL on port 3306.

Security design:

```text
exam-app-sg
        ↓
      3306
        ↓
rds-mysql-sg
```

No internet access was granted to the database.

This follows production-grade security principles.

---

## Step 4: Creating Database Backup

Before migration, a complete backup was created from the Dockerized MySQL database.

Backup command:

```bash
docker exec exam-mysql \
mysqldump -u root -p exam_results > exams_results_backup.sql
```

Result:

```text
exams_results_backup.sql
```

Backup size:

```text
2.3 KB
```

Verification confirmed:

```text
7 student records
```

were successfully exported.

Lesson learned:

```text
Always create a backup before performing any migration.
```

---

## Challenge 2: Private RDS Connectivity

An attempt was made to connect directly from the old EC2 instance to Amazon RDS.

Connection failed.

Root Cause:

The old EC2 instance existed outside the newly created VPC.

Meanwhile:

```text
RDS
```

was deployed inside private subnets with:

```text
Public Access = Disabled
```

Therefore:

```text
Old EC2
      ✗
Cannot Reach RDS
```

Resolution:

Migration operations were moved to an application server located inside the VPC.

Lesson learned:

```text
Knowing credentials is not enough.
Network access is equally important.
```

---

## Challenge 3: Secure File Transfer Strategy

The SQL backup file needed to be transferred to a server capable of accessing RDS.

An initial SCP-based approach failed due to SSH key authentication restrictions.

Rather than using a developer laptop as a bridge, a production-oriented solution was chosen.

Migration strategy:

```text
SQL Backup
     ↓
Amazon S3
     ↓
Application Server
     ↓
Amazon RDS
```

This approach more closely resembles real-world cloud migration workflows.

---

## Challenge 4: AWS CLI Authentication Failure

While uploading the backup file to S3, the following error occurred:

```text
Unable to locate credentials
```

Root Cause:

The EC2 instance did not possess AWS credentials.

Resolution:

An IAM Role was created and attached to the EC2 instance.

Role:

```text
exam-ec2-s3-role
```

Permission:

```text
AmazonS3FullAccess
```

This enabled secure, temporary AWS credentials without storing access keys on the server.

Lesson learned:

```text
Production systems should use IAM Roles instead of AWS access keys.
```

---

## Step 5: Migrating Backup Through Amazon S3

Migration path:

```text
Docker MySQL
      ↓
mysqldump
      ↓
SQL Backup
      ↓
Amazon S3
      ↓
Application EC2
      ↓
Amazon RDS
```

The backup file was successfully uploaded to S3 and downloaded on the application server.

---

## Challenge 5: Schema Validation Before Import

Before importing the backup, existing tables in Amazon RDS were inspected.

Unexpected discovery:

RDS contained:

```text
students_results
```

while the SQL backup contained:

```text
results
```

Inspection command:

```bash
grep -i "CREATE TABLE" exams_results_backup.sql
```

Output:

```sql
CREATE TABLE `results`
```

Root Cause:

A test table had been manually created earlier during RDS validation.

Resolution:

The test table was removed before migration.

Lesson learned:

```text
Always inspect source and target schemas before importing data.
```

---

## Step 6: Importing Data into Amazon RDS

Migration command:

```bash
mysql \
-h <rds-endpoint> \
-u admin \
-p exam_results < exams_results_backup.sql
```

Import completed successfully.

Verification:

```sql
SHOW TABLES;

SELECT COUNT(*) FROM results;
```

Result:

```text
7 records migrated successfully
```

---

## Final Architecture

After migration:

```text
Internet
   ↓
Application Load Balancer
   ↓
Auto Scaling Group
   ↓
FastAPI Application
   ↓
Amazon RDS MySQL
```

The database is now:

* Centrally managed
* Accessible by all application servers
* Independent of EC2 lifecycle
* Ready for scaling
* Suitable for production-style deployments

---

## Key Lessons Learned

1. Infrastructure can be provisioned through CLI when the AWS Console fails.
2. Databases should be deployed in private subnets.
3. Security Groups should reference application security groups instead of public CIDR ranges.
4. Always take backups before migration.
5. Network accessibility is as important as credentials.
6. IAM Roles are preferred over access keys.
7. Amazon S3 provides a secure migration intermediary.
8. Validate source and target schemas before importing data.
9. Managed databases simplify operations and improve reliability.
10. Separating the database layer is essential for scalable cloud architectures.

---

## Migration Outcome

```text
Database Migration Status : SUCCESSFUL
Source                    : Docker MySQL
Target                    : Amazon RDS MySQL
Records Migrated          : 7
Downtime                  : Minimal
Architecture              : Production-Oriented
```
