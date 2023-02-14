<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.check_tag(tag)}
      &nbsp;${tag.name}
    </p>
  </div>
</div>