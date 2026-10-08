# Spring + Damper in Parallel
# attached to a fixed wall on the left
# and being pulled by a force on the right

# If code does not run, make sure the following libraries are installed:
# numpy, matplotlib
# install with:
# python -m pip install -r requirements.txt

import math
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np


class SpringDamperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parallel Spring-Damper System Simulator")
        self.geometry("1100x800")
        self.create_widgets()
        self.run_simulation()

    def create_widgets(self):
        control_frame = ttk.LabelFrame(self, text="Simulation Controls")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        row = 0

        ttk.Label(control_frame, text="Applied Force F(t)").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.force_type = ttk.Combobox(
            control_frame,
            values=[
                "Constant: f",
                "Sinusoidal: f*sin(w*t)",
                "Exp Decay: f*exp(-0.5*t)",
                "Damped Sine: f*exp(-0.5*t)*sin(w*t)",
            ],
            state="readonly",
        )
        self.force_type.current(0)
        self.force_type.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Force Magnitude f (N)").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.force_magnitude_entry = ttk.Entry(control_frame)
        self.force_magnitude_entry.insert(0, "10.0")
        self.force_magnitude_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Frequency w (rad/s)").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.input_w_entry = ttk.Entry(control_frame)
        self.input_w_entry.insert(0, "1.0")
        self.input_w_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Spring Model").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.spring_type_entry = ttk.Combobox(
            control_frame,
            values=["Linear (F_s = k*x_s)", "Nonlinear (F_s = k*x_s^3)"],
            state="readonly",
        )
        self.spring_type_entry.current(0)
        self.spring_type_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Damper Model").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.damper_type_entry = ttk.Combobox(
            control_frame,
            values=["Linear (F_d = b*v_d)", "Nonlinear (F_d = b*v_d^3)"],
            state="readonly",
        )
        self.damper_type_entry.current(0)
        self.damper_type_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Spring Constant k (N/m)").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.spring_constant_entry = ttk.Entry(control_frame)
        self.spring_constant_entry.insert(0, "3.0")
        self.spring_constant_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Damping Constant b (N*s/m)").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.damping_constant_entry = ttk.Entry(control_frame)
        self.damping_constant_entry.insert(0, "1.0")
        self.damping_constant_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Initial Spring Displacement x_s0 (m)").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.initial_displacement_entry = ttk.Entry(control_frame)
        self.initial_displacement_entry.insert(0, "0.0")
        self.initial_displacement_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Label(control_frame, text="Total Simulation Time (s)").grid(
            row=row, column=0, sticky=tk.W, pady=2
        )
        self.simulation_time_entry = ttk.Entry(control_frame)
        self.simulation_time_entry.insert(0, "10.0")
        self.simulation_time_entry.grid(row=row, column=1, pady=2)
        row += 1

        ttk.Button(control_frame, text="Run Simulation", command=self.run_simulation).grid(
            row=row, column=0, columnspan=2, pady=15
        )

        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(7, 7), dpi=100)
        self.ax_pos = self.fig.add_subplot(211)
        self.ax_energy = self.fig.add_subplot(212)
        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()

    def get_force(self, t, f, w):
        force_name = self.force_type.get()
        if "Constant" in force_name:
            return float(f)
        if "Sinusoidal" in force_name:
            return float(f) * math.sin(w * t)
        if "Exp Decay" in force_name:
            return float(f) * math.exp(-0.5 * t)
        if "Damped Sine" in force_name:
            return float(f) * math.exp(-0.5 * t) * math.sin(w * t)
        return float(f)

    def get_spring_force(self, x_s, k):
        spring_model = self.spring_type_entry.get()
        if "Linear" in spring_model:
            return k * x_s
        return k * x_s**3

    def calc_velocity_d(self, F_s, F_t, b):
        F_d = F_t - F_s
        damper_model = self.damper_type_entry.get()
        if "Linear" in damper_model:
            return F_d / b
        if abs(F_d) < 1e-12:
            return 0.0
        return math.copysign((abs(F_d) / b) ** (1.0 / 3.0), F_d)

    def run_simulation(self):
        try:
            f = float(self.force_magnitude_entry.get())
            w = float(self.input_w_entry.get())
            k = float(self.spring_constant_entry.get())
            b = float(self.damping_constant_entry.get())
            x0 = float(self.initial_displacement_entry.get())
            T_max = float(self.simulation_time_entry.get())

            if k <= 0 or b <= 0 or T_max <= 0:
                raise ValueError(
                    "Spring constant k, damping constant b, and simulation time T_max must be positive."
                )
        except ValueError as exc:
            messagebox.showerror("Input Error", f"Invalid parameter value: {exc}")
            return

        dt = 0.005
        n_steps = max(int(T_max / dt), 2)
        t = np.linspace(0.0, T_max, n_steps + 1)

        x_s = np.zeros_like(t)
        v_d = np.zeros_like(t)
        F_applied = np.zeros_like(t)
        E_spring = np.zeros_like(t)
        E_damper = np.zeros_like(t)
        W_input = np.zeros_like(t)

        x_s[0] = x0

        for i in range(n_steps):
            F_t = self.get_force(t[i], f, w)
            F_s = self.get_spring_force(x_s[i], k)
            F_applied[i] = F_t
            v_d[i] = self.calc_velocity_d(F_s, F_t, b)
            x_s[i + 1] = x_s[i] + v_d[i] * dt

            if "Linear" in self.spring_type_entry.get():
                E_spring[i] = 0.5 * k * (x_s[i] ** 2)
            else:
                E_spring[i] = 0.25 * k * (x_s[i] ** 4)

            if i > 0:
                W_input[i] = W_input[i - 1] + F_applied[i - 1] * v_d[i - 1] * dt
                F_d = F_applied[i - 1] - self.get_spring_force(x_s[i - 1], k)
                E_damper[i] = E_damper[i - 1] + F_d * v_d[i - 1] * dt

        F_applied[-1] = self.get_force(t[-1], f, w)
        v_d[-1] = self.calc_velocity_d(self.get_spring_force(x_s[-1], k), F_applied[-1], b)
        if "Linear" in self.spring_type_entry.get():
            E_spring[-1] = 0.5 * k * (x_s[-1] ** 2)
        else:
            E_spring[-1] = 0.25 * k * (x_s[-1] ** 4)

        W_input[-1] = W_input[-2] + F_applied[-2] * v_d[-2] * dt
        F_d_last = F_applied[-2] - self.get_spring_force(x_s[-2], k)
        E_damper[-1] = E_damper[-2] + F_d_last * v_d[-2] * dt

        self.ax_pos.clear()
        self.ax_energy.clear()

        self.ax_pos.plot(t, x_s, "b-", label="Spring Position x(t)")
        self.ax_pos.set_title("Spring Displacement vs. Time")
        self.ax_pos.set_xlabel("Time (s)")
        self.ax_pos.set_ylabel("Displacement (m)")
        self.ax_pos.grid(True)
        self.ax_pos.legend()

        self.ax_energy.plot(t, E_spring, "y-", label="Stored Spring Energy")
        self.ax_energy.plot(t, E_damper, "r-", label="Dissipated Damper Energy")
        self.ax_energy.plot(t, W_input, "g-", label="Work Done by Applied Force")
        self.ax_energy.set_title("Energy & Work vs. Time")
        self.ax_energy.set_xlabel("Time (s)")
        self.ax_energy.set_ylabel("Energy (J)")
        self.ax_energy.grid(True)
        self.ax_energy.legend()

        self.fig.tight_layout()
        self.canvas.draw_idle()


if __name__ == "__main__":
    app = SpringDamperApp()
    app.mainloop()