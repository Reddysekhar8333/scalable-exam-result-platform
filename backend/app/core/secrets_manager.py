import json
import boto3

SECRET_NAME = "exam-result-platform/rds"
REGION_NAME = "us-east-1"


def get_db_secret():
    client = boto3.client(
        service_name="secretsmanager",
        region_name=REGION_NAME
    )
    
    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    return json.loads(response["SecretString"])