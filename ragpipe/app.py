import streamlit as st
import subprocess
import sys
import os
import time


def main():
    st.title(r"$\textsf{\tiny Research Impact Assessment Framework}$" + "\n" + r"Use-Case-Study Generator")
    
    # Create input fields for each argument
    query_author = st.text_input(r"$\textsf{\tiny Author name to search for}$", value="Anthony Weiss")
    query_topic = st.text_input(r"$\textsf{\tiny Topic for Use-case Study}$", value="Elastagen")
    query_keywords = st.text_input(r"$\textsf{\tiny Keywords for query (separated by commas)}$", value="elastin, tissue engineering, elastagen")
    col1, col2 = st.columns(2)
    with col1:
        research_period_start = st.text_input(r"$\textsf{\tiny Research period start (year)}$", value=2013)
    with col2:
        research_period_end = st.text_input(r"$\textsf{\tiny Research period end (year)}$", value=2023)

    organisation = st.text_input(r"$\textsf{\tiny Organisation}$", value="The University of Sydney")
    language_style = st.selectbox(r"$\textsf{\tiny Language style for report}$", options=['analytical', 'journalistic', 'academic', 'legal', 'medical'], index=0)

    impact_period_start = 2013
    impact_period_end = 2023
    path_documents = st.text_input(r"$\textsf{\tiny Local document store}$", value='../test_data/Weiss_docs')

    # File uploaders
    if st.file_uploader(r"$\textsf{\tiny Upload your documents}$", type=None, accept_multiple_files=True):
        st.write('Documents uploaded!')

    # Button to run the RAGscholar process
    if st.button('Generate Use-case Study'):

        # Prepare the command to run rag.py as a subprocess
        cmd = [
            sys.executable,
            '-u',
            "rag.py",
            "--query_author", query_author,
            "--query_topic", query_topic,
            "--keywords", query_keywords,
            "--research_period_start", str(research_period_start),
            "--research_period_end", str(research_period_end),
            "--impact_period_start", str(impact_period_start),
            "--impact_period_end", str(impact_period_end),
            "--organisation", organisation,
            "--language_style", language_style,
            "--path_documents", path_documents
        ]

        # Create containers for the spinner and output
        spinner_container = st.empty()
        output_container = st.container()

        output_area = st.empty()
        output_area.text_area("Process Info", value="Initiating process engine...", height=400, label_visibility = 'hidden', key=f"text_0")

        def update_text(output):
            # callback function
            output_area.text_area("Process Info", value=output, height=400, label_visibility = 'hidden', key = f"text_{time.time()}")
            
            
        with spinner_container, st.spinner("### Generating Use-case Study"):
            with output_container:
                st.markdown("#### Process Information:")
                
            # Run the subprocess and capture its output in real-time
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

            # Initialize a list to store the last 5 lines
            last_lines = []

            # Read and display the output line by line
            while process.poll() is None:
                line = process.stdout.readline()
                if not line:
                    continue
                
                # Add the new line to the list
                last_lines.append(line.strip())
                
                # Keep only the last 4 lines
                if len(last_lines) > 4:
                    last_lines.pop(0)
                
                # Join the last lines and display them
                output = "\n".join(last_lines)
                with output_container:
                    update_text(output)

            # Wait for the subprocess to finish
            process.wait()

        if process.returncode == 0:
            st.success('Use-case study generated successfully.')
        else:
            st.error('An error occurred while generating the use-case study.')

if __name__ == '__main__':
    main()
