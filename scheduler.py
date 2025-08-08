# scheduler.py

def fcfs(processes):
    processes.sort(key=lambda x: x['arrival_time'])  # আগমনের সময় অনুযায়ী sort
    time = 0
    schedule = []

    for p in processes:
        start_time = max(time, p['arrival_time'])  # CPU ফাঁকা না থাকলে অপেক্ষা করবে
        completion_time = start_time + p['burst_time']
        waiting_time = start_time - p['arrival_time']
        turnaround_time = completion_time - p['arrival_time']

        schedule.append({
            'PID': p['pid'],
            'Start Time': start_time,
            'Completion Time': completion_time,
            'Waiting Time': waiting_time,
            'Turnaround Time': turnaround_time
        })

        time = completion_time

    return schedule
