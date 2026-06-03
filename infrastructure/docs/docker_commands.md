# Docker Commands Cheat Sheet - Scalable Exam Result Platform

# 1. Verify Docker Installation

Check Docker version:

```bash
docker --version
```

Check Docker Compose version:

```bash
docker compose version
```

---

# 2. Pull Redis Image

Download Redis image from Docker Hub.

```bash
docker pull redis
```

---

# 3. Create Redis Container

```bash
docker run -d --name redis-container -p 6379:6379 redis
```

Parameters:

* d = detached mode
* name = container name
* p = port mapping

---

# 4. Start Existing Redis Container

```bash
docker start redis-container
```

---

# 5. Stop Container

```bash
docker stop redis-container
```

---

# 6. Remove Container

```bash
docker rm redis-container
```

---

# 7. View Running Containers

```bash
docker ps
```

Example:

```text
exam-api
exam-mysql
exam-redis
```

---

# 8. View All Containers

Including stopped containers.

```bash
docker ps -a
```

---

# 9. View Docker Images

```bash
docker images
```

Example:

```text
exam-result-api
redis
mysql
```

---

# 10. Build FastAPI Docker Image

Navigate to backend directory.

```bash
docker build -t exam-result-api .
```

Explanation:

* t = tag image
* exam-result-api = image name

---

# 11. Run FastAPI Image Manually

```bash
docker run -it exam-result-api
```

Useful for debugging startup issues.

---

# 12. Create Full Stack Using Docker Compose

Navigate to project root.

```bash
docker compose up -d --build
```

Explanation:

* build = rebuild images
* d = detached mode

Creates:

* FastAPI Container
* MySQL Container
* Redis Container

---

# 13. Stop Entire Stack

```bash
docker compose down
```

Stops:

* FastAPI
* MySQL
* Redis

---

# 14. Restart Entire Stack

```bash
docker compose restart
```

---

# 15. Rebuild Everything

After code changes:

```bash
docker compose up -d --build
```

---

# 16. View Container Logs

FastAPI:

```bash
docker logs exam-api
```

MySQL:

```bash
docker logs exam-mysql
```

Redis:

```bash
docker logs exam-redis
```

---

# 17. Follow Live Logs

FastAPI:

```bash
docker logs -f exam-api
```

MySQL:

```bash
docker logs -f exam-mysql
```

Redis:

```bash
docker logs -f exam-redis
```

---

# 18. Enter FastAPI Container

```bash
docker exec -it exam-api bash
```

Useful for:

* Checking files
* Debugging
* Running commands

---

# 19. Enter MySQL Container

```bash
docker exec -it exam-mysql bash
```

---

# 20. Enter Redis Container

```bash
docker exec -it exam-redis sh
```

---

# 21. Open MySQL Client

```bash
docker exec -it exam-mysql mysql -u root -p
```

Enter password when prompted.

---

# 22. Show Databases

Inside MySQL:

```sql
SHOW DATABASES;
```

---

# 23. Use Exam Database

```sql
USE exam_results;
```

---

# 24. Show Tables

```sql
SHOW TABLES;
```

---

# 25. View Student Data

```sql
SELECT * FROM results;
```

---

# 26. Open Redis CLI

```bash
docker exec -it exam-redis redis-cli
```

---

# 27. Check Redis Connectivity

```redis
PING
```

Expected:

```text
PONG
```

---

# 28. Show All Redis Keys

```redis
KEYS *
```

Example:

```text
result:HT12345
result:HT12346
```

---

# 29. View Cached Result

```redis
GET result:HT12346
```

---

# 30. Delete Specific Cache

```redis
DEL result:HT12346
```

---

# 31. Remove Entire Docker Stack

WARNING: Deletes containers.

```bash
docker compose down
```

---

# 32. Remove Stack + Volumes

WARNING: Deletes database data.

```bash
docker compose down -v
```

---

# 33. Remove Docker Image

```bash
docker rmi exam-result-api
```

---

# 34. Remove Unused Containers

```bash
docker container prune
```

---

# 35. Remove Unused Images

```bash
docker image prune
```

---

# 36. Remove Everything Unused

```bash
docker system prune -a
```

Use carefully.

---

# Commands Used During This Project

Step 1

```bash
docker --version
```

Step 2

```bash
docker pull redis
```

Step 3

```bash
docker run -d --name redis-container -p 6379:6379 redis
```

Step 4

```bash
docker start redis-container
```

Step 5

```bash
docker build -t exam-result-api .
```

Step 6

```bash
docker images
```

Step 7

```bash
docker run -it exam-result-api
```

Step 8

```bash
docker compose up -d --build
```

Step 9

```bash
docker ps
```

Step 10

```bash
docker logs exam-api
```

Step 11

```bash
docker logs exam-mysql
```

Step 12

Swagger Testing

```text
/docs
```

Step 13

Redis Testing

```text
/redis-test
```

Step 14

CSV Upload

```text
POST /admin/upload-results
```

Step 15

Cache Testing

```text
GET /results/{hall_ticket}
```

---

# AWS Deployment Commands (Upcoming Phase)

Install Docker:

```bash
sudo yum update -y
sudo yum install docker -y
```

Start Docker:

```bash
sudo systemctl start docker
```

Enable Docker:

```bash
sudo systemctl enable docker
```

Install Git:

```bash
sudo yum install git -y
```

Clone Repository:

```bash
git clone <repository_url>
```

Navigate:

```bash
cd scalable-exam-result-platform
```

Deploy:

```bash
docker compose up -d --build
```

Verify:

```bash
docker ps
```
