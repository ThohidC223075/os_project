# app.py
import streamlit as st
from scheduler import fcfs
import pandas as pd

st.set_page_config(page_title="CPU Scheduler", layout="centered")

st.title("🧠 CPU Scheduling Visualizer - FCFS")

st.markdown("প্রসেস এর তথ্য নিচে ইনপুট দাও:")

n = st.number_input("প্রসেস সংখ্যা", min_value=1, max_value=10, step=1)

process_data = []

for i in range(n):
    st.markdown(f"### প্রসেস {i+1}")
    pid = f"P{i+1}"
    arrival_time = st.number_input(f"{pid} এর Arrival Time", min_value=0, key=f"arrival{i}")
    burst_time = st.number_input(f"{pid} এর Burst Time", min_value=1, key=f"burst{i}")
    process_data.append({"pid": pid, "arrival_time": arrival_time, "burst_time": burst_time})

if st.button("⚙️ FCFS চালাও"):
    result = fcfs(process_data)

    df = pd.DataFrame(result)
    st.subheader("📊 প্রসেস সিডিউল টেবিল")
    st.dataframe(df)

    avg_waiting_time = sum(p['Waiting Time'] for p in result) / len(result)
    avg_turnaround_time = sum(p['Turnaround Time'] for p in result) / len(result)

    st.markdown(f"### ⏱️ গড় অপেক্ষার সময়: `{avg_waiting_time:.2f}`")
    st.markdown(f"### 🔁 গড় টার্ন-অ্যারাউন্ড সময়: `{avg_turnaround_time:.2f}`")

    st.subheader("🟦 গ্যান্ট চার্ট")
    chart = ""
    for p in result:
        chart += f"| {p['PID']} "
    chart += "|\n"
    for p in result:
        chart += f"{p['Start Time']}    "
    chart += f"{result[-1]['Completion Time']}"

    st.code(chart)
