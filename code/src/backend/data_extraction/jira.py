import os
from atlassian import Jira
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
# Configuration
JIRA_URL = "https://error-402.atlassian.net"  # Replace with your JIRA URL
ATLASSIAN_USER = os.getenv("CONFLUENCE_USER")  # Replace with your Atlassian account email
ATLASSIAN_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")  # Replace with your Atlassian API token
TICKET_KEY = "CCS-8"  # Replace with the JIRA ticket key

def get_jira_ticket_details(ticket_key):
    try:
        # Initialize the JIRA client
        jira = Jira(
            url=JIRA_URL,
            username=ATLASSIAN_USER,
            password=ATLASSIAN_API_TOKEN
        )
        
        # Fetch ticket details
        issue = jira.issue(ticket_key)
        
        # Print the issue details in a readable format
        print(json.dumps(issue, indent=4))

        return issue

    except Exception as e:
        print(f"Error fetching ticket details: {e}")


# print(get_jira_ticket_details(TICKET_KEY))