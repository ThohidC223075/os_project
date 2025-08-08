import streamlit as st
import os
import pandas as pd

# ======== Scheduling Algorithms ==========

# FCFS Algorithm
def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    time = 0
    schedule = []

    for p in processes:
        start_time = max(time, p['arrival_time'])
        completion_time = start_time + p['burst_time']
        waiting_time = start_time - p['arrival_time']
        turnaround_time = completion_time - p['arrival_time']

        schedule.append({
            'File Name': p['pid'],
            'Start Time': start_time,
            'Completion Time': completion_time,
            'Waiting Time': waiting_time,
            'Turnaround Time': turnaround_time
        })

        time = completion_time
    return schedule

# SJF (Non-Preemptive)
def sjf(processes):
    processes.sort(key=lambda x: x['arrival_time'])
    time = 0
    schedule = []
    completed = []

    while len(completed) < len(processes):
        ready_queue = [p for p in processes if p['arrival_time'] <= time and p not in completed]
        if not ready_queue:
            time += 1
            continue
        next_proc = min(ready_queue, key=lambda x: x['burst_time'])
        start_time = time
        completion_time = start_time + next_proc['burst_time']
        waiting_time = start_time - next_proc['arrival_time']
        turnaround_time = completion_time - next_proc['arrival_time']

        schedule.append({
            'File Name': next_proc['pid'],
            'Start Time': start_time,
            'Completion Time': completion_time,
            'Waiting Time': waiting_time,
            'Turnaround Time': turnaround_time
        })
        time = completion_time
        completed.append(next_proc)
    return schedule

# Round Robin
def round_robin(processes, quantum=4):
    queue = processes.copy()
    time = 0
    schedule = []
    remaining_bt = {p['pid']: p['burst_time'] for p in queue}
    arrived = []
    completed = []

    while queue or arrived:
        arrived += [p for p in queue if p['arrival_time'] <= time]
        queue = [p for p in queue if p['arrival_time'] > time]

        if not arrived:
            time += 1
            continue

        current = arrived.pop(0)
        pid = current['pid']
        exec_time = min(quantum, remaining_bt[pid])
        start_time = time
        time += exec_time
        remaining_bt[pid] -= exec_time

        schedule.append({
            'File Name': pid,
            'Start Time': start_time,
            'Execution Time': exec_time,
            'End Time': time
        })

        if remaining_bt[pid] > 0:
            current['arrival_time'] = time
            queue.append(current)
        else:
            completed.append(pid)

    # From schedule => build final output
    results = {}
    for entry in schedule:
        pid = entry['File Name']
        if pid not in results:
            results[pid] = {
                'File Name': pid,
                'Start Time': entry['Start Time'],
                'Completion Time': entry['End Time'],
                'Waiting Time': 0,
                'Turnaround Time': 0
            }
        results[pid]['Completion Time'] = entry['End Time']

    for p in processes:
        pid = p['pid']
        turnaround = results[pid]['Completion Time'] - p['arrival_time']
        waiting = turnaround - p['burst_time']
        results[pid]['Turnaround Time'] = turnaround
        results[pid]['Waiting Time'] = waiting

    return list(results.values()), schedule

# ========== File Handling & Burst Time ==========

def estimate_burst_from_file(path):
    size_in_kb = os.path.getsize(path) / 1024
    return max(1, round(size_in_kb))

def load_files(folder="files"):
    files = sorted(os.listdir(folder))
    processes = []
    for i, fname in enumerate(files):
        path = os.path.join(folder, fname)
        burst = estimate_burst_from_file(path)
        processes.append({
            'pid': fname,
            'arrival_time': i,
            'burst_time': burst
        })
    return processes

# ========== Streamlit UI Starts ==========

st.set_page_config(page_title="CPU Scheduling Visualizer", layout="centered")
st.title("💻 CPU Scheduling Visualizer (FCFS, SJF, Round Robin)")

folder = "files"
if not os.path.exists(folder):
    st.error(f"📁 `{folder}` ফোল্ডার খুঁজে পাওয়া যায়নি। অনুগ্রহ করে ফোল্ডারে কিছু ফাইল রাখুন।")
    st.stop()

processes = load_files(folder)
st.subheader("📂 ইনপুট ফাইল ডেটা")
st.dataframe(pd.DataFrame(processes))

algo = st.selectbox("📌 একটি CPU Scheduling অ্যালগরিদম বেছে নিন:", ["FCFS", "SJF", "Round Robin"])

if algo == "Round Robin":
    quantum = st.number_input("🕓 টাইম কোয়ান্টাম দিন (default 4):", min_value=1, value=4)

if st.button("🚀 Run Scheduling"):
    if algo == "FCFS":
        result = fcfs(processes)
    elif algo == "SJF":
        result = sjf(processes)
    elif algo == "Round Robin":
        result, rr_log = round_robin(processes, quantum=quantum)

    st.subheader("📊 Scheduling Result Table")
    st.dataframe(pd.DataFrame(result))

    avg_waiting = sum(p['Waiting Time'] for p in result) / len(result)
    avg_turnaround = sum(p['Turnaround Time'] for p in result) / len(result)

    st.markdown(f"### ⏱️ গড় অপেক্ষার সময়: `{avg_waiting:.2f}` সেকেন্ড")
    st.markdown(f"### 🔁 গড় টার্ন-অ্যারাউন্ড সময়: `{avg_turnaround:.2f}` সেকেন্ড")

    st.subheader("🟦 Gantt Chart")
    gantt = ""
    if algo != "Round Robin":
        for p in result:
            gantt += f"| {p['File Name']} "
        gantt += "|\n"
        for p in result:
            gantt += f"{p['Start Time']}    "
        gantt += f"{result[-1]['Completion Time']}"
    else:
        for p in rr_log:
            gantt += f"| {p['File Name']} "
        gantt += "|\n"
        for p in rr_log:
            gantt += f"{p['Start Time']}    "
        gantt += f"{rr_log[-1]['End Time']}"
    st.code(gantt)
