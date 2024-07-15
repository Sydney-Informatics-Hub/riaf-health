import unittest
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import the rag module
sys.path.append(str(Path(__file__).parent.parent))

from rag import RAGscholar

class TestRAGscholar(unittest.TestCase):
    def setUp(self):
        # Set up any necessary test environment
        pass

    def test_RAGscholar_run1(self):
        rag = RAGscholar(path_templates='./templates/',
                         fname_system_prompt='Prompt_context.md',
                         fname_report_template='Report.md',
                         outpath='../../results/',
                         path_index='../../index_store',
                         path_documents=None,
                         language_style="analytical",
                         load_index_from_storage=False)

        query_author = "Anthony Weiss"
        query_topic = "Elastagen"
        keywords = "elastin, tissue engineering, elastagen"
        research_period_start = 2013
        research_period_end = 2023
        impact_period_start = 2013
        impact_period_end = 2023
        organisation = "University of Sydney"

        # Run the RAGscholar
        rag.run(query_topic,
                query_author,
                keywords,
                organisation,
                research_period_start,
                research_period_end,
                impact_period_start,
                impact_period_end,
                scholarai_delete_pdfs=False)

        # Add assertions to check the expected outcomes
        # For example:
        self.assertTrue(os.path.exists(os.path.join(rag.outpath, "Use_Case_Study.md")))
        self.assertTrue(os.path.exists(os.path.join(rag.outpath, "Use_Case_Study.docx")))
        self.assertTrue(os.path.exists(os.path.join(rag.outpath, "ragscholar.log")))

if __name__ == '__main__':
    unittest.main()
