# Spring + Damper in Parallel
# attached to a fixed wall on the left
# and being pulled by a force on the right

# If code does not run, make sure the following libraries are installed:
# numpy, matplotlib
# install with:
# python -m pip install -r requirements.txt

# note this file has to be downloaded and run on computer or else tkinter wont work b/c it doesn't have a display :(

import math
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.figure import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# ---------- AESTHETICS ---------------
# background
bg = ""
# header & buttons
h_b = ""
text = ""

# -------------------------------------

class SpringDamperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Parallel Spring-Damper System Simulator")
        self.geometry("1100x800")
        self.create_widgets()
        self.run_simulation()

    def create_widgets(self):
        control_frame = ttk.LabelFrame(self, text="Simulation Controls", padding=15)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(12,6), pady=12)
        control_frame.config(width=300)
        # this stops parent frame from shrinking or expanding to fit child widgets 
        control_frame.pack_propagate(False)
        control_frame.columnconfigure(1, weight=1)

        row = 0

        ttk.Label(control_frame, text="Applied Force F(t)").grid(
            row=row, column=0, sticky=tk.W, pady=6
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
        self.force_type.grid(row=row, column=1, pady=6)
        row += 1

        # f is the constant the force oscillates around 
        ttk.Label(control_frame, text="Force Magnitude f (N)").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.force_magnitude_entry = ttk.Entry(control_frame)
        self.force_magnitude_entry.insert(0, "10.0")
        self.force_magnitude_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Label(control_frame, text="Frequency w (rad/s)").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.input_w_entry = ttk.Entry(control_frame)
        self.input_w_entry.insert(0, "1.0")
        self.input_w_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Label(control_frame, text="Spring Model").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.spring_type_entry = ttk.Combobox(
            control_frame,
            values=["Linear (F_s = k*x_s)", "Nonlinear (F_s = k*x_s^3)"],
            state="readonly",
        )
        self.spring_type_entry.current(0)
        self.spring_type_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Label(control_frame, text="Damper Model").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.damper_type_entry = ttk.Combobox(
            control_frame,
            values=["Linear (F_d = b*v_d)", "Nonlinear (F_d = b*v_d^3)"],
            state="readonly",
        )
        self.damper_type_entry.current(0)
        self.damper_type_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Label(control_frame, text="Spring Constant k (N/m)").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.spring_constant_entry = ttk.Entry(control_frame)
        self.spring_constant_entry.insert(0, "3.0")
        self.spring_constant_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Label(control_frame, text="Damping Constant b (N*s/m)").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.damping_constant_entry = ttk.Entry(control_frame)
        self.damping_constant_entry.insert(0, "1.0")
        self.damping_constant_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Label(control_frame, text="Initial Spring Displacement x_s0 (m)").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.initial_displacement_entry = ttk.Entry(control_frame)
        self.initial_displacement_entry.insert(0, "0.0")
        self.initial_displacement_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Label(control_frame, text="Total Simulation Time (s)").grid(
            row=row, column=0, sticky=tk.W, pady=6
        )
        self.simulation_time_entry = ttk.Entry(control_frame)
        self.simulation_time_entry.insert(0, "10.0")
        self.simulation_time_entry.grid(row=row, column=1, pady=6)
        row += 1

        ttk.Button(control_frame, text="Run Simulation", command=self.run_simulation).grid(
            row=row, column=0, columnspan=2, pady=15
        )

        # -------------- PLOT FRAME -----------------
        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig = Figure(figsize=(7, 7), dpi=100)
        # 4 subplots (VERTICAL)
        # mechanical system diagram (of the spring and damper + all that)
        self.ax_system = self.fig.add_subplot(411)
        # Spring displacement plot
        self.ax_displacement = self.fig.add_subplot(412)
        # Energy plot
        self.ax_energy = self.fig.add_subplot(413)
        # work plot
        self.ax_work = self.fig.add_subplot(414)
        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()

        # ------------------------------------------

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

    def draw_system(self):
            ax = self.ax_system
            ax.clear()
            ax.set_xlim(0,10)
            ax.set_ylim(0, 6)
            ax.axis("off")
    
            # -------- fixed wall -------- 
            wall_x = 1.2
            ax.plot(
                [wall_x, wall_x]
                [1, 5],
                linewidth=5,
                color="black" )
            # cool wall hatch marks
            for y in np.linspace(1,5,17):
                ax.plot([wall_x -0.25, wall_x],[y-0.15, y+0.15], color="gray", linewidth=1)
            ax.text(wall_x - 0.15, 5.35, "Fixed Wall", ha="center", fontsize=9)
    
            # -------- SPRING -------- 
            spring_y = 4.0
            spring_x_start = wall_x
            spring_x_end = force_left
            n_coils = 12
            amplitude = 0.25
            x = np.linspace(
                spring_x_start,
                spring_x_end,
                2*n_coils + 1
            )
            y=np.ones_like(x)*spring_y
            for i in range(1, len(x)-1):
                y[i] += amplitude if i % 2 else -amplitude
    
            ax.plot(x,y,linewidth=2)
            ax.text(4.6,4.45, "Spring (k)", ha="center", fontsize=9)
    
            #  -------- Damper -------- 
            damper_y = 2.0
            ax.plot(
                [wall_x, 3.8],
                [damper_y, damper_y],
                linewidth=2
            )
            # damper body
            damper_left = 3.8
            damper_right = 5.4
            ax.add_patch(
                Rectangle((damper_left, damper_y - 0.35), damper_right - damper_left,
                               0.7, fill=False, linewidth=2)
            )
            # damper piston
            ax.plot([damper_right, 7.0], [damper_y, damper_y], linewidth=2)
            ax.plot([7.0, force_left], [damper_y, damper_y], linewidth=2)
            ax.text(4.6, 1.45, "Damper (b)", ha="center", fontsize=9)
    
            # --------  Applied force arrow -------- 
            ax.annotate("", xy=(9.8, 3), xytext=(8.8, 3),
                arrowprops=dict(arrowstyle ="->",linewidth=2)
            )
            ax.text(9.3, 3.45, "F(t)", ha="center", fontsize=11)
    
            # Title
            ax.set_title("Parallel Spring-Damper System", fontsize=12, fontweight="bold", pad=8)

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

        self.draw_system()
        self.ax_displacement.clear()
        self.ax_energy.clear()
        self.ax_work.clear()

        # SPRING DISPLACEMENT PLOT 
        self.ax_displacement.plot(t, x_s, "g-", label="Spring Displacement x(t)")
        self.ax_displacement.set_title("Spring Displacement vs. Time")
        self.ax_displacement.set_xlabel("Time (s)")
        self.ax_displacement.set_ylabel("Displacement (m)")
        self.ax_displacement.grid(True)
        self.ax_displacement.legend()

        # Energy Plot 
        self.ax_energy.plot(t, E_spring, "b-", label="Stored Spring Energy")
        self.ax_energy.plot(t, E_damper, "r-", label="Dissipated Damper Energy")
        self.ax_energy.set_title("Energy vs. Time")
        self.ax_energy.set_xlabel("Time (s)")
        self.ax_energy.set_ylabel("Energy (J)")
        self.ax_energy.grid(True)
        self.ax_energy.legend()

        # WORK PLOT 
        self.ax_work.plot(t, W_input, "y-", label="Work Done by Applied Force")
        self.ax_work.set_title("Work vs. Time")
        self.ax_work.set_xlabel("Time (s)")
        self.ax_work.set_ylabel("Work (J)")   
        self.ax_work.grid(True)
        self.ax_work.legend()

        self.fig.tight_layout()
        self.canvas.draw_idle()

    
        

if __name__ == "__main__":
    app = SpringDamperApp()
    app.mainloop()