import requests
import csv
import json
import ssl
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login_to_prisma_cloud(login_url, access_key, secret_key):
    headers = {'Content-Type': 'application/json'}
    auth_data = {
        "username": access_key,
        "password": secret_key
    }
    try:
        response = requests.post(login_url, headers=headers, json=auth_data, verify=ssl.CERT_NONE)
        response.raise_for_status()
        token = response.json().get('token')
        if token:
            print("Successfully generated token.")
        else:
            print("Token not found in the response")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def get_repos_from_prisma_cloud(api_url, jwt_token):
    headers = {
        'content-type': 'application/json',
        'x-redlock-auth': jwt_token
    }
    endpoint = f"{api_url}/repositories"

    try:
        response = requests.get(endpoint, headers=headers, verify=ssl.CERT_NONE)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def generate_csv(repos, output_file):
    if not repos:
        print("No repositories to write to CSV.")
        return

    fieldnames = repos[0].keys()

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repos:
            writer.writerow(repo)

    print(f"CSV file '{output_file}' has been generated successfully.")

# APII login
BASE_URL = "https://api3.prismacloud.io"
API_URL = f"{BASE_URL}/code/api/v1"
LOGIN_URL = f"{BASE_URL}/login"
ACCESS_KEY = "d9071b9f-8a3d-4f5f-87e8-ebc4fe857518"
SECRET_KEY = "3taQez3V1Na7X3HE0lPRK53JeBs="
OUTPUT_FILE = "prisma_cloud_repos.csv"


jwt_token = login_to_prisma_cloud(LOGIN_URL, ACCESS_KEY, SECRET_KEY)

if jwt_token:
    print("Authentication successful. Proceeding to fetch repositories.")
    
    repos = get_repos_from_prisma_cloud(API_URL, jwt_token)
    if repos:
        print(f"Found {len(repos)} repositories.")
        generate_csv(repos, OUTPUT_FILE)
    else:
        print("Failed to retrieve repositories.")
else:
    print("Failed to obtain JWT token. Cannot proceed with fetching repositories.")
