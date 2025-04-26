import flask
from flask.views import MethodView
import os
from google.cloud import secretmanager
from edamam_api import get_recipes, get_recipe_details
from google_calendar import create_calendar_event
import urllib.parse
import json

# Function to access secret from Secret Manager
def access_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/cloud-puttaswamyballari-varshi/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Load environment variables
EDAMAM_APP_ID = access_secret("edamam-app-id")
EDAMAM_APP_KEY = access_secret("edamam-app-key")


# Flask application setup
app = flask.Flask(__name__)

# Index view
class Index(MethodView):
    def get(self):
        return flask.render_template('index.html')

# Recipes view
class Recipes(MethodView):
    def post(self):
        ingredients = flask.request.form['ingredients']
        recipes = get_recipes(ingredients, EDAMAM_APP_ID, EDAMAM_APP_KEY)
        return flask.render_template('recipes.html', recipes=recipes)

# Recipe details view
class RecipeDetails(MethodView):
    def get(self, uri):
        uri = urllib.parse.unquote(uri)
        if uri.startswith("http:/") and not uri.startswith("http://"):
            uri = uri.replace("http:/", "http://", 1)
        print(uri)
        recipe = get_recipe_details(uri, EDAMAM_APP_ID, EDAMAM_APP_KEY)
        return flask.render_template('recipe_details.html', recipe=recipe)


# Add to calendar view
class AddToCalendar(MethodView):
    def post(self):
        start_time = flask.request.form['start_datetime']
        end_time = flask.request.form['end_datetime']
        start_time = f"{start_time}:00-07:00"
        end_time = f"{end_time}:00-07:00"
        event_details = {
            'summary': flask.request.form['title'],
            'description': flask.request.form['description'],
            'start': {'dateTime': start_time, 'timeZone': 'America/Los_Angeles'},
            'end': {'dateTime': end_time, 'timeZone': 'America/Los_Angeles'}
        }

        print(event_details)
        user_email = flask.request.form.get('user_email')
        print(user_email)
        service_account_info = access_secret("service_account")
        service_account_info_json = json.loads(service_account_info)

        event = create_calendar_event(event_details, service_account_info_json, user_email)
        #return flask.jsonify(event)
        if event and 'htmlLink' in event:
            return flask.redirect(event['htmlLink'])
        else:
            return {'message': 'No permission to add events in your calendar, Give mealplanner@cloud-puttaswamyballari-varshi.iam.gserviceaccount.com email permissions to create events in your calendar'}
            #return flask.jsonify({'status': 'failure', 'message': "Event creation failed or no link found"})

# Register views
app.add_url_rule('/', view_func=Index.as_view('index'), methods=['GET'])
app.add_url_rule('/recipes', view_func=Recipes.as_view('recipes'), methods=['POST'])
app.add_url_rule('/recipe/<path:uri>', view_func=RecipeDetails.as_view('recipe_details'), methods=['GET'])
app.add_url_rule('/add_to_calendar', view_func=AddToCalendar.as_view('add_to_calendar'), methods=['POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
