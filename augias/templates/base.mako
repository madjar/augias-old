<%inherit file="style.mako"/>

<%def name="menu_item(obj, name)">
    <li
        %if request.context == obj:
            class="active"
        %endif
            ><a href="${request.resource_url(obj)}">${name}</a></li>
</%def>


<%block name="navbar">
    <ul class="nav">
        % for notebook in request.root.notebooks():
            ${menu_item(notebook, notebook)}
        % endfor
    ##                    TODO : check when there are a lot of those
                                    <li><a href="#" data-toggle="modal" data-target="#newNotebookModal">Add new notebook</a></li>
    </ul>
    % if request.user:
        <div class="navbar-text pull-right">Logged in as ${request.user}
            <a id="changeName" href="#" title="Change user name"><i class="icon-edit"></i></a>.
            <a id="signout" href="#" >logout</a></div>
    % else:
        <div class="navbar-form pull-right"><button id="signin" class="btn">Sign In</button></div>
    % endif
</%block>

% for message in request.session.pop_flash():
    <div class="alert ${message.cssclass() if hasattr(message, 'level') else 'alert-info'}">
        <button type="button" class="close" data-dismiss="alert">×</button>
    ${message}
    </div>
% endfor
${next.body()}


<form method="POST" action="${request.resource_url(request.root, 'new_notebook')}">
    <div id="newNotebookModal" class="modal hide fade">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal" aria-hidden="true">&times;</a>
            <h3>Add new notebook</h3>
        </div>
        <div class="modal-body">
            <label>Label name</label>
            <input type="text" id="newNotebookInput" name="name" placeholder="Type something…">
            ${h.csrf_token(request)}
        </div>
        <div class="modal-footer">
            <a href="#" class="btn" data-dismiss="modal" aria-hidden="true">Cancel</a>
            <button type="submit" class="btn btn-primary">Create notebook</button>
        </div>
    </div>
</form>

<script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.2.2/js/bootstrap.min.js"></script>
<script type="text/javascript">
    $(function(){
        $("#changeName").popover({
            placement: 'bottom',
            html: true,
            title: 'Change user name',
            content: '<form action="${request.resource_url(request.root, 'change_username')}" method="POST"><input id="changeNameInput" type="text" name="username" placeholder="${request.user}">${h.csrf_token(request)}</form>'
        }).click(function(e){
                    $('#changeNameInput').focus();
                });
        $('#newNotebookModal').on('shown', function () {
            $('#newNotebookInput').focus();
        });
    })
</script>
<script src="https://login.persona.org/include.js" type="text/javascript"></script>
<script type="text/javascript">${request.persona_js}</script>
