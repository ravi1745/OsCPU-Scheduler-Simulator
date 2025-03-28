import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Process:
    def __init__(self, pid, at, bt, priority=0):
        self.pid = pid
        self.at = at  
        self.bt = bt  
        self.priority = priority  
        self.wt = 0   
        self.tat = 0  

class CPUSchedulerSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent CPU Scheduler Simulator")
        self.root.geometry("800x600")
        
        self.processes = []
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Number of Processes:").grid(row=0, column=0, padx=5, pady=5)
        self.num_procs = tk.Entry(self.root)
        self.num_procs.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Time Quantum (for RR):").grid(row=1, column=0, padx=5, pady=5)
        self.time_quantum = tk.Entry(self.root)
        self.time_quantum.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Enter Processes", command=self.input_processes).grid(row=2, column=0, columnspan=2, pady=10)

        
        tk.Label(self.root, text="Select Algorithm:").grid(row=3, column=0, padx=5, pady=5)
        self.algo_var = tk.StringVar(value="FCFS")
        algorithms = [("FCFS", "FCFS"), ("SJF", "SJF"), ("Round Robin", "RR"), ("Priority", "Priority")]
        for i, (text, value) in enumerate(algorithms):
            tk.Radiobutton(self.root, text=text, variable=self.algo_var, value=value).grid(row=3, column=i+1, padx=5)

        tk.Button(self.root, text="Run Simulation", command=self.run_simulation).grid(row=4, column=0, columnspan=5, pady=10)

    def input_processes(self):
        try:
            n = int(self.num_procs.get())
            if n <= 0:
                raise ValueError("Number of processes must be positive!")
            
            self.processes.clear()
            
            input_window = tk.Toplevel(self.root)
            input_window.title("Enter Process Details")
            input_window.geometry("400x300")

            tk.Label(input_window, text="PID | Arrival Time | Burst Time | Priority").pack()
            entries = []
            for i in range(n):
                frame = tk.Frame(input_window)
                frame.pack(pady=5)
                pid = tk.Entry(frame, width=5)
                at = tk.Entry(frame, width=10)
                bt = tk.Entry(frame, width=10)
                pri = tk.Entry(frame, width=10)
                pid.insert(0, f"P{i+1}")
                pid.pack(side=tk.LEFT, padx=5)
                at.pack(side=tk.LEFT, padx=5)
                bt.pack(side=tk.LEFT, padx=5)
                pri.pack(side=tk.LEFT, padx=5)
                entries.append((pid, at, bt, pri))

            def save_processes():
                try:
                    for pid_e, at_e, bt_e, pri_e in entries:
                        pid = pid_e.get()
                        at = float(at_e.get())
                        bt = float(bt_e.get())
                        pri = float(pri_e.get() or 0)  
                        if at < 0 or bt <= 0:
                            raise ValueError("Invalid arrival or burst time!")
                        self.processes.append(Process(pid, at, bt, pri))
                    input_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid input: {e}")

            tk.Button(input_window, text="Save", command=save_processes).pack(pady=10)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid number of processes: {e}")

    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes entered!")
            return

        algo = self.algo_var.get()
        if algo == "RR":
            try:
                quantum = float(self.time_quantum.get())
                if quantum <= 0:
                    raise ValueError("Time quantum must be positive!")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid time quantum: {e}")
                return
        else:
            quantum = None

        if algo == "FCFS":
            gantt, avg_wt, avg_tat = self.fcfs()
        elif algo == "SJF":
            gantt, avg_wt, avg_tat = self.sjf()
        elif algo == "RR":
            gantt, avg_wt, avg_tat = self.round_robin(quantum)
        elif algo == "Priority":
            gantt, avg_wt, avg_tat = self.priority()

        self.display_results(gantt, avg_wt, avg_tat)

    def fcfs(self):
        processes = sorted(self.processes, key=lambda x: x.at)
        current_time = 0
        gantt = []
        for p in processes:
            if current_time < p.at:
                current_time = p.at
            gantt.append((p.pid, current_time, current_time + p.bt))
            p.wt = current_time - p.at
            p.tat = p.wt + p.bt
            current_time += p.bt
        avg_wt = sum(p.wt for p in processes) / len(processes)
        avg_tat = sum(p.tat for p in processes) / len(processes)
        return gantt, avg_wt, avg_tat

    def sjf(self):
        processes = sorted(self.processes, key=lambda x: x.at)
        current_time = 0
        gantt = []
        completed = []
        while processes or completed:
            available = [p for p in processes if p.at <= current_time]
            if not available and processes:
                current_time = processes[0].at
                continue
            shortest = min(available, key=lambda x: x.bt)
            processes.remove(shortest)
            gantt.append((shortest.pid, current_time, current_time + shortest.bt))
            shortest.wt = current_time - shortest.at
            shortest.tat = shortest.wt + shortest.bt
            current_time += shortest.bt
            completed.append(shortest)
        avg_wt = sum(p.wt for p in completed) / len(completed)
        avg_tat = sum(p.tat for p in completed) / len(completed)
        return gantt, avg_wt, avg_tat

    def round_robin(self, quantum):
        processes = sorted(self.processes, key=lambda x: x.at)
        queue = []
        current_time = 0
        gantt = []
        remaining_bt = {p.pid: p.bt for p in processes}
        while processes or queue:
            while processes and processes[0].at <= current_time:
                queue.append(processes.pop(0))
            if not queue:
                current_time = processes[0].at if processes else current_time + 1
                continue
            p = queue.pop(0)
            exec_time = min(quantum, remaining_bt[p.pid])
            gantt.append((p.pid, current_time, current_time + exec_time))
            current_time += exec_time
            remaining_bt[p.pid] -= exec_time
            if remaining_bt[p.pid] > 0:
                queue.append(p)
            else:
                p.tat = current_time - p.at
                p.wt = p.tat - p.bt
        avg_wt = sum(p.wt for p in self.processes) / len(self.processes)
        avg_tat = sum(p.tat for p in self.processes) / len(self.processes)
        return gantt, avg_wt, avg_tat

    def priority(self):
        processes = sorted(self.processes, key=lambda x: x.at)
        current_time = 0
        gantt = []
        completed = []
        while processes or completed:
            available = [p for p in processes if p.at <= current_time]
            if not available and processes:
                current_time = processes[0].at
                continue
            highest = min(available, key=lambda x: x.priority)  
            processes.remove(highest)
            gantt.append((highest.pid, current_time, current_time + highest.bt))
            highest.wt = current_time - highest.at
            highest.tat = highest.wt + highest.bt
            current_time += highest.bt
            completed.append(highest)
        avg_wt = sum(p.wt for p in completed) / len(completed)
        avg_tat = sum(p.tat for p in completed) / len(completed)
        return gantt, avg_wt, avg_tat

    def display_results(self, gantt, avg_wt, avg_tat):
        
        fig, ax = plt.subplots(figsize=(8, 2))
        for pid, start, end in gantt:
            ax.barh(0, end - start, left=start, height=0.5, align='center')
            ax.text((start + end) / 2, 0, pid, ha='center', va='center', color='white')
        ax.set_ylim(-1, 1)
        ax.set_xlabel("Time")
        ax.set_yticks([])
        ax.set_title("Gantt Chart")

        result_window = tk.Toplevel(self.root)
        result_window.title("Simulation Results")
        canvas = FigureCanvasTkAgg(fig, master=result_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        tk.Label(result_window, text=f"Average Waiting Time: {avg_wt:.2f}").pack()
        tk.Label(result_window, text=f"Average Turnaround Time: {avg_tat:.2f}").pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerSimulator(root)
    root.mainloop()
