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


def test_97209f739ca8_downgrade():
    mod = _load_migration("20250620_97209f739ca8")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        assert mock_op.drop_table.call_count > 0


def test_b522888918c5_downgrade():
    mod = _load_migration("20250727_b522888918c5")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        mock_op.create_table.assert_called_once()


def test_163919059dcc_downgrade():
    mod = _load_migration("20260222_163919059dcc")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        mock_op.drop_column.assert_called_once()


def test_2a6f4a9d1c3e_downgrade():
    mod = _load_migration("20260305_2a6f4a9d1c3e")
    with patch.object(mod, "op") as mock_op:
        mock_batch = MagicMock()
        mock_op.batch_alter_table.return_value.__enter__ = MagicMock(
            return_value=mock_batch
        )
        mock_op.batch_alter_table.return_value.__exit__ = MagicMock(return_value=False)
        mod.downgrade()
        mock_batch.drop_constraint.assert_called_once()
        mock_batch.create_foreign_key.assert_called_once()


def test_9c1d6e7a4b2f_downgrade():
    mod = _load_migration("20260305_9c1d6e7a4b2f")
    with patch.object(mod, "op") as mock_op:
        mock_batch = MagicMock()
        mock_op.batch_alter_table.return_value.__enter__ = MagicMock(
            return_value=mock_batch
        )
        mock_op.batch_alter_table.return_value.__exit__ = MagicMock(return_value=False)
        mod.downgrade()
        mock_batch.drop_constraint.assert_called_once()
        mock_batch.create_foreign_key.assert_called_once()


def test_4fd5be91a2c7_downgrade():
    mod = _load_migration("20260308_4fd5be91a2c7")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        assert mock_op.drop_index.call_count == 3


def test_d3a6f1b2c9e4_downgrade():
    mod = _load_migration("20260308_d3a6f1b2c9e4")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        assert mock_op.drop_index.call_count == 4


def test_6f7a9c1e2b3d_downgrade():
    mod = _load_migration("20260309_6f7a9c1e2b3d")
    # downgrade is just `pass`
    mod.downgrade()


def test_ef6388976d02_downgrade():
    mod = _load_migration("20260328_ef6388976d02")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        mock_op.add_column.assert_called_once()


def test_6ae8eb2273ab_downgrade():
    mod = _load_migration("20260411_6ae8eb2273ab")
    with patch.object(mod, "op") as mock_op:
        mod.downgrade()
        assert mock_op.drop_column.call_count == 5
