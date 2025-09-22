import streamlit as st
from py.daily_chores import model
import pandas as pd


# Define chores, durations, and days needed
chores_enter = st.text_input(
    "Enter Chore Needed"
)
if chores_enter:
    durations_enter = st.number_input(
        "Enter Chore Duration (minutes)", step=1
    )
    if durations_enter:
        days_needed_enter = st.number_input(
            "Enter Days Needed per Week", step=1, min_value=1, max_value=7
        )
add = st.button("Add Chores")
reset = st.button("Reset Chores")
if add:
    st.session_state.chores.append(chores_enter)
    st.session_state.durations[chores_enter] = int(durations_enter)
    st.session_state.days_needed[chores_enter] = int(days_needed_enter)
    st.success(f"Added chore: {chores_enter}")
    chore_frame = pd.DataFrame({
        "Chore": st.session_state.chores,
        "Duration (minutes)": [st.session_state.durations[c] for c in st.session_state.chores],
        "Days Needed": [st.session_state.days_needed[c] for c in st.session_state.chores]
    })
    st.write("### Current Chores")
    st.dataframe(chore_frame)

max_minutes_per_day = st.number_input(
    "Max Minutes Per Day", min_value=1, value=120
)
if reset:
    st.session_state.chores = []
    st.session_state.durations = {}
    st.session_state.days_needed = {}
    st.success("Chores reset")

if st.button("Generate Schedule"):
    builder = model.BuildModel(
        st.session_state.chores, 
        st.session_state.durations, 
        st.session_state.days_needed, 
        max_minutes_per_day
    )


    builder.create_model()
    builder.add_constraints()
    builder.set_objective()
    builder.solve()

    chore_model = builder.model

    # ------------------------------------------------------------------------
    # Output the schedule as a DataFrame with total minutes per day

    schedule_data = []
    day_minutes = {}

    for d in chore_model.DAYS:
        total_minutes = 0
        for c in chore_model.CHORES:
            if chore_model.x[c, d].value == 1:
                schedule_data.append({"Day": d, "Chore": c, "Minutes": builder.durations[c]})
                total_minutes += builder.durations[c]
        if total_minutes > 0:
            day_minutes[d] = total_minutes

    if schedule_data:
        df_schedule = pd.DataFrame(schedule_data)
        st.write("### Schedule")
        st.dataframe(df_schedule)

        # Show total minutes per day
        df_totals = pd.DataFrame([
            {"Day": d, "Total Minutes": m} for d, m in day_minutes.items()
        ])
        st.write("### Total Minutes Per Day")
        st.dataframe(df_totals)
    else:
        st.write("No schedule generated.")