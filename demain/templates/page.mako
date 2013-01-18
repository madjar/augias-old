<%inherit file="base.mako"/>
<%namespace name="h" file="helpers.mako"/>

<h2>What shall I do now ?</h2>
%if suggested_something:
    <p><i class="icon-thumbs-up"></i> Got 15 minutes ? Why not do a few things ?</p>
%endif

<div class="row-fluid">
    <div class="span9">
        ${h.display_tasks(urgent_tasks, 3)}
        </div>
    <div class="span3 well" >
        <h3>Recent executions</h3>
        %for execution in last_executions:
            <p>${h.display_execution(execution)}</p>
        %endfor
    </div>
</div>
<h2>All tasks</h2>
${h.display_tasks(tasks)}
