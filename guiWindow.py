import tkinter as tk

import win32gui
import d3dshot as ds
import cv2 as cv


class WindowSelection():
   # vars
   window = ''
   root=tk.Tk()
   root_frame = tk.Frame(root)
   # window list
   window_frame = tk.Frame(root_frame)
   window_sub_frame = tk.Frame(window_frame)
   listbox = tk.Listbox(window_sub_frame)
   scrollbar = tk.Scrollbar(window_sub_frame)

   # trim values
   trim_l = 0
   trim_r = 0
   trim_t = 0
   trim_b = 0
   cross_x = 0
   cross_y = 0

   # Window and Crosshair trims
   entry_frame = tk.Frame(root_frame)
   entry_sub_frame = tk.Frame(entry_frame)
   trim_frame = tk.Frame(entry_sub_frame)
   cross_frame = tk.Frame(entry_sub_frame)
   # trim window entry boxes
   trim_l_entry = tk.Entry(trim_frame)
   trim_r_entry = tk.Entry(trim_frame)
   trim_t_entry = tk.Entry(trim_frame)
   trim_b_entry = tk.Entry(trim_frame)
   # trim window labels
   trim_l_label = tk.Label(trim_frame, text='Trim Window Left')
   trim_r_label = tk.Label(trim_frame, text='Trim Window Right')
   trim_t_label = tk.Label(trim_frame, text='Trim Window Top')
   trim_b_label = tk.Label(trim_frame, text='Trim Window Bottom')
   # trim crosshair entry
   cross_x_entry = tk.Entry(cross_frame)
   cross_y_entry = tk.Entry(cross_frame)
   # trim crosshair labels
   cross_x_label = tk.Label(cross_frame, text='Adjust Crosshair X')
   cross_y_label = tk.Label(cross_frame, text='Adjust Crosshair Y')

   def __init__(self):
      # main window settings
      self.root.title('EyeAimer Configuration')
      self.root.geometry("700x400")

      # screenshot capture (SET THIS UP)

      # connect scrollbar to listbox
      self.listbox.config(yscrollcommand=self.scrollbar.set)
      self.scrollbar.config(command=self.listbox.yview)

      # get list of window names
      windows = self.list_window_names()
      windows = list(filter(None, windows))

      # add window names to listbox
      for values in windows:
         self.listbox.insert(tk.END, values)

      # BUTTONS
      # create 'choose window' button
      self.go_button = tk.Button(self.window_frame, text='Select Window', bd = '5', command=lambda: self.launch_trim_window())
      # create 'Apply Trims' button
      self.trim_button = tk.Button(self.entry_frame, text='Apply', bd = '5', command=lambda: self.get_trim_selection())
      # create 'Done' button
      self.continue_button = tk.Button(self.root, text='Done', bd = '5', command=lambda: self.continue_program())

      # PACKING
      # pack into trim frame
      self.trim_l_label.pack(side=tk.TOP)
      self.trim_l_entry.pack(side=tk.TOP)
      self.trim_r_label.pack(side=tk.TOP)
      self.trim_r_entry.pack(side=tk.TOP)
      self.trim_t_label.pack(side=tk.TOP)
      self.trim_t_entry.pack(side=tk.TOP)
      self.trim_b_label.pack(side=tk.TOP)
      self.trim_b_entry.pack(side=tk.TOP)
      # pack into cross frame
      self.cross_x_label.pack(side=tk.TOP)
      self.cross_x_entry.pack(side=tk.TOP)
      self.cross_y_label.pack(side=tk.TOP)
      self.cross_y_entry.pack(side=tk.TOP)

      # pack into window sub frame
      self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
      self.scrollbar.pack(side=tk.LEFT, fill=tk.BOTH)
      # pack into window frame
      self.window_sub_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
      self.go_button.pack(side=tk.TOP, fill=tk.X, expand=True)

      # pack into entry sub frame
      self.trim_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
      self.cross_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
      # pack into entry frame
      self.entry_sub_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
      self.trim_button.pack(side=tk.TOP, fill=tk.X, expand=True)

      # pack into root frame
      self.window_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
      self.entry_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

      # pack into root
      self.root_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
      self.continue_button.pack(side=tk.TOP, fill=tk.X, expand=True)

      # start dialog
      self.root.mainloop()
      
      return
   
   def list_window_names(self):
      window_list = []
      def winEnumHandler(hwnd, ctx):
         if win32gui.IsWindowVisible(hwnd):
               window_list.append(str(win32gui.GetWindowText(hwnd)))
      win32gui.EnumWindows(winEnumHandler, None)
      return window_list

   def get_window_selection(self):
      selection = self.listbox.curselection()
      try:
         sel_value = self.listbox.get(selection[0])
      except:
         print("No Window Selected")
      if selection:
         print(f"Selected Window: {sel_value}")
         self.window=sel_value

      return

   def launch_trim_window(self):
      # get window
      self.get_window_selection()
      # launch viewer window
      self.run_trim_window()
      return

   def run_trim_window(self):
      

      return

   def get_trim_selection(self):
      if self.trim_l_entry.get():
         self.trim_l = self.trim_l_entry.get()
      if self.trim_r_entry.get():
         self.trim_r = self.trim_r_entry.get()
      if self.trim_t_entry.get():
         self.trim_t = self.trim_t_entry.get()
      if self.trim_b_entry.get():
         self.trim_b = self.trim_b_entry.get()
      if self.cross_x_entry.get():
         self.cross_x = self.cross_x_entry.get()
      if self.cross_y_entry.get():
         self.cross_y = self.cross_y_entry.get()

      return
      
   def continue_program(self):
      self.root.destroy()

      return
