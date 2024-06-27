
# Telegram_AWS_Bill_Notification_System

## Overview

This project sets up a serverless architecture using AWS Lambda to fetch AWS billing information and publish it to a Telegram channel daily. The Serverless Framework is used to manage the deployment of the Lambda function and its associated IAM role.

## Prerequisites

- Node.js and npm installed
- Serverless Framework installed (`npm install -g serverless`)
- AWS CLI configured with appropriate credentials
- Your AWS account ID
- Telegram Bot Token and Chat ID

## Deployment

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-repo/aws-monitoring.git
   cd aws-monitoring
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Update `serverless.yml`**

   Replace `YOUR_ACCOUNT_ID` in the `serverless.yml` file with your actual AWS account ID.

4. **Add environment variables**

   Add your Telegram Bot Token and Chat ID to the environment variables in your Lambda handler file or through the Serverless Framework `serverless.yml` file.

5. **Deploy the service**

   ```bash
   serverless deploy
   ```

   This command will create the necessary IAM role, deploy the Lambda function, and set up the daily trigger to fetch billing information and publish it to your Telegram channel.

## What It Does

- **IAM Role Creation**: An IAM role with permissions to create log groups, log streams, put log events, and access Cost Explorer and Budgets services.
- **Lambda Function**: A Python-based Lambda function that fetches AWS billing information.
- **Scheduled Execution**: The Lambda function is triggered daily using an AWS CloudWatch Events rule.
- **Notification**: The fetched billing information is published to a specified Telegram channel.

## Additional Information

- Ensure your Telegram bot has the necessary permissions to send messages to your Telegram channel.
- The Lambda function logs can be monitored in AWS CloudWatch Logs under the log group `/aws/lambda/aws_monitoring`.

## Contributing

If you encounter any issues or have suggestions for improvement, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

