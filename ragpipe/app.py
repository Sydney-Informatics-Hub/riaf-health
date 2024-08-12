import streamlit as st
import subprocess
import sys
import os
import time


def main():
    #Streamlit's default configuration is for development  mode, which does not allow CORS requests.
    #st.set_option('server.enableCORS', True)

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
            st.success('Use-case study generated successfully.')
            fname_out = query_topic + "_by_" + query_author
            fname_out = fname_out.replace(" ", "_")
            outpath = os.path.join('../../results/', fname_out)
            with open(os.path.join(outpath, "Use_Case_Study.md"), "r") as file:
                use_case_study = file.read()
            # add scrollable textboxes for the generated use-case study
            # Write subheader "Generated Use-case Study"
            st.subheader("Generated Use-case Study")
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
            st.error('An error occurred while generating the use-case study.')

import zipfile
import io

if __name__ == '__main__':
    main()

    # Add a button to download all results as a zip file
    if st.button('Download Results'):
        fname_out = query_topic + "_by_" + query_author
        fname_out = fname_out.replace(" ", "_")
        outpath = os.path.join('../../results/', fname_out)
        
        # Create a BytesIO object to store the zip file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(outpath):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, outpath)
                    zip_file.write(file_path, arcname)
        
        # Set the buffer's position to the beginning
        zip_buffer.seek(0)
        
        # Create a download button for the zip file
        st.download_button(
            label="Download Results as ZIP",
            data=zip_buffer,
            file_name=f"{fname_out}_results.zip",
            mime="application/zip"
        )
