<%inherit file="base.mako"/>
<h2>Logs for ${task.name}</h2>

<form class="form-inline" method="POST" action="${request.route_path('execute', task_id=task.id)}">
        <input type="text" name="length" placeholder="Length in minutes"/>
        <input type="hidden" name="task_id" id="executeTaskId"/>
        <button class="btn btn-primary" type="submit">Execute</button>
</form>

<ul>
    %for execution in task.executions:
    <li>${execution.time.strftime('%d/%m/%y %H:%M')} by ${execution.executor}</li>
    %endfor
</ul>