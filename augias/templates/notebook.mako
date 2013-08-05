<%inherit file="base.mako"/>
<%namespace name="mh" file="helpers.mako"/>

%if urgent_tasks:
<h2>What shall I do now ?</h2>
%if suggested_something:
    <p><i class="icon-thumbs-up"></i> Got 15 minutes ? Why not do a few things ?
%if urgent_tasks_time > 15:
 Or you could gather your courage and do it all in ${urgent_tasks_time} minutes.
%endif
</p>
%elif urgent_tasks_time:
<p> You could finish everything in ${urgent_tasks_time} minutes.
%endif
%endif

<div class="row-fluid">
    <div class="span9">
        ${mh.display_tasks(urgent_tasks, 3)}
        <h2>All tasks</h2>
        ${mh.display_tasks(tasks, 3)}
    </div>
    <div class="span3 well" >
        <h3>Recent executions</h3>
        %for execution in last_executions:
                <p>${mh.display_execution(execution)}</p>
        %endfor

        <ul class="unstyled">
            <li><a href="${request.resource_url(notebook, 'report')}" class="btn btn-block">Weekly report</a></li>
            <li><a href="#" class="btn btn-block" data-toggle="modal" data-target="#newTaskModal">Add new task</a></li>
            <li><a href="${request.resource_url(notebook, 'manage')}" class="btn btn-block">Manage</a></li>
            <li><a href="${request.resource_url(notebook, 'delete')}" class="btn btn-danger btn-block">${'Delete' if len(notebook.users) == 1 else 'Leave'}</a></li>
        </ul>
    </div>
</div>




<form id="new_task" method="POST" action="${request.resource_url(notebook, 'new_task')}">
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
