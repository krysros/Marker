<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="p-4 mb-4 border rounded-3">
  <div class="container">
    <h1>${project} <small class="text-body-secondary">${_("CRM for General Contractors")}</small></h1>
    <p class="fs-4">
      ${_("Find recommended companies with a specific business profile and projects that meet the required criteria. Check which companies have implemented the largest number of projects, which subdivisions are the most entrepreneurial and in which industries there is the greatest competition.")}
    </p>
  </div>
</div>

<div class="container">
  <div class="row">
    <div class="col">
      <h2><i class="bi bi-buildings"></i> ${_("Companies")}</h2>
      <p>
        ${_("Companies, corporations, organizations.")}
      </p>
      <p>
        ${button.a_button(icon='folder', color='secondary', url=request.route_url('company_all'))}
        ${button.a_button(icon='search', color='primary', url=request.route_url('company_search'))}
        ${button.a_button(icon='plus-lg', color='success', url=request.route_url('company_add'))}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-briefcase"></i> ${_("Projects")}</h2>
      <p>
        ${_("Currently implemented or completed projects.")}
      </p>
      <p>
        ${button.a_button(icon='folder', color='secondary', url=request.route_url('project_all'))}
        ${button.a_button(icon='search', color='primary', url=request.route_url('project_search'))}
        ${button.a_button(icon='plus-lg', color='success', url=request.route_url('project_add'))}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-tags"></i> ${_("Tags")}</h2>
      <p>
        ${_("Business profiles of companies and types of projects.")}
      </p>
      <p>
        ${button.a_button(icon='folder', color='secondary', url=request.route_url('tag_all'))}
        ${button.a_button(icon='search', color='primary', url=request.route_url('tag_search'))}
        ${button.a_button(icon='plus-lg', color='success', url=request.route_url('tag_add'))}
      </p>
    </div>
  </div>
  <div class="row">
    <div class="col">
      <h2><i class="bi bi-people"></i> ${_("Contacts")}</h2>
      <p>
        ${_("Contacts assigned to companies and projects.")}
      </p>
      <p>
        ${button.a_button(icon='folder', color='secondary', url=request.route_url('contact_all'))}
        ${button.a_button(icon='search', color='primary', url=request.route_url('contact_search'))}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-chat-left-text"></i> ${_("Comments")}</h2>
      <p>
        ${_("Comments on companies and projects.")}
      </p>
      <p>
        ${button.a_button(icon='folder', color='secondary', url=request.route_url('comment_all'))}
        ${button.a_button(icon='search', color='primary', url=request.route_url('comment_search'))}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-bar-chart"></i> ${_("Reports")}</h2>
      <p>
        ${_("Summary of the database content.")}
      </p>
      <p>
        ${button.a_button(icon='folder', color='secondary', url=request.route_url('report'))}
      </p>
    </div>
  </div>
</div>