from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
)
from constructs import Construct

class ImageProcessingPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # CodeCommit Repository
        repository = codecommit.Repository.from_repository_name(
            self, "ImageProcessingRepo", "image-processing-app"
        )

        # CodeBuild Project for CDK Deployment
        build_project = codebuild.PipelineProject(
            self, "CDKBuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": "3.9",
                            "nodejs": "14"
                        },
                        "commands": [
                            "npm install -g aws-cdk",
                            "pip install -r requirements.txt"
                        ]
                    },
                    "build": {
                        "commands": [
                            "cdk synth",
                            "cdk deploy ImageProcessingStack-dev --require-approval never"
                        ]
                    }
                },
                "artifacts": {
                    "base-directory": "cdk.out",
                    "files": "**/*"
                }
            })
        )

        # Add permissions to deploy CloudFormation stacks
        build_project.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "cloudformation:*",
                    "s3:*",
                    "iam:*",
                    "lambda:*",
                    "apigateway:*",
                    "dynamodb:*",
                    "sqs:*",
                    "sns:*",
                    "rekognition:*",
                    "logs:*",
                    "xray:*",
                    "cloudwatch:*"
                ],
                resources=["*"]
            )
        )

        # Pipeline
        source_output = codepipeline.Artifact()
        build_output = codepipeline.Artifact()

        pipeline = codepipeline.Pipeline(
            self, "ImageProcessingPipeline",
            pipeline_name="ImageProcessingPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        codepipeline_actions.CodeCommitSourceAction(
                            action_name="CodeCommit_Source",
                            repository=repository,
                            output=source_output,
                            branch="master"
                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Build_and_Deploy",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="CDK_Build_Deploy",
                            project=build_project,
                            input=source_output,
                            outputs=[build_output]
                        )
                    ]
                )
            ]
        )