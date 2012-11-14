<%inherit file="base.mako"/>
<h2>Logs for ${task.name}</h2>

<div>
    <button class="btn btn-primary" id="chrono">Start chrono</button>
    <p id="time"></p>
</div>
<form class="form-inline" method="POST" action="${request.route_path('execute', task_id=task.id)}">
        <input id="executionLength" type="text" name="length" placeholder="Length in minutes"/>
        <input type="hidden" name="task_id"/>
        <button class="btn btn-primary" type="submit">Execute</button>
</form>

<ul>
    %for execution in task.executions:
    <li>${execution.time.strftime('%d/%m/%y %H:%M')} for ${execution.length} minutes by ${execution.executor}</li>
    %endfor
</ul>

<script type="text/javascript">
    var begin = 0;
    var timerID = 0;

    $("#chrono").click(function(e){
        e.preventDefault();
        if (!timerID){
            begin = new Date();
            timerID = setInterval(chrono, 100);
            $(this).text("Stop chrono");
            chrono();
        } else {
            clearTimeout(timerID);
            timerID = 0;
            $(this).text("Start chrono");
        }
    });

    function chrono(){
        var end = new Date();
        var diff = new Date(end - begin);
        var hours = diff.getHours() - 1;
        $("#time").html(hours + ":" + diff.getMinutes() + ":" + diff.getSeconds());
        var executionMinutes = 60 * hours + diff.getMinutes();
        if (diff.getSeconds() >= 30){
            executionMinutes += 1;
        }
        $("#executionLength").val(executionMinutes);
    }

</script>