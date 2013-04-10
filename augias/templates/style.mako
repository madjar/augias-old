<!DOCTYPE html>
<html lang="en">
<head>
    <title>Augias</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.2.2/css/bootstrap-combined.min.css" rel="stylesheet">
    <link href="${request.static_url('augias:static/custom.css')}" rel="stylesheet">
    <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
</head>
<body>
<div class="container">
    <div class="navbar">
        <div class="navbar-inner">
            <div class="container">
                <a class="brand" href="${request.resource_url(request.root)}">Augias</a>
                <%block name="navbar"></%block>
            </div>
        </div>
    </div>
    ${next.body()}
</div>
</body>
</html>
