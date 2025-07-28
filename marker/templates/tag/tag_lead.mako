<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.checkbox(tag, selected=request.identity.selected_tags, url=request.route_url('tag_check', tag_id=tag.id, slug=tag.slug))}
      &nbsp;${tag.name}
    </p>
  </div>
</div>