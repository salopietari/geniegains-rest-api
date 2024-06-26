*** Settings ***
Library           RequestsLibrary
Library           OperatingSystem
Library           Collections
Library           String

*** Variables ***
# No need to touch any variables here, just run tests.
# 1: python manage.py runserver
# 2: robot robot_tests/user.robot
# Tests will take care of deleting everything created during the tests.
${BASE_URL}           http://localhost:8000/
${REGISTER_USERNAME}    user234xz3f1
${REGISTER_EMAIL}    user234xz3f1@example.com
${REGISTER_PASS}    sk-j3s93>d3#
${REGISTER_UNIT}    metric
${REGISTER_EXPERIENCE}    beginner
${TOKEN}    None
${EXERCISE_ID}    None

*** Test Cases ***
Register User Successfully
    Create Session    Register Session    ${BASE_URL}
    ${data}=        Create Dictionary    username=${REGISTER_USERNAME}    password=${REGISTER_PASS}    confirm_password=${REGISTER_PASS}    email=${REGISTER_EMAIL}    unit=${REGISTER_UNIT}    experience=${REGISTER_EXPERIENCE}
    ${headers}=     Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Register Session    /register    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    201
    ${TOKEN}=    Set Variable    ${response.json()['token']}
    Set Global Variable    ${TOKEN}
    Delete All Sessions

Get All Exercises
    Create Session    Exercise Session    ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Exercise Session    /exercise    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Create Exercise
    Create Session    Exercise Session    ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    name=UpperBody    note=This is a note    type=G
    ${response}=    POST On Session    Exercise Session    /exercise    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${EXERCISE_ID}=    Set Variable    ${response.json()['id']}
    Set Global Variable    ${EXERCISE_ID}
    Delete All Sessions

Get Details Of An Exercise
    Create Session    Exercise Session    ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Exercise Session    /exercise/${EXERCISE_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Edit Exercise
    Create Session    Exercise Session    ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    name=LowerBody    note=This is a note    type=G
    ${response}=    PATCH On Session    Exercise Session    /exercise/${EXERCISE_ID}    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete Exercise
    Create Session    Exercise Session    ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    DELETE On Session    Exercise Session    /exercise/${EXERCISE_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete User
    Create Session    Delete Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    password=${REGISTER_PASS}
    ${response}=    DELETE On Session    Delete Session    /user    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions