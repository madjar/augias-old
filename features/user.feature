Feature: remind the user to set a name

  Scenario: User with no name
      Given a logged-in user named ""
       When I go to "/"
       Then I should see "Hey, it looks like you haven't set a username"

  Scenario: User with a name
      Given a logged-in user named "Georges"
       When I go to "/"
       Then I should not see "Hey, it looks like you haven't set a username"
