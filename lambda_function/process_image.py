# lambda_function/process_image.py
import boto3
import os
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Process each record from SQS
        for record in event['Records']:
            try:
                # Parse the message body from SQS
                if isinstance(record['body'], str):
                    message_body = json.loads(record['body'])
                else:
                    message_body = record['body']
                
                # Extract S3 event information
                if 'Records' in message_body:
                    s3_record = message_body['Records'][0]
                    bucket_name = s3_record['s3']['bucket']['name']
                    object_key = s3_record['s3']['object']['key']
                else:
                    # Direct invocation or different format
                    logger.error(f"Unexpected message format: {message_body}")
                    continue
                
                logger.info(f"Processing image: {object_key} from bucket: {bucket_name}")
                
                # Process the image with Rekognition
                response = rekognition.detect_labels(
                    Image={'S3Object': {'Bucket': bucket_name, 'Name': object_key}},
                    MaxLabels=10
                )
                
                # Extract labels from response
                labels = [label['Name'] for label in response['Labels']]
                logger.info(f"Detected labels: {labels}")
                
                # Save results to DynamoDB
                table_name = os.environ['PRODUCT_TAG_DATABASE']
                table = dynamodb.Table(table_name)
                
                item = {
                    'ImageKey': object_key,
                    'Labels': labels,
                    'ProcessedTimestamp': context.invoked_function_arn  # Added timestamp
                }
                
                table.put_item(Item=item)
                logger.info(f"Saved results to DynamoDB table: {table_name}")
                
                # Notify via SNS
                topic_arn = os.environ['SNS_TOPIC_ImageProcessing']
                message = {
                    'bucket': bucket_name,
                    'imageKey': object_key,
                    'labels': labels,
                    'status': 'success'
                }
                
                sns.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(message),
                    Subject=f'Image Processing Complete: {object_key}'
                )
                logger.info(f"Published notification to SNS topic: {topic_arn}")
                
            except Exception as record_error:
                logger.error(f"Error processing record: {str(record_error)}")
                # Continue processing other records even if one fails
                continue
        
        return {
            'statusCode': 200,
            'body': 'Processing complete'
        }
        
    except Exception as e:
        error_message = f"Error in lambda_handler: {str(e)}"
        logger.error(error_message)
        
        # Try to publish failure to SNS if possible
        try:
            sns.publish(
                TopicArn=os.environ['SNS_TOPIC_ImageProcessing'],
                Message=json.dumps({
                    'status': 'error',
                    'error': error_message
                }),
                Subject='Image Processing Error'
            )
        except Exception:
            # If SNS publish fails, just log it
            logger.error("Could not publish error to SNS")
        
        return {
            'statusCode': 500,
            'body': error_message
        }