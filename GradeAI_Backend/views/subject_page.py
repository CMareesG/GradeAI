
# import streamlit as st
# import os
# st.markdown("""
# <style>
# button {
#     height: 120px !important;
#     font-size: 18px !important;
#     border-radius: 12px !important;
# }
# </style>
# """, unsafe_allow_html=True)
# DATA_PATH = "data"

# def show_subject_page():

#     st.markdown("## Select Subject")
#     st.write("Choose a subject to evaluate answer sheets")

#     subjects = os.listdir(DATA_PATH)

#     cols = st.columns(3)

#     for i, subject in enumerate(subjects):
#         with cols[i % 3]:

#             if st.button(subject.upper(), use_container_width=True):
#                 st.session_state.selected_subject = subject
#                 st.session_state.page = "evaluation"
#                 st.rerun()