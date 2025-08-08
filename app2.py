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

# Preemptive SJF (SRTF)
def sjf_preemptive(processes):
    n = len(processes)
    remaining_bt = [p['burst_time'] for p in processes]
    completed = 0
    current_time = 0
    start_time = [-1] * n
    is_completed = [False] * n
    schedule = []

    while completed != n:
        idx = -1
        min_bt = float('inf')
        for i in range(n):
            if (processes[i]['arrival_time'] <= current_time and
                not is_completed[i] and
                remaining_bt[i] < min_bt and remaining_bt[i] > 0):
                min_bt = remaining_bt[i]
                idx = i

        if idx == -1:
            current_time += 1
            continue

        if start_time[idx] == -1:
            start_time[idx] = current_time

        remaining_bt[idx] -= 1
        schedule.append({
            'File Name': processes[idx]['pid'],
            'Start Time': current_time,
            'Execution Time': 1,
            'End Time': current_time + 1
        })
        current_time += 1

        if remaining_bt[idx] == 0:
            is_completed[idx] = True
            completed += 1
            processes[idx]['start_time'] = start_time[idx]
            processes[idx]['completion_time'] = current_time
            processes[idx]['turnaround_time'] = current_time - processes[idx]['arrival_time']
            processes[idx]['waiting_time'] = processes[idx]['turnaround_time'] - processes[idx]['burst_time']

    # Build final summary output
    final_schedule = []
    for p in processes:
        final_schedule.append({
            'File Name': p['pid'],
            'Start Time': p['start_time'],
            'Completion Time': p['completion_time'],
            'Waiting Time': p['waiting_time'],
            'Turnaround Time': p['turnaround_time']
        })

    return final_schedule, schedule

# Preemptive Priority Scheduling
def priority_preemptive(processes):
    n = len(processes)
    remaining_bt = [p['burst_time'] for p in processes]
    completed = 0
    current_time = 0
    start_time = [-1] * n
    is_completed = [False] * n
    schedule = []

    while completed != n:
        idx = -1
        highest_priority = float('inf')
        for i in range(n):
            if (processes[i]['arrival_time'] <= current_time and
                not is_completed[i] and
                processes[i].get('priority', 0) < highest_priority):
                highest_priority = processes[i].get('priority', 0)
                idx = i

        if idx == -1:
            current_time += 1
            continue

        if start_time[idx] == -1:
            start_time[idx] = current_time

        remaining_bt[idx] -= 1
        schedule.append({
            'File Name': processes[idx]['pid'],
            'Start Time': current_time,
            'Execution Time': 1,
            'End Time': current_time + 1
        })
        current_time += 1

        if remaining_bt[idx] == 0:
            is_completed[idx] = True
            completed += 1
            processes[idx]['start_time'] = start_time[idx]
            processes[idx]['completion_time'] = current_time
            processes[idx]['turnaround_time'] = current_time - processes[idx]['arrival_time']
            processes[idx]['waiting_time'] = processes[idx]['turnaround_time'] - processes[idx]['burst_time']

    final_schedule = []
    for p in processes:
        final_schedule.append({
            'File Name': p['pid'],
            'Start Time': p['start_time'],
            'Completion Time': p['completion_time'],
            'Waiting Time': p['waiting_time'],
            'Turnaround Time': p['turnaround_time']
        })

    return final_schedule, schedule

# ========== File Handling & Burst Time ==========

def estimate_burst_from_file(path):
    size_in_kb = os.path.getsize(path) / 1024
    return max(1, round(size_in_kb))

import random  # 🔁 Random এর জন্য

def load_files(folder="files"):
    files = sorted(os.listdir(folder))
    processes = []
    for fname in files:
        path = os.path.join(folder, fname)
        
        # Random values
        arrival_time = random.randint(0, 10)
        burst = random.randint(1, 10)
        priority = random.randint(1, 10)

        processes.append({
            'pid': fname,
            'arrival_time': arrival_time,
            'burst_time': burst,
            'priority': priority
        })
    return processes

# ========== Streamlit UI Starts ==========

st.set_page_config(page_title="CPU Scheduling Visualizer", layout="centered")
st.title("💻 CPU Scheduling Visualizer (FCFS, SJF, Round Robin, Preemptive SJF & Priority)")

folder = st.text_input("📁 ফোল্ডারের পথ দিন (ডিফল্ট: files)", "files")

if not os.path.exists(folder):
    st.error(f"📁 `{folder}` ফোল্ডার পাওয়া যায়নি। অনুগ্রহ করে `{folder}` ফোল্ডারে ফাইল রাখুন।")
    st.stop()

