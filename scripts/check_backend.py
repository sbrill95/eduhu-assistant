import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

try:
    from app.main import app
    print("Backend importiert erfolgreich!")
except ImportError as e:
    print(f"Backend ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Backend Exception: {e}")
    sys.exit(1)
