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
${REGISTER_PASS}    password
${REGISTER_UNIT}    metric
${REGISTER_EXPERIENCE}    beginner
${TOKEN}    None
${TRACKING_ID}    None

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

Get All Trackings
    Create Session    Tracking Session   ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Tracking Session    /tracking    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Create Tracking
    Create Session    Tracking Session    ${BASE_URL}
    ${data}=    Create Dictionary    tracking_name="Paino"
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    POST On Session    Tracking Session    /tracking    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${TRACKING_ID}=    Set Variable    ${response.json()['id']}
    Set Global Variable    ${TRACKING_ID}
    Delete All Sessions

Get Additions Related To Tracking
    Create Session    Tracking Session    ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    GET On Session    Tracking Session    /tracking/${TRACKING_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete Tracking
    Create Session    Tracking Session    ${BASE_URL}
    ${headers}=     Create Dictionary    Authorization=Token ${TOKEN}
    ${response}=    DELETE On Session    Tracking Session    /tracking/${TRACKING_ID}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Delete User
    Create Session    Delete Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${data}=    Create Dictionary    password=${REGISTER_PASS}
    ${response}=    DELETE On Session    Delete Session    /user    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
    Delete All Sessions