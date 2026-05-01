"""Tests for alembic migration downgrade and env functions."""

import importlib
import sys
from unittest.mock import MagicMock, patch


def _load_migration(name):
    return importlib.import_module(f"marker.alembic.versions.{name}")


# --- alembic/env.py ---


def test_alembic_env_offline_mode():
    """Cover alembic/env.py lines 29-31, 55: offline migration path."""
    import alembic

    mod_name = "marker.alembic.env"
    saved_mod = sys.modules.pop(mod_name, None)

    mock_ctx = MagicMock()
    mock_ctx.config.config_file_name = "testing.ini"
    mock_ctx.is_offline_mode.return_value = True
    mock_ctx.begin_transaction.return_value.__enter__ = MagicMock()
    mock_ctx.begin_transaction.return_value.__exit__ = MagicMock(return_value=False)

    original_context = getattr(alembic, "context", None)
    original_sys_mod = sys.modules.get("alembic.context")

    with (
        patch("pyramid.paster.setup_logging"),
        patch(
            "pyramid.paster.get_appsettings",
            return_value={"sqlalchemy.url": "sqlite://"},
        ),
    ):
        # Replace both the alembic package attribute and sys.modules entry
        alembic.context = mock_ctx
        sys.modules["alembic.context"] = mock_ctx
        try:
            mod = importlib.import_module(mod_name)
            mock_ctx.configure.assert_called()
            mock_ctx.run_migrations.assert_called()
        finally:
            # Restore everything
            if original_context is not None:
                alembic.context = original_context
            else:
                delattr(alembic, "context")
            if original_sys_mod is not None:
                sys.modules["alembic.context"] = original_sys_mod
            else:
                sys.modules.pop("alembic.context", None)
            sys.modules.pop(mod_name, None)
            if saved_mod is not None:
                sys.modules[mod_name] = saved_mod


# --- migration downgrades ---


def test_9ca296fb5e5a_downgrade():
    mod = _load_migration("20260501_9ca296fb5e5a")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        assert mock_op.drop_index.call_count == 8
        assert mock_op.drop_table.call_count == 15
