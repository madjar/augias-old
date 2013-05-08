from nose.tools import *

@when('I go to "{path}"')
def step(context, path):
    context.result = context.app.get(path)
    context.result = context.result.maybe_follow()

@when('I go to "{path}" (expecting an error)')
def step(context, path):
    context.result = context.app.get(path, expect_errors=True)

@when('I click "{link}"')
def step(context, link):
    context.result = context.result.click(link)
    context.result = context.result.maybe_follow()

@when('I click the first "{link}"')
def step(context, link):
    context.result = context.result.click(link, index=0)
    context.result = context.result.maybe_follow()


@when('I click on button "{text}"')
def step(context, text):
    for form in context.result.forms.values():
        for button in form.html.findAll('button'):
            if text in button.text:
                context.result = form.submit(button['name'])
                context.result = context.result.maybe_follow()
                return
    else:
        raise Exception('No form found')

@when('I fill the form "{form}"')
def step(context, form):
    context.form = context.result.forms[form]

@when('I enter "{content}" in "{field}"')
def step(context, content, field):
    context.form[field] = content

@when('I submit the form')
def step(context):
    context.result = context.form.submit()
    context.result = context.result.maybe_follow()


@then('I should see "{content}"')
def step(context, content):
    assert_in(content, context.result)

@then('I should not see "{content}"')
def step(context, content):
    assert_not_in(content, context.result)
