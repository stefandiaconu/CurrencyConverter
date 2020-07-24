import tkinter as tk
from tkinter import ttk
from tkinter import Frame
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import datetime


class Main(Frame):
    def __init__(self, window, *args, **kwargs):
        Frame.__init__(self, window, *args, **kwargs)
        self.window = window
        self.window.title("Currency Converter")
        self.window.rowconfigure(0, weigh=1)
        self.window.columnconfigure(0, weight=1)

        self.base_tuple = ()
        self.target_tuple = ()
        self.rates = {}
        self.days_graph_list = []
        self.values_graph_list = []

        self.one_week_bool = False
        self.one_month_bool = False
        self.one_year_bool = False

        self.exchange = 0
        self.base_entry_temp = 1
        self.url = 'https://api.exchangeratesapi.io/'
        self.base_currency = "EUR"
        self.target_currency = "GBP"

        self.create_widgets()
        self.get_rates()

    def create_widgets(self):
        # Entry variables
        self.base_var = tk.IntVar()
        self.base_var.set(self.base_entry_temp)
        self.base_var.trace_add('write', self.calculate_rate)
        self.target_var = tk.IntVar()
        self.target_combo_var = tk.StringVar()
        self.target_combo_var.trace_add('write', self.target_combo_changed)

        self.main_frame = ttk.Frame(self.window)
        self.main_frame.grid(column=0, row=0, sticky='wne', padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        # self.main_frame.columnconfigure(2, weight=1)

        self.base_entry = ttk.Entry(self.main_frame, textvariable=self.base_var)
        self.base_entry.grid(column=0, row=0, sticky='ew', ipady=5)
        self.target_entry = ttk.Entry(self.main_frame, textvariable=self.target_var, state='disabled')
        self.target_entry.grid(column=1, row=0, sticky='ew', ipady=5)
        self.base_combo = ttk.Combobox(self.main_frame, state='readonly')
        self.base_combo.bind('<<ComboboxSelected>>', self.base_combo_changed)
        self.base_combo.grid(column=0, row=1, sticky='ew')
        self.target_combo = ttk.Combobox(self.main_frame, state='readonly', textvariable=self.target_combo_var)
        self.target_combo.grid(column=1, row=1, sticky='ew')

        # Creating a photoimage object to use image
        photo = tk.PhotoImage(file='swap.png')
        photo_mini = photo.subsample(20)
        self.swap_button = ttk.Button(self.main_frame, image=photo_mini, command=self.swap_rates)
        self.swap_button.image = photo_mini
        self.swap_button.grid(column=2, row=0, rowspan=2)

        self.graph_frame = ttk.Frame(self.main_frame)
        self.graph_frame.grid(column=0, row=2, sticky='enw', columnspan=3)
        self.graph_frame.columnconfigure(0, weight=1)
        self.graph_frame.columnconfigure(1, weight=1)
        self.graph_frame.columnconfigure(2, weight=1)
        self.graph_frame.columnconfigure(3, weight=1)
        # self.graph_frame.rowconfigure(1, weight=1)
        self.info_label = ttk.Label(self.graph_frame, text="Last:")
        self.info_label.grid(column=0, row=0)
        self.one_week_button = ttk.Button(self.graph_frame, text="1 Week", command=self.one_week_display)
        self.one_week_button.grid(column=1, row=0)
        self.one_month_button = ttk.Button(self.graph_frame, text="1 Month", command=self.one_month_display)
        self.one_month_button.grid(column=2, row=0)
        self.one_year_button = ttk.Button(self.graph_frame, text="1 Year", command=self.one_year_display)
        self.one_year_button.grid(column=3, row=0)
        
    def get_rates(self):
        url_call = self.url + 'latest?base=' + self.base_currency
        self.response = requests.get(url_call).json()

        self.rates[self.response['base']] = 1
        for key, value in self.response['rates'].items():
            self.rates[key] = value

        for key in self.rates.keys():
            self.base_tuple += (str(key),)
            self.target_tuple += (str(key),)

        self.reset_combos(self.base_currency, self.target_currency)

    def calculate_rate(self, *args):
        if len(self.base_entry.get()) != 0:
            self.target_var.set(round(self.base_var.get() * self.exchange, 2))
        elif len(self.base_entry.get()) == 0:
            self.target_var.set(0)

    def swap_rates(self):
        self.base_entry_temp = self.base_var.get()
        self.base_currency = self.target_combo.get()
        self.target_currency = self.base_combo.get()

        self.clear_combos()

        url_call = self.url + 'latest?base=' + self.base_currency
        self.response = requests.get(url_call).json()

        self.rates[self.response['base']] = 1
        for key, value in self.response['rates'].items():
            self.rates[key] = value

        for key in self.rates.keys():
            self.base_tuple += (str(key),)
            self.target_tuple += (str(key),)

        self.reset_combos(self.base_currency, self.target_currency)

    def target_combo_changed(self, *args):
        if self.target_combo_var.get() in self.rates:
            self.exchange = self.rates[self.target_combo.get()]
            self.calculate_rate()
            if self.one_week_bool:
                self.one_week_display()
            if self.one_month_bool:
                self.one_month_display()
            if self.one_year_bool:
                self.one_year_display()

    def base_combo_changed(self, *args):
        if self.base_combo.get() == self.target_combo.get():
            self.swap_rates()
        else:
            self.base_entry_temp = self.base_var.get()
            self.target_currency = self.target_combo.get()
            self.base_currency = self.base_combo.get()

            self.clear_combos()

            url_call = self.url + 'latest?base=' + self.base_currency
            self.response = requests.get(url_call).json()

            self.rates[self.response['base']] = 1
            for key, value in self.response['rates'].items():
                self.rates[key] = value

            for key in self.rates.keys():
                self.base_tuple += (str(key),)
                self.target_tuple += (str(key),)

            self.reset_combos(self.base_currency, self.target_currency)

    def clear_combos(self):
        self.rates = {}
        self.base_tuple = ()
        self.base_combo['values'] = self.base_tuple
        self.target_tuple = ()
        self.target_combo['values'] = self.target_tuple

    def reset_combos(self, base, target):
        if (len(self.base_tuple) > 0) and (len(self.target_tuple) > 0):
            self.base_combo['values'] = self.base_tuple
            self.target_combo['values'] = self.target_tuple

            if base in self.base_combo['values']:
                self.base_combo.current(self.base_tuple.index(base))

            if target in self.target_combo['values']:
                self.target_combo.current(self.target_tuple.index(target))
                self.target_var.set(round(self.base_entry_temp * self.rates[self.target_combo.get()], 2))

    def one_week_display(self):
        self.one_week_bool = True
        self.one_month_bool = False
        self.one_year_bool = False

        self.clear_graph_values()

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=7)

        url_call = self.url + 'history?start_at=' + str(start_date) + '&end_at=' + str(end_date) + '&base=' + self.base_combo.get()
        self.response = requests.get(url_call).json()

        self.get_graph_xaxis()
        self.get_graph_yaxis()

        self.draw_canvas()

    def one_month_display(self):
        self.one_week_bool = False
        self.one_month_bool = True
        self.one_year_bool = False

        self.clear_graph_values()

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)

        url_call = self.url + 'history?start_at=' + str(start_date) + '&end_at=' + str(end_date) + '&base=' + self.base_combo.get()
        self.response = requests.get(url_call).json()

        self.get_graph_xaxis()
        self.get_graph_yaxis()

        self.draw_canvas()

        # # Display the nth label on x-axis
        n = 5
        self.display_nth_label(n)

    def one_year_display(self):
        self.one_week_bool = False
        self.one_month_bool = False
        self.one_year_bool = True

        self.clear_graph_values()

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365)

        url_call = self.url + 'history?start_at=' + str(start_date) + '&end_at=' + str(end_date) + '&base=' + self.base_combo.get()
        self.response = requests.get(url_call).json()

        self.get_graph_xaxis()
        self.get_graph_yaxis()

        self.draw_canvas()

        # Display the nth label on x-axis
        n = 21
        self.display_nth_label(n)

    def draw_canvas(self, *args):
        fig = Figure(figsize=(5, 5), dpi=100)
        self.a = fig.add_subplot(211)
        self.a.tick_params(rotation=45)

        self.a.plot(self.days_graph_list, self.values_graph_list)

        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=1, sticky='enw', columnspan=4)

        toolbar_frame = ttk.Frame(self.graph_frame)
        toolbar_frame.grid(column=0, row=2, sticky='enw', columnspan=4)

        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()
        canvas._tkcanvas.grid()

    def get_graph_xaxis(self):
        for key in sorted(self.response['rates'].keys()):
            self.days_graph_list.append(key)

    def get_graph_yaxis(self):
        if self.base_combo.get() != self.target_combo.get():
            for key in self.days_graph_list:
                self.values_graph_list.append(self.response['rates'][key][self.target_combo.get()])
        else:
            for key in self.days_graph_list:
                self.values_graph_list.append(1)

    def display_nth_label(self, n):
        for index, label in enumerate(self.a.xaxis.get_ticklabels()):
            if index % n != 0:
                label.set_visible(False)

    def clear_graph_values(self):
        self.days_graph_list = []
        self.values_graph_list = []


# Start main loop
if __name__ == "__main__":
    root = tk.Tk()
    main = Main(root)
    main.mainloop()
