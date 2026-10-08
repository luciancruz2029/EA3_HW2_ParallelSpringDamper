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
# for bolding default font
import tkinter.font as tkfont 
from tkinter import ttk, messagebox

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.figure import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# ---------- AESTHETICS ---------------

# colors for the status messages
color_info = "#1d76db" # "what to do next"
color_busy = "#fd831f" # running or inputs changed
color_fin = "#27852c" # finished
color_error = "#c62828" # somethings wrong w/ input

# numbero f characters in every input box/ dropdown
# ensures they all line up
input_width= 30
# -------------------------------------

# THIS ENTIRE CLASS IS THE MAIN WINDOW 
# CamelCase = Class !!!
class SpringDamperApp(tk.Tk):
    # Text on run button
    run_text = "Step 2: \u25b6 Run Simulation"
    busy_text = "Running..."

    def __init__(self):
        super().__init__()
        self.title("Parallel Spring-Damper System Simulator")
        self.geometry("1300x900")

        # has the user completed at least one simulation?
        self.has_run = False 
        # are we in the middle of a simulation now?
        self.is_running = False
        self._vars = []

        self.create_widgets()

        # the diagram is just there for the users to understand what they are stimulating, but it is not animated 
        # so draw it at the start
        self.draw_system()
        self.canvas_sys.draw()

        # the plots tell the user to enter their inputs and click run FIRST
        self.show_placeholder('Enter your parameters on the left, \n then click "Run Simulation"')
        # place the cursor on the first input box (makes it obvious where to start #userfriendly)
        self.force_magnitude_entry.focus_set()

    # --------- build input rows ----------
    def add_entry(self, parent, row, label, default):
        # label on the left and a text box on the right
        ttk.Label(parent, text=label, wraplength=190).grid(row=row, column=0, sticky=tk.W, pady=5)
        var = tk.StringVar(value=default)
        entry=ttk.Entry(parent,textvariable=var, width=input_width)
        entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
        # trace tells python to call this funciton everytime the text changes
        var.trace_add("write", self.on_input_changed)
        # add it onto the entries
        self._vars.append(var)
        return entry
    def add_combo(self, parent, row, label, values):
        # label on left, drop down on right 
        ttk.Label(parent, text=label, wraplength=190).grid(row=row, column=0, sticky=tk.W, pady=5)
        combo = ttk.Combobox(parent, values=values, state="readonly", width=input_width)
        # the default is the first option in the list 
        combo.current(0)
        combo.grid(row=row, column=1, sticky=tk.EW, pady=5)
        combo.bind("<<ComboboxSelected>>", self.on_input_changed)
        return combo
        
    # ----------------------- THE GUI ----------------------------
    def create_widgets(self):
        self.bold_font = tkfont.nametofont("TkDefaultFont").copy()
        self.bold_font.configure(weight="bold")
        style = ttk.Style()
        style.configure("Run.TButton", font=self.bold_font, padding=8)
        style.configure("TLabelframe.Label", font=self.bold_font)

        # ------------ LEFT SIDE: inputs on top, diagram below
        left_panel = ttk.Frame(self, width=490)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(12,6), pady=12)
        # stop parent frame from shrinking or expanding to fit child widgets
        left_panel.pack_propagate(False)

        # INPUTS 
        control_frame = ttk.LabelFrame(left_panel, text="Step 1: Enter your parameters", padding=12)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        control_frame.columnconfigure(1, weight=1)

        # row tracks what grid were on
        # label = column 0
        # inputs = column 1
        row = 0

        self.force_type = self.add_combo(control_frame, row, "Applied Force F(t)", 
                                         ["Constant: f",
                                          "Sinusoidal: f*sin(w*t)",
                                          "Exp Decay: f*exp(-0.5*t)",
                                          "Damped Sine: f*exp(-0.5*t)*sin(w*t)",],)
        row += 1

        # f is the constant the force oscillates around 
        self.force_magnitude_entry = self.add_entry(control_frame, row, "Force Magnitude f (N)", "10.0")
        row += 1

        # note w only matters for sinusoidal forces :P
        self.input_w_entry = self.add_entry(control_frame, row, "Frequency w (rad/s)", "1.0")
        row += 1

        # spring type 
        self.spring_type_entry = self.add_combo(control_frame, row, "Spring Model", 
            ["Linear (F_s = k*x_s)", "Nonlinear (F_s = k*x_s^3)"],
        )
        row += 1

        # damper type 
        self.damper_type_entry = self.add_combo( control_frame, row, "Damper Model",
            ["Linear (F_d = b*v_d)", "Nonlinear (F_d = b*v_d^3)"],
        )
        row += 1

        # spring constant 
        self.spring_constant_entry = self.add_entry(control_frame, row, "Spring Constant k (N/m)", "3.0")
        row += 1

        # damping constant
        self.damping_constant_entry = self.add_entry(control_frame, row, "Damping Constant b (N*s/m)", "1.0")
        row += 1

        # initial displacement (spring)
        self.initial_displacement_entry = self.add_entry(control_frame, row, "Initial Spring Displacement x_s0 (m)", "0.0")
        row += 1

        # simulation time (s)
        self.simulation_time_entry = self.add_entry(control_frame, row, "Total Simulation Time (s)", "10.0")
        row += 1

        # ----- Run Button ----------------------------
        self.run_button = ttk.Button(control_frame, text=self.run_text, style="Run.TButton", command=self.on_run_clicked,)
        self.run_button.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(14,6))
        row +=1 

        # ---- Status Messages ---
        self.status_label = ttk.Label(control_frame, text="", font=self.bold_font, wraplength=440, justify=tk.LEFT)
        self.status_label.grid(row=row, column=0, columnspan=2, sticky=tk.W)
        self.set_status("Enter your parameters above, then click Run Simulation.", color_info)

        # System Diagram ! :P
        diagram_frame = ttk.LabelFrame(left_panel, text="System diagram", padding=6)
        diagram_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(10,0))

        self.fig_sys = Figure(figsize=(4.6, 2.8), dpi=100)
        self.ax_system = self.fig_sys.add_subplot(111)
        self.fig_sys.subplots_adjust(left=0.02, right =0.98, top=0.88,bottom=0.02)
        self.canvas_sys = FigureCanvasTkAgg(self.fig_sys, master=diagram_frame)
        self.canvas_sys.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # -------------- RIGHT SIDE: PLOT FRAME -----------------
        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # constrained_layout b/c dont want plot and labels to overlap :P
        self.fig = Figure(figsize=(7, 7), dpi=100, constrained_layout=True)
        # 3 subplots (VERTICAL)
        self.ax_displacement = self.fig.add_subplot(311)
        # Energy plot
        self.ax_energy = self.fig.add_subplot(312)
        # work plot
        self.ax_work = self.fig.add_subplot(313)

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()

        # ------------------------------------------
    # getting all the user feedback, like status messages, placeholder text, and any inputs changed messages
    def set_status(self,message,color):
        #change message under run button and its color
        self.status_label.config(text=message,foreground=color)

    def on_input_changed(self, *args):
        # run when user edits input box or dropdown optin
        if self.is_running:
            return
        if self.has_run:
            # plots need to be udpated
            self.set_status("Inputs changed: Click Run Simulation to update the plots", color_busy)
        else: 
            self.set_status("Ready? Click Run Simulation to see the results.", color_info)
    
    def show_placeholder(self, message): 
        # erase results plots 
        plots = [ 
            (self.ax_displacement, "Spring Displacement vs. Time"),
            (self.ax_energy, "Energy vs. Time"),
            (self.ax_work, "Work vs. Time"),
        ]
        for ax, title in plots:
            ax.clear()
            ax.set_title(title)
            # no ticks if plot is blank
            ax.set_xticks([])
            ax.set_yticks([])
            ax.text(0.5, 0.5, message, transform=ax.transAxes,
                    ha="center", va="center", fontsize=12, color="gray")
        self.canvas.draw()

   # Other physics functions to make this thing scientific 
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

    # DIAGRAM --------------------- Function to draw the system ------------------
    def draw_system(self):
            ax = self.ax_system
            ax.clear()
            ax.set_xlim(0,10)
            ax.set_ylim(0, 6)
            # dont want an axis b/c its jut a drawing :P
            ax.axis("off")
            # movable bar the force pulls on 
            # !!! note the bar doesn't have a mass!!!
            force_left = 8.0 
            bar_bottom, bar_top = 1.0, 5.0
            
            # -------- fixed wall -------- 
            wall_x = 1.2
            ax.plot([wall_x, wall_x], [bar_bottom, bar_top],
                linewidth=5,color="black" )
            # cool wall hatch marks
            for y in np.linspace(bar_bottom, bar_top,17):
                ax.plot([wall_x -0.25, wall_x],[y-0.15, y+0.15], color="gray", linewidth=1)
            ax.text(wall_x - 0.15, bar_top +0.35, "Fixed Wall", ha="center", fontsize=9)

            # --- Movable Bar (right)
            ax.plot([force_left, force_left], [bar_bottom, bar_top], linewidth=5, color="black")
            
            # -------- SPRING -------- 
            spring_y = 4.0
            coil_start = wall_x + 0.8
            coil_end = force_left -0.8
            n_coils = 10
            amplitude = 0.25
            xc = np.linspace(coil_start, coil_end, 2*n_coils+1)
            yc = np.full_like(xc, spring_y)
            # odd values go UP
            yc[1:-1:2] += amplitude
            # even values go DOWN
            yc[2:-1:2] -= amplitude 
            # connect spring wire to wall and bar 
            spring_x= np.concatenate(([wall_x],xc, [force_left]))
            spring_yy = np.concatenate(([spring_y], yc, [spring_y]))

            ax.plot(spring_x,spring_yy,linewidth=2, color="tab:blue")
            # place the text in the center of the spring :P (wall + force/2 aka the average)
            ax.text((wall_x + force_left) /2, spring_y+0.55, "Spring (k)", ha="center", fontsize=9)
    
            #  -------- Damper -------- 
            damper_y = 2.0
            body_left, body_right = 3.6, 5.6
            half_h = 0.35
            piston_x = 4.4
            # this draws the rod from the wall to the piston head 
            ax.plot([wall_x, piston_x], [damper_y, damper_y], linewidth=2, color="tab:red")
           # drawing the piston head inside the cylinder
            ax.plot([piston_x, piston_x], [damper_y - half_h + 0.08, damper_y + half_h - 0.08], linewidth=4, color="tab:red")
            # drawing the cylinder/box of the damper
            ax.plot([body_left, body_right], [damper_y+half_h, damper_y +half_h], linewidth=2, color="tab:red")
            ax.plot([body_left, body_right], [damper_y - half_h, damper_y -half_h], linewidth=2, color="tab:red")
            ax.plot([body_right,body_right], [damper_y -half_h, damper_y+half_h], linewidth=2, color="tab:red")
            # a damper is open on the left and closed on the right
            # ok now we draw the rod from the closed end to the movable bar (force)
            ax.plot([body_right, force_left], [damper_y, damper_y], linewidth=2, color="tab:red")
            ax.text((wall_x+force_left)/2, damper_y-0.75, "Damper (b)", ha="center", fontsize=9)
            
            # --------  Applied force arrow -------- 
            ax.annotate("", xy=(9.8, 3.0), xytext=(force_left +0.1, 3.0),
                arrowprops=dict(arrowstyle ="->",linewidth=2.5, color="black"))
            ax.text(9.0, 3.35, "F(t)", ha="center", fontsize=10)
    
            # Title
            ax.set_title("Parallel Spring-Damper System", fontsize=11, fontweight="bold", pad=6)

