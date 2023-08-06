*** Settings ***

Library          Selenium2Library  timeout=5  implicit_wait=0.2
Library          String
Library          DebugLibrary
Resource         keywords.txt
Library          bika.lims.testing.Keywords
Resource         plone/app/robotframework/selenium.robot
Resource         plone/app/robotframework/saucelabs.robot
Variables        plone/app/testing/interfaces.py
Variables        bika/lims/tests/variables.py
Suite Setup      Start browser
Suite Teardown   Close All Browsers

*** Variables ***

${ar_factory_url}  portal_factory/AnalysisRequest/Request%20new%20analyses/ar_add

*** Test Cases ***

Add ARs by Row
    Check the AR Add By Row javascript
    Create Primary AR By Row With Template
    Create Primary AR By Row
    Create Mulitple Primary ARs By Row With Template

Check Javascript
    Check the AR Add javascript

Analysis Request with no samping or preservation workflow
    Go to                     ${PLONEURL}/clients/client-1
    Click Link                Add
    ${ar_id}=                 Complete ar_add form with template Bore
    Go to                     ${PLONEURL}/clients/client-1/analysisrequests
    Execute transition receive on items in form_id analysisrequests
    Log out
    Log in                    test_analyst    test_analyst
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Submit results with out of range tests
    Log out
    Log in                    test_labmanager1    test_labmanager1
    Wait until page contains  You are now logged in
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/manage_results
    Add new Copper analysis to ${ar_id}
    ${ar_id} state should be sample_received
    Go to                     ${PLONEURL}/clients/client-1/${ar_id}/base_view
    Execute transition verify on items in form_id lab_analyses
    Log out
    Log in                    test_labmanager1    test_labmanager1
    # There is no "retract" transition on verified analyses - but there should/will be.
    # Go to                     ${PLONEURL}/clients/client-1/${ar_id}/base_view
    # Execute transition retract on items in form_id lab_analyses

Create two different ARs from the same sample.
    Create Primary AR
    Create Secondary AR
    In a client context, only allow selecting samples from that client.

*** Keywords ***

Start browser
    Open browser                        ${PLONEURL}/login_form
    Log in                              test_labmanager         test_labmanager
    Wait until page contains            You are now logged in
    Set selenium speed                  ${SELENIUM_SPEED}

Check the AR Add By Row javascript
   # check that the Contact CC auto-fills correctly when a contact is selected
    Log out
    Log in                      test_labmanager1    test_labmanager1
    Wait until page contains    You are now logged in
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains    Happy
    Select from list            layout      rows
    Click Link                  Add
    SelectDate                          ar_0_SamplingDate       1
    Select From Dropdown                ar_0_SampleType         Water
    Select from dropdown                Contact            Rita
    Click element               ar_0_Analyses
    Wait until page contains    Select Analyses for AR

    # check that we can expand and collaps the analysis categories
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    wait until page contains            Clostridia
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    element should not be visible             Clostridia
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    page should contain                 Clostridia

    # check analysis values appear
    click element                       xpath=.//th[@id="cat_field_Water Chemistry"]
    wait until page contains            pH (field)
    Select checkbox                     xpath=//input[@title="pH (field)"]
    wait until page contains            14

    Click element                       xpath=//th[@id="cat_lab_Metals"]
    Select checkbox                     xpath=//input[@title="Calcium"]
    Click Button                        Submit
    Set Selenium Timeout                10
    Click element                       ar_0_Analyses
    Wait until page contains            Select Analyses for AR
    wait until page contains            Temperature
    wait until page contains            Calcium

# XXX Automatic expanded categories
# XXX Restricted categories
# XXX preservation workflow
# XXX copy across in all fields

Check the AR Add javascript
   # check that the Contact CC auto-fills correctly when a contact is selected
    Log out
    Log in                    test_labmanager1    test_labmanager1
    Wait until page contains  You are now logged in
    Go to                     ${PLONEURL}/clients/client-1
    Wait until page contains  Happy
    Click Link                Add
    SelectDate                          ar_0_SamplingDate       1
    Select From Dropdown                ar_0_SampleType         Water
    Select from dropdown                ar_0_Contact            Rita
    Xpath Should Match X Times          //div[@class='reference_multi_item']   1
    Select from dropdown                ar_0_Contact            Neil
    Select from dropdown                ar_0_Priority           High
    Xpath Should Match X Times          //div[@class='reference_multi_item']   2

    # check that we can expand and collaps the analysis categories
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    wait until page contains            Clostridia
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    element should not be visible             Clostridia
    click element                       xpath=.//th[@id="cat_lab_Microbiology"]
    page should contain                 Clostridia

