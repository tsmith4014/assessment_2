import requests
import threading
import json
import time


def send_request(base_url, endpoint, method='GET', data=None):
    url = f"{base_url}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    while True:  # Continuously send requests
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data))
                if response.status_code == 201:  # If the POST request was successful
                    # Make a GET request to retrieve the 'task_id'
                    get_response = requests.get(url)
                    if get_response.status_code == 200:  # If the GET request was successful
                        tasks = get_response.json().get('tasks', [])
                        if tasks:
                            # Get the 'task_id' of the last task
                            task_id = tasks[-1].get('task_id')
                            print(f"Created task with ID: {task_id}. The Force is strong with this one.")
                            # Make a PUT request to update the 'is_done' status of the task
                            put_url = f"{url}/{task_id}"
                            put_data = {'is_done': True}
                            put_response = requests.put(put_url, headers=headers, data=json.dumps(put_data))
                            if put_response.status_code == 200:  # If the PUT request was successful
                                print(f"Updated task with ID: {task_id} to complete. The task has been completed, young Jedi.")
                            else:
                                print(f"PUT request failed with status code: {put_response.status_code}. The Dark Side I sense in you.")
                        else:
                            print(f"No tasks found. These are not the tasks you're looking for.")
                    else:
                        print(f"GET request failed with status code: {get_response.status_code}. The disturbance in the Force I feel.")
            elif method == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(data))
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                print(f"Unsupported method: {method}. Do or do not. There is no try.")

            print(f"Response from {method} {endpoint}: {response.status_code}. May the Force be with you.")
        except Exception as e:
            print(f"Request to {method} {endpoint} failed: {e}. I've got a bad feeling about this.")


def simulate_load(base_url, endpoints, num_threads, duration):
    """
    Simulates load by sending multiple requests to the specified endpoints concurrently.

    Args:
        base_url (str): The base URL of the API.
        endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
        num_threads (int): The number of threads to use for sending requests.
        duration (int): The duration to run the stress test for in seconds.

    Returns:
        None
    """
    threads = []
    for endpoint, method, data in endpoints:
        for _ in range(num_threads):
            thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
            threads.append(thread)
            thread.start()
            time.sleep(duration / num_threads)  # Spread out the start times of the threads over the duration

    for thread in threads:
        thread.join()

# Base URL of your Flask application
base_url = 'http://18.133.233.130'  # Replace with your actual base URL of the backend EC2 server

# -------------------------
# Stress Test Section (Crashing the Server)
# -------------------------
print("Starting Stress Test (Crashing the Server)")
stress_endpoints = [
    ('/todos', 'POST', {'title': 'Send in the Storm Troopers', 'description': 'Resistance is futile'}),
    ('/todos/1', 'PUT', {'is_done': True}),  # Update the task with ID 1 to complete
    ('/todos/2', 'DELETE', None),  # Delete the task with ID 2
]


# Start with 3 threads for 5 minutes
simulate_load(base_url, stress_endpoints, num_threads=3, duration=5*60)

# Ramp up to 20 threads
simulate_load(base_url, stress_endpoints, num_threads=20, duration=10*60)








##############################################################old variations and version below, all over the place############################
# import requests
# import threading
# import json
# import time


# def send_request(base_url, endpoint, method='GET', data=None):
#     """
#     Sends an HTTP request to the specified endpoint.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoint (str): The endpoint to send the request to.
#         method (str, optional): The HTTP method to use (default is 'GET').
#         data (dict, optional): The data to send with the request (default is None).

#     Returns:
#         None

#     Raises:
#         None
#     """
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 if response.status_code == 201:  # If the POST request was successful
#                     # Make a GET request to retrieve the 'task_id'
#                     get_response = requests.get(url)
#                     if get_response.status_code == 200:  # If the GET request was successful
#                         tasks = get_response.json().get('tasks', [])
#                         if tasks:
#                             # Get the 'task_id' of the last task
#                             task_id = tasks[-1].get('task_id')
#                             print(f"Created task with ID: {task_id}")
#                         else:
#                             print(f"No tasks found")
#                     else:
#                         print(f"GET request failed with status code: {get_response.status_code}")
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#             else:
#                 print(f"Unsupported method: {method}")

