<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="p-4 mb-4 border rounded-3">
  <div class="container">
    <h1>${project} <small class="text-muted">${_("Information about companies and projects")}</small></h1>
    <p class="fs-4">
      ${_("Find the most frequently recommended companies with a specific business profile and projects that meet the required criteria. Check which companies have implemented the largest number of projects, which regions are the most entrepreneurial and in which industries there is the greatest competition.")}
    </p>
  </div>
</div>

<div class="container">
  <div class="row">
    <div class="col">
      <h2><i class="bi bi-buildings"></i> ${_("Companies")}</h2>
      <p>
        ${_("Recently added companies.")}
      </p>
      <p>
        ${button.show('company_all')}
        ${button.search('company_search')}
        ${button.add('company_add')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-briefcase"></i> ${_("Projects")}</h2>
      <p>
        ${_("Currently implemented or completed projects.")}
      </p>
      <p>
        ${button.show('project_all')}
        ${button.search('project_search')}
        ${button.add('project_add')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-tags"></i> ${_("Tags")}</h2>
      <p>
        ${_("Business profiles of companies and types of projects.")}
      </p>
      <p>
        ${button.show('tag_all')}
        ${button.search('tag_search')}
        ${button.add('tag_add')}
      </p>
    </div>
  </div>
  <div class="row">
    <div class="col">
      <h2><i class="bi bi-people"></i> ${_("Contacts")}</h2>
      <p>
        ${_("Contacts assigned to the company and projects.")}
      </p>
      <p>
        ${button.show('contact_all')}
        ${button.search('contact_search')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-chat-left-text"></i> ${_("Comments")}</h2>
      <p>
        ${_("Comments on companies and projects.")}
      </p>
      <p>
        ${button.show('comment_all')}
        ${button.search('comment_search')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-bar-chart"></i> ${_("Reports")}</h2>
      <p>
        ${_("Summary of the database content.")}
      </p>
      <p>
        ${button.show('report')}
      </p>
    </div>
  </div>
</div>