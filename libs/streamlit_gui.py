import streamlit as st 
import streamlit_authenticator as stauth 
from datetime import datetime
import pytz 
import hashlib 
from typing import Dict, Generator, Tuple, List 
import dropbox 
import dropbox.files 
import pandas as pd 
import pypandoc 
from pypdf import PdfReader, PdfWriter
import io 
import csv 
from pathlib import Path 
import threading 
import logging 
import time 
import tempfile 
import base64 
import os 
import re 
from dotenv import load_dotenv 

from .ai_gateways.gateway import AICompanyGateway 
from .streamlit_logger import setup_logger 
from .file import read_md 
from .ai_gateways.objects import TextBlock, DocumentBlock

class StreamlitGUI: 
    def __init__(self, conf:Dict) -> None: 
        """Set up the object

        Args:
            conf_file (Dict): a dictionary with the opts of the app 
        """
        # load secrets environment variables 
        load_dotenv(conf['secrets_env_fpath'])
        # set the global vars
        self.page_title = conf['page_title'] # the title for the page 
        self.page_icon = conf['page_icon'] # the icon to use for the page 
        self.ai_company = conf['ai_company'] # the name of the AI company to use 
        self.ai_model = conf['model'] # the name of the AI model to use 
        self.ai_model_params = conf['model_params'] # the parameters for the AI model 
        self.interviewer_system_message = read_md(conf['interviewer_system_message_fpath']) # the system prompt for the interviewer bot 
        self.writer_system_message = read_md(conf['writer_system_message_fpath']) # the system prompt for the writer bot 
        self.generate_summary_prompt = read_md(conf['generate_summary_prompt_fpath']) # the generate summary prompt for the writer bot 
        self.auth_required = conf['auth_required'] # True if logins are enabled and authentication is required, False otherwise 
        self.auth_config = conf['auth_config_fpath'] # the path to authentication config file 
        self.interviewer_avatar = conf['interviewer_avatar'] # the string for the interviewer avatar
        self.user_avatar = conf['user_avatar'] # the string for the user avatar
        self.first_interviewer_message = conf['first_interviewer_message'] # the first message that the bot will send 
        self.closing_messages = conf['closing_messages'] # a dict that maps closing code to closing message 
        self.dropbox_path = conf['dropbox_fpath'] # the path to the dropbox data folder to store the transcripts 
        self.interview_instructions = read_md(conf['interview_instructions_fpath']) # the instructions to display for the bot 
        self.logger_name = conf['logger_name'] # the name of logger 
        self.file_uploader_title = conf['file_uploader_title'] # the title of the file uploader widget 
        self.file_uploader_help_text = conf['file_uploader_help_text'] # the help text for the file uploader widget 
        self.report_a_bug_url = conf['report_a_bug_url'] # the url to point to for the report a bug button 

        # set up the page 
        st.set_page_config(
            page_title=self.page_title, 
            page_icon=self.page_icon, 
            menu_items={
                'About': self.interview_instructions, 
                'Report a bug': self.report_a_bug_url
            }
        )

        if self.auth_required: 
            # set up the authentication 
            self.authenticator = stauth.Authenticate(self.auth_config, auto_hash=False)

        # create some containers for the header (where the title will live) and for the chat (where chat history will live) 
        self.header_container = st.container() 
        self.error_container = st.container() 
        self.instructions_container = st.container() 
        self.file_upload_container = st.container() 
        self.uploaded_file_container = st.container() 
        self.chat_container = st.container() 


    def setup(self) -> None: 
        """Sets up the components of the page"""
        # set the title of the page 
        with self.header_container: 
            st.markdown("## " + self.page_title) 
            # add some html code that hides the file uploader list from streamlit 
            css = """
                <style>
                    div[data-testid="stFileUploaderFile"] {
                        display: none;
                    }
                    div.st-emotion-cache-fis6aj.e17y52ym5 {
                        display: none;
                    }
                </style>
            """
            st.markdown(css, unsafe_allow_html=True)
        self.setup_session_vars() 
        self.display_login_page() 
        self.display_instructions_expander() 
        self.display_file_uploader() 
        self.display_uploaded_file() 
        self.display_load_past_session() 
        self.display_restart_interview_button()
        self.display_bot_switch_button() 
        self.display_generate_summary_button() 
        self.display_user_input() 


    def run(self) -> None: 
        """Main function that runs the whole page"""
        self.setup() 
        self.display_message_history() 
        if st.session_state.reached_error: 
            self.display_error_message() 
        else: 
            if st.session_state.interview_status and not st.session_state.first_instructions_shown: 
                self.display_instructions()
            if st.session_state.interview_status and not st.session_state.transcript_history: 
                self.stream_initial_message() 
            if st.session_state.interview_status and not st.session_state.first_instructions_shown: 
                time.sleep(1) 
                # change flag so that the dialog doesn't show up anymore 
                st.session_state.first_instructions_shown = True 
            if st.session_state.ai_processing: 
                # get the response from the AI 
                self.stream_message() 
                if not st.session_state.reached_error: 
                    # if there was no error then let's go back to normal 
                    st.session_state.ai_processing = False 
                st.rerun()


    # --------------------------------------------------------------------------
    # frontend 
    # --------------------------------------------------------------------------


    def setup_session_vars(self) -> None: 
        """Sets up the session vars

        Initializes any session variables that haven't been initialized yet 
        """
        if not self.auth_required: 
            # since we're not doing logins set these session vars to defaults
            st.session_state.authentication_status = True 
            st.session_state.username = 'testuser'
            st.session_state.show_login_form = False 

        if self.auth_required and 'show_login_form' not in st.session_state:
            # flag for whether to show the login page or not 
            st.session_state.show_login_form = True 

        if "interview_status" not in st.session_state: 
            # flag for whether the interview is active or not 
            st.session_state.interview_status = st.session_state.get('authentication_status', False) 

        if "transcript_history" not in st.session_state: 
            # will store the transcript history of the conversation so far
            st.session_state.transcript_history = [] 

        if 'session_id' not in st.session_state and 'username' in st.session_state: 
            # store the start time of the interview 
            st.session_state.start_time = int(datetime.now(pytz.timezone('UTC')).timestamp()) 

            # create and store the session ID of the interview 
            data = f"{st.session_state.username}+{st.session_state.start_time}"
            st.session_state.session_id = hashlib.sha256(data.encode()).hexdigest() 

        if 'first_instructions_shown' not in st.session_state: 
            # flag for whether the instructions have been shown for the first time or not 
            st.session_state.first_instructions_shown = False 

        if 'show_confirm_restart' not in st.session_state: 
            # flag for whether to show a confirm restart message
            st.session_state.show_confirm_restart = False 
            st.session_state.show_confirm_restart_time = 0 
        else: 
            if st.session_state.show_confirm_restart: 
                if time.time() - st.session_state.show_confirm_restart_time > 20: 
                    # if it's been more than a minute since the confirm has been shown, turn it back to original 
                    st.session_state.show_confirm_restart = False 

        if 'found_closing_msg' not in st.session_state: 
            # flag for whether the AI outputted a closing message 
            st.session_state.found_closing_msg = False 

        if 'uploaded_file_content' not in st.session_state: 
            # object to store the uploaded file 
            st.session_state.uploaded_file_content = None 
            st.session_state.uploaded_file_name = None 

        if 'reached_error' not in st.session_state: 
            # flag for whether we reached an error or not 
            st.session_state.reached_error = False 
            st.session_state.shown_error_message = ''

        if 'active_bot' not in st.session_state: 
            # flag for which bot is active in the conversation right now 
            st.session_state.active_bot = 'interviewer' # interviewer or writer

        if 'ai_processing' not in st.session_state: 
            # flag for whether the AI is processing the transcript and generating a response 
            st.session_state.ai_processing = False 

        if 'chat_input_counter' not in st.session_state: 
            # NOTE: a counter for the chat input that forces Streamlit to rerender 
            # the chat input widget. Necessary because when we continually disable
            # and reenable the widget between AI messages like we do, the focus 
            # on the chat input is lost and so the first character that the user 
            # types is used to refocus the widget and the second character onwards
            # is actually typed, but this means the first character typed is lost 
            # Creating a new widget each time prevents this, but users must click 
            # the input after each response to start typing.
            st.session_state.chat_input_counter = 0 

        if 'log' not in st.session_state: 
            # objects for logging 
            log_stream, log = setup_logger(self.logger_name)
            st.session_state.log = log 
            st.session_state.log_stream = log_stream 


    def display_login_page(self) -> None: 
        """Display the login page and the log out button after authentication success"""
        if self.auth_required: 
            # only do this if we're using logins 
            if st.session_state.show_login_form:
                # if the session state says show the form, then show it 
                with st.empty(): 
                    try: 
                        # show the login form 
                        self.authenticator.login()
                    except Exception as e: 
                        st.error(e) 

                with st.empty(): 
                    if st.session_state.get('authentication_status') is False: 
                        # password is wrong
                        st.error("Username/password is incorrect") 
                    elif st.session_state.get('authentication_status'):
                        # password is right so change the flag and rerun the script
                        st.session_state.show_login_form = False 
                        st.rerun() 

            if st.session_state.get('authentication_status'): 
                # when authentication is confirmed, show the logout button
                self.log("info", "User logged in", st.session_state.to_dict())
                self.log("info", f"Current active bot: {st.session_state.active_bot}", st.session_state.to_dict())
                with st.sidebar: 
                    # welcome the user 
                    st.write(f"# Welcome {st.session_state.get('name')}")
                    st.session_state.interview_status = True 
                    # add logout button that runs self.on_logout when hit 
                    self.authenticator.logout(callback=self.on_logout) 


    def display_instructions_expander(self) -> None: 
        """Shows the instructions expander"""
        if not st.session_state.show_login_form: 
            with self.instructions_container: 
                with st.expander("See instructions"): 
                    st.markdown(self.interview_instructions)


    @st.dialog(f"Conversation Guide", width='large')
    def display_instructions(self) -> None: 
        """Displays instructions in a pop up dialog"""
        st.markdown(self.interview_instructions)


    def display_file_uploader(self) -> None: 
        """Displays the file upload section"""
        if not st.session_state.show_login_form and st.session_state.interview_status and not st.session_state.reached_error: 
            with self.file_upload_container: 
                # add option to upload one pdf here 
                st.file_uploader(
                    label=f"**{self.file_uploader_title}**", 
                    type="pdf", 
                    accept_multiple_files=False, 
                    on_change=self.on_file_upload,
                    key='file_uploader',
                    help=self.file_uploader_help_text, 
                    label_visibility='visible', 
                    disabled=st.session_state.ai_processing # disable when the AI is processing
                )


    def display_uploaded_file(self) -> None: 
        if not st.session_state.show_login_form and st.session_state.interview_status and not st.session_state.reached_error and st.session_state.uploaded_file_name: 
            with self.uploaded_file_container: 
                st.markdown(f"Uploaded file: {st.session_state.uploaded_file_name}")


    def display_restart_interview_button(self) -> None: 
        """Displays the restart interview"""
        if not st.session_state.show_login_form: 
            # add 'Restart' button to the side bar
            with st.sidebar: 
                if st.session_state.show_confirm_restart: 
                    # show confirmation message 
                    st.markdown("**Are you sure you want to restart?**\nYou will be starting the conversation from scratch")
                    # add the button and runs self.on_restart_button when hit 
                    st.button(
                        label="**Confirm**", 
                        help='Confirm restarting the conversation', 
                        on_click=self.on_restart_button, 
                        type='primary', 
                        disabled=st.session_state.ai_processing # disable when the AI is processing
                    )
                else: 
                    st.markdown("To restart the conversation from scratch, click restart below")
                    # add the button and runs self.on_restart_button when hit 
                    st.button(
                        label="Restart", 
                        help='Restart the conversation', 
                        on_click=self.on_restart_button, 
                        disabled=st.session_state.ai_processing # disable when the AI is processing
                    )


    def display_bot_switch_button(self) -> None: 
        """Displays a button that allows users to switch between bots"""
        if not st.session_state.show_login_form and st.session_state.interview_status and not st.session_state.reached_error: 
            if st.session_state.active_bot == 'interviewer': 
                # check if "Start Report Writer" is in the last AI message. If so, highlight it on screen
                ai_messages = [x for x in st.session_state.transcript_history if x['role'] == 'assistant']
                highlight_button = len(ai_messages) > 0 and 'start report writer' in ai_messages[-1]['content'].lower() 
                with st.sidebar: 
                    st.markdown("To start the report writer bot, click the button below")
                    st.button(
                        label='Start Report Writer', 
                        help='Start the report writer bot', 
                        on_click=self.on_start_report_writer, 
                        type='primary' if highlight_button else 'secondary', # highlight the button when "Start Report Writer" is mentioned in the last AI message 
                        disabled=st.session_state.ai_processing # disable when the AI is processing
                    )
            elif st.session_state.active_bot == 'writer': 
                with st.sidebar: 
                    st.markdown("To return to the interviewer bot, click the button below") 
                    st.button(
                        label='Return to Interviewer', 
                        help='Return to the interviewer bot', 
                        on_click=self.on_return_to_interviewer, 
                        disabled=st.session_state.ai_processing # disable when the AI is processing
                    )
            else: 
                raise ValueError(f"Could not recognize active_bot value of '{st.session_state.active_bot}'")



    def display_generate_summary_button(self) -> None: 
        """Displays the generate summary button"""
        if not st.session_state.show_login_form and st.session_state.interview_status and not st.session_state.reached_error and st.session_state.active_bot == 'writer': 
            # button is always displayed unless we are in the login page to allow people to generate the document at any time 
            with st.sidebar: 
                st.markdown("To download the referee report as a Word document, click download below") 
                # add the button and runs self.on_generate_summary_button when hit 
                st.button(
                    label="Download", 
                    help='Download the referee report as a Word document', 
                    on_click=self.on_generate_summary_button, 
                    disabled=st.session_state.ai_processing # disable when the AI is processing
                )


    def display_load_past_session(self) -> None: 
        """Displays a button that can load a past session"""
        if not st.session_state.show_login_form: 
            with st.sidebar: 
                st.markdown("To load a past session, click below")
                st.button(
                    label="Load a Past Session", 
                    help="Check for past sessions and load them", 
                    on_click=self.on_load_past_session_button, 
                    disabled=st.session_state.ai_processing # disable when the AI is processing
                )


    def display_message_history(self) -> None: 
        """Displays the full message history so far"""
        if not st.session_state.show_login_form: 
            # always show the message history unless we are showing the login page 
            with self.chat_container: 
                for row in st.session_state.transcript_history: 
                    # first set the avatar 
                    if row['role'] == 'assistant': 
                        avatar = self.interviewer_avatar 
                    elif row['role'] == 'user': 
                        avatar = self.user_avatar 

                    # now display the message 
                    with st.chat_message(row['role'], avatar=avatar): 
                        st.markdown(row['content']) 


    def display_user_input(self) -> None: 
        """Display the user input """
        if st.session_state.interview_status and not st.session_state.reached_error and not st.session_state.found_closing_msg: 
            # only display the user input section if the interview is active 
            # display the input section and runs self.on_user_input_submit when text submitted 
            st.chat_input(
                placeholder="Your message here", 
                key=f"user_input_{st.session_state.chat_input_counter}", # use a counter to force Streamlit to rerender the widget to avoid the first character lost bug when disabling and reenabling this widget between AI messages 
                on_submit=self.on_user_input_submit, 
                disabled=st.session_state.ai_processing # disable when the AI is processing
            )


    def display_error_message(self) -> None: 
        """Displays an error message"""
        def try_again(): 
            """Call back function for trying again"""
            self.log("warning", "Trying again after error", st.session_state.to_dict())
            # reset reached error 
            st.session_state.reached_error = False 
            # reset the error message 
            st.session_state.shown_error_message = '' 
            # return back to interview status 
            st.session_state.interview_status = True 

        with self.error_container: 
            st.error(st.session_state.shown_error_message)
            st.button("Try again", on_click=try_again)

        # set the interview state to False as it's over 
        st.session_state.interview_status = False 


    # --------------------------------------------------------------------------
    # backend 
    # --------------------------------------------------------------------------


    def on_logout(self, *args, **kwargs) -> None: 
        """Function that runs when log out button is hit"""
        self.log("warning", "Logging out", st.session_state.to_dict())

        # stop the interview 
        st.session_state.interview_status = False 
        # show the login form 
        st.session_state.show_login_form = True
        # reset instructions flag 
        st.session_state.first_instructions_shown = False 
        # reset reached error 
        st.session_state.reached_error = False 
        # reset the ai processing flag 
        st.session_state.ai_processing = False 

        # remove any other session variable to start over 
        for key in ['active_bot', 'transcript_history', 'start_time', 'session_id', 'log', 'log_stream', 'show_confirm_restart', 'found_closing_msg', 'uploaded_file_name', 'uploaded_file_content']: 
            if key in st.session_state:
                del st.session_state[key]


    def on_user_input_submit(self) -> None: 
        """Function that runs when user input is submitted"""
        try: 
            # get the user inputs 
            text = st.session_state[f"user_input_{st.session_state.chat_input_counter}"]
            st.session_state.chat_input_counter += 1 # increase the counter to force a rerender 

            self.log("warning", f"User input: {text}", st.session_state.to_dict())

            # display the user input 
            with self.chat_container: 
                message = st.chat_message('user', avatar=self.user_avatar) 
                message.markdown(text)

            # save the user input  
            self.save_msg_to_session('user', text)

            # save to the transcript so far to dropbox 
            thread = threading.Thread(target=self.save_transcript_to_dropbox, args=(st.session_state.to_dict(),)) 
            thread.start() 

            # set to true to start the AI processing and streaming 
            st.session_state.ai_processing = True 
        except Exception as e: 
            st.session_state.reached_error = True 
            st.session_state.shown_error_message = "An error occurred processing your message. Please press the try again button and resubmit your message. If issues persist, you can report a bug using the menu item on the top right corner"
            self.log("error", f"Error processing user input: {e}", st.session_state.to_dict())


    def on_file_upload(self) -> None: 
        """Function that runs when a file is uploaded

        The function will read the file as base64, and then save it to dropbox
        """
        def get_num_pages(pdf_bytesio:io.BytesIO) -> int: 
            """Reads the number of pages in a PDF 

            Args:
                pdf_bytesio (io.BytesIO): the PDF bytes data to look at 

            Returns:
                int: the number of pages 
            """
            reader = PdfReader(pdf_bytesio)
            pdf_bytesio.seek(0) 
            return len(reader.pages) 

        def truncate_pdf(pdf_bytesio:io.BytesIO, max_pages:int) -> io.BytesIO: 
            """Truncates a PDF to a certain number of pages 

            Args:
                pdf_bytesio (io.BytesIO): the PDF bytes data
                max_pages (int): the number of pages to truncate to 

            Returns:
                io.BytesIO: the PDF bytes data for the truncated PDF 
            """
            reader = PdfReader(pdf_bytesio) 
            pdf_bytesio.seek(0) 
            writer = PdfWriter()
            for i in range(min(max_pages, len(reader.pages))): 
                writer.add_page(reader.pages[i]) 

            output_bytesio = io.BytesIO() 
            writer.write(output_bytesio) 
            output_bytesio.seek(0)
            return output_bytesio 

        def count_tokens_with_pdf() -> int: 
            """Counts the number of tokens in the message after including the PDF 

            Returns:
                int: the number of tokens in the message
            """
            client = AICompanyGateway.factory(
                company=self.ai_company, 
                api_key=os.environ.get(f"API_KEY_{self.ai_company.upper()}"), 
                api_secret=os.environ.get(f"API_SECRET_{self.ai_company.upper()}"), 
                region=os.environ.get(f"REGION_{self.ai_company.upper()}")
            ) 
            system_message = self.interviewer_system_message if st.session_state.active_bot == 'interviewer' else self.writer_system_message
            num_tokens = client.count_tokens(model=self.ai_model, messages=self.get_messages_for_ai(), system_message=system_message)
            return num_tokens 
        try: 
            uploaded_file = st.session_state.file_uploader
            if uploaded_file: 
                with self.uploaded_file_container: 
                    with st.spinner("Uploading file"): 
                        self.log("warning", f"Uploaded file {uploaded_file.name}", st.session_state.to_dict())
                        if self.ai_company in ['anthropic', 'bedrock']: 
                            truncated = False 
                            # check the size and truncate if necessary 
                            pdf_bytes = uploaded_file.getvalue() 
                            pdf_bytesio = io.BytesIO(pdf_bytes) 
                            num_pages = get_num_pages(pdf_bytesio)
                            if self.ai_company == 'anthropic' and num_pages > 100: 
                                # first truncate to first 100 pages if original is longer than 100 pages (only for Anthropic)
                                self.log("warning", f"Uploaded file has more than 100 pages: {num_pages} pages. Truncating to first 100 pages now", st.session_state.to_dict())
                                pdf_bytesio = truncate_pdf(pdf_bytesio, max_pages=100)
                                truncated = True 

                            # now check the number of tokens 
                            st.session_state.uploaded_file_content = pdf_bytesio.getvalue()
                            num_tokens = count_tokens_with_pdf()
                            self.log("info", f"Current PDF leads to {num_tokens} tokens", st.session_state.to_dict())
                            while num_tokens > 180_000: # TODO: might not want to hard code this? 
                                # continue truncating 5 pages each time until under token limit 
                                self.log("warning", "Current PDF is over the limit for tokens. Truncating by 5 pages now", st.session_state.to_dict())
                                # truncate 5 pages
                                num_pages = get_num_pages(pdf_bytesio) 
                                pdf_bytesio = truncate_pdf(pdf_bytesio, max_pages=num_pages-5) 
                                # check the number of tokens again 
                                st.session_state.uploaded_file_content = pdf_bytesio.getvalue()
                                num_tokens = count_tokens_with_pdf()
                                self.log("info", f"Current PDF leads to {num_tokens} tokens", st.session_state.to_dict())
                                truncated = True 

                            # finally ready to move on 
                            num_pages = get_num_pages(pdf_bytesio)
                            self.log("info", f"Final PDF for AI has {num_pages} pages and {num_tokens} tokens", st.session_state.to_dict())
                            st.session_state.uploaded_file_name = uploaded_file.name
                            if truncated: 
                                # since we truncated, we should let the user know 
                                st.info(f"Please note: your PDF has been automatically truncated to the first {num_pages} pages due to size limits.")

                            # also save the document to dropbox so that we can know what was uploaded 
                            pdf_bytesio.seek(0) 
                            thread = threading.Thread(target=self.save_file_upload_to_dropbox, args=(st.session_state.to_dict(), uploaded_file.name, pdf_bytesio)) 
                            thread.start() 
                        else: 
                            # don't read it or save it but let the user know it's uploaded for UX 
                            st.session_state.uploaded_file_name = uploaded_file.name
        except Exception as e: 
            st.session_state.reached_error = True 
            st.session_state.shown_error_message = "An error occurred uploading your file. Please ensure that your file is less than 100 pages long. You can reupload the file by clicking try again and reuploading your file. If issues persist, you can report a bug using the menu item on the top right corner"
            self.log('error', f"Error processing file upload: {e}", st.session_state.to_dict())


    @st.dialog("Load Past Session", width='large')
    def on_load_past_session_button(self) -> None: 
        self.log("warning", "Checking for past sessions", st.session_state.to_dict()) 
        with st.spinner('Checking for past sessions', show_time=True): 
            past_transcripts_map = self.get_past_sessions(st.session_state.session_id, st.session_state.start_time)
            self.log("info", f"Found {len(past_transcripts_map)} past sessions", st.session_state.to_dict())
        if len(past_transcripts_map) > 0: 
            # there are past transcripts so show to the user 
            session_chosen = st.selectbox(
                'Select a session', 
                past_transcripts_map, 
                index=None, 
                placeholder='Select a past session...', 
                label_visibility='collapsed'
            )

            if session_chosen: 
                # if a session has been chosen, show a preview of the conversation 
                self.log("info", f"Previewing session {session_chosen}", st.session_state.to_dict())

                # build the conversation preview 
                session_conversation = "" 
                for row in past_transcripts_map[session_chosen]['transcript']: 
                    session_conversation += f"**{row['role'].capitalize()}:** {row['content']}\n\n"

                # limit the preview so that the page doesn't get too big
                if len(session_conversation) >= 1500: 
                    session_conversation = session_conversation[:1500].strip() + '...'

                # show the preview 
                st.markdown(f"**Session conversation:**\n\n{session_conversation}")

                # add note about uploaded file 
                if past_transcripts_map[session_chosen]['uploaded_file'] is not None: 
                    st.markdown(f"Uploaded file: {past_transcripts_map[session_chosen]['uploaded_file']['name']}")

                # add confirmation button to move forward with the chosen session 
                confirm_button = st.button(
                    label='Choose session', 
                    help='Click to load the currently selected session', 
                    type='primary', 
                    use_container_width=False
                )
                if confirm_button: 
                    # when confirmed, load the session 
                    self.log("warning", f"Chose session {session_chosen}", st.session_state.to_dict())
                    # check for closing messages
                    st.session_state.interview_status = True 
                    st.session_state.found_closing_msg = False 
                    self.log("warning", f"Checking for closing messages in past session {session_chosen}", st.session_state.to_dict()) 
                    for row in st.session_state.transcript_history: 
                        found_closing_msg, _ = self.check_closing_messages(row['content']) 
                        if found_closing_msg: 
                            st.session_state.interview_status = False 
                            st.session_state.found_closing_msg = True 
                            self.log("info", "Found closing message", st.session_state.to_dict())
                            break 
                    if not st.session_state.found_closing_msg: 
                        self.log("info", "Did not find closing message", st.session_state.to_dict())
                    # set the variables 
                    st.session_state.transcript_history = past_transcripts_map[session_chosen]['transcript'] 
                    st.session_state.active_bot = st.session_state.transcript_history[-1]['active_bot'] # set the active bot to the status of the last message to recreate conditions
                    st.session_state.session_id = past_transcripts_map[session_chosen]['transcript'][0]['session_id'] 
                    if past_transcripts_map[session_chosen]['uploaded_file'] is not None: 
                        st.session_state.uploaded_file_content = past_transcripts_map[session_chosen]['uploaded_file']['content']
                        st.session_state.uploaded_file_name = past_transcripts_map[session_chosen]['uploaded_file']['name']
                    else: 
                        st.session_state.uploaded_file_content = None 
                    self.log("info", f"Restarting using {session_chosen} transcript", st.session_state.to_dict())
                    st.rerun() 
        else: 
            st.markdown("No past sessions found")


    @st.dialog("Conversation Summary Document")
    def on_generate_summary_button(self) -> None: 
        """Function that runs when the generate summary button is hit 

        Creates a pop up dialog that shows a loading spinner and then displays a download button 
        """
        self.log("warning", "Generating summary document", st.session_state.to_dict())
        # start the loading spinner and show the time elapsed so far 
        with st.spinner("Generating document", show_time=True):
            try: 
                message = st.empty() 
                message.markdown("This process may take a few minutes. Please be patient and **do not press \"x\" or close this window**.")
                # ask the AI to generate a summary 
                client = AICompanyGateway.factory(
                    company=self.ai_company, 
                    api_key=os.environ.get(f"API_KEY_{self.ai_company.upper()}"), 
                    api_secret=os.environ.get(f"API_SECRET_{self.ai_company.upper()}"), 
                    region=os.environ.get(f"REGION_{self.ai_company.upper()}")
                ) 
                generate_message = [TextBlock(role='user', type='text', text=self.generate_summary_prompt)]
                summary = client.create_message(
                    model=self.ai_model, 
                    messages=self.get_messages_for_ai() + generate_message, 
                    model_params=self.ai_model_params,
                    system_message=self.writer_system_message 
                )

                # check if there are any closing messages in there 
                _, summary = self.check_closing_messages(summary) 
            except Exception as e: 
                st.session_state.reached_error = True 
                st.session_state.shown_error_message = "An error occurred generating the document. Please press the try again button and press the generate button again. If issues persist, you can report a bug using the menu item on the top right corner"
                self.log("error", f"Error asking AI to generate summary: {e}", st.session_state.to_dict())
                return 

            try: 
                # add the title to the top 
                summary = f"# Conversation Summary\n\nGenerated on {datetime.now(pytz.timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S UTC')} by {st.session_state.name}\n\n" + summary 

                # convert the markdown into word doc 
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp_file: 
                    temp_path = tmp_file.name 

                    pypandoc.convert_text(
                        source=summary,
                        to="docx",
                        format="md",
                        outputfile=temp_path 
                    )

                    # read in the bytes 
                    with open(temp_path, "rb") as f: 
                        doc_content = f.read() 

                    doc_bytes = io.BytesIO(doc_content) 

            except Exception as e: 
                st.session_state.reached_error = True 
                self.log("error", f"Error creating docx document: {e}", st.session_state.to_dict())
                st.session_state.shown_error_message = "An error occurred generating the document. Please press the try again button and press the generate button again. If issues persist, you can report a bug using the menu item on the top right corner"
                return 

        # save the document to dropbox 
        thread = threading.Thread(target=self.save_summary_to_dropbox, args=(st.session_state.to_dict(), doc_bytes)) 
        thread.start() 

        # display download button 
        message.markdown("To download the summary document, click download below")
        st.download_button(
            label='Download document', 
            help='Download conversation summary document', 
            data=doc_bytes,
            file_name=f"{st.session_state.username}_interview_summary.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            on_click="ignore", 
            icon=":material/download:"
        )


    def on_restart_button(self) -> None: 
        """Function that runs when the restart button is hit"""
        if st.session_state.show_confirm_restart: 
            # if the user clicked confirm then restart
            self.log("warning", "Restarting interview", st.session_state.to_dict())
            # reset some session state variables 
            for key in ['active_bot', 'transcript_history', 'start_time', 'session_id', 'log', 'log_stream', 'show_confirm_restart', 'found_closing_msg', 'uploaded_file_content', 'uploaded_file_name']: 
                if key in st.session_state:
                    del st.session_state[key]
            # restart the interview 
            st.session_state.interview_status = True 
            # reset reached error 
            st.session_state.reached_error = False 
            # reset to original restart button
            st.session_state.show_confirm_restart = False 
            # reset the ai processing flag 
            st.session_state.ai_processing = False 
        else: 
            # ask for confirmation 
            st.session_state.show_confirm_restart = True 
            st.session_state.show_confirm_restart_time = time.time() 


    def stream_initial_message(self) -> None: 
        """Streams the initial message from the AI"""
        self.log("warning", "Streaming initial message", st.session_state.to_dict())
        with self.chat_container: 
            with st.chat_message('assistant', avatar=self.interviewer_avatar): 
                # stream the message 
                streamlit_msg = st.empty() 
                for i in range(0, len(self.first_interviewer_message), len(self.first_interviewer_message) // 10): 
                    streamlit_msg.markdown(self.first_interviewer_message[:i] + "▌")
                    time.sleep(0.025)
                streamlit_msg.markdown(self.first_interviewer_message)
        self.log("info", "Finished streaming initial message", st.session_state.to_dict())
        self.save_msg_to_session('assistant', self.first_interviewer_message)


    def stream_message(self) -> None: 
        """Helper function to stream messages from the AI"""
        try: 
            # choose the system messsage based on the current active bot
            if st.session_state.active_bot == 'interviewer': 
                system_message = self.interviewer_system_message 
            elif st.session_state.active_bot == 'writer': 
                system_message = self.writer_system_message 
            else: 
                raise ValueError(f"Could not recognize active_bot value of '{st.session_state.active_bot}'")
            client = AICompanyGateway.factory(
                company=self.ai_company, 
                api_key=os.environ.get(f"API_KEY_{self.ai_company.upper()}"), 
                api_secret=os.environ.get(f"API_SECRET_{self.ai_company.upper()}"), 
                region=os.environ.get(f"REGION_{self.ai_company.upper()}")
            ) 
            stream = client.stream_message(
                model=self.ai_model, 
                messages=self.get_messages_for_ai(), 
                model_params=self.ai_model_params, 
                system_message=system_message
            )
            self.stream_message_to_interface(stream) 
        except Exception as e: 
            st.session_state.reached_error = True 
            self.log("error", f"Error streaming message from AI: {e}", st.session_state.to_dict())
            st.session_state.shown_error_message = "An error occurred generating a response from the AI. Please press the try again button. If issues persist, you can report a bug using the menu item on the top right corner"


    def stream_message_to_interface(self, stream:Generator) -> None: 
        """Helper function to stream AI messages to the interface 

        Args:
            stream (Generator): the generator that contains the messages being streamed 
        """ 
        self.log("warning", "Streaming message", st.session_state.to_dict())
        streaming_first_msg = not st.session_state.transcript_history 
        try: 
            with self.chat_container: 
                # stream messages within the chat container
                with st.chat_message("assistant", avatar=self.interviewer_avatar): 
                    # stream messages as the assistant 
                    streamlit_msg = st.empty() # streamlit object for where the message will go 
                    with st.spinner("*Thinking...*"): 
                        msg_so_far = next(stream) # record the message received so far
                        found_closing_msg, closing_msg = self.check_closing_messages(msg_so_far) 
                    streamlit_msg.markdown("▌")
                    for chunk in stream: 
                        # iterate through the stream and add the results 
                        if chunk: 
                            msg_so_far += chunk 
                        found_closing_msg, closing_msg = self.check_closing_messages(msg_so_far) 
                        if found_closing_msg: 
                            streamlit_msg.empty() 
                            break 
                        if len(msg_so_far) > 10: 
                            streamlit_msg.markdown(msg_so_far + "▌")

                    # after all the text has streamed
                    if found_closing_msg: 
                        # we found a closing message, so display closing message and shut down the conversation 
                        final_msg = closing_msg
                        st.session_state.interview_status = False 
                        st.session_state.found_closing_msg = True 
                    else: 
                        # did not find closing message, display the message sent 
                        final_msg = msg_so_far 

                    # display the message received 
                    streamlit_msg.markdown(final_msg)

                    self.log("warning", f"Got final message {final_msg}", st.session_state.to_dict())

                    # save the message to the session 
                    self.save_msg_to_session('assistant', final_msg)

                    # save the transcript to dropbox 
                    if not streaming_first_msg: 
                        thread = threading.Thread(target=self.save_transcript_to_dropbox, args=(st.session_state.to_dict(),)) 
                        thread.start() 
        except Exception as e: 
            st.session_state.reached_error = True 
            self.log("error", f"Error streaming message from AI: {e}", st.session_state.to_dict())
            st.session_state.shown_error_message = "An error occurred generating a response from the AI. Please press the try again button. If issues persist, you can report a bug using the menu item on the top right corner"


    def on_start_report_writer(self) -> None: 
        """Function that runs when the user wants to start the report writing bot"""
        self.log("warning", "Switching from interviewer bot to writer bot", st.session_state.to_dict())
        st.session_state.active_bot = 'writer' 
        st.session_state.ai_processing = True 


    @st.dialog("Return to Interviewer")
    def on_return_to_interviewer(self) -> None: 
        """Function that runs when the user wants to go from report writing bot to the interviewer"""
        # display a warning message that history will be removed 
        self.log("info", "Showing warning message for returning to interviewer", st.session_state.to_dict())
        warning_message = """
            Are you sure you want to return to the interviewer? This will:
            - Delete your current draft report and any edits made here
            - Take you back to continue discussing the paper with the interviewer bot in stage 1
        """
        st.markdown(warning_message)
        confirm_button = st.button(
            label='Confirm', 
            help='Click to return to the interviewer bot', 
            type='primary', 
            use_container_width=False 
        )
        if confirm_button: 
            self.log("warning", "Switching from writer bot to interviewer bot", st.session_state.to_dict())
            st.session_state.active_bot = 'interviewer' 
            st.session_state.ai_processing = False 
            # remove history because the report writing bot should always start from the end of the conversation 
            st.session_state.transcript_history = [x for x in st.session_state.transcript_history if x['active_bot'] == 'interviewer']
            st.rerun() 

    # --------------------------------------------------------------------------
    # utils 
    # --------------------------------------------------------------------------


    def log(self, level:str, message:str, session_state:Dict) -> None: 
        """Logs messages to dropbox 

        Args:
            level (str): the level to log at 
            message (str): the message to log 
            session_state (Dict): the current session state 
        """
        show_traceback = level.upper() == "ERROR"
        session_state["log_stream"].seek(0, 2) 

        level = getattr(logging, level.upper())
        session_state['log'].log(level, f"{session_state['session_id']}\t{message}", exc_info=show_traceback) 

        session_state['log_stream'].seek(0) 
        thread = threading.Thread(target=self.save_log_to_dropbox, args=(session_state, session_state['log_stream'])) 
        thread.start() 
        session_state['log_stream'].seek(0, 2) 


    def save_log_to_dropbox(self, session_state:Dict, log_stream:io.BytesIO) -> None: 
        """Saves logs to dropbox 

        Args:
            session_state (Dict): the current session state
            log_stream (io.BytesIO): the log stream with all the log messages 
        """
        save_fpath = Path(self.dropbox_path)/session_state['username']/f"log+{session_state['username']}+{session_state['start_time']}.log"

        content = log_stream.getvalue().encode("utf-8") 

        self.save_to_dropbox(io.BytesIO(content), str(save_fpath))


    def save_transcript_to_dropbox(self, session_state:Dict) -> None: 
        """Saves the transcript to dropbox 

        Usually runs in a separate thread to not interrupt the main chatbot experience 

        Args:
            session_state (Dict): the current session state dict to reference inside the thread 
        """
        # creates the path to save to 
        save_fpath = Path(self.dropbox_path)/session_state['username']/f"transcript+{session_state['username']}+{session_state['session_id']}.csv"

        self.log("warning", f"Saving transcript to dropbox to {save_fpath}", session_state)

        # save the transcript history 
        df = pd.DataFrame(session_state['transcript_history'])
        csv_content = io.BytesIO() 
        df.to_csv(csv_content, index=False, encoding='utf-8')
        csv_content.seek(0)
        self.save_to_dropbox(csv_content, str(save_fpath))

        self.log("info", "Finished saving transcript to dropbox", session_state)


    def save_summary_to_dropbox(self, session_state:Dict, doc_content:io.BytesIO) -> None: 
        """Saves the summary docx to dropbox 

        Usually runs in a separate thread to not interrupt the main chatbot experience 

        Args:
            session_state (Dict): the current session state dict to reference inside the thread 
            doc_content (io.BytesIO): the docx data to save 
        """
        # create the path to save to 
        save_fpath = Path(self.dropbox_path)/session_state['username']/f"summary_document+{session_state['username']}+{session_state['session_id']}+{int(datetime.now(pytz.timezone('UTC')).timestamp())}.docx"

        self.log("warning", f"Saving summary document to dropbox to {save_fpath}", session_state)

        # save the content to dropbox 
        self.save_to_dropbox(doc_content, str(save_fpath))

        self.log("info", "Finished saving summary document to dropbox", session_state)


    def save_file_upload_to_dropbox(self, session_state:Dict, file_name:str, doc_content:io.BytesIO) -> None: 
        """Saves the uploaded file to dropbox 

        Usually runs in a separate thread to not interrupt the main chatbot experience 

        Args:
            session_state (Dict): the current session state dict to reference inside the thread 
            file_name (str): the name of the file
            doc_content (io.BytesIO): the docx data to save 
        """
        # create the path to save to 
        save_fpath = Path(self.dropbox_path)/session_state['username']/f"uploaded_file+{session_state['username']}+{session_state['session_id']}+{int(datetime.now(pytz.timezone('UTC')).timestamp())}+{file_name}"

        self.log("warning", f"Saving uploaded file to dropbox to {save_fpath}", session_state)

        # save the content to dropbox 
        self.save_to_dropbox(doc_content, str(save_fpath))

        self.log("info", "Finished uploading file to dropbox", session_state)


    def save_to_dropbox(self, content:io.BytesIO, save_fpath:str) -> None: 
        """Saves some content to dropbox 

        Usually runs in a separate thread to not interrupt the main chatbot experience 

        Args:
            content (io.BytesIO): the content to save
            save_fpath (str): the path to save to 
        """
        tries = 3
        for x in range(1, tries+1): 
            try: 
                # create the dropbox client 
                dbx = dropbox.Dropbox(oauth2_refresh_token=os.environ.get('REFRESH_TOKEN_DROPBOX'), app_key=os.environ.get('APP_KEY_DROPBOX'), app_secret=os.environ.get('APP_SECRET_DROPBOX')) 

                # upload the file to dropbox and overwrite the existing file 
                dbx.files_upload(
                    content.read(), 
                    save_fpath, 
                    mode=dropbox.files.WriteMode("overwrite")
                ) 
                break 
            except: 
                time.sleep(2 ** x)


    def save_msg_to_session(self, role:str, content:str) -> None: 
        """Saves messages in the conversation to our session state variables 

        Args:
            role (str): the role of the message sender
            content (str): the message sent 
        """
        st.session_state.transcript_history.append({
            'time': datetime.now(pytz.timezone('UTC')).isoformat(timespec='milliseconds'), 
            'session_id': st.session_state.session_id, 
            'active_bot': st.session_state.active_bot, 
            'user': st.session_state.username, 
            'role': role, 
            'content': content 
        })


    def get_messages_for_ai(self) -> List[Dict[str, str]]: 
        """Gets the messages for the AI from the transcript history 

        Returns:
            List[Dict[str, str]]: a list of dicts with the messages for the AI
        """
        messages = [] 
        if st.session_state.active_bot == 'interviewer': 
            # messages for the interviewer bot 
            if st.session_state.uploaded_file_content: 
                # only giving the bot knowledge of the paper during the interview stage 
                if self.ai_company == 'anthropic': 
                    # PDF support is available for Anthropic native API 
                    messages.append(
                        DocumentBlock(
                            role='user', 
                            type='document', 
                            name='manuscript',
                            format="pdf", 
                            source={
                                'type': 'base64', 
                                'media_type': 'application/pdf', 
                                'data': base64.b64encode(st.session_state.uploaded_file_content).decode('utf-8')
                            },
                            accompanying_text=TextBlock(
                                role='user', 
                                type='text',
                                text='The evaluator has attached the following file to provide you with additional context. Please read the file thoroughly to help make the conversation more context aware. You do not need to acknowledge receipt of this document.'
                            )
                        )
                    )
                elif self.ai_company == 'bedrock': 
                    # PDF support is available for Bedrock Converse API 
                    messages.append(
                        DocumentBlock(
                            role='user', 
                            type='document', 
                            name='manuscript',
                            format="pdf", 
                            source={
                                "bytes": st.session_state.uploaded_file_content
                            },
                            accompanying_text=TextBlock(
                                role='user', 
                                type='text',
                                text='The evaluator has attached the following file to provide you with additional context. Please read the file thoroughly to help make the conversation more context aware. You do not need to acknowledge receipt of this document.'
                            )
                        )
                    )
            for row in st.session_state.transcript_history: 
                if row['active_bot'] == 'interviewer': 
                    # only include the interviewer messages when talking to the interviewer bot 
                    messages.append(TextBlock(role=row['role'], type='text', text=row['content']))
        elif st.session_state.active_bot == 'writer': 
            # messages for the report writer bot
            interviewer_transcript = "" 
            for row in st.session_state.transcript_history: 
                if row['active_bot'] == 'interviewer': 
                    # record the interviewer transcript for the initial message 
                    interviewer_transcript += f"*{row['role'].capitalize()}:* {row['content']}\n"
                elif row['active_bot'] == 'writer': 
                    # include the writer bot stage messages in the AI transcript 
                    messages.append(TextBlock(role=row['role'], type='text', text=row['content']))
            # insert the interviewer transcript as the initial message 
            messages.insert(
                0, 
                TextBlock(
                    role='user', 
                    type='text', 
                    text=f"My transcript with the AI was as follows:\n{interviewer_transcript}\nPlease output a first draft of the report for me that contains all the comments that I've bought up. Let's start the review process here."
                )
            )
        else: 
            raise ValueError(f"Could not recognize active_bot value of '{st.session_state.active_bot}'")
        return messages 


    def check_closing_messages(self, msg:str) -> Tuple[bool, str]: 
        """Check if a message contains any of the closing messages 

        Args:
            msg (str): the message to check 

        Returns:
            Tuple[bool, str]: a tuple that returns a bool of whether a closing message was found and a string of the final message 
        """
        for c, m in self.closing_messages.items(): 
            if c.lower() in msg.lower() or m.lower() in msg.lower(): 
                return True, m 
        return False, msg 


    def search_files_dropbox(self, fpath:str, regex_pattern:str) -> List[dropbox.files.FileMetadata]: 
        """Searches for files inside a dropbox folder that matches a particular regex pattern

        Args:
            fpath (str): the path to the dropbox folder to search in 
            regex_pattern (str): the regex pattern for the file name

        Returns:
            List[dropbox.files.FileMetadata]: a list of files in the folder 
        """
        dbx = dropbox.Dropbox(oauth2_refresh_token=os.environ.get('REFRESH_TOKEN_DROPBOX'), app_key=os.environ.get('APP_KEY_DROPBOX'), app_secret=os.environ.get('APP_SECRET_DROPBOX')) 
        pattern = re.compile(regex_pattern, re.IGNORECASE)
        found_files = [] 

        # do the initial search
        result = dbx.files_list_folder(fpath, limit=100) 
        for entry in result.entries: 
            if isinstance(entry, dropbox.files.FileMetadata) and pattern.match(entry.name):
                found_files.append(entry)

        # Handle pagination if there are many files
        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata) and pattern.match(entry.name):
                    found_files.append(entry)
        return found_files


    @st.cache_resource(show_spinner=False)
    def get_past_sessions(_self, current_session_id:str, start_time:int) -> Dict: 
        """Function that searches for past sessions in dropbox 

        Args:
            current_session_id (str): the current session ID so that we don't include it 
            start_time (int): the start time of the current session to help with accurate resource caching

        Returns:
            Dict: a dictionary that maps session name to a dictionary {'transcript': [contains transcript], 'uploaded_file': {'name': [name of file], 'content': [pdf content]}}
        """
        # connect to dropbox 
        dbx = dropbox.Dropbox(oauth2_refresh_token=os.environ.get('REFRESH_TOKEN_DROPBOX'), app_key=os.environ.get('APP_KEY_DROPBOX'), app_secret=os.environ.get('APP_SECRET_DROPBOX')) 

        # search for transcript files 
        transcripts_fpath = Path(_self.dropbox_path)/st.session_state['username']
        past_transcripts = _self.search_files_dropbox(str(transcripts_fpath), '^transcript.*\.csv$')
        # sort by oldest first 
        past_transcripts.sort(key=lambda x: x.server_modified)

        past_transcripts_map = {}
        session_count = 1
        for transcript in past_transcripts: # sort by oldest first 
            # get the transcript 
            fname = transcript.name 
            past_transcript_session_id = fname.replace('.csv', '').split('+')[-1] 
            if past_transcript_session_id == current_session_id: 
                # skip current session 
                continue 
            _self.log("warning", f"Downloading transcript {fname}", st.session_state.to_dict())
            _, response = dbx.files_download(str(transcripts_fpath/fname))
            content = response.content.decode('utf-8') 
            _self.log("info", f"Finished downloading transcript {fname}", st.session_state.to_dict())

            # read the transcript and save it 
            _self.log("warning", f"Reading transcript {fname}", st.session_state.to_dict())
            csv_reader = csv.DictReader(io.StringIO(content))
            transcript_data = [row for row in csv_reader] 
            first_time = datetime.fromisoformat(transcript_data[0]['time']).astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S EST')
            past_transcripts_map[f"Session {session_count} from {first_time}"] = {'transcript': transcript_data} 
            _self.log("info", f"Finished reading transcript {fname}", st.session_state.to_dict())

            # find uploaded file 
            past_uploaded_file = _self.search_files_dropbox(str(transcripts_fpath), f'^uploaded_file\+{re.escape(st.session_state.username)}\+{re.escape(past_transcript_session_id)}\+.*\.pdf$')
            if past_uploaded_file: 
                # if there was an uploaded file, get the last uploaded file 
                last_uploaded_file = max(
                    [x.name for x in past_uploaded_file], 
                    key=lambda x: int(x.replace('.pdf', '').split('+')[-2]) # max by the timestamp 
                ) 
                # download file from dropbox 
                _self.log("warning", f"Downloading file {last_uploaded_file}", st.session_state.to_dict())
                _, response = dbx.files_download(str(transcripts_fpath/last_uploaded_file))
                _self.log("info", f"Finished downloading file {last_uploaded_file}", st.session_state.to_dict())

                # read the contents of the file 
                _self.log("warning", f"Reading file {last_uploaded_file}", st.session_state.to_dict())
                content = response.content
                # save it 
                past_transcripts_map[f"Session {session_count} from {first_time}"]['uploaded_file'] = {
                    'name': last_uploaded_file.split('+')[-1], 
                    'content': content 
                }
                _self.log("info", f"Finished reading file {last_uploaded_file}", st.session_state.to_dict())
            else: 
                # no uploaded file so set to None 
                past_transcripts_map[f"Session {session_count} from {first_time}"]['uploaded_file'] = None 
            session_count += 1
        return past_transcripts_map 
