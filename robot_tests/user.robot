*** Settings ***
Library           RequestsLibrary
Library           OperatingSystem
Library           Collections
Library           String

*** Variables ***
${BASE_URL}           http://localhost:8000/
${REGISTER_USERNAME}    
${REGISTER_EMAIL}    
${REGISTER_PASS}    
${REGISTER_UNIT}    
${REGISTER_EXPERIENCE}    
${TOKEN}    None

*** Test Cases ***
Register User Successfully
    Create Session    Register Session    ${BASE_URL}
    ${data}=        Create Dictionary    username=${REGISTER_USERNAME}    password=${REGISTER_PASS}    confirmPassword=${REGISTER_PASS}    email=${REGISTER_EMAIL}    unit=${REGISTER_UNIT}    experience=${REGISTER_EXPERIENCE}
    ${headers}=     Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Register Session    /register    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Should Not Contain    ${response.text}    error
    ${TOKEN}=    Set Variable    ${response.json()['token']}
    Set Global Variable    ${TOKEN}
    Delete All Sessions

Login User Successfully
    Create Session    Login Session    ${BASE_URL}
    ${data}=    Create Dictionary    email=${REGISTER_EMAIL}    password=${REGISTER_PASS}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Login Session    /login    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Delete All Sessions

Logout User Successfully
    Create Session    Logout Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Authorization=Token ${TOKEN}
    ${response}=    POST On Session    Logout Session    /logout    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    204
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