#             print(f"Response from {method} {endpoint}: {response.status_code}")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}")


# def simulate_load(base_url, endpoints, num_threads, duration):
#     """
#     Simulates load by sending multiple requests to the specified endpoints concurrently.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
#         num_threads (int): The number of threads to use for sending requests.
#         duration (int): The duration to run the stress test for in seconds.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
#             threads.append(thread)
#             thread.start()
#             time.sleep(duration / num_threads)  # Spread out the start times of the threads over the duration

#     for thread in threads:
#         thread.join()

# # Base URL of your Flask application
# base_url = 'http://18.133.233.130'  # Replace with your actual base URL

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Send in the Storm Troopers', 'description': 'Resistance is futile'}),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]

# # Start with 3 threads for 5 minutes
# simulate_load(base_url, stress_endpoints, num_threads=3, duration=5*60)

# # Ramp up to 20 threads
# simulate_load(base_url, stress_endpoints, num_threads=20, duration=10*60)








# import requests
# import threading
# import json
# import time

# def send_request(base_url, endpoint, method='GET', data=None):
#     """
#     Sends an HTTP request to the specified endpoint.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoint (str): The endpoint to send the request to.
#         method (str, optional): The HTTP method to use (default is 'GET').
#         data (dict, optional): The data to send with the request (default is None).

#     Returns:
#         None

#     Raises:
#         None
#     """
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 if response.status_code == 201:  # If the POST request was successful
#                     # Make a GET request to retrieve the 'task_id'
#                     get_response = requests.get(url)
#                     if get_response.status_code == 200:  # If the GET request was successful
#                         tasks = get_response.json().get('tasks', [])
#                         if tasks:
#                             # Get the 'task_id' of the last task
#                             task_id = tasks[-1].get('task_id')
#                             print(f"Created task with ID: {task_id}")
#                             # Make a PUT request to update the 'is_done' status of the task
#                             put_url = f"{url}/{task_id}"
#                             put_data = {'is_done': True}
#                             put_response = requests.put(put_url, headers=headers, data=json.dumps(put_data))
#                             print(f"PUT request sent to {put_url} with data {put_data}")
#                             if put_response.status_code == 200:  # If the PUT request was successful
#                                 print(f"Updated task with ID: {task_id} to complete")
#                             else:
#                                 print(f"PUT request failed with status code: {put_response.status_code}")
#                         else:
#                             print(f"No tasks found")
#                     else:
#                         print(f"GET request failed with status code: {get_response.status_code}")
#                 else:
#                     print(f"POST request to {endpoint} failed with status code: {response.status_code}")
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#                 print(f"Imperial forces have updated {endpoint} with a PUT request!")
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#                 print(f"Death Star has obliterated {endpoint} with a DELETE request!")
#             else:
#                 print(f"Unsupported method: {method}")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}")


# def simulate_load(base_url, endpoints, num_threads):
#     """
#     Simulates load by sending multiple requests to the specified endpoints concurrently.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
#         num_threads (int): The number of threads to use for sending requests.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
#             threads.append(thread)
#             thread.start()

#     for thread in threads:
#         thread.join()

# # Base URL of your Flask application
# base_url = 'http://35.178.184.247'  # Replace with your actual base URL

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Send in the Storm Troopers', 'description': 'Resistance is futile'}),
#     ('/todos/1', 'PUT', {'title': 'Update', 'description': 'Update description'}),
#     ('/todos/1', 'DELETE', None),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]

# # Start with threads at level you want to test, for 3 worker gunicorn start with 3 threads then increase to 20-30, using more than one ec2 instance makes this easy to ramp up.
# simulate_load(base_url, stress_endpoints, num_threads=30)


# import requests
# import threading
# import json
# import time


