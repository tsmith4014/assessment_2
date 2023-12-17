import requests
import threading
import json

def send_request(base_url, endpoint, method='GET', data=None):
    """
    Sends an HTTP request to the specified endpoint.

    Args:
        base_url (str): The base URL of the API.
        endpoint (str): The endpoint to send the request to.
        method (str, optional): The HTTP method to use (default is 'GET').
        data (dict, optional): The data to send with the request (default is None).

    Returns:
        None

    Raises:
        None
    """
    url = f"{base_url}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    while True:  # Continuously send requests
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data))
            elif method == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(data))
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                print(f"Unsupported method: {method}")
                break  # Exit loop if method is unsupported

            print(f"Response from {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"Request to {method} {endpoint} failed: {e}")

def simulate_load(base_url, endpoints, num_threads):
    """
    Simulates load by sending multiple requests to the specified endpoints concurrently.

    Args:
        base_url (str): The base URL of the API.
        endpoints (list): A list of tuples containing the endpoint, HTTP method, and data for each request.
        num_threads (int): The number of threads to use for sending requests.

    Returns:
        None
    """
    threads = []
    for endpoint, method, data in endpoints:
        for _ in range(num_threads):
            thread = threading.Thread(target=lambda: send_request(base_url, endpoint, method, data))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()
    # The join() method is a built-in method provided by the threading module in Python. It is used to make the main thread wait until all the threads in the list have completed their execution.

# Base URL of your Flask application
base_url = 'http://3.8.238.76'  # Replace with your actual base URL

# -------------------------
# Stress Test Section (Crashing the Server)
# -------------------------
print("Starting Stress Test (Crashing the Server)")
stress_endpoints = [
    ('/todos', 'POST', {'title': 'Stress Test task', 'description': 'This is a stress test task'}),
    # Add more intensive POST, PUT, DELETE endpoints
]
simulate_load(base_url, stress_endpoints, num_threads=20)







# import requests
# import threading
# import json

# def send_request(base_url, endpoint, method='GET', data=None):
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     try:
#         if method == 'GET':
#             response = requests.get(url)
#         elif method == 'POST':
#             response = requests.post(url, headers=headers, data=json.dumps(data))
#         elif method == 'PUT':
#             response = requests.put(url, headers=headers, data=json.dumps(data))
#         elif method == 'DELETE':
#             response = requests.delete(url)
#         else:
#             print(f"Unsupported method: {method}")
#             return

#         print(f"Response from {method} {endpoint}: {response.status_code}")
#     except Exception as e:
#         print(f"Request to {method} {endpoint} failed: {e}")

# def simulate_load(base_url, endpoints, request_per_thread, num_threads):
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: [send_request(base_url, endpoint, method, data) for _ in range(request_per_thread)])
#             threads.append(thread)
#             thread.start()

#     for thread in threads:
#         thread.join()

# # Base URL of your Flask application
# base_url = 'http://3.8.238.76'  # Replace with your actual base URL

# # -------------------------
# # Balanced Load Test Section
# # -------------------------
# print("Starting Balanced Load Test")
# balanced_endpoints = [
#     ('/todos', 'GET', None),
#     ('/todos', 'POST', {'title': 'Test task', 'description': 'This is a test task'}),
#     # Add more endpoints as needed for a balanced load
# ]
# simulate_load(base_url, balanced_endpoints, request_per_thread=10, num_threads=3)
# simulate_load(base_url, balanced_endpoints, request_per_thread=20, num_threads=5)
# # ... you can add more gradual steps here

# # -------------------------
# # Stress Test Section (Crashing the Server)
# # -------------------------
# print("Starting Stress Test (Crashing the Server)")
# stress_endpoints = [
#     ('/todos', 'POST', {'title': 'Stress Test task', 'description': 'This is a stress test task'}),
#     # Add more intensive POST, PUT, DELETE endpoints
# ]
# simulate_load(base_url, stress_endpoints, request_per_thread=1000, num_threads=20)


