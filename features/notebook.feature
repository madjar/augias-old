Feature: Notebook

  Scenario: First run creates a notebook
      Given a logged-in user named "Georges"
       When I go to "/"
       Then I should see "Georges&#39;s notebook"

  Scenario: Unauthorized user
      Given a notebook named "Stuff to do"
       When I go to "/1" (expecting an error)
       Then I should see "403 Forbidden"


  Scenario: Invite someone to a notebook
     Given a logged-in user named "Georges"
      When I go to "/"
       And I click "Manage"
       And I fill the form "invite"
       And I enter "tagada.tsoin@example.com" in "email"
       And I submit the form
      Then I should see "tagada.tsoin@example.com"

  Scenario: Accepting an invite
     Given a logged-in user named "Georges"
       And a notebook named "Stuff to do"
       And the user's email is invited to the notebook
      When I go to "/"
      Then I should see "Stuff to do"
      When I click on button "accept invite"
      Then I should see "Stuff to do</a>"

  Scenario: decline an invite
     Given a logged-in user named "Georges"
       And a notebook named "Stuff to do"
       And the user's email is invited to the notebook
      When I go to "/"
      Then I should see "Stuff to do"
      When I click on button "decline invite"
      Then I should see "Invite to Stuff to do declined"
       And I should not see "Stuff to do</a>"

