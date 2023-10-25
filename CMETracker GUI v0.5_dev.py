# -*- coding: utf-8 -*-
"""
Created on Thu Jul 3 14:25:06 2023

@author: lbr20
"""
## Import packages
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import find_peaks, peak_widths
import numpy as np


#%% Options window 
class OptionsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Options")
        self.geometry("225x200")
        
## Create buttons and labels       
        ## Prominence 
        self.prominence_label = tk.Label(self, text="Prominence")
        self.prominence_entry = tk.Entry(self)
        self.prominence_entry.insert(0, "1")
        
        ## FPS
        self.fps_label = tk.Label(self, text="FPS")
        self.fps_entry = tk.Entry(self)
        self.fps_entry.insert(0, "1")
        
        ## Peak height
        self.relative_peak_height_label = tk.Label(self, text="Relative Peak Height")
        self.relative_peak_height_entry = tk.Entry(self)
        self.relative_peak_height_entry.insert(0, "1")
        
        ## Plot width checkbox
        self.plot_widths_var = tk.IntVar()
        self.plot_widths_checkbox = tk.Checkbutton(self, text="Plot widths", variable=self.plot_widths_var)
        
        ## Save button
        self.save_button = tk.Button(self, text="Save", command=self.save_values)
        
        ## Arrange the layout of the options window
        self.prominence_label.pack()
        self.prominence_entry.pack()
        self.fps_label.pack()
        self.fps_entry.pack()
        self.relative_peak_height_label.pack()
        self.relative_peak_height_entry.pack()
        self.plot_widths_checkbox.pack()
        self.save_button.pack()

## Options window functions
    ## Save button
    def save_values(self):
        try:
            prominence = int(self.prominence_entry.get())
            fps = float(self.fps_entry.get())
            relative_peak_height = float(self.relative_peak_height_entry.get())
            plot_widths = self.plot_widths_var.get()
            
            if not (0 <= relative_peak_height <= 1):
                raise ValueError("Relative Peak Height must be between 0 and 1.")
            
            self.master.set_options(prominence, fps, relative_peak_height, plot_widths)
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

#%% Main Window

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CMETracker v0.5_dev")
        # self.geometry("1000x500")

## Set variables
        self.current_graph = None
        self.prominence = 1
        self.fps = 0.1
        self.relative_peak_height = 1
        self.plot_widths = False
        self.options_window = None
        self.results_table_timediff = None
        self.results_table_width = None
        self.selected_elements = []
        
## Create buttons and labels 
        ## Test button
        #self.test_button = tk.Button(self, text="Test", command=self.display_values)
    
        ## Listbox 1
        self.elements_list1 = tk.Listbox(self, height=18, width=10)
        self.elements_list1.bind("<Button-1>", lambda event: self.plot_data(self.elements_list1))
        
        ## Left and right buttons
        self.transfer_frame = tk.Frame(self)
        self.transfer_right_button = tk.Button(self.transfer_frame, text=">", command=self.transfer_right, width=5)
        self.transfer_left_button = tk.Button(self.transfer_frame, text="<", command=self.transfer_left, width=5)
        
        ## Listbox 2
        self.elements_list2 = tk.Listbox(self, height=18, width=10)
        #self.elements_list2.bind("<Button-1>", lambda event: self.plot_data(self.elements_list2))
        
        ## The graph canvas
        self.graph_frame = tk.Frame(self, bg='white', width=400, height=300)
        self.graph_panel = tk.Canvas(self.graph_frame, bg='white', width=400, height=300)
        
        ## All buttons on the right side
        self.load_file_button = tk.Button(self, text="Load File", command=self.open_csv_file, width=15)
        self.options_button = tk.Button(self, text="Options", command=self.open_options, width=15)
        self.batch_process_button = tk.Button(self, text="Batch Process", command=self.batch_process, state=tk.DISABLED, width=15)
        self.plot_timediff_button = tk.Button(self, text="Plot Time Differences", command=self.plot_timedifferences, state=tk.DISABLED, width=15)
        self.plot_widths_button = tk.Button(self, text="Plot Peak Widths", command=self.plot_peak_widths, state=tk.DISABLED, width=15)
        self.save_graph_button = tk.Button(self, text="Save Graph", command=self.save_graph, width=15)
        
        ## Arrange the layout of the mainwindow
        ## Left side
        self.elements_list1.pack(side=tk.LEFT)
        self.transfer_frame.pack(side=tk.LEFT)
        self.elements_list2.pack(side=tk.LEFT)       
        self.transfer_left_button.pack(side=tk.TOP)
        self.transfer_right_button.pack(side=tk.BOTTOM)
        
        ## Graph canvas
        self.graph_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.graph_panel.pack()
        self.graph_frame.configure(relief=tk.SOLID, borderwidth=1) ## Apply frame styling
        
        ## Right side
        self.load_file_button.pack(side=tk.TOP, padx=10, pady=(5, 5))
        self.options_button.pack(side=tk.TOP, padx=10, pady=(5, 5))
        self.batch_process_button.pack(side=tk.TOP, padx=10, pady=(5, 5))
        self.plot_timediff_button.pack(side=tk.TOP, padx=10, pady=(5, 5))
        self.plot_widths_button.pack(side=tk.TOP, padx=10, pady=(5, 5))
        self.save_graph_button.pack(side=tk.BOTTOM, padx=10, pady=10)

