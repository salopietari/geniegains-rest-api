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

Logout User Successfully
    Create Session    Logout Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    POST On Session    Logout Session    /logout    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions

Login User Successfully
    Create Session    Login Session    ${BASE_URL}
    ${data}=    Create Dictionary    email=${REGISTER_EMAIL}    password=${REGISTER_PASS}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Login Session    /login    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${TOKEN}=    Set Variable    ${response.json()['token']}
    Set Global Variable    ${TOKEN}
    Delete All Sessions

Login User With Token
    Create Session    Login Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    POST On Session    Login Session    /token_login    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Register Available Username Successfully
    Create Session    Register Session    ${BASE_URL}
    ${data}=          Create Dictionary    username=${REGISTER_USERNAME}available
    ${headers}=       Create Dictionary    Content-Type=application/json
    ${response}=      POST On Session    Register Session    register/username    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Register Available Email Successfully
    Create Session    Register Session    ${BASE_URL}
    ${data}=          Create Dictionary    email=${REGISTER_EMAIL}available
    ${headers}=       Create Dictionary    Content-Type=application/json
    ${response}=      POST On Session    Register Session    register/email    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Get User Details
    Create Session    User Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    User Session    /user    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Update User Details
    Create Session    Update Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    email=${REGISTER_EMAIL}    username=${REGISTER_USERNAME}    unit=${REGISTER_UNIT}    experience=${REGISTER_EXPERIENCE}    password=${REGISTER_PASS}
    ${response}=    PATCH On Session    Update Session    /user    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${TOKEN}=    Set Variable    ${response.json()['token']}
    Set Global Variable    ${TOKEN}
    Delete All Sessions

Logout All Devices
    Create Session    Logout Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    POST On Session    Logout Session    /logout-all    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions

Delete User
    Create Session    Login Session    ${BASE_URL}
    ${data}=    Create Dictionary    email=${REGISTER_EMAIL}    password=${REGISTER_PASS}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Login Session    /login    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${TOKEN}=    Set Variable    ${response.json()['token']}
    Set Global Variable    ${TOKEN}
    Create Session    Delete Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    password=${REGISTER_PASS}
    ${response}=    DELETE On Session    Delete Session    /user    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions