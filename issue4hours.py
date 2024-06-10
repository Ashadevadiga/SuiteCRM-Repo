import requests
import hashlib
import json
import time
import csv

# Define the SuiteCRM REST API URL
url = "http://20.119.77.134/SuiteCRM-7.14.3/service/v4_1/rest.php"

# Function to make REST API requests
def rest_request(method, arguments):
    post_data = {
        "method": method,
        "input_type": "JSON",
        "response_type": "JSON",
        "rest_data": json.dumps(arguments),
    }
    response = requests.post(url, data=post_data)
    return response.json()

# Function to authenticate and obtain a session ID
def login():
    user_auth = {
        'user_name': 'admin',
        'password': hashlib.md5('admin'.encode()).hexdigest(),
    }
    args = {
        'user_auth': user_auth,
        'application_name': 'My SuiteCRM REST Client',
        'name_value_list': []
    }
    result = rest_request('login', args)
    return result['id']

# Function to get the details of an issue by ID
def get_issue_details(issue_id, session_id):
    entry_args = {
        'session': session_id,
        'module_name': 'Tasks',
        'id': issue_id,
        'select_fields': ['name', 'date_start', 'date_due','status'],
        'link_name_to_fields_array': [],
    }
    result = rest_request('get_entry', entry_args)
    return result['entry_list'][0]['name_value_list']

# Function to fetch updated issue IDs since the last check
# Function to fetch updated issue IDs since the last check
def get_updated_issue_ids(session_id):
    # Update the query to fetch only the issues that were updated in the last 4 hours and not created in the last 4 hours
    query = "(tasks.date_modified >= NOW() - INTERVAL 4 HOUR AND tasks.date_entered < NOW() - INTERVAL 4 HOUR)"
    args = {
        'session': session_id,
        'module_name': 'Tasks',
        'query': query,
        'order_by': '',
        'offset': 0,
        'select_fields': ['id'],
        'link_name_to_fields_array': [],
        'max_results': 100,
        'deleted': 0,
    }
    result = rest_request('get_entry_list', args)
    print("Response from get_entry_list API:", result)  # Add this line to print the response
    return [entry['id'] for entry in result['entry_list']]

# Function to monitor for updates and write to CSV
def monitor_issue_updates(session_id):
    # Get the list of updated issue IDs since the last check
    updated_issue_ids = get_updated_issue_ids(session_id)
    
    # Open a CSV file for writing
    with open('updated1_issues.csv', 'w', newline='') as csvfile:
        fieldnames = ['Issue ID', 'Issue Name', 'Start Date', 'Due Date', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Display the details of updated issues
        for issue_id in updated_issue_ids:
            updated_issue_details = get_issue_details(issue_id, session_id)
            print(f"Updated Issue ID: {issue_id}")
            print(f"Issue Details: {updated_issue_details}")

            # Write the issue details to the CSV file
            writer.writerow({
                'Issue ID': issue_id,
                'Issue Name': updated_issue_details['name']['value'],
                'Start Date': updated_issue_details['date_start']['value'],
                'Due Date': updated_issue_details['date_due']['value'],
                'Status': updated_issue_details['status']['value'],
            })

# Main function
if __name__ == "__main__":
    # Authenticate and obtain a session ID
    session_id = login()
    
    # Monitor for updates
    monitor_issue_updates(session_id)