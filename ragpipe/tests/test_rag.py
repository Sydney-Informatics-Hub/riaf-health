import unittest
import sys
import os
from pathlib import Path
import io
from contextlib import redirect_stdout, redirect_stderr

# Add the parent directory to sys.path to import the rag module
sys.path.append(str(Path(__file__).parent.parent))

from rag import main

class TestRAGscholar(unittest.TestCase):
    def setUp(self):
        # Set up any necessary test environment
        pass

    def test_main_function(self):
        # Capture stdout and stderr
        captured_output = io.StringIO()
        captured_error = io.StringIO()

        # Prepare test arguments
        test_args = [
            "rag.py",
            "--query_author", "Anthony Weiss",
            "--query_topic", "Elastagen",
            "--keywords", "elastin, tissue engineering, elastagen",
            "--research_period_start", "2013",
            "--research_period_end", "2023",
            "--impact_period_start", "2013",
            "--impact_period_end", "2023",
            "--organisation", "University of Sydney",
            "--language_style", "analytical",
            "--path_documents", "None"
        ]

        # Redirect stdout and stderr, and run the main function
        with redirect_stdout(captured_output), redirect_stderr(captured_error):
            sys.argv = test_args
            main()

        # Check if the expected files are created
        results_path = Path('../../results/Elastagen_by_Anthony_Weiss')
        self.assertTrue(results_path.exists())
        self.assertTrue((results_path / "Use_Case_Study.md").exists())
        self.assertTrue((results_path / "Use_Case_Study.docx").exists())
        self.assertTrue((results_path / "ragscholar.log").exists())

        # Optionally, you can print captured output and error for debugging
        # print("Captured output:", captured_output.getvalue())
        # print("Captured error:", captured_error.getvalue())

if __name__ == '__main__':
    unittest.main()
