# Social_Listener

## How to set up and run  the Project
### Create a virtual environment
**python3 -m venv .venv**

### Install dependencies first
**pip3 install -r requirements.txt**

### Database config
Make sure you have changed the settings.py file in the core directory to suite you database details and then run this command:\
**python3 manage.py makemigrations**\
then: **python3 manage.py migrate**


### Run the server
**python3 manage.py runserver**

## How to access the app
Click [App](http://127.0.0.1:8000) or type *http://127.0.0.1:8000* on your browser  to access the web application.