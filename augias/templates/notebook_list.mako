<%inherit file="base.mako"/>

## TODO : improve this notebook
<ul>
% for notebook in notebooks:
<li><a href="${request.resource_url(notebook)}">${notebook}</a></li>
% endfor
</ul>
