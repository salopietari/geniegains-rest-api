*** Settings ***
Library           RequestsLibrary
Library           OperatingSystem
Library           Collections
Library           String

*** Variables ***
${BASE_URL}           http://localhost:8000/
${UNIT}               
${EXPERIENCE}         
# in your db
${TOKEN}              
${TOKEN2}             
${USERNAME}           
${PASSWORD}
           
# not in your db
${EXISTING_USERNAME}  
${REGISTER_USERNAME}  
${REGISTER_EMAIL}     

*** Test Cases ***
Register User Successfully
    [Documentation]    Test registering a user successfully
    Create Session    Register Session    ${BASE_URL}
    ${data}=        Create Dictionary    username=${REGISTER_USERNAME}    password=${PASSWORD}    confirmPassword=${PASSWORD}    email=${REGISTER_EMAIL}    unit=${UNIT}    experience=${EXPERIENCE}
    ${headers}=     Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Register Session    /register    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    Should Not Contain    ${response.text}    error

Login User Successfully
    [Documentation]    Test logging in a user successfully
    Create Session    Login Session    ${BASE_URL}
    ${data}=    Create Dictionary    username=${USERNAME}    password=${PASSWORD}
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    Login Session    /login    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200
    ${token}=    Set Variable If    "error" not in ${response.text}    ${response.text}    None
    Should Not Be Empty    ${token}

Logout User Successfully
    [Documentation]    Test logging out a user successfully
    Create Session    Logout Session    ${BASE_URL}
    ${headers}=    Create Dictionary    Content-Type=application/json    Auth-Token=${TOKEN}
    ${response}=    POST On Session    Logout Session    /logout    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200

Test Register Available Username
    [Documentation]    Test registering an available username
    Create Session    Register Session    ${BASE_URL}
    ${data}=          Create Dictionary    username=${EXISTING_USERNAME}
    ${headers}=       Create Dictionary    Content-Type=application/json
    ${response}=      POST On Session    Register Session    /register/username    json=${data}    headers=${headers}
    Should Be Equal As Strings    ${response.status_code}    200