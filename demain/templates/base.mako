<%namespace name="h" file="helpers.mako"/>
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Demain</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.2.2/css/bootstrap-combined.min.css" rel="stylesheet">
    <link href="${request.static_url('demain:static/custom.css')}" rel="stylesheet">
    <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    <script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.2.2/js/bootstrap.min.js"></script>
    <script src="https://login.persona.org/include.js" type="text/javascript"></script>
    <script type="text/javascript">${request.persona_js}</script>
</head>
<body>

    <%def name="menu_item(obj, name)">
        <li
            %if request.context == obj:
                class="active"
            %endif
                ><a href="${request.resource_url(obj)}">${name}</a></li>
    </%def>

<div class="container">
    <div class="navbar">
        <div class="navbar-inner">
            <div class="container">
                <a class="brand" href="${request.resource_url(request.root)}">Demain</a>
                <ul class="nav">
                    % for page in request.root.pages():
                        ${menu_item(page, page)}
                    % endfor
##                    TODO : check when there are a lot of those
                    <li><a href="#" data-toggle="modal" data-target="#newPageModal">Add new page</a></li>
                </ul>
                % if request.user:
                        <div class="navbar-text pull-right">Logged in as ${request.user}
                            <a id="changeName" href="#" title="Change user name"><i class="icon-edit"></i></a>.
                            <a id="signout" href="#" >logout</a></div>
                % else:
                        <div class="navbar-form pull-right"><button id="signin" class="btn">Sign In</button></div>
                % endif
            </div>
        </div>
    </div>
    % for message in request.session.pop_flash():
            <div class="alert ${message.cssclass() if hasattr(message, 'level') else 'alert-info'}">
                <button type="button" class="close" data-dismiss="alert">×</button>
            ${message}
            </div>
    % endfor
    ${next.body()}
</div>

<form method="POST" action="${request.resource_url(request.root, 'new_page')}">
    <div id="newPageModal" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal" aria-hidden="true">&times;</a>
        <h3>Add new page</h3>
    </div>
    <div class="modal-body">
        <label>Label name</label>
        <input type="text" id="newPageInput" name="name" placeholder="Type something…">
        ${h.csrf_token(request)}
    </div>
    <div class="modal-footer">
        <a href="#" class="btn" data-dismiss="modal" aria-hidden="true">Cancel</a>
        <button type="submit" class="btn btn-primary">Create page</button>
    </div>
</div>
</form>

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
        $('#newPageModal').on('shown', function () {
            $('#newPageInput').focus();
        });
    })
</script>
</body>
</html>
