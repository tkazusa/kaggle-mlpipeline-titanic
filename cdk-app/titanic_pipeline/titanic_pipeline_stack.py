from aws_cdk import aws_iam
from aws_cdk import aws_sagemaker as sagemaker
from aws_cdk import core


class TitanicPipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        sm_notebook_exec_role = aws_iam.Role(
            self,
            id="titanic-pipeline-sm-notebook-execution-role",
            assumed_by=aws_iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[sm_fullaccess_policy, sm_notebook_s3_access_policy],
        )

        # --------------------------------------------- #
        # SageMaker Notebook Instance
        # --------------------------------------------- #

        instance_type = "ml.t3.medium"
        role_arn = sm_notebook_exec_role.role_arn
        # LifeCycleConfigName = "clone-github-repo"
        # LifecycleScriptStr = open("sage_nw/onstart.sh", "r").read()

        sagemaker_notebook = sagemaker.CfnNotebookInstance(
            self,
            id="titanic-pipeline-notebook",
            instance_type=instance_type,
            role_arn=role_arn,
        )
