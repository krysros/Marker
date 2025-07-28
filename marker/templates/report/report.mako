<%inherit file="layout.mako"/>

<h2><i class="bi bi-bar-chart"></i> ${_("Reports")}</h2>
<hr>
<p class="lead">${lead}</p>
<%include file="report_table.mako"/>
