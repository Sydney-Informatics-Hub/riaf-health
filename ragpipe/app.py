import streamlit as st  
from rag import RAGscholar

def main():  
    st.title(r"$\textsf{\tiny Research Impact Assessment Framework}$" + "\n" + r"Use-Case-Study Generator")
      
    # Create input fields for each argument  
    query_author = st.text_input(r"$\textsf{\tiny Author name to search for}$", value="Anthony Weiss")  
    query_topic = st.text_input(r"$\textsf{\tiny Topic for Use-case Study}$", value = "Elastagen")  
    query_keywords = st.text_input(r"$\textsf{\tiny Keywords for query (separated by commas)}$", value = "elastin, tissue engineering, elastagen")  
    col1, col2 = st.columns(2)
    with col1:
        research_period_start = st.text_input(r"$\textsf{\tiny Research period start (year)}$", value = 2013) 
    with col2: 
        research_period_end = st.text_input(r"$\textsf{\tiny Research period end (year)}$", value = 2023)  

    organisation = st.text_input(r"$\textsf{\tiny Organisation}$", value = "The University of Sydney")  
    language_style = st.selectbox(r"$\textsf{\tiny Language style for report}$", options=['analytical', 'journalistic', 'academic', 'legal', 'medical'], index=0)  

    # impact_period_start = st.text_input('Impact period start (year)', value = 2013)  
    # impact_period_end = st.text_input('Impact period end (year)', value = 2023)  
    impact_period_start = 2013
    impact_period_end = 2023
    path_documents = st.text_input(r"$\textsf{\tiny Local document store}$", value = '../test_data/Weiss_docs')

    # File uploaders  
    # path_documents = st.write(r"$\textsf{\tiny Path to directory with your documents}$")  
    if st.file_uploader(r"$\textsf{\tiny Upload your documents}$", type=None, accept_multiple_files=True)  :
        st.write('Documents uploaded!')

    
  
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
            benchmark_review=True  
        )  

        # # Get the content from the StringIO object and display it  
        # output_text = output_stream.getvalue()  
        # st.text_area("Output", value=output_text, height=300, disabled=False)  
        # output_stream.close()  
  
        # st.success('Use-case study generated successfully.')  
  
if __name__ == '__main__':  
    main()  
