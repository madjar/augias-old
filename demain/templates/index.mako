<%inherit file="base.mako"/>
Logged in as ${request.user}.
${request.persona_button}

<table class="table table-hover">
    <thead>
    <tr>
        <th>Name</th>
        <th>Periodicity</th>
        <th>Last execution</th>
        <th></th>
    </tr>
    </thead>
    <tbody>
            %for task in tasks:
            <tr class="${task.emergency()}">
                <td>${task.name}</td>
                <td>${task.periodicity}</td>
                <td><a href="${request.resource_path(task)}">${task.last_execution.strftime('%d/%m/%y %H:%M')}</a></td>
                <td>
                    <a href="${request.resource_path(task)}" class="btn btn-small">Execute</a>
                </td>
            </tr>
            %endfor
    </tbody>
</table>