# def send_request(base_url, endpoint, method='GET', data=None):
#     """
#     Sends an HTTP request to the specified endpoint.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoint (str): The endpoint to send the request to.
#         method (str, optional): The HTTP method to use (default is 'GET').
#         data (dict, optional): The data to send with the request (default is None).

#     Returns:
#         None

#     Raises:
#         None
#     """
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 if response.status_code == 201:  # If the POST request was successful
#                     # Make a GET request to retrieve the 'task_id'
#                     get_response = requests.get(url)
#                     if get_response.status_code == 200:  # If the GET request was successful
#                         tasks = get_response.json().get('tasks', [])
#                         if tasks:
#                             # Get the 'task_id' of the last task
#                             task_id = tasks[-1].get('task_id')
#                             print(f"Created task with ID: {task_id}")
#                         else:
#                             print(f"No tasks found")
#                     else:
#                         print(f"GET request failed with status code: {get_response.status_code}")
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#             else:
#                 print(f"Unsupported method: {method}")

#             print(f"Response from {method} {endpoint}: {response.status_code}")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}")


# def simulate_load(base_url, endpoints, num_threads, duration):
#     """
#     Simulates load by sending multiple requests to the specified endpoints concurrently.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
#         num_threads (int): The number of threads to use for sending requests.
#         duration (int): The duration to run the stress test for in seconds.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
#             threads.append(thread)
#             thread.start()
#             time.sleep(duration / num_threads)  # Spread out the start times of the threads over the duration

#     for thread in threads:
#         thread.join()

# # Base URL of your Flask application
# base_url = 'http://3.8.238.76'  # Replace with your actual base URL

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Send in the Storm Troopers', 'description': 'Resistance is futile'}),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]

# # Start with 3 threads for 5 minutes
# simulate_load(base_url, stress_endpoints, num_threads=3, duration=5*60)

# # Ramp up to 20 threads
# simulate_load(base_url, stress_endpoints, num_threads=20, duration=5*60)


###################this version will update/put################
# def send_request(base_url, endpoint, method='GET', data=None):
#     """
#     Sends an HTTP request to the specified endpoint.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoint (str): The endpoint to send the request to.
#         method (str, optional): The HTTP method to use (default is 'GET').
#         data (dict, optional): The data to send with the request (default is None).

#     Returns:
#         None

#     Raises:
#         None
#     """
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 if response.status_code == 201:  # If the POST request was successful
#                     # Make a GET request to retrieve the 'task_id'
#                     get_response = requests.get(url)
#                     if get_response.status_code == 200:  # If the GET request was successful
#                         tasks = get_response.json().get('tasks', [])
#                         if tasks:
#                             # Get the 'task_id' of the last task
#                             task_id = tasks[-1].get('task_id')
#                             print(f"Created task with ID: {task_id}")
#                             # Make a PUT request to update the 'is_done' status of the task
#                             put_url = f"{url}/{task_id}"
#                             put_data = {'is_done': True}
#                             put_response = requests.put(put_url, headers=headers, data=json.dumps(put_data))
#                             print(f"PUT request sent to {put_url} with data {put_data}")
#                             if put_response.status_code == 200:  # If the PUT request was successful
#                                 print(f"Updated task with ID: {task_id} to complete")
#                             else:
#                                 print(f"PUT request failed with status code: {put_response.status_code}")
#                         else:
#                             print(f"No tasks found")
#                     else:
#                         print(f"GET request failed with status code: {get_response.status_code}")
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#             else:
#                 print(f"Unsupported method: {method}")

#             print(f"Response from {method} {endpoint}: {response.status_code}")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}")


########################################################################################

# def send_request(base_url, endpoint, method='GET', data=None):
#     """
#     Sends an HTTP request to the specified endpoint.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoint (str): The endpoint to send the request to.
#         method (str, optional): The HTTP method to use (default is 'GET').
#         data (dict, optional): The data to send with the request (default is None).

#     Returns:
#         None

