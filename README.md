# GymJunkie-rest-api
## Installation
### Software Requirements
pgAdmin4 version 7.6: https://www.pgadmin.org/download/ <br>
python version 3.11.8: https://www.python.org/downloads/
### Setup
1. Setup pgAdmin4 and create an empty database.
2. Clone repository to your own PC.
3. Create a .env file to the project root and fill out the variable values based on your pgAdmin4 data (See images 1 & 2):<br>
Image 1.<br>
![image](https://github.com/salopietari/gymjunkie-rest-api/assets/122457202/39121726-2fd4-4979-99f3-e8f4f84f7b6e) <br>
Image 2. <br>
![image](https://github.com/salopietari/gymjunkie-rest-api/assets/122457202/51578c57-5565-4928-a3a1-86ce2df38dfd) <br>
4. (Optional but recommended) Create a virtual environment, activate it and install project dependencies: <br>
On Windows create virtual environment: 'python -m venv env' <br>
On Windows activate virtual environment: 'env\Scripts\active'
5. Install project dependencies: <br>
On Windows: 'pip install -r requirements.txt'
6. Migrate django database to pgAdmin4: <br>
'python manage.py makemigrations' <br>
'python manage.py migrate'
7. Runserver: <br>
'python manage.py runserver'
