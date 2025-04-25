from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_lambda as lambda_,
    aws_lambda_event_sources as events,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_s3_notifications as s3_notifications,
    aws_cloudwatch as cw,
    aws_cloudwatch_actions as cw_actions,
)
from constructs import Construct

class ImageProcessingStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        removal_policy = RemovalPolicy.RETAIN if stage == "prod" else RemovalPolicy.DESTROY

        # ✅ DynamoDB Table
        table = dynamodb.Table(
            self,
            "ProductTagsTable",
            table_name=f"product_tag_table-{stage}",
            partition_key=dynamodb.Attribute(name="ImageKey", type=dynamodb.AttributeType.STRING),
            removal_policy=removal_policy,
        )

        # ✅ S3 Bucket
        bucket = s3.Bucket(
            self,
            "ProductImagesBucket",
            versioned=True,
            removal_policy=removal_policy,
        )

        # ✅ SNS Topic + Email Subscription
        topic = sns.Topic(self, f"ImageProcessingTopic-{stage}")
        topic.add_subscription(subscriptions.EmailSubscription("mehdi.sghaier@draexlmaier.com"))  

        # ✅ Dead Letter Queue
        dlq = sqs.Queue(self, "ImageProcessingDLQ")

        # ✅ SQS Queue with DLQ
        queue = sqs.Queue(
            self,
            "ImageProcessingQueue",
            visibility_timeout=Duration.seconds(300),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,
                queue=dlq
            )
        )

        # ✅ Lambda Function with X-Ray Tracing
        lambda_function = lambda_.Function(
            self, "ImageProcessingFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="process_image.lambda_handler",
            code=lambda_.Code.from_asset("lambda_function"),
            timeout=Duration.seconds(60),
            tracing=lambda_.Tracing.ACTIVE,  # Enable X-Ray
            environment={
                "PRODUCT_TAG_DATABASE": table.table_name,
                "QUEUE_URL": queue.queue_url,
                "SNS_TOPIC_ImageProcessing": topic.topic_arn,
            }
        )

        # ✅ Permissions
        bucket.grant_read(lambda_function)
        table.grant_write_data(lambda_function)
        topic.grant_publish(lambda_function)
        queue.grant_consume_messages(lambda_function)

        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rekognition:DetectLabels", "xray:PutTraceSegments", "xray:PutTelemetryRecords"],
                resources=["*"]
            )
        )

        # ✅ Lambda listens to SQS
        lambda_function.add_event_source(events.SqsEventSource(queue))

        # ✅ S3 notifies SQS on object creation
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3_notifications.SqsDestination(queue)
        )

        # ✅ CloudWatch Alarm for Lambda Errors
        error_alarm = cw.Alarm(
            self, "LambdaErrorAlarm",
            metric=lambda_function.metric_errors(),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Alarm when the Lambda function has an error",
            alarm_name=f"{stage}-LambdaErrorAlarm"
        )
        error_alarm.add_alarm_action(cw_actions.SnsAction(topic))

        # ✅ CloudWatch Alarm for Lambda Duration
        duration_alarm = cw.Alarm(
            self, "LambdaDurationAlarm",
            metric=lambda_function.metric_duration(),
            threshold=50000,  # 50 seconds
            evaluation_periods=1,
            alarm_description="Alarm when Lambda execution time exceeds 50s",
            alarm_name=f"{stage}-LambdaDurationAlarm"
        )
        duration_alarm.add_alarm_action(cw_actions.SnsAction(topic))

        # ✅ Outputs
        CfnOutput(self, "S3BucketName", value=bucket.bucket_name)
        CfnOutput(self, "DynamoDBTableName", value=table.table_name)
        CfnOutput(self, "ImageProcessingTopicArn", value=topic.topic_arn)
        CfnOutput(self, "QueueUrl", value=queue.queue_url)
        CfnOutput(self, "LambdaFunctionName", value=lambda_function.function_name)
