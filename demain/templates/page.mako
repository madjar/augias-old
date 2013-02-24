<%inherit file="base.mako"/>
<%namespace name="mh" file="helpers.mako"/>

<h2>What shall I do now ?</h2>
%if suggested_something:
    <p><i class="icon-thumbs-up"></i> Got 15 minutes ? Why not do a few things ?</p>
%endif

<div class="row-fluid">
    <div class="span9">
        ${mh.display_tasks(urgent_tasks, 3)}
        </div>
    <div class="span3 well" >
        <h3>Recent executions</h3>
        %for execution in last_executions:
            <p>${mh.display_execution(execution)}</p>
        %endfor
    </div>
</div>
<h2>All tasks</h2>
${mh.display_tasks(tasks)}

<a href="${request.resource_url(page, 'delete')}" class="btn btn-danger">${'Delete' if len(page.users) == 1 else 'Leave'}</a>
<a href="${request.resource_url(page, 'manage')}" class="btn">Manage</a>
<a href="#" class="btn" data-toggle="modal" data-target="#newTaskModal">Add new task</a>

<form method="POST" action="${request.resource_url(page, 'new_task')}">
    <div id="newTaskModal" class="modal hide fade">
        <div class="modal-header">
            <a href="#" class="close" data-dismiss="modal" aria-hidden="true">&times;</a>
            <h3>Add new task</h3>
        </div>
        <div class="modal-body">
            <label for="newTaskInput">Name</label>
            <input type="text" id="newTaskInput" name="name" placeholder="Type something…">
            <label for="newTaskPeriodicity">Periodicity in days</label>
            <input type="number" id="newTaskPeriodicity" name="periodicity" placeholder="Eg: 14">
            ${h.csrf_token(request)}
        </div>
        <div class="modal-footer">
            <a href="#" class="btn" data-dismiss="modal" aria-hidden="true">Cancel</a>
            <button type="submit" class="btn btn-primary">Create task</button>
        </div>
    </div>
</form>