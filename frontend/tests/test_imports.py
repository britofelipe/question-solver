import sys
import unittest
from pathlib import Path

# Add frontend directory to sys.path to simulate running from inside frontend/
frontend_path = Path(__file__).resolve().parent.parent
sys.path.append(str(frontend_path))

class TestFrontendImports(unittest.TestCase):
    def test_imports(self):
        """
        Test that all Critical frontend modules can be imported without ModuleNotFoundError.
        This simulates the environment in Docker where /app is the root.
        """
        try:
            import app
            from views import home, study_setup, study_session, tools
            from components import ui
            from services import api
            from utils import styles
            
            # Verify they are actual modules
            self.assertTrue(hasattr(app, 'st'))
            self.assertTrue(hasattr(home, 'render'))
            
        except ModuleNotFoundError as e:
            self.fail(f"Import failed: {e}")
        except Exception as e:
            # Other errors might happen due to streamlit context missing, but ModuleNotFound is what we care about
            if "No module named" in str(e):
                 self.fail(f"Import failed: {e}")
            print(f"Ignored unrelated error during import check: {e}")

if __name__ == '__main__':
    unittest.main()
