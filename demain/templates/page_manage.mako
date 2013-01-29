<%inherit file="base.mako"/>
<%namespace name="h" file="helpers.mako"/>

<h2>Manage ${page}</h2>
<h3>People with access</h3>

<ul>
    %for u in page.users:
        <li>${u}</li>
    %endfor
</ul>

<h3>Invite people</h3>
<form method="POST">
    ${h.csrf_token(request)}
    <label for="email">Email</label>
    <input id="email" type="email" name="email"/>
    <div><button type="submit" class="btn">Inviter</button></div>
</form>

<h3>Invited people</h3>

<ul>
    %for i in page.invites:
    <li>${i}</li>
    %endfor
</ul>
