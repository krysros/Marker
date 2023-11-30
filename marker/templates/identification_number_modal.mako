<div class="modal-dialog modal-dialog-centered">
  <div class="modal-content">
    <div class="modal-header">
      <h5 class="modal-title">${_("Identification number")}</h5>
    </div>
    <div class="modal-body">
      <form action="${request.current_route_path()}" method="post">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="mb-3">
          ${form.NIP.label}
          ${form.NIP(class_="form-control")}
        </div>
        <div class="mb-3">
          ${form.REGON.label}
          ${form.REGON(class_="form-control")}
        </div>
        <div class="mb-3">
          ${form.KRS.label}
          ${form.KRS(class_="form-control")}
        </div>
        <div class="mb-3">
          ${form.court.label}
          ${form.court(class_="form-control")}
        </div>
      </form>
    </div>
    <div class="modal-footer">
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${_("Close")}</button>
      <button type="submit" class="btn btn-primary" id="submit" name="submit">${_("Save")}</button>
    </div>
  </div>
</div>