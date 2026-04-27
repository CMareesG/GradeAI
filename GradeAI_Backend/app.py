import streamlit as st

from views.evaluation_page import show_subject_page
from views.evaluation_page import show_evaluation_page

st.set_page_config(page_title="Evaluation System", layout="wide")

# Session state init
if "page" not in st.session_state:
    st.session_state.page = "subjects"

# Routing
if st.session_state.page == "subjects":
    show_subject_page()

elif st.session_state.page == "evaluation":
    show_evaluation_page()