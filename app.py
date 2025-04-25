import os
import aws_cdk as cdk
from Image_stack.image_process_stack import ImageProcessingStack
from pipeline.pipeline_stack import ImageProcessingPipelineStack

app = cdk.App()

# Deploy the pipeline stack
ImageProcessingPipelineStack(
    app, 
    "ImageProcessingPipelineStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION', 'eu-west-1')
    )
)

# Conditionally deploy environments for local development/testing
# These won't be used by the pipeline but are useful for manual deployment
if os.getenv('MANUAL_DEPLOY', 'false').lower() == 'true':
    # Dev environment
    ImageProcessingStack(
        app, 
        "ImageProcessingStack-dev",
        stage="dev",
        env=cdk.Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=os.getenv('CDK_DEFAULT_REGION', 'eu-west-1')
        )
    )
    
    # Prod environment
    ImageProcessingStack(
        app, 
        "ImageProcessingStack-prod",
        stage="prod",
        env=cdk.Environment(
            account=os.getenv('CDK_DEFAULT_ACCOUNT'),
            region=os.getenv('CDK_DEFAULT_REGION', 'eu-west-1')
        )
    )

app.synth()