import requests
import hashlib
import json

url = "http://20.119.77.134/SuiteCRM-7.14.3/service/v4_1/rest.php"

def rest_request(method, arguments):
    post_data = {
        "method": method,
        "input_type": "JSON",
        "response_type": "JSON",
        "rest_data": json.dumps(arguments),
    }
    response = requests.post(url, data=post_data)
    return response.json()

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

entry_args = {
    'session': sess_id,
    'module_name': 'Tasks',
    'query': "",
    'order_by': '',
    'offset': 0,
    'select_fields': ['name', 'description', 'date_start','id'],
    'link_name_to_fields_array': [],
    'max_results': 100,
    'deleted': 0,
}

result = rest_request('get_entry_list', entry_args)

# Print name, summary, and start date for each task
for task in result['entry_list']:
    task_info = task['name_value_list']
    name = task_info['name']['value']
    summary = task_info['description']['value']
    start_date = task_info['date_start']['value']
    id = task_info['id']['value']  # Get the id here
    print(f"Name: {name}\nSummary: {summary}\nStart Date: {start_date}\nID: {id}\n")