#     Raises:
#         None
#     """
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 if response.status_code == 201:  # If the POST request was successful
#                     # Make a GET request to retrieve the 'task_id'
#                     get_response = requests.get(url)
#                     if get_response.status_code == 200:  # If the GET request was successful
#                         tasks = get_response.json().get('tasks', [])
#                         if tasks:
#                             # Get the 'task_id' of the last task
#                             task_id = tasks[-1].get('task_id')
#                             print(f"Created task with ID: {task_id}")
#                         else:
#                             print(f"No tasks found")
#                     else:
#                         print(f"GET request failed with status code: {get_response.status_code}")
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#             else:
#                 print(f"Unsupported method: {method}")

#             print(f"Response from {method} {endpoint}: {response.status_code}")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}")

# def simulate_load(base_url, endpoints, num_threads):
#     """
#     Simulates load by sending multiple requests to the specified endpoints concurrently.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
#         num_threads (int): The number of threads to use for sending requests.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             if method == 'POST':
#                 # Send a POST request to create a new task and get the ID of the newly created task
#                 new_task_id = send_request(base_url, endpoint, method, data)
#                 if new_task_id is not None:
#                     # Send a DELETE request to delete the task that was just created
#                     delete_endpoint = f"{endpoint}/{new_task_id}"
#                     thread = threading.Thread(target=lambda: send_request(base_url, delete_endpoint, 'DELETE'))
#                     threads.append(thread)
#                     thread.start()
#             else:
#                 thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
#                 threads.append(thread)
#                 thread.start()

#     for thread in threads:
#         thread.join()
#     # The join() method is a built-in method provided by the threading module in Python. It is used to make the main thread wait until all the threads in the list have completed their execution.

# # Base URL of your Flask application
# base_url = 'http://3.8.238.76'  # Replace with your actual base URL

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Send in the Storm Troopers', 'description': 'Resistance is futile'}),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]
# simulate_load(base_url, stress_endpoints, num_threads=20)




# import requests
# import threading
# import json

# def send_request(base_url, endpoint, method='GET', data=None):
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 if response.status_code == 201:  # If the POST request was successful
#                     # Make a GET request to retrieve the 'task_id'
#                     get_response = requests.get(url)
#                     if get_response.status_code == 200:  # If the GET request was successful
#                         tasks = get_response.json().get('tasks', [])
#                         if tasks:
#                             # Get the 'task_id' of the last task
#                             task_id = tasks[-1].get('task_id')
#                             print(f"Created task with ID: {task_id}")
#                         else:
#                             print(f"No tasks found")
#                     else:
#                         print(f"GET request failed with status code: {get_response.status_code}")
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#             else:
#                 print(f"Unsupported method: {method}")

#             print(f"Response from {method} {endpoint}: {response.status_code}")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}")

# def simulate_load(base_url, endpoints, num_threads):
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             if method == 'POST':
#                 # Send a POST request to create a new task and get the ID of the newly created task
#                 new_task_id = send_request(base_url, endpoint, method, data)
#                 if new_task_id is not None:
#                     # Send a DELETE request to delete the task that was just created
#                     delete_endpoint = f"{endpoint}/{new_task_id}"
#                     thread = threading.Thread(target=lambda: send_request(base_url, delete_endpoint, 'DELETE'))
#                     threads.append(thread)
#                     thread.start()
#             else:
#                 thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
#                 threads.append(thread)
#                 thread.start()

#     for thread in threads:
#         thread.join()



# # Base URL of your Flask application
# base_url = 'http://3.8.238.76'  # Replace with your actual base URL

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Send in the Storm Troopers', 'description': 'Resistance is futile'}),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]
# simulate_load(base_url, stress_endpoints, num_threads=20)




# def send_request(base_url, endpoint, method='GET', data=None):
#     """
#     Sends an HTTP request to the specified endpoint.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoint (str): The endpoint to send the request to.
#         method (str, optional): The HTTP method to use (default is 'GET').
#         data (dict, optional): The data to send with the request (default is None).