Create Primary AR
    Log in                      test_labmanager  test_labmanager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact                Rita
    Select from dropdown        ar_0_Template               Bore
    Select Date                 ar_0_SamplingDate           @{time}[2]
    Set Selenium Timeout        30
    Click Button                Save
    Set Selenium Timeout        10
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains    ${ar_id}
    Select checkbox             xpath=//input[@item_title="${ar_id}"]
    Click button                xpath=//input[@value="Receive sample"]
    Wait until page contains    saved
    [return]                    ${ar_id}

Create Primary AR By Row
    Log in                      test_labmanager  test_labmanager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Input text                  ar_count    2
    Select from list            layout      rows
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        Contact                     Rita
    Select Date                 ar_0_SamplingDate           @{time}[2]
    Select from dropdown        ar_0_SampleType             Water
    Click element               ar_0_Analyses
    Wait until page contains    Select Analyses for AR
    Click element               xpath=//th[@id="cat_lab_Metals"]
    Select checkbox             xpath=//input[@title="Calcium"]
    Click Button                Submit
    Set Selenium Timeout        10
    ${Analyses} =               Get value    xpath=//input[@id="ar_0_Analyses"]
    Log                         ${Analyses}
    Should Be Equal             ${Analyses}    Calcium
    Click Button                Save
    Wait until page contains    was successfully created.
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains    ${ar_id}
    Select checkbox             xpath=//input[@item_title="${ar_id}"]
    Click button                xpath=//input[@value="Receive sample"]
    Wait until page contains    saved
    [return]                    ${ar_id}

Create Mulitple Primary ARs By Row With Template
    Log in                      test_labmanager  test_labmanager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Input text                  ar_count    2
    Select from list            layout      rows
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        Contact                     Rita
    Select Date                 ar_0_SamplingDate           @{time}[2]
    Select from dropdown        ar_0_Template               Bore
    Set Selenium Timeout        10
    ${Analyses} =               Get value    xpath=//input[@id="ar_0_Analyses"]
    Log                         ${Analyses}
    Should Be Equal             ${Analyses}    Calcium, Magnesium
    Click Element               //img[contains(@class, 'TemplateCopyButton')]
    Click Element               //img[contains(@class, 'SamplingDateCopyButton')]
    Click Button                Save
    Wait until page contains    were successfully created.
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id_1} =                Set Variable  ${ar_id.split()[2]}
    ${ar_id_1} =                Set Variable  ${ar_id_1.split(',')[0]}
    ${ar_id_2} =                Set Variable  ${ar_id.split()[3]}
    ${ar_id_2} =                Set Variable  ${ar_id_2.split(',')[0]}
    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains    ${ar_id_1}
    Page should contain         ${ar_id_2}

Create Primary AR By Row With Template
    Log in                      test_labmanager  test_labmanager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Input text                  ar_count    2
    Select from list            layout      rows
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        Contact                     Rita
    Select Date                 ar_0_SamplingDate           @{time}[2]
    Select from dropdown        ar_0_Template               Bore
    Set Selenium Timeout        10
    ${Analyses} =               Get value    xpath=//input[@id="ar_0_Analyses"]
    Log                         ${Analyses}
    Should Be Equal             ${Analyses}    Calcium, Magnesium
    Click Button                Save
    Wait until page contains    was successfully created.
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    Go to                       http://localhost:55001/plone/clients/client-1/analysisrequests
    Wait until page contains    ${ar_id}
    Select checkbox             xpath=//input[@item_title="${ar_id}"]
    Click button                xpath=//input[@value="Receive sample"]
    Wait until page contains    saved
    [return]                    ${ar_id}


Create Secondary AR
    Log in                      test_labmanager  test_labmanager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-1
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact                Rita
    Select from dropdown        ar_0_Template               Bruma
    select from dropdown        ar_0_Sample
    Set Selenium Timeout        30
    Click Button                Save
    Set Selenium Timeout        2
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}


In a client context, only allow selecting samples from that client.
    Log in                      test_labmanager  test_labmanager
    @{time} =                   Get Time        year month day hour min sec
    Go to                       ${PLONEURL}/clients/client-2
    Wait until page contains element    css=body.portaltype-client
    Click Link                  Add
    Wait until page contains    Request new analyses
    Select from dropdown        ar_0_Contact               Johanna
    Select from dropdown        ar_0_Template              Bore    1
    Run keyword and expect error
    ...   ValueError: Element locator 'xpath=//div[contains(@class,'cg-colItem')][1]' did not match any elements.
    ...   Select from dropdown        ar_0_Sample


