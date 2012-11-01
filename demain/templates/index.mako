<%inherit file="base.mako"/>


<table class="table">
    <thead>
    <tr>
        <th>Name</th>
        <th>Length</th>
        <th>Periodicity</th>
        <th>Last execution</th>
    </tr>
    </thead>
    <tbody>
    %for task in tasks:
        <tr>
            <td>${task.name}</td>
            <td>${task.length}</td>
            <td>${task.periodicity}</td>
            <td>${task.last_execution}</td>
        </tr>
    %endfor
    </tbody>
</table>