# import requests
# import threading
# import json

# def send_request(base_url, endpoint, method='GET', data=None):
#     url = f"{base_url}{endpoint}"
#     headers = {'Content-Type': 'application/json'}
#     try:
#         if method == 'GET':
#             response = requests.get(url)
#         elif method == 'POST':
#             response = requests.post(url, headers=headers, data=json.dumps(data))
#         elif method == 'PUT':
#             response = requests.put(url, headers=headers, data=json.dumps(data))
#         elif method == 'DELETE':
#             response = requests.delete(url)
#         else:
#             print(f"Unsupported method: {method}")
#             return

#         print(f"Response from {method} {endpoint}: {response.status_code}")
#     except Exception as e:
#         print(f"Request to {method} {endpoint} failed: {e}")

# def simulate_load(base_url, endpoints, request_per_thread, num_threads):
#     threads = []
#     for endpoint, method, data in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: [send_request(base_url, endpoint, method, data) for _ in range(request_per_thread)])
#             threads.append(thread)
#             thread.start()

#     for thread in threads:
#         thread.join()

# endpoints = [
#     ('/todos', 'GET', None),
#     ('/todos/1', 'GET', None),
#     ('/todos', 'POST', {'title': 'Test task', 'description': 'This is a test task'}),
#     ('/todos/1', 'PUT', {'title': 'Updated task', 'description': 'This is an updated task', 'is_done': 1}),
#     ('/todos/1', 'DELETE', None),
# ]

# base_url = 'http://localhost:80'  # Replace with your actual base URL
# request_per_thread = 10
# num_threads = 5

# simulate_load(base_url, endpoints, request_per_thread, num_threads)


# import requests
# import threading

# def send_request(endpoint):
#     url = f"http://3.8.238.76{endpoint}"
#     try:
#         response = requests.get(url)
#         print(f"Response from {endpoint}: {response.status_code}")
#     except Exception as e:
#         print(f"Request to {endpoint} failed: {e}")

# def simulate_load(endpoints, request_per_thread, num_threads):
#     """
#     Simulates load by sending multiple requests to the given endpoints using multiple threads.

#     Args:
#         endpoints (list): List of endpoints to send requests to.
#         request_per_thread (int): Number of requests to send per thread.
#         num_threads (int): Number of threads to use for sending requests.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: [send_request(endpoint) for _ in range(request_per_thread)])
#             threads.append(thread)
#             thread.start()

#     for thread in threads:
#         thread.join()

# endpoints = ['/', '/todos', '/todos/1']  # Target endpoints
# # simulate_load(100, 10) 
# simulate_load(endpoints, 1000, 50)  # Adjust these values as needed for load/stress testing





#below is has the base url as an argument

# import requests
# import threading

# def send_request(base_url, endpoint):
#     url = f"{base_url}{endpoint}"
#     try:
#         response = requests.get(url)
#         print(f"Response from {endpoint}: {response.status_code}")
#     except Exception as e:
#         print(f"Request to {endpoint} failed: {e}")

# def simulate_load(base_url, endpoints, request_per_thread, num_threads):
#     """
#     Simulates load by sending multiple requests to the given endpoints using multiple threads.

#     Args:
#         base_url (str): The base URL of the server to send requests to.
#         endpoints (list): List of endpoints to send requests to.
#         request_per_thread (int): Number of requests to send per thread.
#         num_threads (int): Number of threads to use for sending requests.

#     Returns:
#         None
#     """
#     threads = []
#     for endpoint in endpoints:
#         for _ in range(num_threads):
#             thread = threading.Thread(target=lambda: [send_request(base_url, endpoint) for _ in range(request_per_thread)])
#             threads.append(thread)
#             thread.start()

#     for thread in threads:
#         thread.join()

# base_url = 'http://3.8.238.76'
# endpoints = ['/', '/todos', '/todos/1']  # Target endpoints
# simulate_load(base_url, endpoints, 1000, 50)  # Adjust these values as needed for load/stress testing