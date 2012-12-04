<%inherit file="base.mako"/>
<%namespace name="h" file="helpers.mako"/>

<h2>Urgent tasks</h2>
${h.display_tasks(urgent_tasks)}

<h2>All tasks</h2>
${h.display_tasks(tasks)}
