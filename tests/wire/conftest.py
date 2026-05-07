import sys
from pathlib import Path

# Add the tests/ directory to sys.path so that `from utils.pin_mocked import ...`
# resolves correctly in the wire test subpackage.
sys.path.insert(0, str(Path(__file__).parent.parent))
