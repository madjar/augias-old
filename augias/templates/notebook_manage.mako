<%inherit file="base.mako"/>

<h2>Manage ${notebook}</h2>
<h3>People with access</h3>

<ul>
    %for u in notebook.users:
        <li>${u}</li>
    %endfor
</ul>

<h3>Invite people</h3>
<form id="invite" method="POST" action="${request.resource_path(notebook, 'invite')}">
    ${h.csrf_token(request)}
    <label for="email">Email</label>
    <input id="email" type="email" name="email"/>
    <div><button type="submit" class="btn">Inviter</button></div>
</form>

<h3>Invited people</h3>

<ul>
    %for i in notebook.invites:
    <li>${i}</li>
    %endfor
</ul>
