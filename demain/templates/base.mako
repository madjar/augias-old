<!DOCTYPE html>
<html lang="en">
<head>
    <title>Demain</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.1.1/css/bootstrap-combined.min.css" rel="stylesheet">
    <link href="${request.static_url('demain:static/custom.css')}" rel="stylesheet">
    <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    <script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.2.1/js/bootstrap.min.js"></script>
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
                    ${menu_item(request.root, "Dashboard")}
                </ul>
                % if request.user:
                        <div class="navbar-text pull-right">Logged in as ${request.user}. <a id="signout" href="#">logout</a></div>
                % else:
                        <div class="navbar-form pull-right"><button id="signin" class="btn">Sign In</button></div>
                % endif
            </div>
        </div>
    </div>
    % for message in request.session.pop_flash():
            <div class="alert ${'alert-'+message.clazz if message.clazz else ''}">
                <button type="button" class="close" data-dismiss="alert">×</button>
            ${message}
            </div>
    % endfor
    ${next.body()}
</div>
</body>
</html>
