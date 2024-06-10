import requests
import hashlib
import json
import psycopg2
from datetime import datetime, timedelta

# SuiteCRM API URL
url = "http://20.119.77.134/SuiteCRM-7.14.3/service/v4_1/rest.php"

# Database connection information
hostname = '172.203.218.218'
port = '5432'
username = 'suitecrm'
password = 'test@123'
database = 'suitedb'

# Connect to the database
connection = psycopg2.connect(
    host=hostname,
    port=port,
    user=username,
    password=password,
    database=database
)
cursor = connection.cursor()

# Function to make REST requests
def rest_request(method, arguments):
    post_data = {
        "method": method,
        "input_type": "JSON",
        "response_type": "JSON",
        "rest_data": json.dumps(arguments),
    }
    response = requests.post(url, data=post_data)
    return response.json()

# Authenticate user
user_auth = {
    'user_name': 'admin',
    'password': hashlib.md5('admin'.encode()).hexdigest(),
}
app_name = 'My SuiteCRM REST Client'
name_value_list = []

args = {
    'user_auth': user_auth,
    'application_name': app_name,
    'name_value_list': name_value_list
}

result = rest_request('login', args)
sess_id = result['id']

# Retrieve tasks data
entry_args = {
    'session': sess_id,
    'module_name': 'Tasks',
    'query': "(tasks.date_modified >= NOW() - INTERVAL 4 HOUR AND tasks.date_entered < NOW() - INTERVAL 4 HOUR)",
    'order_by': '',
    'offset': 0,
    'select_fields': ['id', 'name', 'summary_c', 'date_start', 'status', 'duedate_c', 'priority', 'date_modified'],
    'link_name_to_fields_array': [],
    'max_results': 100,
    'deleted': 0,
}

result = rest_request('get_entry_list', entry_args)

# Insert data into the database
for task in result['entry_list']:
    task_info = task['name_value_list']
    name = task_info.get('name', {}).get('value', None)
    summary_c = task_info.get('summary_c', {}).get('value', None)
    start_date = task_info.get('date_start', {}).get('value', None)
    status = task_info.get('status', {}).get('value', None)
    duedate_c = task_info.get('duedate_c', {}).get('value', None)
    priority = task_info.get('priority', {}).get('value', None)
    date_modified = task_info.get('date_modified', {}).get('value', None)
    

    # Check if start_date is empty and replace with NULL
    start_date = start_date if start_date else None

    # Check if duedate_c is empty and replace with NULL
    duedate_c = duedate_c if duedate_c else None

    # Check if date_modified is empty and replace with NULL
    date_modified = date_modified if date_modified else None

    # SQL query to insert or update data into the database
    query = """
INSERT INTO ISSUES (name, summary_c, date_start, status, duedate_c, priority, date_modified) 
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (name) DO UPDATE SET
    summary_c = EXCLUDED.summary_c,
    date_start = EXCLUDED.date_start,
    status = EXCLUDED.status,
    duedate_c = EXCLUDED.duedate_c,
    priority = EXCLUDED.priority,
    date_modified = EXCLUDED.date_modified
RETURNING *; -- Return the inserted or updated row
"""

    cursor.execute(query, (name, summary_c, start_date, status, duedate_c, priority, date_modified))

    # Fetch and print the newly inserted or updated row
    inserted_or_updated_row = cursor.fetchone()
    print("Newly Inserted or Updated Row:", inserted_or_updated_row)

# Commit the transaction
connection.commit()

# Close cursor and connection
cursor.close()
connection.close()