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
3. Create a .env file to the project root and fill out the variable values based on your pgAdmin4 data (See images 1 & 2)<br>
Image 1. Create .env file here in the root of the project<br>
![image](https://github.com/salopietari/gymjunkie-rest-api/assets/122457202/7b66efc3-26d7-4df8-9fd8-e44ebc9a785e) <br>
Image 2. Here are the contents of the .env file, be sure to use your own values<br>
![image](https://github.com/salopietari/gymjunkie-rest-api/assets/122457202/51578c57-5565-4928-a3a1-86ce2df38dfd) <br>
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
`python manage.py runserver`
## Robotframework tests
How to run robotframework tests located in robot_tests/
> [!NOTE]
> Requires that the project dependencies have been installed from requirements.txt (See Backend setup).
### Robotframework setup
1. Runserver <br>
`python manage.py runserver`
2. Set variables in .robot file(s) (See Image 3) <br>
Image 3. <br>
![Alt text](image.png)
> [!NOTE]
> Requires your database to actually contain valid data.
### Robotframework run tests
1. Run robot test <br>
`robot robot_tests/user.robot`
2. See results <br>
![Alt text](image-1.png)