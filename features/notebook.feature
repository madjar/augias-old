Feature: Notebook
  
  Scenario: First run creates a notebook
      Given a logged-in user named "Georges"
       When I go to "/"
       Then I should be redirected
        And I should see "Georges&#39;s notebook"

  Scenario: Unauthorized user
       When I go to "/" (expecting an error)
       Then I should see "403 Forbidden"
       
