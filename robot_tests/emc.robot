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
${MOVEMENT_ID}    None
${EMC_ID}    None

*** Test Cases ***
Register User Successfully
    Create Session    Register Session    ${BASE_URL}
    ${data}=        Create Dictionary    username=${REGISTER_USERNAME}    password=${REGISTER_PASS}    confirmPassword=${REGISTER_PASS}    email=${REGISTER_EMAIL}    unit=${REGISTER_UNIT}    experience=${REGISTER_EXPERIENCE}
    ${headers}=     Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Register Session    /register    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${TOKEN}=    Set Variable    ${response.json()['token']}
    Set Global Variable    ${TOKEN}
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

Create A New Movement
    Create Session    Movement Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    name=bench press    category=chest
    ${response}=    POST On Session    Movement Session    /movement    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${MOVEMENT_ID}=    Set Variable    ${response.json()['id']}
    Set Global Variable    ${MOVEMENT_ID}
    Delete All Sessions

Get All Emcs
    Create Session    Emc Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Emc Session    /exercisemovementconnection    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Create Emc
    Create Session    Emc Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    exercise_id=${EXERCISE_ID}    movement_id=${MOVEMENT_ID}    reps=10    weight=100    time=${4}
    ${response}=    POST On Session    Emc Session    /exercisemovementconnection    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${EMC_ID}=    Set Variable    ${response.json()['id']}
    Set Global Variable    ${EMC_ID}
    Delete All Sessions

Get All Emcs By Exercise Id
    Create Session    Emc Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Emc Session    /exercisemovementconnection/${EXERCISE_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Edit Emcs By Exercise Id
    Create Session    Emc Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    id=${EMC_ID}    reps=${1}    weight=${1}    time=${1}
    ${response}=    PATCH On Session    Emc Session    /exercisemovementconnection/${EXERCISE_ID}    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete Emc
    Create Session    Emc Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    DELETE On Session    Emc Session    /exercisemovementconnection/${EMC_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions

Delete User
    Create Session    Delete Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    password=${REGISTER_PASS}
    ${response}=    DELETE On Session    Delete Session    /user    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions