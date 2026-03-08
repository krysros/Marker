<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.checkbox(tag, url=request.route_url('tag_check', tag_id=tag.id, slug=tag.slug), is_checked=is_tag_selected)}
      &nbsp;${tag.name}
    </p>
  </div>
</div>