<%inherit file="base.mako"/>
<%namespace name="h" file="helpers.mako"/>

<h2>${task.name}</h2>

<div class="row">
    <div class="span3">${h._display_task(task)}</div>
    <div class="span9">
##        TODO : aligner ça correctment
        <div style="padding: 10px 0;">
            <button class="btn btn-primary" id="chrono">Start chrono</button>
            <span id="time"></span>
        </div>
        <form class="form-inline" method="POST" action="${request.resource_path(task, 'execute')}">
            <input id="executionLength" type="text" name="length" placeholder="Length in minutes"/>
            <label class="checkbox">
                <input name="collective" type="checkbox"> Collective execution
            </label>
            <input type="hidden" name="task_id"/>
            <button class="btn btn-primary" type="submit">Execute</button>
        </form>
        <p>If you're not sure, leave the duration empty and it will be ignored in the statistics.</p>
    </div>
</div>


<ul>
        %for execution in task.executions:
            <li>${execution.time.strftime('%d/%m/%y %H:%M')}
                %if execution.length is not None:
                    for ${execution.length} minutes
                %endif
            by ${execution.executor or "everybody"}</li>
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