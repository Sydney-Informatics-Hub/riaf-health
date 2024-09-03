import streamlit as st
import subprocess
import sys
import os
import time
import shutil
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Define the output path for the generated use-case study
OUTPATH = '../../results/'


def login():
    with open('streamlit_secrets.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
        )
    
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        name, authentication_status, username = authenticator.login(max_concurrent_users = 10) #'Login', 'main'

    if authentication_status:
        #print('name', name)
        #print('username', username)
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')



def main():
    #Streamlit's default configuration is for development  mode, which does not allow CORS requests.
    #st.set_option('server.enableCORS', True)
    # Initialization
    if 'uploaded' not in st.session_state:
        st.session_state['uploaded'] = 0
    if 'stage' not in st.session_state:
        st.session_state['stage'] = 'process'
    if 'path_documents' in st.session_state:
        st.session_state['uploaded'] = None

    # Check if st.session_state['path_documents'] already exists
    if 'path_documents' not in st.session_state:
        path_documents = os.path.join(OUTPATH, 'temp_' + str(time.time()))
        st.session_state['path_documents'] = path_documents
        os.makedirs(path_documents, exist_ok=True)


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
    with col1:
        impact_period_start = st.text_input(r"$\textsf{\small Impact period start (year)}$", value=research_period_start )
    with col2:
        impact_period_end = st.text_input(r"$\textsf{\small Impact period end (year)}$", value=research_period_end)

    organisation = st.text_input(r"$\textsf{\small Organisation}$", value="The University of Sydney")
    language_style = st.selectbox(r"$\textsf{\small Language style for report}$", options=['analytical', 
                                                                                           'journalistic', 
                                                                                           'academic', 
                                                                                           'scientific commentary', 
                                                                                           'objective',
                                                                                           'narrative',
                                                                                           'engaging'], index=0)


    # Additional context input
    additional_context = st.text_area(r"$\textsf{\small Additional context and instructions}$", value="", height=100)

    uploaded_files = st.file_uploader(r"$\textsf{\small Upload your documents}$", type=None, accept_multiple_files=True)
    savefiles = False
    if len(uploaded_files) > 0:
        # check if the temporary directory exist already
        if (st.session_state.uploaded == 0):
            savefiles = True
        else:
            # check if the uploaded files are different from the previous ones
            if uploaded_files != st.session_state.uploaded:
                savefiles = True

    if savefiles:
        st.session_state['uploaded'] = uploaded_files 
        progress_bar = st.progress(0)
        total_files = len(uploaded_files)
        for i, uploaded_file in enumerate(uploaded_files):
            # Create the full path for the file
            save_path = os.path.join(st.session_state.path_documents, uploaded_file.name)
            # Save the uploaded file to the specified path
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Update the progress bar
            progress_bar.progress((i + 1) / total_files)


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
            "--path_documents", st.session_state.path_documents,
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
            outpath = os.path.join(OUTPATH, fname_out)
            print('Creating zip file for results...')
            # Create a BytesIO object to store the zip file
            zip_filename = os.path.join(OUTPATH,f"Results_{fname_out}")
            # add the time generated to the filename
            zip_filename = zip_filename + "_" + time.strftime("%Y-%m-%d-%H%M")
            shutil.make_archive(zip_filename, 'zip', outpath)
            zip_filename = zip_filename + ".zip"
            st.session_state['stage'] = 'generated'
            st.session_state['zip_filename'] = zip_filename
            st.session_state['fname_out'] = fname_out
            st.session_state['outpath_md'] = os.path.join(outpath, "Use_Case_Study.md")
        else:
            st.session_state['stage'] = 'failed'
            st.error('An error occurred while generating the use-case study.')

 
    # for testing download
    #st.session_state['stage'] = 'generated'
    #st.session_state['zip_filename'] = '../../results/Results_Elastagen_by_Anthony_Weiss_2024-09-03-0056.zip'
    #st.session_state['fname_out'] = 'Elastagen_by_Anthony_Weiss'
    #st.session_state['outpath_md'] = '../../results/Elastagen_by_Anthony_Weiss/Use_Case_Study.md'

    # Add a button to download all results as a zip file
    if st.session_state.stage == 'generated':
        st.text("")          
        with open(st.session_state.zip_filename, "rb") as fp:
            if st.download_button(
                label="Download Results",
                data=fp,
                file_name= f"Results_{st.session_state.fname_out}.zip",
                mime="application/zip"):
                # make sure the download is complete before displaying the success message
                time.sleep(5)
                st.success('Download complete.')
            
            # wait for the download to complete
            #time.sleep(5)


    if st.session_state.stage == 'generated': 
        with open(st.session_state.outpath_md, "r") as file:
            use_case_study = file.read()
        # add scrollable textboxes for the generated use-case study
        st.text("")
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
        # Cleanup the temporary directory, check if exists first
        #if os.path.exists(st.session_state.path_documents):
        #    shutil.rmtree(st.session_state.path_documents)


 
if __name__ == '__main__':
    login()
    if st.session_state["authentication_status"]:
        main()
