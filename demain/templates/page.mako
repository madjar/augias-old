<%inherit file="base.mako"/>
<%namespace name="h" file="helpers.mako"/>

<h2>What shall I do now ?</h2>
${h.display_tasks(urgent_tasks)}

<h2>All tasks</h2>
${h.display_tasks(tasks)}
