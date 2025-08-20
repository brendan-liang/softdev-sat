#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File:         main.py
# Program:      trackademic
# Desc:         Academic organising and tracking tool! Main file and entry point
#               to run the app.

# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     16-08-2025

# Import UI libraries
import customtkinter as ctk
from tkinter import messagebox

# Import custom modules
from screens import calendar, signin, signup, sidebar
from utils import account, colour, icon

# Class:    App
# Desc:     Main app class that handles the UI and main loop
# Inherits: ctk.CTk (main app class from the customtkinter library)
class App(ctk.CTk):
    # Method:   __init__
    # Desc:     Initialise the app
    # Inputs:   title (str): Title of the app window
    # Outputs:  None
    def __init__(self, title:str="App") -> None:
        super().__init__()
        # Load icons
        icon.load_icons()
        # Setup window
        self.title(title)
        self.geometry("1280x720")
        self.minsize(1280, 720)
        self.frame_main = None
        # Build UI
        self.construct()

    # Method:   construct
    # Desc:     Build the UI of the app
    # Inputs:   None
    # Outputs:  None
    def construct(self) -> None:
        # Configure rows + columns
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=20)
        
        # Check signin
        signed_in = account.check_signin()
        if signed_in:
            sidebar.construct(self, self.frame_main)
            self.frame_main = calendar.construct(self)
        else:
            self.frame_main = signin.construct(self)
            
    # Method:   clear_frame
    # Desc:     Clear the main frame
    # Inputs:   None
    # Outputs:  None
    def clear_frame(self) -> None:
        if not self.frame_main:
            return

        for widget in self.frame_main.winfo_children():
            widget.destroy()

        self.frame_main.destroy()
    
# Create app object and run
app = App("trackademic")

app.mainloop()