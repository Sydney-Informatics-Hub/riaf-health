import streamlit as st
import subprocess
import sys
import os
import time
import shutil
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from PIL import Image

# Define the output path for the generated use-case study
OUTPATH = '../../results/'

def display_logo():
    logo_path = "./templates/logo.jpeg"
    if os.path.exists(logo_path):
        image = Image.open(logo_path)
        # Calculate new width to maintain aspect ratio
        aspect_ratio = image.width / image.height
        new_height = 150
        new_width = int(new_height * aspect_ratio)
        image = image.resize((new_width, new_height))
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image)
    else:
        st.warning("Logo image not found.")

def login():
    display_logo()  # Add this line to display the logo

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
    query_author = st.text_input(r"$\textsf{\small Author name to search for (separate multiple authors by comma)}$", 
                                 value="",
                                 help="""Enter author names, e.g., Anthony Weiss, Kate Curtis. 
                                 The app will retrieve publications and other public content for each author on the list.
                                 Note that the processing time will be longer for more author names,
                                 and a author list of less than five main contributors is recommended.""")
    query_topic = st.text_input(r"$\textsf{\small Topic for Use-case Study}$", 
                                value="",
                                help="""Title or topic for the Use Case Study to be generated.
                                This will be the main topic that will guide the generation process.
                                Note that you can add more specific instructions and context in the section `Additional context and instructions` below.
                                """)
    query_keywords = st.text_input(r"$\textsf{\small Keywords for publication query (separated by commas)}$", 
                                   value="",
                                   help="""Enter all relevant keywords related to the study. 
                                   This will assist the app in selecting relevant publications.""")
    col1, col2 = st.columns(2)
    with col1:
        research_period_start = st.text_input(r"$\textsf{\small Research period start (year)}$", value=2013, 
                                              help="Specify the starting year of the active research timeframe for the Use Case Study.")
    with col2:
        research_period_end = st.text_input(r"$\textsf{\small Research period end (year)}$", value=2024,
                                            help="Specify the final year of the active research timeframe for the Use Case Study.")
    with col1:
        impact_period_start = st.text_input(r"$\textsf{\small Impact period start (year)}$", value=research_period_start,
                                            help="Specify the starting year of the research impact timeframe for the Use Case Study." )
    with col2:
        impact_period_end = st.text_input(r"$\textsf{\small Impact period end (year)}$", value=research_period_end,
                                          help="Specify the final year of the research impact timeframe for the Use Case Study.")

    organisation = st.text_input(r"$\textsf{\small Organisation}$", value="The University of Sydney", 
                                 help="Affiliation: University or organisation that hosted the research")
    
    language_style = st.selectbox(r"$\textsf{\small Language style for report}$", options=['analytical', 
                                                                                           'journalistic', 
                                                                                           'academic', 
                                                                                           'scientific commentary', 
                                                                                           'objective',
                                                                                           'narrative',
                                                                                           'engaging'], index=0,
                                                                                           help="Specify the language style for writing the Use Case Study.")


    # Additional context input
    additional_context = st.text_area(r"$\textsf{\small Additional context and instructions}$", value="", height=100,
                                      help="""
                                      ## Context Help
                                      
                                      Add here any additional information, topical context, or instructions that might be relevant for the Use Case Study.
                                      
                                      ## Example information to include:
                                      - List your key, related grants (titles, and amounts of funding) 
                                      - List any HDRs (name) working on this project, or working on related research with you (To capture key higher degree research students)
                                      - List any ECRs (name) working on this project, or working on related research with you (To capture ECRs/researcher development)
                                      - List any key collaborating partners (e.g. other universities, government organisations, industry partners or community groups) involved in this project or research
                                      (To capture key collaborations/partners in the research/for the researcher)
                                      - Any project details, commercial spin-offs, patents etc. 
                                      
                                      DO NOT ADD ANY CONFIDENTIAL OR PRIVATE INFORMATION.
                                      """
                                      )

    uploaded_files = st.file_uploader(r"$\textsf{\small Upload your documents}$", type=None, accept_multiple_files=True,
                                      help="""Add here any files that might be relevant to Use Case Study.
                                      Also add any publications that have restricted access for automatic download.
                                      DO NOT UPLOAD ANY CONFIDENTIAL OR PRIVATE DATA.
                                      """)
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


    # Add a button to download all results as a zip file
    if st.session_state.stage == 'generated':
        st.divider()           
        with open(st.session_state.zip_filename, "rb") as fp:
            if st.download_button(
                label="Download Results",
                data=fp,
                file_name= f"Results_{st.session_state.fname_out}.zip",
                mime="application/zip"):
                # make sure the download is complete before displaying the success message
                #time.sleep(5)
                st.success('Download complete.')
        

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

        ### Cleanup the temporary directory:
        #if os.path.exists(st.session_state.path_documents):
        #    shutil.rmtree(st.session_state.path_documents)


 
if __name__ == '__main__':
    st.set_page_config(page_title="RIAF AI", page_icon=":robot:")
    hide_streamlit_style = """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    login()
    if st.session_state["authentication_status"]:
        main()
