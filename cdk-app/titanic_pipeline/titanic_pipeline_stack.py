from aws_cdk import aws_iam
from aws_cdk import aws_sagemaker as sagemaker
from aws_cdk import core


class TitanicPipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ### SageMaker Notebook ###
        # --------------------------------------------- #
        # IAM Role for SageMaker Notebook Instance
        # --------------------------------------------- #
        # SageMaker Full Access Pilicy
        sm_fullaccess_policy = aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            "AmazonSageMakerFullAccess"
        )

        # Permissions for SageMaker to access S3 buckets in account
        sm_notebook_s3_access_policy_statement = aws_iam.PolicyStatement(
            actions=["s3:*"],
            effect=aws_iam.Effect.ALLOW,
            resources=["arn:aws:s3:::*"],
        )

        sm_notebook_s3_access_policy = aws_iam.ManagedPolicy(
            self,
            id="sm_notebook_s3_access_policy",
            statements=[sm_notebook_s3_access_policy_statement],
        )

        # Permission for SageMaker to utilize StepFunctions for pipeline creation
        sfn_fullaccess_policy = aws_iam.ManagedPolicy.from_aws_managed_policy_name(
            "AWSStepFunctionsFullAccess"
        )

        sm_notebook_exec_role = aws_iam.Role(
            self,
            id="titanic-pipeline-sm-notebook-execution-role",
            assumed_by=aws_iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                sm_fullaccess_policy,
                sm_notebook_s3_access_policy,
                sfn_fullaccess_policy,
            ],
        )

        # --------------------------------------------- #
        # SageMaker Notebook Instance
        # --------------------------------------------- #

        instance_type = "ml.t3.medium"
        role_arn = sm_notebook_exec_role.role_arn

        sagemaker_notebook = sagemaker.CfnNotebookInstance(
            self,
            id="titanic-pipeline-notebook",
            instance_type=instance_type,
            role_arn=role_arn,
            default_code_repository="https://github.com/tkazusa/kaggle-mlpipeline-titanic.git",
        )

        ### Step Functions Workflow Execution Role ###
        # --------------------------------------------- #
        # CloudWatchEvents managed policies
        # --------------------------------------------- #
        cloudwatchevents_fullaccess_policy = (
            aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                "CloudWatchEventsFullAccess"
            )
        )

        # --------------------------------------------- #
        # SFn inline policies
        # --------------------------------------------- #

        sfn_workflow_exec_inline_policy_steps_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "sagemaker:CreateTransformJob",
                "sagemaker:DescribeTransformJob",
                "sagemaker:StopTransformJob",
                "sagemaker:CreateProcessingJob",
                "sagemaker:DescribeProcessingJob",
                "sagemaker:StopProcessingJob",
                "sagemaker:CreateTrainingJob",
                "sagemaker:DescribeTrainingJob",
                "sagemaker:StopTrainingJob",
                "sagemaker:CreateHyperParameterTuningJob",
                "sagemaker:DescribeHyperParameterTuningJob",
                "sagemaker:StopHyperParameterTuningJob",
                "sagemaker:CreateModel",
                "sagemaker:CreateEndpointConfig",
                "sagemaker:CreateEndpoint",
                "sagemaker:DeleteEndpointConfig",
                "sagemaker:DeleteEndpoint",
                "sagemaker:UpdateEndpoint",
                "sagemaker:ListTags",
                "lambda:InvokeFunction",
                "sqs:SendMessage",
                "sns:Publish",
                "ecs:RunTask",
                "ecs:StopTask",
                "ecs:DescribeTasks",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "batch:SubmitJob",
                "batch:DescribeJobs",
                "batch:TerminateJob",
                "glue:StartJobRun",
                "glue:GetJobRun",
                "glue:GetJobRuns",
                "glue:BatchStopJobRun",
            ],
            resources=["*"],
        )
        sfn_workflow_exec_inline_policy_passrole_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iam:PassRole"],
            resources=["*"],
            conditions={
                "StringEquals": {"iam:PassedToService": "sagemaker.amazonaws.com"}
            },
        )
        sfn_workflow_exec_inline_policy_event_statement = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["events:PutTargets", "events:PutRule", "events:DescribeRule"],
            resources=[
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTrainingJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTransformJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTuningJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForECSTaskRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForBatchJobsRule",
            ],
        )

        # --------------------------------------------- #
        # SFn workflow execution role
        # --------------------------------------------- #

        sfn_workflow_exec_role = aws_iam.Role(
            self,
            id="stepfunctions-workflow-exection-role",
            assumed_by=aws_iam.ServicePrincipal("states.amazonaws.com"),
            managed_policies=[
                cloudwatchevents_fullaccess_policy,
            ],
            inline_policies={
                "sfn-inline-policy": aws_iam.PolicyDocument(
                    statements=[
                        sfn_workflow_exec_inline_policy_steps_statement,
                        sfn_workflow_exec_inline_policy_passrole_statement,
                        sfn_workflow_exec_inline_policy_event_statement,
                    ]
                )
            },
        )
