import requests
import json

# Function to get all Docker Hub namespaces and save to JSON
def get_all_namespaces():
    page = 1
    namespaces = set()

    while True:
        response = requests.get(
            f"https://hub.docker.com/api/content/v1/products/search?q=&type=image&page_size=100&page={page}"
        )
        if response.status_code != 200:
            break

        try:
            data = response.json()
        except ValueError:
            break

        if not data or 'summaries' not in data or not data['summaries']:
            break

        for item in data['summaries']:
            if 'publisher' in item and 'name' in item['publisher']:
                namespaces.add(item['publisher']['name'])

        page += 1

    return list(namespaces)

# Save namespaces to a JSON file
all_namespaces = get_all_namespaces()
with open('docker_namespaces.json', 'w') as json_file:
    json.dump(all_namespaces, json_file, indent=4)

print("Namespaces saved to docker_namespaces.json")
