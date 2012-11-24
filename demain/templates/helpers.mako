<%def name="_display_task(task)">
    <a href="${request.resource_path(task)}" class="task-link">
        <div class="task ${task.emergency_class()}">
            <div class="pull-right">${task.periodicity} days</div>
            <h4>${task.name}</h4>
            <p>${task.last_execution and nice_date(task.last_execution)}</p>
        </div>
    </a>
</%def>

<%def name="display_tasks(tasks)">
    <% tasks = list(reversed(tasks)) %>
    % while tasks:
        <div class="row">
            % for i in range(4):
            % if tasks:
                    <div class="span3">${_display_task(tasks.pop())}</div>
            % endif
            % endfor
        </div>
    % endwhile
</%def>

<%!
    import datetime
    current_year = datetime.date.today().year

    def nice_date(date):
        result = date.strftime('%A %d %B')
        if date.year != current_year:
            result += date.strftime(' %Y')
        return result
%>