#     Returns:
#         None

#     Raises:
#         None
#     """
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#             else:
#                 print(f"Unsupported method: {method}")
#                 break  # Exit loop if method is unsupported

#             print(f"Response from {method} {endpoint}: {response.status_code}")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}")

# def simulate_load(base_url, endpoints, num_threads):
#     """
#     Simulates load by sending multiple requests to the specified endpoints concurrently.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
#         num_threads (int): The number of threads to use for sending requests.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
#             threads.append(thread)
#             thread.start()

#     for thread in threads:
#         thread.join()
#     # The join() method is a built-in method provided by the threading module in Python. It is used to make the main thread wait until all the threads in the list have completed their execution.

# # Base URL of your Flask application
# base_url = 'http://3.8.238.76'  # Replace with your actual base URL

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Stress Test task', 'description': 'This is a stress test task'}),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]
# simulate_load(base_url, stress_endpoints, num_threads=20)


# import requests
# import threading
# import json
# import time


# def send_request(base_url, endpoint, method='GET', data=None):
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     while True:  # Continuously send requests
#         try:
#             if method == 'GET':
#                 response = requests.get(url)
#             elif method == 'POST':
#                 response = requests.post(url, headers=headers, data=json.dumps(data))
#                 if response.status_code == 201:  # If the POST request was successful
#                     # Make a GET request to retrieve the 'task_id'
#                     get_response = requests.get(url)
#                     if get_response.status_code == 200:  # If the GET request was successful
#                         tasks = get_response.json().get('tasks', [])
#                         if tasks:
#                             # Get the 'task_id' of the last task
#                             task_id = tasks[-1].get('task_id')
#                             print(f"Created task with ID: {task_id}. The Force is strong with this one.")
#                             # Make a PUT request to update the 'is_done' status of the task
#                             put_url = f"{url}/{task_id}"
#                             put_data = {'is_done': True}
#                             put_response = requests.put(put_url, headers=headers, data=json.dumps(put_data))
#                             if put_response.status_code == 200:  # If the PUT request was successful
#                                 print(f"Updated task with ID: {task_id} to complete. The task has been completed, young Jedi.")
#                             else:
#                                 print(f"PUT request failed with status code: {put_response.status_code}. The Dark Side I sense in you.")
#                         else:
#                             print(f"No tasks found. These are not the tasks you're looking for.")
#                     else:
#                         print(f"GET request failed with status code: {get_response.status_code}. The disturbance in the Force I feel.")
#             elif method == 'PUT':
#                 response = requests.put(url, headers=headers, data=json.dumps(data))
#             elif method == 'DELETE':
#                 response = requests.delete(url)
#             else:
#                 print(f"Unsupported method: {method}. Do or do not. There is no try.")

#             print(f"Response from {method} {endpoint}: {response.status_code}. May the Force be with you.")
#         except Exception as e:
#             print(f"Request to {method} {endpoint} failed: {e}. I've got a bad feeling about this.")


# def simulate_load(base_url, endpoints, num_threads, duration):
#     """
#     Simulates load by sending multiple requests to the specified endpoints concurrently.

#     Args:
#         base_url (str): The base URL of the API.
#         endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
#         num_threads (int): The number of threads to use for sending requests.
#         duration (int): The duration to run the stress test for in seconds.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
#             threads.append(thread)
#             thread.start()
#             time.sleep(duration / num_threads)  # Spread out the start times of the threads over the duration

#     for thread in threads:
#         thread.join()

# # Base URL of your Flask application
# base_url = 'http://18.133.233.130'  # Replace with your actual base URL

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Send in the Storm Troopers', 'description': 'Resistance is futile'}),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]

# # Start with 3 threads for 5 minutes
# simulate_load(base_url, stress_endpoints, num_threads=3, duration=5*60)

# # Ramp up to 20 threads
# simulate_load(base_url, stress_endpoints, num_threads=20, duration=10*60)
