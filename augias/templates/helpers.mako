## Display on task. Put it in a span3 if you don't want it to too long
<%def name="_display_task(task)">
    <a href="${request.resource_path(task)}" class="task-link">
        <div class="task ${task.emergency_class()}">
            <div class="pull-right">${task.periodicity} days</div>
            <h4>
                %if task.suggested:
                        <span class="glyphicon glyphicon-thumbs-up"></span>
                %endif
            ${task}</h4>
            % if task.mean_execution:
                <div class="pull-right">${int(task.mean_execution)} mins</div>
            % endif
            <p>${task.last_execution and h.nice_date(task.last_execution)}</p>
        </div>
    </a>
</%def>


## Display a list of tasks in a nice grid
<%def name="display_tasks(tasks, width=4)">
    <% tasks = list(reversed(tasks)) %>
    % while tasks:
        <div class="row">
            % for i in range(width):
            % if tasks:
                    <div class="col-md-${12//width}">${_display_task(tasks.pop())}</div>
            % endif
            % endfor
        </div>
    % endwhile
</%def>


<%def name="display_execution(execution, name=True)">
    %if name:
        ${execution.task} <span class="text-muted">by</span>
    %endif
    ${execution.executor or "everybody"}
    <span class="text-muted">&ndash;</span> ${h.nice_date(execution.time)}
    %if execution.length is not None:
        (${execution.length} mins)
    %endif
</%def>
