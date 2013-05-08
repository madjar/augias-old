Feature: tasks

  Background:
        Given a logged-in user named "Georges"
         When I go to "/"

  Scenario: Adding a task
       When I go to "/"
        And I fill the form "new_task"
        And I enter "Clean the fridge" in "name"
        And I enter "15" in "periodicity"
        And I submit the form
       Then I should see "Clean the fridge"
        And I should see "15 days"

  Scenario: Submitting a task
      Given I have a task named "Clean the fridge"
       When I go to "/"
        And I click the first "Clean the fridge"
        And I fill the form "execution"
        And I enter "15" in "length"
        And I submit the form
       Then I should see "<li> Georges"
        And I should see "(15 mins)"
