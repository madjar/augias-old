<%inherit file="base.mako"/>

<% delete = len(notebook.users) == 1 %>

% if delete:
    <h2>Delete ${notebook} ?</h2>
    <p>You are the only person of notebook ${notebook}. Are you sure you want to delete it ?</p>
    % if notebook.tasks:
        <p>All the tasks will be deleted :</p>
        <ul>
            % for task in notebook.tasks:
                <li>${task}</li>
            % endfor
        </ul>
    % endif
% else:
    <h2>Leave ${notebook} ?</h2>
    <p>As there are other users on notebook ${notebook}, it won't be deleted.</p>
    <p>You won't have acces to it, unless invited again.</p>
% endif

<form method="POST">
    ${h.csrf_token(request)}
    <button type="submit" class="btn btn-danger">${'Delete' if delete else 'Leave'}</button>
</form>
