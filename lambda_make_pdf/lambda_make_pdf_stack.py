from aws_cdk import (
    # Duration,
    Stack,
    Duration,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,

)
from constructs import Construct

class LambdaMakePdfStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # S3
        bucket = s3.Bucket(self, 
                           "images1689e81f-4313-4cf0-8184-abb0d0808b6a", 
                           bucket_name="images1689e81f-4313-4cf0-8184-abb0d0808b6a")
        # S3 access policies
        s3ReadWrite = iam.PolicyStatement(
                actions = ["s3:GetObject", "s3:PutObject"],
                resources = [bucket.bucket_arn + "/*"]
                )

        s3ListObjects = iam.PolicyStatement(
                actions = ["s3:ListBucket"],
                resources = [bucket.bucket_arn]
                )

        # Lambda
        lambdaFunction = lambda_.Function(self,
                                          "CreatePdfFunction",
                                          runtime=lambda_.Runtime.PYTHON_3_8,
                                          code=lambda_.code.from_asset('src'),
                                          handler='code.handler',
                                          initial_policy=[s3ReadWrite, s3ListObjects], 
                                          timeout=Duration.seconds(180),
                                          function_name="CreatePdfFunctionCDK")

