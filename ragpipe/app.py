import streamlit as st
import subprocess
import sys
import os
import time
import shutil
import io

OUTPATH = '../../results/'


def main():
    #Streamlit's default configuration is for development  mode, which does not allow CORS requests.
    #st.set_option('server.enableCORS', True)
    # Initialization
    if 'stage' not in st.session_state:
        st.session_state['stage'] = 'process'

    st.title(r"$\textsf{\tiny RIAF Use-Case-Study Generator}$")
    
    # Create input fields for each argument
    query_author = st.text_input(r"$\textsf{\small Author name to search for}$", value="Anthony Weiss")
    query_topic = st.text_input(r"$\textsf{\small Topic for Use-case Study}$", value="Elastagen")
    query_keywords = st.text_input(r"$\textsf{\small Keywords for publication query (separated by commas)}$", value="elastin, tissue engineering, elastagen")
    col1, col2 = st.columns(2)
    with col1:
        research_period_start = st.text_input(r"$\textsf{\small Research period start (year)}$", value=2013)
    with col2:
        research_period_end = st.text_input(r"$\textsf{\small Research period end (year)}$", value=2023)

    organisation = st.text_input(r"$\textsf{\small Organisation}$", value="The University of Sydney")
    language_style = st.selectbox(r"$\textsf{\small Language style for report}$", options=['analytical', 'journalistic', 'academic', 'legal', 'medical'], index=0)

    impact_period_start = 2013
    impact_period_end = 2023
    path_documents = st.text_input(r"$\textsf{\small Local document store}$", value='../test_data/Weiss_docs')

    # Additional context input
    additional_context = st.text_area(r"$\textsf{\small Additional context and instructions}$", value="", height=100)

    # File uploaders
    if st.file_uploader(r"$\textsf{\small Upload your documents}$", type=None, accept_multiple_files=True):
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
            "--path_documents", path_documents,
            "--additional_context", additional_context
        ]

        # Create containers for the spinner and output
        spinner_container = st.empty()
        output_container = st.container()

        output_area = st.empty()
        output_area.text_area(r"$\textsf{\large Process Info}$", value="Initiating process engine...", height=300, key=f"text_0")

        def update_text(output):
            # callback function
            output_area.text_area(r"$\textsf{\large Process Info}$", value=output, height=300, key = f"text_{time.time()}")
            #output_area.text_area("Process Info", value=output, height=300, label_visibility = 'hidden', key = f"text_{time.time()}")

        st.text("")
            
        with spinner_container, st.spinner("### Generating Use-case Study"):
                
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
            st.session_state['stage'] = 'generated'
            st.success('Use-case study generated successfully.')
            fname_out = query_topic + "_by_" + query_author
            fname_out = fname_out.replace(" ", "_")
            outpath = os.path.join(OUTPATH, fname_out)
            with open(os.path.join(outpath, "Use_Case_Study.md"), "r") as file:
                use_case_study = file.read()
            # add scrollable textboxes for the generated use-case study
            # Write subheader "Generated Use-case Study"
            st.subheader("Preview")
            with st.container(height=500):
                st.markdown(
                    """
                    <div style="max-height: 500px; overflow-y: auto;">
                    {content}
                    </div>
                    """.format(content=use_case_study),
                    unsafe_allow_html=True,
                )
        else:
            st.session_state['stage'] = 'failed'
            st.error('An error occurred while generating the use-case study.')

        # Add a button to download all results as a zip file
        if st.session_state.stage == 'generated':          
            # Create a BytesIO object to store the zip file
            print('Creating zip file for results...')
            zip_filename = os.path.join(OUTPATH,f"Results_{fname_out}")
            shutil.make_archive(zip_filename, 'zip', outpath)
            zip_filename = zip_filename + ".zip"

            with open(zip_filename, "rb") as fp:
                btn = st.download_button(
                    label="Download Results",
                    data=fp,
                    file_name= f"Results_{fname_out}.zip",
                    mime="application/zip"
                )  



if __name__ == '__main__':
    main()
