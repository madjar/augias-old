<%inherit file="base.mako"/>
Logged in as ${request.user}.
${request.persona_button}

<table class="table table-hover">
    <thead>
    <tr>
        <th>Name</th>
        <th>Length</th>
        <th>Periodicity</th>
        <th>Last execution</th>
        <th></th>
    </tr>
    </thead>
    <tbody>
            %for task in tasks:
            <tr class="${task.emergency()}">
                <td>${task.name}</td>
                <td>${task.length}</td>
                <td>${task.periodicity}</td>
                <td><a href="${request.route_path('task', task_id=task.id)}">${task.last_execution.strftime('%d/%m/%y %H:%M')}</a></td>
                <td>
                    <button class="btn btn-small" onclick="execute('${task.name}', ${task.id})">Execute</button>
                </td>
            </tr>
            %endfor
    </tbody>
</table>


<div id="execute" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="executeLabel" aria-hidden="true">
    <form method="POST" action="${request.route_path('execute')}">
        <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
            <h3 id="executeLabel"></h3>
        </div>
        <div class="modal-body">
            <label>How long did it last ?</label>
            <input type="text" name="length" placeholder="Length in minutes"/>
            <input type="hidden" name="task_id" id="executeTaskId"/>
        </div>
        <div class="modal-footer">
            <button class="btn" type="button" data-dismiss="modal" aria-hidden="true">Close</button>
            <button class="btn btn-primary" type="submit">Execute</button>
        </div>
    </form>
</div>

<script type="text/javascript">
    function execute(task_name, task_id) {
        $('#executeLabel').text(task_name);
        $('#executeTaskId').attr('value', task_id);
        $('#execute').modal();
    }
</script>