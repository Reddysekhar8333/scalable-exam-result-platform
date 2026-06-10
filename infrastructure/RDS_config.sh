# allow mysql access from exam-app-sg
aws ec2 authorize-security-group-ingress 
--group-id sg-0b9c8e5f1a2b3c4d 
--protocol tcp 
--port 3306 
--source-group APP_SG_ID # ex: sg-02f5190ac436c6270 
 

# create RDS instance
aws rds create-db-instance 
  --db-instance-identifier exam-results-db 
  --engine mysql 
  --engine-version 8.0 
  --db-instance-class db.t3.micro 
  --allocated-storage 20 
  --storage-type gp3 
  --master-username admin 
  --master-user-password "YOUR_PASSWORD" 
  --db-name exam_results 
  --db-subnet-group-name exam-db-subnet-group 
  --vpc-security-group-ids sg-0d8fd7b627c33b26a 
  --no-publicly-accessible