📷 Image Processing Application on AWS
This project is an event-driven, serverless image processing system built using AWS CDK (Python).
It automatically processes images uploaded to an S3 bucket, detects objects using Amazon Rekognition, stores results in DynamoDB, and sends notifications via SNS.
A full CI/CD pipeline using CodeCommit, CodeBuild, and CodePipeline ensures automated deployment.

🛠️ Architecture
Amazon S3: Stores uploaded product images.

Amazon SQS: Buffers S3 event notifications and ensures reliable processing.

AWS Lambda: Processes images, uses Rekognition to detect labels, saves results to DynamoDB, and sends notifications.

Amazon Rekognition: Detects labels/tags within images.

Amazon DynamoDB: Stores processed image metadata and tags.

Amazon SNS: Sends email notifications after processing or in case of errors.

Amazon CloudWatch: Monitors Lambda function errors and durations through alarms.

AWS CodeCommit: Hosts the application source code.

AWS CodePipeline: Orchestrates continuous integration and deployment (CI/CD).

AWS CodeBuild: Builds and deploys the infrastructure using AWS CDK.

📂 Project Structure
bash
Copy
Edit
├── cdk.json
├── README.md
├── lambda_function/
│   └── process_image.py   # Lambda function for processing images
├── stack/
│   ├── image_processing_stack.py  # Infrastructure: S3, SQS, SNS, Lambda, DynamoDB, CloudWatch
│   └── image_processing_pipeline_stack.py  # CI/CD Pipeline: CodeCommit, CodeBuild, CodePipeline
├── requirements.txt
└── ...
🚀 Deployment Workflow
Upload an image to the S3 bucket.

S3 Event triggers an SQS message.

Lambda function is triggered by the SQS message:

Downloads the image from S3.

Detects labels using Rekognition.

Stores image metadata and detected labels into DynamoDB.

Sends an SNS notification (email) with the detection results.

CloudWatch alarms monitor and alert if Lambda experiences high error rates or long runtimes.

🧪 CI/CD Pipeline
Source: Pulls the code from CodeCommit repository (master branch).

Build:

Installs dependencies (Python & CDK).

Synthesizes the CDK CloudFormation templates.

Deploys the ImageProcessingStack-dev environment.

Permissions: CodeBuild has wide deployment permissions across S3, Lambda, DynamoDB, SQS, SNS, Rekognition, CloudFormation, CloudWatch, X-Ray.

⚙️ Features
✅ Serverless architecture (auto-scaling, no server maintenance)

✅ Event-driven using S3 + SQS + Lambda

✅ Image recognition using Amazon Rekognition

✅ DynamoDB storage for image metadata and tags

✅ Email notifications after each image processing

✅ Dead Letter Queue (DLQ) to handle failed processing safely

✅ CloudWatch alarms for Lambda monitoring

✅ X-Ray tracing for Lambda performance and debugging

✅ Automated deployments with CI/CD Pipeline (CodeCommit + CodeBuild + CodePipeline)

✅ Environment isolation (dev or prod) with configurable removal policies

🔧 How to Deploy
Install AWS CDK if not already installed:

bash
Copy
Edit
npm install -g aws-cdk
Install project dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Bootstrap your AWS environment (only once per account/region):

bash
Copy
Edit
cdk bootstrap
Deploy the stack:

bash
Copy
Edit
cdk deploy ImageProcessingStack-dev
📜 Environment Variables for Lambda
PRODUCT_TAG_DATABASE - DynamoDB table name where image labels are stored.

QUEUE_URL - SQS Queue URL where messages are received.

SNS_TOPIC_ImageProcessing - SNS Topic ARN for notifications.

📧 Notifications
You will receive an email notification upon:

Successful image processing (with labels detected)

Any processing error or Lambda function failure (via CloudWatch alarms)

Default email recipient:
mehdi.sghaier@draexlmaier.com

📈 Monitoring
CloudWatch Alarms trigger if:

Lambda errors > 1 per evaluation period.

Lambda execution time > 50 seconds.

X-Ray Tracing is enabled for end-to-end debugging of Lambda functions.

🧹 Resource Cleanup
If you're deploying in a non-production environment (dev), resources will be automatically destroyed when you delete the stack.
For production (prod), resources like S3 bucket and DynamoDB table are retained.

🙌 Author
Mehdi Sghaier