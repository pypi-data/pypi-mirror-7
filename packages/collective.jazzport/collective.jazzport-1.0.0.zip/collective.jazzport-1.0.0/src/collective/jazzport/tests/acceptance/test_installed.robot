# bin/robot-server collectivejazzport.testing.JAZZPORT_ROBOT_TESTING
# bin/robot src/collective/jazzport/tests/acceptance/test_installed.robot

*** Settings ***

Resource  jazzport.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Plone is installed
    Go to  ${PLONE_URL}
    Page should contain  Powered by Plone
