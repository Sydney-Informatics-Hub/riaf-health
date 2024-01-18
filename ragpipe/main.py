# Main Script for generating the Use-Case Study Report

import argparse
from rag import RAGscholar

def main():
    parser = argparse.ArgumentParser(description='RAG Scholar')
    parser.add_argument('--query_author', type=str,
                        help='Author name to search for')
    parser.add_argument('--query_topic', type=str, help='Topic for Uue-case Study')
    parser.add_argument('--research_period', type=str, help='Research period')
    parser.add_argument('--impact_period', type=str, help='Impact period')
    parser.add_argument('--organisation', type=str, help='Organisation')
    parser.add_argument('--path_templates', type=str, help='Path to templates', default='./templates/')
    parser.add_argument('--fname_system_prompt', type=str, help='Filename for system prompt', default='Prompt_context.md')
    parser.add_argument('--fname_report_template', type=str, help='Filename for report template', default='Report.md')
    parser.add_argument('--outpath', type=str, help='Output path', default='../../results/')
    parser.add_argument('--path_index', type=str, help='Path to index', default='../../index_store')

    args = parser.parse_args()

    # Check is args are passed, if not ask user for input for arguments that have no default value:
    if args.query_topic is None:
        args.query_topic = input("Enter topic for use-case study: ")
    if args.query_author is None:
        args.query_author = input("Enter author name(s) to search for: ")
    if args.organisation is None:
        args.organisation = input("Enter organisation: ")
    if args.research_period is None:
        args.research_period = input("Enter research period: ")
    if args.impact_period is None:
        args.impact_period = input("Enter impact period: ")
    
    
    rag = RAGscholar(path_templates=args.path_templates,
                    fname_system_prompt=args.fname_system_prompt,
                    fname_report_template=args.fname_report_template,
                    outpath=args.outpath,
                    path_index=args.path_index, 
                    path_openai_key='../../openai_sih_key.txt')
 
    rag.run(args.query_topic,
            args.query_author,
            args.research_period,
            args.impact_period,
            args.organisation)
