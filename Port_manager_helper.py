import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
import random

class Worker:
    def __init__(self, worker_id, full_name, field, activity, imo_number=0):
        self.worker_id = worker_id
        self.__full_name = full_name  # Making full_name private
        self.field = field
        self.activity = activity
        self.imo_number = imo_number

    def assign_task(self):
        return (f"ID: {self.worker_id}, {self.get_full_name()} "
            "is performing assigned task.")

    # Getter method to access private full_name attribute
    def get_full_name(self):
        return self.__full_name

class CraneOperator(Worker):
    def assign_task(self):
        return (f"ID: {self.worker_id}, {self.get_full_name()} "
            "has been assigned to his crane post.")

class TrailerDriver(Worker):
    def assign_task(self):
        return (f"ID: {self.worker_id}, {self.get_full_name()} "
            "is getting his trailer ready.")

class TowingBoatCaptain(Worker):
    def assign_task(self):
        return (f"ID: {self.worker_id}, {self.get_full_name()} "
            "is getting his towing boat ready.")

class GuideBoatCaptain(Worker):
    def assign_task(self):
        return (f"ID: {self.worker_id}, {self.get_full_name()} "
            "is analyzing towing route.")

class WorkerFactory:
    @staticmethod
    def create_worker(worker_id, full_name, field, activity, imo_number=None):
        if field == 'Crane operator':
            return CraneOperator(worker_id, full_name, field, activity,
                                 imo_number)
        elif field == 'Trailer driver':
            return TrailerDriver(worker_id, full_name, field, activity,
                                 imo_number)
        elif field == 'Towing boat captain':
            return TowingBoatCaptain(worker_id, full_name, field, activity,
                                    imo_number)
        elif field == 'Guiding boat captain':
            return GuideBoatCaptain(worker_id, full_name, field, activity,
                                    imo_number)
        else:
            return Worker(worker_id, full_name, field, activity, imo_number)

class Port:
    def __init__(self, space):
        self.space = space

port = Port(100)

def create_workers_from_csv(csv_file):
    workers = []
    df = pd.read_csv(csv_file, delimiter=';', dtype={'IMO Number': str})
    df = df.dropna(subset=['IMO Number'])
    df['IMO Number'] = df['IMO Number'].astype(float).astype(int)
    for index, row in df.iterrows():
        worker = WorkerFactory.create_worker(row['ID'], row['Full Name'],
                                             row['Field'], row['Activity'],
                                             row['IMO Number'])
        workers.append(worker)
    return workers

def select_random_workers(workers, imo_number):
    available_workers = [worker for worker in workers
        if worker.activity == "Free"]
    if len(available_workers) < 6:
        messagebox.showerror("Error", "Not enough available workers.")
        return []
    crane_operators = [worker for worker in available_workers
        if worker.field == 'Crane operator']
    trailer_drivers = [worker for worker in available_workers
        if worker.field == 'Trailer driver']
    towing_boat_captains = [worker for worker in available_workers
        if worker.field == 'Towing boat captain']
    guiding_boat_captains = [worker for worker in available_workers
        if worker.field == 'Guiding boat captain']
    selected_workers = random.sample(crane_operators,
                                    min(2, len(crane_operators))) + \
                       random.sample(trailer_drivers,
                                     min(2, len(trailer_drivers))) + \
                       random.sample(towing_boat_captains,
                                     min(1, len(towing_boat_captains))) + \
                       random.sample(guiding_boat_captains,
                                     min(1, len(guiding_boat_captains)))
    for worker in selected_workers:
        worker.activity = "Busy"
        worker.imo_number = imo_number
        update_activity_in_csv(worker)
    return selected_workers

def update_activity_in_csv(worker):
    csv_file_path = "Worker_list.csv"
    df = pd.read_csv(csv_file_path, delimiter=';')
    imo_number = int(worker.imo_number)
    df.loc[df['ID'] == worker.worker_id,
        ['Activity', 'IMO Number']] = ['Busy', imo_number]
    df.to_csv(csv_file_path, index=False, sep=';')

def submit():
    selection = ship_entry.get()
    imo = imo_entry.get()
    if not imo.isdigit() or len(imo) < 7 or len(imo) > 8:
        messagebox.showerror("Error",
            "Invalid IMO number. Please enter a 7 or 8-digit numerical value.")
        return False

    if selection == "1":
        # Ship submission process
        if is_imo_in_port(imo):
            messagebox.showerror("Error",
                "IMO number already exists in the port.")
            return False
        if len(pd.read_csv("Docked_ships.csv")) - 1 >= port.space:
            messagebox.showerror("Error", "The port is full.")
            return False
        save_imo_number(imo)
        csv_file_path = "Worker_list.csv"
        workers = create_workers_from_csv(csv_file_path)
        available_workers = [worker for worker in workers
            if worker.activity == "Free"]
        if len(available_workers) < 6:
            messagebox.showerror("Error", "Not enough available workers.")
            return False
        selected_workers = select_random_workers(available_workers, imo)
        formatted_text = ""
        for worker in selected_workers:
            formatted_text += f"{worker.assign_task()}\n"
        worker_list_window = tk.Toplevel(root)
        worker_list_window.title("Worker List")
        worker_list_label = tk.Label(worker_list_window, text=formatted_text)
        worker_list_label.pack()
        return True

    elif selection == "2":
        # Ship leaving process
        if not is_imo_in_port(imo):
            messagebox.showerror("Error", "No such ship is in the port.")
            return False
        update_workers_activity_to_free(imo)
        remove_imo_number(imo)
        messagebox.showinfo("Success",
            "The ship has been successfully removed from the port.")
        return True

    else:
        messagebox.showerror("Error", 
            "Invalid selection. Please choose either 1 or 2.")
        return False

def save_imo_number(imo_number):
    imo_df = pd.DataFrame({"IMO Number": [imo_number]})
    imo_df.to_csv("Docked_ships.csv", index=False, mode='a',
                  header=not os.path.exists("Docked_ships.csv"))

def remove_imo_number(imo_number):
    csv_file_path = "Docked_ships.csv"
    df = pd.read_csv(csv_file_path)
    df = df[df['IMO Number'] != int(imo_number)]
    df.to_csv(csv_file_path, index=False)

def is_imo_in_port(imo_number):
    if not os.path.exists("Docked_ships.csv"):
        return False
    df = pd.read_csv("Docked_ships.csv")
    return str(imo_number) in df['IMO Number'].astype(str).values

def update_workers_activity_to_free(imo_number):
    csv_file_path = "Worker_list.csv"
    df = pd.read_csv(csv_file_path, delimiter=';')
    df.loc[df['IMO Number'] == int(imo_number), 'Activity'] = 'Free'
    df.loc[df['IMO Number'] == int(imo_number), 'IMO Number'] = 0
    df.to_csv(csv_file_path, index=False, sep=';')

root = tk.Tk()
root.title("Cargo Port Manager")
root.geometry("300x200")
instructions_label = tk.Label(root, text="Type 1 or 2:")
instructions_label.pack()

instructions_label = tk.Label(root, text=" 1. Incoming ship")
instructions_label.pack()

instructions_label = tk.Label(root, text="2. Leaving ship")
instructions_label.pack()

ship_entry = tk.Entry(root)
ship_entry.pack()

imo_label = tk.Label(root, text="Ship IMO Number:")
imo_label.pack()

imo_entry = tk.Entry(root)
imo_entry.pack()

submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.pack()
root.mainloop()
