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
${MOVEMENT_ID}    None
${TRAININGPLAN_ID}    None

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

Create A New Movement
    Create Session    Movement Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    name=bench press    category=chest
    ${response}=    POST On Session    Movement Session    /movement    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${MOVEMENT_ID}=    Set Variable    ${response.json()['id']}
    Set Global Variable    ${MOVEMENT_ID}
    Delete All Sessions

Get All Trainingplans
    Create Session    Trainingplan Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Trainingplan Session    /trainingplan    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Create Trainingplan
    Create Session    Trainingplan Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${movements}=    Evaluate    eval("[{}]".format(${MOVEMENT_ID}))
    ${data}=    Create Dictionary    name=Test Trainingplan    movements=${movements}
    ${response}=    POST On Session    Trainingplan Session    /trainingplan    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${TRAININGPLAN_ID}=    Set Variable    ${response.json()['id']}
    Set Global Variable    ${TRAININGPLAN_ID}
    Delete All Sessions

Get Details Of A Trainingplan By Id
    Create Session    Trainingplan Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Trainingplan Session    /trainingplan/${TRAININGPLAN_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Edit Trainingplan By Id
    Create Session    Trainingplan Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${movements}=    Evaluate    eval("[{}]".format(${MOVEMENT_ID}))
    ${data}=    Create Dictionary    name=Test Trainingplan Edited    movements_to_remove=${movements}    movements_to_add=${movements}
    ${response}=    PATCH On Session    Trainingplan Session    /trainingplan/${TRAININGPLAN_ID}    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete Trainingplan
    Create Session    Trainingplan Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    DELETE On Session    Trainingplan Session    /trainingplan/${TRAININGPLAN_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete User
    Create Session    Delete Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    password=${REGISTER_PASS}
    ${response}=    DELETE On Session    Delete Session    /user    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions