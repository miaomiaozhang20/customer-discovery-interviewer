import os

from libs.streamlit_gui import StreamlitGUI
from libs.streamlit_conf import read_conf

if __name__ == "__main__":
    development_state = os.environ.get('DEVELOPMENT_STATE')
    if os.environ.get("IS_PULL_REQUEST") == 'true':
        development_state = 'render-development'
    conf = read_conf('./customer-discovery-interviewer.conf', development_state)
    app = StreamlitGUI(conf)
    app.run()
