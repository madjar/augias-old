<%inherit file="base.mako"/>

<h2>Weekly report for ${notebook}</h2>
<h3>${begin} - ${end}</h3>


<% persons = notebook.users %>

<table class="table">
    <tr><th></th>
        %for p in persons:
                <th>${p}</th>
        %endfor
        <th>shared execution</th>
        <th>Total</th>
    </tr>
    %for task, task_by_person in by_task:
        <tr>
            <td>${task}</td>
        %for person in persons:
                <td>${task_by_person[person]}</td>
        %endfor
            <td>${task_by_person[None]}</td>
            <td>${task_by_person['total']}</td>
        </tr>
    %endfor
    <tr>
        <td>Total</td>
        %for person in persons:
                <td>${by_person[person]}</td>
        %endfor
        <td>${by_person[None]}</td>
        <td>${total}</td>
    </tr>
</table>


<p>Legend : total time <span class="text-muted">(~guessed time)  +  executions with no data and no possible guessing</span></p>

<p><a href="${request.resource_path(notebook, 'report', query={'ago':ago+1})}">And before ?</a></p>
