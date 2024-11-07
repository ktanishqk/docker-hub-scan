import requests
import json
import os
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

DOCKER_HUB_BASE_URL = "https://hub.docker.com"

# Step 1: Authenticate and get token
def get_auth_token(username, password):
    url = f"{DOCKER_HUB_BASE_URL}/v2/users/login"
    response = requests.post(url, json={"username": username, "password": password})
    response.raise_for_status()
    return response.json().get("token")

# Step 2: Get all repositories in a namespace
def get_all_repositories(namespace, token):
    url = f"{DOCKER_HUB_BASE_URL}/v2/repositories/{namespace}?page_size=100"
    headers = {"Authorization": f"Bearer {token}"}
    repositories = []
    
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        repositories.extend(data.get("results", []))
        url = data.get("next")
    
    return repositories

# Step 3: Get repository information
def get_repository_details(namespace, repository, token):
    url = f"{DOCKER_HUB_BASE_URL}/v2/repositories/{namespace}/{repository}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Step 4: Get repository tags
def get_repository_tags(namespace, repository, token):
    url = f"{DOCKER_HUB_BASE_URL}/v2/repositories/{namespace}/{repository}/tags"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("results", [])

# Step 5: Collect data for a repository
def collect_repository_data(namespace, repository, token):
    repo_details = get_repository_details(namespace, repository, token)
    tags = get_repository_tags(namespace, repository, token)
    
    collected_data = {
        "Image Name": repo_details.get("name"),
        "Description": repo_details.get("description"),
        "Pulls": repo_details.get("pull_count"),
        "Stars Count": repo_details.get("star_count"),
        "Tags": [tag.get("name") for tag in tags],
        "By": repo_details.get("namespace"),
        "Last Updated": repo_details.get("last_updated"),
        "Official Status": "Official" if repo_details.get("is_official") else "Community",
    }
    return collected_data

if __name__ == "__main__":
    try:
        # Get username and password from environment variables
        USERNAME = os.getenv("DOCKER_HUB_USERNAME")
        PASSWORD = os.getenv("DOCKER_HUB_PASSWORD")
        
        if not USERNAME or not PASSWORD:
            raise EnvironmentError("Docker Hub username and password must be set in environment variables.")
        
        # Authenticate and get token
        token = get_auth_token(USERNAME, PASSWORD)
        
        # List of known namespaces (usernames or organizations)
        namespaces = ["library", "nginx", "mysql", "alpine"]
        
        # Collect data for each namespace and each repository within it
        all_data = []
        for namespace in tqdm(namespaces, desc="Processing namespaces"):
            repositories = get_all_repositories(namespace, token)
            for repo in tqdm(repositories, desc=f"Collecting data for namespace: {namespace}", leave=False):
                repository_name = repo.get("name")
                data = collect_repository_data(namespace, repository_name, token)
                all_data.append(data)
        
        # Save all collected data to a JSON file
        with open("docker_hub_data.json", "w") as json_file:
            json.dump(all_data, json_file, indent=2)
        
        print("Data successfully saved to docker_hub_data.json")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except EnvironmentError as e:
        print(e)