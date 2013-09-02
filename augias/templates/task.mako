<%inherit file="base.mako"/>
<%namespace name="mh" file="helpers.mako"/>

<h2>${task}</h2>

<div class="row">
    <div class="col-md-3">${mh._display_task(task)}</div>
    <div class="col-md-9">
##        TODO : aligner ça correctment
        <form id='execution' class="form-inline" method="POST" action="${request.resource_path(task, 'execute')}" style="padding: 10px 0;">
        <div class="row">
            <div class="input-group col-md-3">
                <input class="form-control" id="executionLength" type="text" name="length" placeholder="Length in minutes"/>
                <span class="input-group-btn">
                    <a href="#" class="btn btn-default" id="chrono"><span class="glyphicon glyphicon-time"></span></a>
                </span>
            </div>

            <div class="col-md-3">
            <select class="form-control" name="executor">
                %for user in task.notebook.users:
                        <option value="${user.email}" ${'selected' if user == request.user else ''}>${user}</option>
                %endfor
                <option value="">Collective execution</option>
            </select>
            </div>

            <input type="hidden" name="task_id"/>
            ${h.csrf_token(request)}
            <div class="col-md-2">
            <button class="btn btn-primary" type="submit">Execute</button>
            </div>
        </div>
        </form>
        <p>If you're not sure, leave the duration empty and it will be ignored in the statistics.</p>
    </div>
</div>

<p>Means execution time : ${'{:.1f}'.format(task.mean_execution)} minutes.</p>

<div id="chart_div"></div>

<ul>
        %for execution in task.executions:
            <li>${mh.display_execution(execution, name=False)}</li>
        %endfor
</ul>

<script type="text/javascript">
    var begin = 0;
    var timerID = 0;
    var current = null;

    $("#chrono").click(function(e){
        e.preventDefault();
        if (!timerID){
            begin = new Date();
            if(current) {
                begin.setSeconds(begin.getSeconds() - current/1000);
            }
            timerID = setInterval(chrono, 100);
            $(this).button('toggle');
            chrono();
        } else {
            clearTimeout(timerID);
            timerID = 0;
            $(this).button('toggle');
        }
    });

    function chrono(){
        var end = new Date();
        var diff = new Date(end - begin);
        current = end.getTime() - begin.getTime();
        var hours = diff.getHours() - 1;
        var display_str = diff.getMinutes() + ":" + diff.getSeconds();
        if (hours != 0) {
            display_str = hours + ':' + display_str;
        }
        $("#executionLength").val(display_str);
        var executionMinutes = 60 * hours + diff.getMinutes();
        if (diff.getSeconds() >= 30){
            executionMinutes += 1;
        }
    }

</script>

% if task.executions:
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script type="text/javascript">
    google.load('visualization', '1.0', {'packages':['corechart']});
    google.setOnLoadCallback(drawChart);

    function drawChart() {
        var data = new google.visualization.DataTable(${data});
        var options = {'title':'Executions',
            'width':400,
            'height':300};

        var chart = new google.visualization.ScatterChart(document.getElementById('chart_div'));
        chart.draw(data, options);
    }
</script>
% endif