## Main Window functions        
    
    # ## Test button function
    # def display_values(self):
    #     if self.prominence is not None:
    #         print("Prominence:", self.prominence)
    #     if self.fps is not None:
    #         print("FPS:", self.fps)
    #     if self.relative_peak_height is not None:
    #         print("Relative Peak Height:", self.relative_peak_height)
    #     if self.plot_widths == 0:
    #         print("Plot Widths: Not Checked")
    #     elif self.plot_widths == 1:
    #         print("Plot Widths: Checked")
    
    ## Open Optionswindow
    def open_options(self):
        if self.options_window:
            self.options_window.destroy()
        self.options_window = OptionsWindow(self)
        if self.prominence is not None:
            self.options_window.prominence_entry.delete(0, tk.END)
            self.options_window.prominence_entry.insert(0, str(self.prominence))
        if self.fps is not None:
            self.options_window.fps_entry.delete(0, tk.END)
            self.options_window.fps_entry.insert(0, str(self.fps))
        if self.relative_peak_height is not None:
            self.options_window.relative_peak_height_entry.delete(0, tk.END)
            self.options_window.relative_peak_height_entry.insert(0, str(self.relative_peak_height))
        if self.plot_widths is not None:
            self.options_window.plot_widths_var.set(self.plot_widths)
            
    ## Acquire current option settings (Has no button, but is used by the save_values function)        
    def set_options(self, prominence, fps, relative_peak_height, plot_widths):
        self.prominence = prominence
        self.fps = fps
        self.relative_peak_height = relative_peak_height
        self.plot_widths = plot_widths
    
    ## Load File
    def open_csv_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.filename:
            self.df, self.subset_names = self.subset_data(self.filename)
            self.display_elements(self.subset_names)
        
        
    ## Subset File (Has no button, but is used by the open_csv_file function)  
    def subset_data(self, filename):
        self.df = pd.read_csv(self.filename, index_col=0)
        self.df = self.df.drop(columns=['Area', 'StdDev', 'IntDen', 'RawIntDen'])
        self.unique_ids = self.df['ID'].unique()
        self.subset_names = []
        for id_value in self.unique_ids:
            self.subset_name = f"Event {id_value}"
            self.subset_names.append(self.subset_name)
        self.batch_process_button.config(state=tk.NORMAL)
        return self.df, self.subset_names
    
    ## Fill Listbox with Events (Has no button, but is used by the open_csv_file function) 
    def display_elements(self, subset_names):
        self.elements_list1.delete(0, tk.END)
        self.elements_list2.delete(0, tk.END)
        for subset_name in subset_names:
            self.elements_list1.insert(tk.END, subset_name)
            
    ## Plot graphs (Action happens when you click an element in the listbox) 
    def plot_data(self, listbox):
        selected_index = listbox.curselection()
        if selected_index:
            subset_df = self.df[self.df['ID'] == selected_index[0]]
            plot_widths = self.plot_widths
            prominence = self.prominence
            relative_peak_height = self.relative_peak_height

            if plot_widths:
                subset_df_0 = subset_df[subset_df['Ch'] == 1].reset_index(drop=True)
                subset_df_1 = subset_df[subset_df['Ch'] == 2].reset_index(drop=True)

                x = subset_df_0['Mean']
                y = subset_df_1['Mean']

                peaks_ch1, _ = find_peaks(x, prominence=prominence)
                peaks_ch2, _ = find_peaks(y, prominence=prominence)
                results_ch1 = peak_widths(x, peaks_ch1, rel_height = relative_peak_height)
                results_ch2 = peak_widths(y, peaks_ch2, rel_height = relative_peak_height)

                fig, ax = plt.subplots()
                plt.plot(x, '-g', lw=0.5, label='Channel 1')
                plt.plot(y, '-r', lw=0.5,  label='Channel 2')

                plt.plot(peaks_ch1, x[peaks_ch1], "v", color='g')
                plt.hlines(*results_ch1[1:], color='k', lw=0.2, linestyle='dashed')
                plt.plot(peaks_ch2, y[peaks_ch2], "v", color='r')
                plt.hlines(*results_ch2[1:], color='k', lw=0.2, linestyle='dashed')
                plt.xlabel('Frame')
                plt.ylabel('Mean signal intensity')
                ax.set_title(f"Data Plot for: {listbox.get(selected_index)}")
                plt.legend(['Channel 1', 'Channel 2'])

            else:
                subset_df_0 = subset_df[subset_df['Ch'] == 1].reset_index(drop=True)
                subset_df_1 = subset_df[subset_df['Ch'] == 2].reset_index(drop=True)
                
                if self.fps is not None:
                    subset_df_0.index = subset_df_0.index * (1 / self.fps)
                    subset_df_1.index = subset_df_1.index * (1 / self.fps)

                x = subset_df_0['Mean']
                y = subset_df_1['Mean']

                locpeak1, _ = find_peaks(x, prominence=prominence) 
                locpeak2, _ = find_peaks(y, prominence=prominence)

                fig, ax = plt.subplots()
                plt.plot(x, '-gv', lw=0.5, markevery=locpeak1)
                plt.plot(y, '-rv', lw=0.5, markevery=locpeak2)
                plt.ylabel('Mean signal intensity')
                plt.xlabel('Time[s]')
                plt.title("Composite plot")
                ax.set_title(f"Data Plot for: {listbox.get(selected_index)}")
                plt.legend(['Channel 1 signal', 'Channel 2 Signal'])

            canvas = FigureCanvasTkAgg(fig, master=self.graph_panel)
            canvas.draw()

            if self.current_graph is not None:
                self.current_graph.get_tk_widget().pack_forget()

            canvas.get_tk_widget().pack()
            self.current_graph = canvas
  
    def transfer_right(self): ## Places events in the right listbox
        selected_indices = self.elements_list1.curselection()
        for index in reversed(selected_indices):
            item = self.elements_list1.get(index)
            if item not in self.elements_list2.get(0, tk.END):
                self.elements_list2.insert(tk.END, item)
        self.elements_list1.selection_clear(0, tk.END)
            
    def transfer_left(self): ## Removes events from the left listbox
        selected_indices = self.elements_list2.curselection()
        for index in reversed(selected_indices):
            self.elements_list2.delete(index)
        self.elements_list2.selection_clear(0, tk.END)
                
    def batch_process(self): ## Action from the batch process button
        directory_path = filedialog.askdirectory(title = 'Choose save directory')
        if directory_path:
            self.save_dir = directory_path + '/'
            print(self.save_dir)
    
        self.results_table_width = pd.DataFrame()
        self.results_table_timediff = pd.DataFrame()
    
        for index in range(self.elements_list2.size()):
            item = self.elements_list2.get(index)
            id_value = int(item.split()[1])
            subset_df = self.df[self.df['ID'] == id_value]
            subset_df_0 = subset_df[subset_df['Ch'] == 1].reset_index(drop=True)
            subset_df_1 = subset_df[subset_df['Ch'] == 2].reset_index(drop=True)
            x = subset_df_0['Mean']
            y = subset_df_1['Mean']
    
            peaks_ch1, _ = find_peaks(x, prominence=self.prominence)
            peaks_ch2, _ = find_peaks(y, prominence=self.prominence)
            results_ch1 = peak_widths(x, peaks_ch1, rel_height=self.relative_peak_height)
            results_ch2 = peak_widths(y, peaks_ch2, rel_height=self.relative_peak_height)
    
            widths_ch1 = pd.Series(results_ch1[0]) * (1 / self.fps)
            widths_ch2 = pd.Series(results_ch2[0]) * (1 / self.fps)
    
            ## Save Peakwidths
            self.results_table_width['ID' + str(id_value) + '_ch1_widths'] = widths_ch1
            self.results_table_width['ID' + str(id_value) + '_ch2_widths'] = widths_ch2
            self.results_table_width.to_csv(self.save_dir + 'Widths.csv', index=False)  # Create variable out
    
            ## Calculate timedifference between two peaks and at what timepoints peaks are
            peaks_ch1 = np.sort(peaks_ch1)
            peakdiff_ch1 = np.diff(peaks_ch1) * (1 / self.fps)
    
            peaks_ch2 = np.sort(peaks_ch2)
            peakdiff_ch2 = np.diff(peaks_ch2) * (1 / self.fps)
    
            peakdiff_ch1 = pd.Series(peakdiff_ch1)
            peakdiff_ch2 = pd.Series(peakdiff_ch2)
    
            ## Save Timedifferences
            self.results_table_timediff['ID' + str(id_value) + '_ch1_time_between_peaks'] = peakdiff_ch1
            self.results_table_timediff['ID' + str(id_value) + '_ch2_time_between_peaks'] = peakdiff_ch2
            self.results_table_timediff.to_csv(self.save_dir + 'Timedifferences.csv', index=False)  # Create variable out
    
        self.plot_timediff_button.config(state=tk.NORMAL)  ## Activates plot timediff button
        self.plot_widths_button.config(state=tk.NORMAL)  ## Activates plot widhts button
        
    def plot_timedifferences(self): ## Plots timedifferences plot when you click the button
        if self.results_table_timediff is not None:
            print("Results Table Timedifferences:")
            print(self.results_table_timediff)
            
            ## Extract channel 1
            df_timediff_ch1 = self.results_table_timediff.filter(like='ch1')
            stack_timediff_ch1 = df_timediff_ch1.stack()
            stack_timediff_ch1 = stack_timediff_ch1.to_numpy()

            ## Exctract channel 2
            df_timediff_ch2 = self.results_table_timediff.filter(like='ch2')
            stack_timediff_ch2 = df_timediff_ch2.stack()
            stack_timediff_ch2 = stack_timediff_ch2.to_numpy()

            ####
            
            ## Create subplots and axes objects
            fig, axes = plt.subplots(1, 2)

            #####################

            ## Channel 1 plot
            axes[0].boxplot(stack_timediff_ch1, showmeans=True, showfliers=False)
            axes[0].set_title("Channel 1")
            axes[0].tick_params(axis='x', which='both', bottom=False, labelbottom=False)

            ## Calculate mean and standard deviation for Channel 1
            mean_ch1 = np.mean(stack_timediff_ch1)
            std_ch1 = np.std(stack_timediff_ch1)

            ## Add mean and standard deviation as text annotations for Channel 1
            axes[0].text(0.95, 0.95, f"Mean: {mean_ch1:.2f}", va='top', ha='right', color='red', transform=axes[0].transAxes)
            axes[0].text(0.95, 0.88, f"Std: {std_ch1:.2f}", va='top', ha='right', color='blue', transform=axes[0].transAxes)

            #####################

            ## Channel 2 plot
            axes[1].boxplot(stack_timediff_ch2, showmeans=True, showfliers=False)
            axes[1].set_title("Channel 2")
            axes[1].tick_params(axis='x', which='both', bottom=False, labelbottom=False)

            ## Calculate mean and standard deviation for Channel 2
            mean_ch2 = np.mean(stack_timediff_ch2)
            std_ch2 = np.std(stack_timediff_ch2)

            ## Add mean and standard deviation as text annotations for Channel 2
            axes[1].text(0.95, 0.95, f"Mean: {mean_ch2:.2f}", va='top', ha='right', color='red', transform=axes[1].transAxes)
            axes[1].text(0.95, 0.88, f"Std: {std_ch2:.2f}", va='top', ha='right', color='blue', transform=axes[1].transAxes)

            #####################

            ## Adjust spacing between subplots
            plt.subplots_adjust(wspace=0.4)

            ## Set supertitle
            plt.suptitle('Timegaps between peaks')
            
            ## Display the plot
            canvas = FigureCanvasTkAgg(fig, master=self.graph_panel)
            canvas.draw()

            if self.current_graph is not None:
                self.current_graph.get_tk_widget().pack_forget()

            canvas.get_tk_widget().pack()
            self.current_graph = canvas 
            
    def plot_peak_widths(self): ## Plots peakwidhts plot when you click the button
        if self.results_table_width is not None:
            print("Results Table Widths:")
            print(self.results_table_width)
            
            ## Extract channel 1
            df_widths_ch1 = self.results_table_width.filter(like='ch1')
            stack_widths_ch1 = df_widths_ch1.stack()
            stack_widths_ch1 = stack_widths_ch1.to_numpy()

            ## Extract channel 2
            df_widths_ch2 = self.results_table_width.filter(like='ch2')
            stack_widths_ch2 = df_widths_ch2.stack()
            stack_widths_ch2 = stack_widths_ch2.to_numpy()
            
            # Create subplots and axes objects
            fig, axes = plt.subplots(1, 2)

            #####################

            ## Channel 1 plot
            axes[0].boxplot(stack_widths_ch1, showmeans=True, showfliers=False)
            axes[0].set_title("Channel 1")
            axes[0].tick_params(axis='x', which='both', bottom=False, labelbottom=False)

            ## Calculate mean and standard deviation for Channel 1
            mean_ch1 = np.mean(stack_widths_ch1)
            std_ch1 = np.std(stack_widths_ch1)

            ## Add mean and standard deviation as text annotations for Channel 1
            axes[0].text(0.95, 0.95, f"Mean: {mean_ch1:.2f}", va='top', ha='right', color='red', transform=axes[0].transAxes)
            axes[0].text(0.95, 0.88, f"Std: {std_ch1:.2f}", va='top', ha='right', color='blue', transform=axes[0].transAxes)

            #####################

            ## Channel 2 plot
            axes[1].boxplot(stack_widths_ch2, showmeans=True, showfliers=False)
            axes[1].set_title("Channel 2")
            axes[1].tick_params(axis='x', which='both', bottom=False, labelbottom=False)

            ## Calculate mean and standard deviation for Channel 2
            mean_ch2 = np.mean(stack_widths_ch2)
            std_ch2 = np.std(stack_widths_ch2)

            ## Add mean and standard deviation as text annotations for Channel 2
            axes[1].text(0.95, 0.95, f"Mean: {mean_ch2:.2f}", va='top', ha='right', color='red', transform=axes[1].transAxes)
            axes[1].text(0.95, 0.88, f"Std: {std_ch2:.2f}", va='top', ha='right', color='blue', transform=axes[1].transAxes)

            #####################

            ## Adjust spacing between subplots
            plt.subplots_adjust(wspace=0.4)

            ## Set supertitle
            plt.suptitle('Peak Widths')
            
            ## Display the plot
            canvas = FigureCanvasTkAgg(fig, master=self.graph_panel)
            canvas.draw()

            if self.current_graph is not None:
                self.current_graph.get_tk_widget().pack_forget()

            canvas.get_tk_widget().pack()
            self.current_graph = canvas
            
    def save_graph(self): ## Saves the currently displayed graph
        if self.current_graph:
            file_path = filedialog.asksaveasfilename(defaultextension=".png")
            if file_path:
                self.current_graph.figure.savefig(file_path, dpi=1200)

if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
