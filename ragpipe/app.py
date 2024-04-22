import streamlit as st  
from rag import RAGscholar

def main():  
    st.title('Research Impact Assessment Framework\nUse-Case-Study Generator')  
      
    # Create input fields for each argument  
    query_author = st.text_input('Author name to search for', value="Anthony Weiss")  
    query_topic = st.text_input('Topic for Use-case Study', value = "Elastagen")  
    query_keywords = st.text_input('Keywords for query (separated by commas)', value = "elastin, tissue engineering, elastagen")  
    research_period_start = st.text_input('Research period start (year)', value = 2013)  
    research_period_end = st.text_input('Research period end (year)', value = 2023)  
    impact_period_start = st.text_input('Impact period start (year)', value = 2013)  
    impact_period_end = st.text_input('Impact period end (year)', value = 2023)  
    organisation = st.text_input('Organisation', value = "The University of Sydney")  
    language_style = st.selectbox('Language style for report', options=['analytical', 'journalistic', 'academic', 'legal', 'medical'], index=0)  

    # File uploaders  
    path_documents = st.write('Path to directory with your documents')  
    if st.file_uploader('Upload your documents', type=None, accept_multiple_files=True)  :
        st.write('Documents uploaded!')
    path_documents = st.text_input("Local do store", value = '../test_data/Weiss_docs')
  
    # Button to run the RAGscholar process  
    if st.button('Generate Use-case Study'):  
        rag = RAGscholar(  
            path_templates='./templates/',  
            fname_system_prompt='Prompt_context.md',  
            fname_report_template='Report.md',  
            outpath='../../results/',  
            path_index='../../index_store',   
            path_documents=path_documents,  
            path_openai_key='../../openai_sih_key.txt',  
            language_style=language_style  
        )  
  
        rag.run(  
            query_topic,  
            query_author,  
            query_keywords,  
            organisation,  
            research_period_start,  
            research_period_end,  
            impact_period_start,  
            impact_period_end,  
            benchmark_review=False  
        )  

        # Get the content from the StringIO object and display it  
        output_text = output_stream.getvalue()  
        st.text_area("Output", value=output_text, height=300, disabled=False)  
        output_stream.close()  
  
        st.success('Use-case study generated successfully.')  
  
if __name__ == '__main__':  
    main()  
