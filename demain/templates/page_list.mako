<%inherit file="base.mako"/>
<%namespace name="h" file="helpers.mako"/>

## TODO : improve this page
<ul>
% for page in pages:
<li><a href="${request.resource_url(page)}">${page}</a></li>
% endfor
</ul>
