# GymJunkie-rest-api
Backend for the mobile app GymJunkie <br>
See frontend: [GymJunkie](https://github.com/eemelimu/GymJunkie)
## Installation
### Software Requirements
pgAdmin4 version 7.6: https://www.pgadmin.org/download/ <br>
python version 3.11.8: https://www.python.org/downloads/
### Backend setup
> [!NOTE]
> Installation commands are for Windows operating system.
1. Setup pgAdmin4 and create an empty database.
2. Clone repository to your own PC.
3. Create a .env file to the project root and fill out the variable values<br>
Image 1. Create .env file here in the root of the project<br>
![image](https://github.com/salopietari/gymjunkie-rest-api/assets/122457202/7b66efc3-26d7-4df8-9fd8-e44ebc9a785e) <br>
Image 2. Here are the contents of the .env file, be sure to use your own values<br>
![image](https://github.com/salopietari/gymjunkie-rest-api/assets/122457202/c7848fb3-f08c-40d5-ac3f-08d5d279183d) <br>
> [!NOTE]
> When running project locally, SECRET_KEY variable can be anything.
4. (Optional but recommended) Create a virtual environment and activate it<br>
`python -m venv env` <br>
`env\Scripts\active`
5. Install project dependencies <br>
`pip install -r requirements.txt`
6. Migrate django database to pgAdmin4 <br>
`python manage.py makemigrations` <br>
`python manage.py migrate`
7. Runserver <br>
`python manage.py runserver`<br>
8. Now you're ready to send requests
## Robotframework tests
How to run robotframework tests located in robot_tests/
> [!NOTE]
> Requires that the project dependencies have been installed from requirements.txt (See Backend setup).
### Run tests
1. Runserver <br>
`python manage.py runserver`
2. Run robot test <br>
`robot robot_tests/`
3. See results <br>
![image](https://github.com/salopietari/gymjunkie-rest-api/assets/122457202/ad582b20-3f46-4dd6-905c-25261eaa6c28)
