<%inherit file="base.mako"/>
<%namespace name="mh" file="helpers.mako"/>

<h2>${task}</h2>

<div class="row">
    <div class="span3">${mh._display_task(task)}</div>
    <div class="span9">
##        TODO : aligner ça correctment
        <form id='execution' class="form-inline" method="POST" action="${request.resource_path(task, 'execute')}" style="padding: 10px 0;">
            <div class="input-append">
                <input id="executionLength" type="text" name="length" placeholder="Length in minutes"/>
                <a href="#" class="btn" id="chrono"><i class="icon-time"></i></a>
            </div>

            <select name="executor">
                %for user in task.page.users:
                        <option value="${user.email}" ${'selected' if user == request.user else ''}>${user}</option>
                %endfor
                <option value="">Collective execution</option>
            </select>
            <input type="hidden" name="task_id"/>
            ${h.csrf_token(request)}
            <button class="btn btn-primary" type="submit">Execute</button>
        </form>
        <p>If you're not sure, leave the duration empty and it will be ignored in the statistics.</p>
    </div>
</div>

<p>Means execution time : ${'{:.1f}'.format(task.mean_execution)} minutes.</p>

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
