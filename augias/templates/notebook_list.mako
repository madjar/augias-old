<%inherit file="base.mako"/>

## TODO : improve this page
<ul>
% for notebook in notebooks:
<li><a href="${request.resource_url(notebook)}">${notebook}</a></li>
% endfor
</ul>

<h2>Invites</h2>
<ul>
%for i in invites:
    <li><form action="${request.resource_path(i.notebook, 'join')}" method="POST">
        ${i.notebook} (invited by ${i.by})
        ${h.csrf_token(request)}
        <button type="submit" name="accept" class="btn btn-link btn-small">accept invite</button>
        <button type="submit" name="decline" class="btn btn-link btn-small">decline invite</button>
    </form></li>
%endfor
</ul>
