import streamlit as st
import subprocess
import sys
import os
import time

class StreamToLogger:
    def __init__(self):
        self.logger = logging.getLogger('MyLogger')
        self.logger.setLevel(logging.INFO)
        self.log_capture_string = StringIO()
        ch = logging.StreamHandler(self.log_capture_string)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def write(self, message):
        if message.strip() != "":
            self.logger.info(message)

    def flush(self):
        pass

    def get_log_contents(self):
        return self.log_capture_string.getvalue()

logger_stream = StreamToLogger()


def capture_output(func, logger_stream):
    old_stdout = sys.stdout
    sys.stdout = logger_stream

    def run_and_capture():
        try:
            func()
        finally:
            sys.stdout = old_stdout

    thread = threading.Thread(target=run_and_capture)
    thread.start()

    return thread



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

        st.title("Streamlit Real-Time Output Example")

        output_area = st.empty()
        logger_stream = StreamToLogger()

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

       
        thread =capture_output(
            rag.run(  
            query_topic,  
            query_author,  
            query_keywords,  
            organisation,  
            research_period_start,  
            research_period_end,  
            impact_period_start,  
            impact_period_end,  
            benchmark_review=True),
            logger_stream)
        
        while thread.is_alive():
            output_area.text(logger_stream.get_log_contents())
            time.sleep(0.1)

        output_area.text(logger_stream.get_log_contents())

    
        # # Get the content from the StringIO object and display it  
        # output_text = output_stream.getvalue()  
        # st.text_area("Output", value=output_text, height=300, disabled=False)  
        # output_stream.close()  
  
        # st.success('Use-case study generated successfully.')  
  
if __name__ == '__main__':  
    main()  
