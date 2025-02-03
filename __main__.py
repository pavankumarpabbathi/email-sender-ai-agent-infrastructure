import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx ##Pulumi for Crosswalk
import json
import os 


IMAGE_URI = os.environ['image_uri']
BEDROCK_MODEL_NAME = os.environ['BEDROCK_MODEL_NAME']
BUCKET_NAME = os.environ['BUCKET_NAME']
EMAIL_APP_PASSWORD = os.environ['EMAIL_APP_PASSWORD']
RECIPIENT_EMAIL_ADDRESS = os.environ['RECIPIENT_EMAIL_ADDRESS']
SENDER_EMAIL_ADDRESS = os.environ['SENDER_EMAIL_ADDRESS']

##In Pulumi Sequence[str] = List of string

lambda_role_args = {
    "assume_role_policy": json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }),
    "description": "Email Sender Lambda Compute Enviroment IAM Role",
    "force_detach_policies": True,
    "managed_policy_arns": [
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
    ],
    "name": "email-sender-lambda-role",
    "tags": {
        "Environment": "Dev",
        "Owner": "DevOps"
    }
}

lambda_iam_role = aws.iam.Role("lambda_role",
    **lambda_role_args
)


##Pulumi Code to create a lmabda function using container Image

lambda_fn_args = {
    "role": lambda_iam_role.arn,
    "architectures": ["x86_64"],
    "description": "Function running the AI Agent",
    "package_type": "Image",
    "timeout": 900,
    "tags": {
      "Environment": "Dev",
      "Owner": "TeamDevOps"
    },
    "name": "email-sender-ai-agent",
    "memory_size": 1024,
    "image_uri": IMAGE_URI,
    "environment": {
        "variables": {
            "BEDROCK_MODEL_NAME": BEDROCK_MODEL_NAME,
            "BUCKET_NAME": BUCKET_NAME,
            "CREWAI_STORAGE_DIR": "/tmp",
            "EMAIL_APP_PASSWORD": EMAIL_APP_PASSWORD,
            "RECIPIENT_EMAIL_ADDRESS": RECIPIENT_EMAIL_ADDRESS,
            "SENDER_EMAIL_ADDRESS": SENDER_EMAIL_ADDRESS
            
        }
    }
}

lambda_fn = aws.lambda_.Function("email-sender-lambda",
   **lambda_fn_args,
   opts=pulumi.ResourceOptions(depends_on=[lambda_iam_role])
 )

# pulumi.export("bucket_name", b.id)
pulumi.export("role_arn", lambda_iam_role.arn)
pulumi.export("role_name", lambda_iam_role.id)
pulumi.export("LambdaARN", lambda_fn.arn)
