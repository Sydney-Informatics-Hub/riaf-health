# Main Script RAG Scholar to generate use-case studies for NSW Health Research Impact Assessment Framework'

import argparse
from rag import RAGscholar

def main():
    parser = argparse.ArgumentParser(description='RAG Scholar generating use-case studies for NSW Health Research Impact Assessment Framework')
    parser.add_argument('--query_author', type=str,
                        help='Author name to search for')
    parser.add_argument('--query_topic', type=str, help='Topic for Uue-case Study')
    parser.add_argument('--query_keywords', type=str, help='Keywords for query')
    parser.add_argument('--research_period_start', type=str, help='Research period start (year)')
    parser.add_argument('--research_period_end', type=str, help='Research period end (year)')
    parser.add_argument('--impact_period_start', type=str, help='Impact period start (year)')
    parser.add_argument('--impact_period_end', type=str, help='Impact period end (year)')
    parser.add_argument('--organisation', type=str, help='Organisation')
    parser.add_argument('--language_style', type=str, help='Language style for report', default='analytical')
    parser.add_argument('--path_documents', type=str, help='Path to directory with your documents', default=None)
    parser.add_argument('--path_templates', type=str, help='Path to templates', default='./templates/')
    parser.add_argument('--fname_system_prompt', type=str, help='Filename for system prompt', default='Prompt_system.md')
    parser.add_argument('--fname_report_template', type=str, help='Filename for report template', default='Report.md')
    parser.add_argument('--outpath', type=str, help='Output path', default='../../results/')
    parser.add_argument('--path_index', type=str, help='Path to index', default='../../index_store')

    args = parser.parse_args()

    # Check is args are passed, if not ask user for input for arguments that have no default value:
    if args.query_topic is None:
        args.query_topic = input("Enter topic for use-case study: ")
    if args.query_keywords is None:
        args.query_keywords = input("Enter keyword(s) for query (separated by commas): ")
    if args.query_author is None:
        args.query_author = input("Enter author name(s) to search for: ")
    if args.organisation is None:
        args.organisation = input("Enter organisation: ")
    if args.research_period_start is None:
        args.research_period_start = input("Enter research period start (year):")
    if args.research_period_end is None:
        args.research_period_end = input("Enter research period end (year):")
    if args.impact_period_start is None:
        args.impact_period_start = input("Enter impact period start (year):")
    if args.impact_period_end is None:
        args.impact_period_end = input("Enter impact period end (year):")
    if args.language_style is None:
        args.language_style = input("Enter language style for report (e.g., analytical, journalistic, academic, legal, medical): ")
    if args.path_documents is None:
        args.path_documents = input("Enter path to directory with your documents: ")

    
    
    rag = RAGscholar(path_templates=args.path_templates,
                    fname_system_prompt=args.fname_system_prompt,
                    fname_report_template=args.fname_report_template,
                    outpath=args.outpath,
                    path_index=args.path_index, 
                    path_documents=args.path_documents,
                    path_openai_key='../../openai_sih_key.txt'
                    language_style=args.language_style)
 
    rag.run(args.query_topic,
            args.query_author,
            args.query_keywords,
            args.organisation,
            args.research_period_start,
            args.research_period_end,
            args.impact_period_start,
            args.impact_period_end)
    

if __name__ == "__main__":
    main()
