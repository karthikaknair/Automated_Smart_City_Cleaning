import tkinter as tk
import random
import time
import paho.mqtt.client as mqtt
import subprocess

class TableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Table Example")
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        # Create table headers
        self.titles = ["Zone", "Current Value", "Lasting Time", "Arriving Value", "Next Operation"]

        # Initialize last time
        self.last_time = time.time()

        # Number of rows and columns
        self.rows = 12
        self.cols = 5

        self.row_last_time = {}  # Define here
        # Populate table content
        self.populate_table()

        # Set weights for columns and rows to allow resizing
        for col in range(self.cols):
            self.frame.columnconfigure(col, weight=1)
        for row in range(1, self.rows + 1):
            self.frame.rowconfigure(row, weight=1)

        # Update the table every 3 seconds
        self.root.after(3000, self.update_table)

        self.latest_mosquitto_data = "0"
        self.init_mqtt_client()
        self.previous_mosquitto_data = "0"

    # ... [Other functions] ...

    def populate_table(self):
        for col, title in enumerate(self.titles):
            label = tk.Label(self.frame, text=title)
            label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        for row in range(1, self.rows + 1):
            for col in range(self.cols):
                if col == 0:
                    # Set values in the first column to specific values
                    values = ["(1,1)", "(2,1)", "(3,1)", "(4,1)", "(1,2)", "(2,2)", "(3,2)", "(4,2)",
                              "(1,3)", "(2,3)", "(3,3)", "(4,3)"]
                    value = values[row - 1]
                elif col == 1:
                    value = "0"
                else:
                    value = ""
                entry = tk.Entry(self.frame, justify="center")
                entry.insert(0, value)
                entry.config(state="readonly")
                entry.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

                # Set font color of the first row to red
                if row == 1:
                    entry.config(fg='red')
        for row in range(1, self.rows + 1):
            self.row_last_time[row] = time.time()

    def init_mqtt_client(self):
        def on_message(client, userdata, message):
            self.latest_mosquitto_data = message.payload.decode()
            # Update the value in the first row, fourth column
            arriving_value_widget = self.frame.grid_slaves(row=1, column=3)[0]
            arriving_value_widget.config(state="normal")
            arriving_value_widget.delete(0, "end")
            arriving_value_widget.insert(0, message.payload.decode())
            arriving_value_widget.config(state="readonly")

        self.client = mqtt.Client()
        self.client.on_message = on_message
        mqtt_broker_host = "172.16.1.166"
        self.client.connect(mqtt_broker_host, 1883, 60)
        topic = "predict"
        self.client.subscribe(topic)
        # Start the client loop in a thread to avoid interfering with the main application loop
        self.client.loop_start()

    # Update the corresponding part in the update_table function
    def publish_to_mosquitto(self):
        cmd = [
            "mosquitto_pub",
            "-h", "172.16.1.166",
            "-t", "location",
            "-m", "1_1"
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Published successfully: 1_1")
        except subprocess.CalledProcessError as e:
            print(f"Publishing failed: {e}")

    def update_table(self):
        print("Updating table...")
        for row in range(1, self.rows + 1):
            current_time = time.time()
            elapsed_time = current_time - self.row_last_time[row]
            if row == 1:
                arriving_value = int(self.latest_mosquitto_data)
            else:
                arriving_value = random.choice([0, 1])

            current_value_widget = self.frame.grid_slaves(row=row, column=1)[0]
            arriving_value_widget = self.frame.grid_slaves(row=row, column=3)[0]
            lasting_time_widget = self.frame.grid_slaves(row=row, column=2)[0]
            next_operation_widget = self.frame.grid_slaves(row=row, column=4)[0]

            try:
                current_value = int(current_value_widget.get())
            except ValueError:
                current_value = 0

            try:
                lasting_time = float(lasting_time_widget.get())
            except ValueError:
                lasting_time = 0

            if row == 1 and arriving_value == self.previous_mosquitto_data:
                lasting_time += elapsed_time

            arriving_value_widget.config(state="normal")
            arriving_value_widget.delete(0, "end")
            arriving_value_widget.insert(0, str(arriving_value))
            arriving_value_widget.config(state="readonly")

            if arriving_value == current_value:
                next_operation_widget.config(state="normal")
                next_operation_widget.delete(0, "end")
                next_operation_widget.insert(0, "to filter")
                next_operation_widget.config(state="readonly")

                lasting_time += elapsed_time
            else:
                if arriving_value == 0:
                    next_operation = "to change current value"
                else:
                    next_operation = "to change and publish"
                    if row == 1:
                        self.publish_to_mosquitto()

                current_value_widget.config(state="normal")
                current_value_widget.delete(0, "end")
                current_value_widget.insert(0, str(arriving_value))
                current_value_widget.config(state="readonly")

                next_operation_widget.config(state="normal")
                next_operation_widget.delete  (0, "end")
                next_operation_widget.insert(0, next_operation)
                next_operation_widget.config(state="readonly")

                lasting_time = 0

            lasting_time_widget.config(state="normal")
            lasting_time_widget.delete(0, "end")
            lasting_time_widget.insert(0, "{:.1f}".format(lasting_time))
            lasting_time_widget.config(state="readonly")

            self.row_last_time[row] = current_time

        self.last_time = current_time
        self.root.after(1000, self.update_table)

root = tk.Tk()
# Estimate the window size
window_width = 850
window_height = 500

# Get the screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate x and y coordinates to place the window in the upper right corner of the screen
x = screen_width - window_width - 100  # Leave a 10-pixel margin
y = 30  # Leave some space to account for the macOS menu bar

# Set the window size and position
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
app = TableApp(root)
root.mainloop()
