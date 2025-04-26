import requests
import urllib.parse

def get_recipes(ingredients, app_id, app_key):
    url = f"https://api.edamam.com/search?q={ingredients}&app_id={app_id}&app_key={app_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses
        if response.status_code == 200:
            return response.json().get('hits', [])
        else:
            return {"status": "error", "message": response.json()}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def get_recipe_details(recipe_uri, app_id, app_key):
    encoded_uri = urllib.parse.quote(recipe_uri, safe='')
    print(recipe_uri)
    print(encoded_uri)
    url = f"https://api.edamam.com/search?r={encoded_uri}&app_id={app_id}&app_key={app_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses
        if response.status_code == 200:
            return response.json()[0]
        else:
            return {"status": "error", "message": response.json()}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}
