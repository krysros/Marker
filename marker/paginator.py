def get_paginator(stmt, page=1, per_page=20):
    return stmt.limit(per_page).offset((page - 1) * per_page)
