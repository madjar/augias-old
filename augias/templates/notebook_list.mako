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
    <li><form action="${request.resource_path(i, 'join')}" method="POST">
    ${i}${h.csrf_token(request)}<button type="submit" class="btn btn-link btn-small">accept invite</button>
    </form></li>
%endfor
</ul>
