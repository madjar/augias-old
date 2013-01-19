<%inherit file="base.mako"/>
<%namespace name="h" file="helpers.mako"/>

<% delete = len(page.users) == 1 %>

% if delete:
    <h2>Delete ${page.name} ?</h2>
    <p>You are the only person of page ${page.name}. Are you sure you want to delete it ?</p>
    % if page.tasks:
        <p>All the tasks will be deleted :</p>
        <ul>
            % for task in page.tasks:
                <li>${task.name}</li>
            % endfor
        </ul>
    % endif
% else:
    <h2>Leave ${page.name} ?</h2>
    <p>As there are other users on page ${page.name}, it won't be deleted.</p>
    <p>You won't have acces to it, unless invited again.</p>
% endif

<form method="POST">
    ${h.csrf_token(request)}
    <button type="submit" class="btn btn-danger">${'Delete' if delete else 'Leave'}</button>
</form>
