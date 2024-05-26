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
${GOAL_ID}    None

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

Get All Goals
    Create Session    Goal Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Goal Session    /goal    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Create Goal
    Create Session    Goal Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    name=Steps    number=${1000000}    end=${1735689600000}    unit=steps
    ${response}=    POST On Session    Goal Session    /goal    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${GOAL_ID}=    Set Variable    ${response.json()['id']}
    Set Global Variable    ${GOAL_ID}
    Delete All Sessions

Get Details Of A Goal By Id
    Create Session    Goal Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Goal Session    /goal/${GOAL_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Get All Additions Regarding One Goal By Id
    Create Session    Goal Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Goal Session    /goal-additions/${GOAL_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete Goal
    Create Session    Goal Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    DELETE On Session    Goal Session    /goal/${GOAL_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete User
    Create Session    Delete Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    password=${REGISTER_PASS}
    ${response}=    DELETE On Session    Delete Session    /user    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions