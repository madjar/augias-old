## Display on task. Put it in a span3 if you don't want it to too long
<%def name="_display_task(task)">
    <a href="${request.resource_path(task)}" class="task-link">
        <div class="task ${task.emergency_class()}">
            <div class="pull-right">${task.periodicity} days</div>
            <h4>
                %if task.suggested:
                        <i class="icon-thumbs-up"></i>
                %endif
            ${task}</h4>
            <div class="pull-right">${int(task.mean_execution)} mins</div>
            <p>${task.last_execution and h.nice_date(task.last_execution)}</p>
        </div>
    </a>
</%def>


## Display a list of tasks in a nice grid
<%def name="display_tasks(tasks, width=4)">
    <% tasks = list(reversed(tasks)) %>
    % while tasks:
        <div class="row-fluid">
            % for i in range(width):
            % if tasks:
                    <div class="span${12//width}">${_display_task(tasks.pop())}</div>
            % endif
            % endfor
        </div>
    % endwhile
</%def>


<%def name="display_execution(execution, name=True)">
    %if name:
        ${execution.task} <span class="muted">by</span>
    %endif
    ${execution.executor or "everybody"}
    <span class="muted">&ndash;</span> ${h.nice_date(execution.time)}
    %if execution.length is not None:
        (${execution.length} mins)
    %endif
</%def>
