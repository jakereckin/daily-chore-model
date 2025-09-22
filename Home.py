import streamlit as st
from py.daily_chores import model


st.title("Daily Chores Scheduler")
st.session_state.chores = []
st.session_state.durations = {}
st.session_state.days_needed = {}