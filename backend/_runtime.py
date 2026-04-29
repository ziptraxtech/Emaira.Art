"""Runtime singletons populated by server.py at startup.

This module is imported by both server.py and routers/architects.py and acts
as a shared namespace, avoiding circular imports.
"""
db = None
User = None
require_auth = None
log_activity = None
logger = None


def init(*, db_handle, user_model, require_auth_fn, log_activity_fn, app_logger):
    """Called once by server.py after its module-level globals are defined."""
    global db, User, require_auth, log_activity, logger
    db = db_handle
    User = user_model
    require_auth = require_auth_fn
    log_activity = log_activity_fn
    logger = app_logger