processes = load_files(folder)
st.subheader("📂 ইনপুট ফাইল ডেটা")
st.dataframe(pd.DataFrame(processes))

algo = st.selectbox("📌 একটি CPU Scheduling অ্যালগরিদম বেছে নিন:", [
    "FCFS", "SJF (Non-Preemptive)", "Round Robin", "SJF (Preemptive)", "Priority (Preemptive)"
])

if algo == "Round Robin":
    quantum = st.number_input("🕓 টাইম কোয়ান্টাম দিন (ডিফল্ট 4):", min_value=1, value=4)

if st.button("🚀 চালান"):
    if algo == "FCFS":
        result = fcfs(processes)
        gantt = ""
        for p in result:
            gantt += f"| {p['File Name']} "
        gantt += "|\n"
        for p in result:
            gantt += f"{p['Start Time']}    "
        gantt += f"{result[-1]['Completion Time']}"
        st.subheader("📊 Scheduling Result Table")
        st.dataframe(pd.DataFrame(result))
        st.markdown(f"### ⏱️ গড় অপেক্ষার সময়: `{sum(p['Waiting Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.markdown(f"### 🔁 গড় টার্ন-অ্যারাউন্ড সময়: `{sum(p['Turnaround Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.subheader("🟦 Gantt Chart")
        st.code(gantt)

    elif algo == "SJF (Non-Preemptive)":
        result = sjf(processes)
        gantt = ""
        for p in result:
            gantt += f"| {p['File Name']} "
        gantt += "|\n"
        for p in result:
            gantt += f"{p['Start Time']}    "
        gantt += f"{result[-1]['Completion Time']}"
        st.subheader("📊 Scheduling Result Table")
        st.dataframe(pd.DataFrame(result))
        st.markdown(f"### ⏱️ গড় অপেক্ষার সময়: `{sum(p['Waiting Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.markdown(f"### 🔁 গড় টার্ন-অ্যারাউন্ড সময়: `{sum(p['Turnaround Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.subheader("🟦 Gantt Chart")
        st.code(gantt)

    elif algo == "Round Robin":
        result, rr_log = round_robin(processes, quantum=quantum)
        gantt = ""
        for p in rr_log:
            gantt += f"| {p['File Name']} "
        gantt += "|\n"
        for p in rr_log:
            gantt += f"{p['Start Time']}    "
        gantt += f"{rr_log[-1]['End Time']}"
        st.subheader("📊 Scheduling Result Table")
        st.dataframe(pd.DataFrame(result))
        st.markdown(f"### ⏱️ গড় অপেক্ষার সময়: `{sum(p['Waiting Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.markdown(f"### 🔁 গড় টার্ন-অ্যারাউন্ড সময়: `{sum(p['Turnaround Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.subheader("🟦 Gantt Chart")
        st.code(gantt)

    elif algo == "SJF (Preemptive)":
        result, preemptive_log = sjf_preemptive(processes)
        gantt = ""
        for p in preemptive_log:
            gantt += f"| {p['File Name']} "
        gantt += "|\n"
        for p in preemptive_log:
            gantt += f"{p['Start Time']}    "
        gantt += f"{preemptive_log[-1]['End Time']}"
        st.subheader("📊 Scheduling Result Table")
        st.dataframe(pd.DataFrame(result))
        st.markdown(f"### ⏱️ গড় অপেক্ষার সময়: `{sum(p['Waiting Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.markdown(f"### 🔁 গড় টার্ন-অ্যারাউন্ড সময়: `{sum(p['Turnaround Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.subheader("🟦 Gantt Chart")
        st.code(gantt)

    elif algo == "Priority (Preemptive)":
        result, preemptive_log = priority_preemptive(processes)
        gantt = ""
        for p in preemptive_log:
            gantt += f"| {p['File Name']} "
        gantt += "|\n"
        for p in preemptive_log:
            gantt += f"{p['Start Time']}    "
        gantt += f"{preemptive_log[-1]['End Time']}"
        st.subheader("📊 Scheduling Result Table")
        st.dataframe(pd.DataFrame(result))
        st.markdown(f"### ⏱️ গড় অপেক্ষার সময়: `{sum(p['Waiting Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.markdown(f"### 🔁 গড় টার্ন-অ্যারাউন্ড সময়: `{sum(p['Turnaround Time'] for p in result) / len(result):.2f}` সেকেন্ড")
        st.subheader("🟦 Gantt Chart")
        st.code(gantt)
