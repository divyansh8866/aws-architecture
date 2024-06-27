`Developer`: Divyansh Patel
## Purpose
The purpose of this service is to facilitate serverless computing for specific tasks within the AWS infrastructure. It is configured to handle events triggered by SQS messages and to provide an HTTP API for external communication.

## Configuration Details

### Provider
The service is configured to use AWS as the cloud provider, utilizing the Python 3.11 runtime in the dev stage, located in the US East 1 region.

### Functions
A Lambda function named "sqsLambdaFunction" is defined to handle events triggered by SQS messages. This function has specific timeout and memory size configurations and is triggered by SQS events with a defined batch size.

### Resources
Several AWS resources are provisioned:
- An SQS queue named "MySqsQueue" is created to handle message queuing.
- An HTTP API named "MyHttpApi" is established, allowing for HTTP-based communication. Access logs are configured for monitoring purposes.
- An IAM role named "MyHttpApiRole" is created to grant necessary permissions for the HTTP API to interact with SQS and logging services.

### Outputs
Several outputs are provided for ease of access:
- The HTTP API endpoint URL is provided for external access.
- The name and reference of the SQS Lambda function are given.
- The ARN and URL of the SQS queue are also provided for reference.

## Conclusion
This Markdown document serves as a user-friendly guide to understanding the purpose, configuration, and outputs of the "my-serverless-service" within the AWS environment. It aims to provide clarity and insight into the functionalities and resources provisioned by the service.
