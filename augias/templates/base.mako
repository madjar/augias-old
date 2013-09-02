<%inherit file="style.mako"/>

<%def name="menu_item(obj, name)">
    <li
        %if request.context == obj:
            class="active"
        %endif
            ><a href="${request.resource_url(obj)}">${name}</a></li>
</%def>


<%block name="navbar">
    % if request.user:
    <ul class="nav navbar-nav">
        % for notebook in request.root.notebooks():
            ${menu_item(notebook, notebook)}
        % endfor
    ##                    TODO : check when there are a lot of those
                                    <li><a href="#" data-toggle="modal" data-target="#newNotebookModal">Add new notebook</a></li>
    </ul>
    % endif
    % if request.user:
        <div class="navbar-text pull-right">Logged in as ${request.user}
            <a id="changeName" href="#" title="Change user name"><span class="glyphicon glyphicon-edit"></span></a>.
            <a id="signout" href="#" >logout</a></div>
    % else:
        <div class="navbar-form pull-right"><button id="signin" class="btn btn-default">Sign In</button></div>
    % endif
</%block>

% if request.user and not request.user.name:
    <div class="alert alert-info">
##        <button type="button" class="close" data-dismiss="alert">&times;</button>
        Hey, it looks like you haven't set a username.
        <button class="btn btn-default" onclick="$('#changeName').popover('show')">Do it now</button>
    </div>
% endif
% for message in request.session.pop_flash():
    <div class="alert ${message.cssclass() if hasattr(message, 'level') else 'alert-info'}">
        <button type="button" class="close" data-dismiss="alert">×</button>
    ${message}
    </div>
% endfor
${next.body()}


<form method="POST" action="${request.resource_url(request.root, 'new_notebook')}">
    <div id="newNotebookModal" class="modal fade">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <a href="#" class="close" data-dismiss="modal" aria-hidden="true">&times;</a>
                    <h3>Add new notebook</h3>
                </div>
                <div class="modal-body">
                    <label for="newNotebookInput">Label name</label>
                    <input class="form-control" type="text" id="newNotebookInput" name="name" placeholder="Type something…">
                    ${h.csrf_token(request)}
                </div>
                <div class="modal-footer">
                    <a href="#" class="btn btn-default" data-dismiss="modal" aria-hidden="true">Cancel</a>
                    <button type="submit" class="btn btn-primary">Create notebook</button>
                </div>
            </div><!-- /.modal-content -->
        </div><!-- /.modal-dialog -->
    </div>
</form>

<script src="//netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>
<script type="text/javascript">
    $(function(){
        $("#changeName").popover({
            placement: 'bottom',
            html: true,
            title: 'Change user name',
            content: '<form action="${request.resource_url(request.root, 'change_username')}" method="POST"><input class="form-control" id="changeNameInput" type="text" name="username" placeholder="${request.user}">${h.csrf_token(request)}</form>'
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
