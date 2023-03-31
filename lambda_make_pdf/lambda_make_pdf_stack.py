from aws_cdk import (
    Stack,
    Duration,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_lambda_python_alpha as alambda_,
    aws_apigateway as apigateway
)
from constructs import Construct

class LambdaMakePdfStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Existing S3
        bucket = s3.Bucket.from_bucket_arn(self, 
                           id = "", 
                           bucket_arn="")
        # S3 access policies
        s3ReadWrite = iam.PolicyStatement(
                actions = ["s3:GetObject", "s3:PutObject"],
                resources = [bucket.bucket_arn + "/*"]
                )

        s3ListObjects = iam.PolicyStatement(
                actions = ["s3:ListBucket"],
                resources = [bucket.bucket_arn]
                )
        #### FOR DEPENDENCIES - SOLUTION 1 : LAMBDA LAYERS ####
        # Lambda LAYERS
        lambdaLayer = lambda_.LayerVersion(self,
                                           "lambda_layer",
                                           code = lambda_.AssetCode("./src/layer/"),
                                           compatible_runtimes = [lambda_.Runtime.PYTHON_3_8])
#        # Lambda
        lambdaFunction = lambda_.Function(self,
                                          "CreatePdfFunction",
                                          runtime=lambda_.Runtime.PYTHON_3_8,
                                          code=lambda_.Code.from_asset('./src/code/'),
                                          handler='Main.handler',
                                          initial_policy=[s3ReadWrite, s3ListObjects], 
                                          timeout=Duration.seconds(180),
                                          function_name="CreatePdfFunctionCDK",
                                          layers = [lambdaLayer],
                                          environment={'iPath':'supplier/images/','oPath':'supplier/pdf/' ,'BUCKET_NAME': bucket.bucket_name})

        ##### SOLUTION 2  - **EXPERIMENTAL** AWS_LAMBDA_PYTHON_ALPHA
#        initiator = alambda_.PythonFunction(
#                self,
#                'CreatePdfFunction',
#                entry = './src/code/',
#                runtime = lambda_.Runtime.PYTHON_3_8,
#                index='Main.py',
#                handler='handler',
#                initial_policy=[s3ReadWrite, s3ListObjects], 
#                timeout=Duration.seconds(180),
#                environment={'iPath':'supplier/images/','oPath':'supplier/pdf/' ,'BUCKET_NAME': bucket.bucket_name}
#                )
        # API Gateway
        api = apigateway.RestApi(self,
                                 'MakePdfGateway',
                                 rest_api_name='PDF Gateway',
                                 description='Gateway for creating internal PDFs'
                                 )

        integration = apigateway.LambdaIntegration(lambdaFunction,
                                                   request_templates={"application/json": '{"statusCode":"200"}'})
        
        api.root.add_method("POST", integration)

