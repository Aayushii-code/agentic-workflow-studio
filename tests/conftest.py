import os
import sys

BACKEND_ROOT = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_ROOT))

import app.executors.bootstrap  # noqa: E402,F401  populate EXECUTOR_REGISTRY for all tests