Complete ar_add form with template ${template}
    Wait until page contains    Request new analyses
    @{time} =                   Get Time        year month day hour min sec
    SelectDate                  ar_0_SamplingDate   @{time}[2]
    Select from dropdown        ar_0_Contact       Rita
    Select from dropdown        ar_0_Priority           High
    Select from dropdown        ar_0_Template       ${template}
    Sleep                       5
    Click Button                Save
    Wait until page contains    created
    ${ar_id} =                  Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                  Set Variable  ${ar_id.split()[2]}
    [return]                    ${ar_id}

Complete ar_add form Without template
    @{time} =                  Get Time        year month day hour min sec
    SelectDate                 ar_0_SamplingDate   @{time}[2]
    Select From Dropdown       ar_0_SampleType    Water
    Select from dropdown       ar_0_Contact       Rita
    Select from dropdown       ar_0_Priority           High
    Click Element              xpath=//th[@id='cat_lab_Water Chemistry']
    Select Checkbox            xpath=//input[@title='Moisture' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Metals']
    Select Checkbox            xpath=//input[@title='Calcium' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Phosphorus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Click Element              xpath=//th[@id='cat_lab_Microbiology']
    Select Checkbox            xpath=//input[@title='Clostridia' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Ecoli' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Enterococcus' and @name='ar.0.Analyses:list:ignore_empty:record']
    Select Checkbox            xpath=//input[@title='Salmonella' and @name='ar.0.Analyses:list:ignore_empty:record']
    Set Selenium Timeout       60
    Click Button               Save
    Wait until page contains   created
    ${ar_id} =                 Get text      //dl[contains(@class, 'portalMessage')][2]/dd
    ${ar_id} =                 Set Variable  ${ar_id.split()[2]}
    [return]                   ${ar_id}

Submit results with out of range tests
    [Documentation]   Complete all received analysis result entry fields
    ...               Do some out-of-range checking, too

    ${count} =                 Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =                 Convert to integer    ${count}
    :FOR    ${index}           IN RANGE    1   ${count+1}
    \    TestResultsRange      xpath=(//input[@type='text' and @field='Result'])[${index}]       5   10
    Sleep                      10s
    Click Element              xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains   Changes saved.

Submit results
    [Documentation]   Complete all received analysis result entry fields

    ${count} =                 Get Matching XPath Count    //input[@type='text' and @field='Result']
    ${count} =                 Convert to integer    ${count}
    :FOR    ${index}           IN RANGE    1   ${count+1}
    \    Input text            xpath=(//input[@type='text' and @field='Result'])[${index}]   10
    Sleep                      10s
    Click Element              xpath=//input[@value='Submit for verification'][1]
    Wait Until Page Contains   Changes saved.

Add new ${service} analysis to ${ar_id}
    Go to                      ${PLONEURL}/clients/client-1/${ar_id}/analyses
    select checkbox            xpath=//input[@alt='Select ${service}']
    click element              save_analyses_button_transition
    wait until page contains   saved.

${ar_id} state should be ${state_id}
    Go to                        ${PLONEURL}/clients/client-1/${ar_id}
    log     span.state-${state_id}   warn
    Page should contain element  css=span.state-${state_id}

TestResultsRange
    [Arguments]  ${locator}=
    ...          ${badResult}=
    ...          ${goodResult}=

    # Log  Testing Result Range for ${locator} -:- values: ${badResult} and ${goodResult}  WARN

    Input Text          ${locator}  ${badResult}
    Press Key           ${locator}   \\9
    Expect exclamation
    Input Text          ${locator}  ${goodResult}
    Press Key           ${locator}   \\9
    Expect no exclamation

Expect exclamation
    sleep  .5
    Page should contain Image   ${PLONEURL}/++resource++bika.lims.images/exclamation.png

Expect no exclamation
    sleep  .5
    Page should not contain Image  ${PLONEURL}/++resource++bika.lims.images/exclamation.png

TestSampleState
    [Arguments]  ${locator}=
    ...          ${sample}=
    ...          ${expectedState}=

    ${VALUE}  Get Value  ${locator}
    Should Be Equal  ${VALUE}  ${expectedState}  ${sample} Workflow States incorrect: Expected: ${expectedState} -
    # Log  Testing Sample State for ${sample}: ${expectedState} -:- ${VALUE}  WARN
