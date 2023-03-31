# Make PDF from Lambda

Project to convert a set of images from S3 to a single .pdf, with footer and watermark.
The request comes from an API Gateway, indicating the base name.
From it, it will search all the files containing the prefix and finally a pdf file will be created on the output folder

## Request
```
{
    base: string,
    items:[{
       prefix: string,
       suffix: string,
       letter: string
    },
    ...
   ],
    solicitor: {
       cpf: string
    },
    info: {
       date: Date
   }
}
```

## Setting the infrastructure
This project also have the cloud definition using CDK: Importing an existing S3 bucket, setting up read/write permissions, creating the Lambda function and integrating it on a API Gateway
