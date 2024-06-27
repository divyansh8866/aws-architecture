import os
import json
import boto3
import requests
from datetime import datetime, timedelta

TELEGRAM_API_TOKEN = "**"
TELEGRAM_CHAT_ID = "**"
AWS_REGION = 'us-east-1'  # Change to your AWS region
BUDGET_NAME = "LearingBudget" # Only if you have already created a budget.
YOUR_AWS_ACCOUNT_ID="***"

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage'
    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Specify MarkdownV2 parsing mode
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to send message to Telegram. Status code: {response.status_code}")
    else:
        print("Message sent successfully to Telegram.")
        
def get_budget_status(budgets_client, budget_name):
    response = budgets_client.describe_budget(
        AccountId=YOUR_AWS_ACCOUNT_ID,  # Replace with your AWS account ID
        BudgetName=budget_name
    )
    budget_status = response['Budget']['BudgetLimit']
    return budget_status

# Uncomment and modify the following line if you want to test the Lambda function locally
# lambda_handler({}, None)


def lambda_handler(event, context):
    # Set up AWS Cost Explorer client
    ce_client = boto3.client('ce', region_name=AWS_REGION)

    # Get today's date
    current_date = datetime.utcnow().strftime('%Y-%m-%d')
    start_of_month = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
    last_month_start = (datetime.utcnow().replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')

    # Get month-to-date cost
    mtd_response = ce_client.get_cost_and_usage(
        TimePeriod={'Start': start_of_month, 'End': current_date},
        Granularity='MONTHLY',
        Metrics=['BlendedCost']
    )
    month_to_date_cost = round(float(mtd_response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']),2)

    # Get last month's total cost
    last_month_response = ce_client.get_cost_and_usage(
        TimePeriod={'Start': last_month_start, 'End': start_of_month},
        Granularity='MONTHLY',
        Metrics=['BlendedCost']
    )
    last_month_cost = round(float(last_month_response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']),2)

    # Get budgets status (you need to set up AWS Budgets for this)
    budgets_client = boto3.client('budgets', region_name=AWS_REGION)
    budget_name = BUDGET_NAME # Replace with your actual budget name
    budget_status = get_budget_status(budgets_client, budget_name)

    # Compose message
    message = (
        f"*AWS Billing Info:*\n"
        f"_Month-to-date Cost:_ *{month_to_date_cost} USD*\n"
        f"_Last Month's Total Cost:_ *{last_month_cost} USD*\n"
        f"_Budgets Status:_ *{budget_status.get('Amount')} {budget_status.get('Unit')}*"
    )
    print(message)

    # Send message to Telegram
    send_telegram_message(message)