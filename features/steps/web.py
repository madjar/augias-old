from nose.tools import *

# TODO : automatic follow redirect
@when('I go to "{path}"')
def step(context, path):
    context.result = context.app.get(path)

@when('I go to "{path}" (expecting an error)')
def step(context, path):
    context.result = context.app.get(path, expect_errors=True)

@when('I follow the redirection')
@then('I should be redirected')
def step(context):
    context.result = context.result.follow()

@when('I click "{link}"')
def step(context, link):
    context.result = context.result.click(link)

@when('I fill the form "{form}"')
def step(context, form):
    context.form = context.result.forms[form]

@when('I enter "{content}" in "{field}"')
def step(context, content, field):
    context.form[field] = content

@when('I submit the form')
def step(context):
    context.result = context.form.submit()


@then('I should see "{content}"')
def step(context, content):
    assert_in(content, context.result)
