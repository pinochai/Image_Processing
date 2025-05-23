import aws_cdk as core
import aws_cdk.assertions as assertions

from image_processing_pipeline.image_processing_pipeline_stack import ImageProcessingPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in image_processing_pipeline/image_processing_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ImageProcessingPipelineStack(app, "image-processing-pipeline")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