# -------- RUNNING THE SIMULATION -----------
    def read_inputs(self):
        fields = [
            ("Force magnitude f", self.force_magnitude_entry),
            ("Frequency w", self.input_w_entry),
            ("Spring constant k", self.spring_constant_entry),
            ("Damping constant b", self.damping_constant_entry),
            ("Initial displacement x_s0", self.initial_displacement_entry),
            ("Total simulation time", self.simulation_time_entry),
        ]

        values = []
        for name, entry in fields:
            try: 
                value = float(entry.get())
                # rejects "nan" and "indf"
                if not math.isfinite(value):
                    raise ValueError
            except ValueError:
                self.set_status(f'"{name}" must be a number.', color_error)
                entry.focus_set()
                # highlights bad text
                entry.selection_range(0, tk.END)
                return None
            values.append(value)

        f,w,k,b,x0, T_max = values
        for name,entry, value in [
            ("Spring constant k", self.spring_constant_entry, k),
            ("Damping constant b", self.damping_constant_entry, b),
            ("Total simulation time", self.simulation_time_entry, T_max),
        ]: 
            if value <=0:
                self.set_status(f'"{name}" must be greater than 0.', color_error)
                entry.focus_set()
                entry.selection_range(0, tk.END)
                return None
        return f, w, k, b, x0, T_max

    def on_run_clicked(self):
        if self.is_running:
            return
        params = self.read_inputs()
        if params is None: 
            return
        self.is_running = True
        # grey out button while running
        self.run_button.config(state="disabled", text=self.busy_text)
        self.set_status("Running simulation...", color_busy)
        self.show_placeholder("Running simulation...")
        self.update()

        # ensure user sees blank "running..." state so they know its restarting
        self.after(400, lambda:self.finish_run(params))

    def finish_run(self, params):
        try:
            results = self.simulate(*params)
            self.plot_results(*results)
            self.has_run = True
            self.set_status(f"Done! Simulated {params[-1]:g} s. Change any input and click Run again to compare.", color_fin,)
        except Exception as exc:
            self.show_placeholder("Something went wrong")
            self.set_status(f"Simulation error: {exc}", color_error)
        finally:
            self.is_running = False
            self.run_button.config(state="normal", text=self.run_text)
    
    def simulate(self, f, w, k, b, x0, T_max):
        # time steps 
        dt = 0.005
        n_steps = max(int(T_max / dt), 2)
        t = np.linspace(0.0, T_max, n_steps + 1)

        # spring displacement
        x_s = np.zeros_like(t)
        # velocity of damper
        v_d = np.zeros_like(t)
        # applied force
        F_applied = np.zeros_like(t)
        # energy stored in spring
        E_spring = np.zeros_like(t)
        # energy dissipated by the damper
        E_damper = np.zeros_like(t)
        # work done by the applied force
        W_input = np.zeros_like(t)

        x_s[0] = x0
        linear_spring = "Linear" in self.spring_type_entry.get()

        for i in range(n_steps):
            F_t = self.get_force(t[i], f, w)
            F_s = self.get_spring_force(x_s[i], k)
            F_applied[i] = F_t
            v_d[i] = self.calc_velocity_d(F_s, F_t, b)
            # new position = old position + velocity * dt
            x_s[i+1] = x_s[i] + v_d[i] *dt

            if linear_spring:
                E_spring[i] = 0.5 *k*(x_s[i] ** 2)
            else:
                E_spring[i] = 0.25 * k*(x_s[i] **4)

            if i > 0:
                W_input[i] = W_input[i-1] + F_applied[i-1] * v_d[i-1] * dt
                F_d = F_applied[i-1] - self.get_spring_force(x_s[i-1], k)
                E_damper[i] = E_damper[i-1] + F_d * v_d[i-1] * dt

        F_applied[-1] = self.get_force(t[-1], f, w)
        v_d[-1] = self.calc_velocity_d(self.get_spring_force(x_s[-1],k), F_applied[-1], b)
        if linear_spring: 
            E_spring[-1] = 0.5*k*(x_s[i]**2)
        else: 
            E_spring[-1] = 0.25 *k *(x_s[i]**4)

        W_input[-1] = W_input[-2] + F_applied[-2] * v_d[-2]*dt
        F_d_last = F_applied[-2] - self.get_spring_force(x_s[-2], k)
        E_damper[-1] = E_damper[-2] + F_d_last * v_d[-2] * dt

        return t, x_s, E_spring, E_damper, W_input

    def plot_results(self, t, x_s, E_spring, E_damper, W_input):
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

        self.canvas.draw()

if __name__ == "__main__":
    app = SpringDamperApp()
    app.mainloop()