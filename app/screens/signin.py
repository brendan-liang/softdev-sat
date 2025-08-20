#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         signin.py
# Program:      trackademic
# Desc:         Signin screen for returning users
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     16-08-2025

# Import UI libraries
import customtkinter as ctk
from tkinter import messagebox

# Import custom modules
from utils import account, colour
from utils.components import HEntry, clear_frame
from screens import signup, calendar, sidebar

# Global variables
entry_name:HEntry = None
entry_pass:HEntry = None

# Function: construct
# Desc:     Build the signin screen
# Inputs:   app (ctk.CTk): The main app instance
# Outputs:  frame_main (ctk.CTkFrame): The main frame of the screen
def construct(app:ctk.CTk) -> ctk.CTkFrame:
    global entry_pass, entry_name
    
    # Crush sidebar
    sidebar.set_mode("closed", app)
    # Configure frame
    frame_main = ctk.CTkFrame(app, fg_color=colour.BG)
    frame_main.grid(row=0, column=1, sticky="nsew")

    frame_main.columnconfigure(0, weight=2)
    frame_main.columnconfigure(1, weight=1)
    frame_main.columnconfigure(2, weight=2)

    frame_main.rowconfigure(0, weight=1)
    frame_main.rowconfigure(1, weight=2)
    frame_main.rowconfigure(2, weight=1)

    # Build form frame
    frame_form = ctk.CTkFrame(frame_main, fg_color="transparent", border_color=colour.GREY, border_width=2)
    frame_form.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    frame_form.columnconfigure(0, weight=1)
    frame_form.rowconfigure(0, weight=6)
    frame_form.rowconfigure(1, weight=1)
    frame_form.rowconfigure(2, weight=1)
    frame_form.rowconfigure(3, weight=1)
    frame_form.rowconfigure(4, weight=6)

    label_title = ctk.CTkLabel(frame_form, text="SIGN IN", anchor="center", fg_color="transparent", font=("sans-serif", 16, "bold"), text_color=colour.TXT)
    label_title.grid(row=0, column=0, padx=10, sticky="sew")

    entry_pass = HEntry(frame_form, "Password", "Type here...", censor=True, on_submit=lambda: try_signin(app, frame_main))
    entry_pass.grid(row=2, column=0, sticky="nsew", padx=30)
    entry_name = HEntry(frame_form, "Username", "Type here...", on_submit=entry_pass.entry.focus)
    entry_name.grid(row=1, column=0, sticky="nsew", padx=30)
    
    entry_pass.lift()

    button_submit = ctk.CTkButton(frame_form, fg_color=colour.ACC, text_color=colour.BG, text="SIGN IN", command=lambda: try_signin(app, frame_main))
    button_submit.grid(row=4, column=0, sticky="n")

    # Build bottom text
    frame_bottom = ctk.CTkFrame(frame_main, fg_color="transparent")
    frame_bottom.grid(row=2, column=1, sticky="s", pady=10)
    

    label_bottom = ctk.CTkLabel(frame_bottom, text="Don't have an account? ", anchor="e", fg_color="transparent", font=("sans-serif", 14), text_color=colour.TXT)
    label_bottom.pack(side="left")
    
    button_bottom = ctk.CTkButton(frame_bottom, text="Sign up", anchor="w", fg_color="transparent", font=("sans-serif", 14, "underline"), height=14, width=1, text_color=colour.ACC, command=lambda: go_signup(app, frame_main), hover_color=colour.BG)
    button_bottom.pack(side="left")

    return frame_main

# Function: validate_pass
# Desc:     Validate the password entry
# Inputs:   app (ctk.CTk): The main app instance
#           frame (ctk.CTkFrame): The main frame of the signin screen
# Outputs:  None
def validate_pass(app:ctk.CTk, frame:ctk.CTkFrame):
    # Validation
    password = entry_pass.entry.get()
    if not password:
        messagebox.showwarning(title="Warning", message="Password cannot be empty!", icon="warning")
        entry_pass.entry.focus()
        return
    # Attempt to signin
    try_signin(app, frame)
    return

# Function: validate_username
# Desc:     Validate the username entry
# Inputs:   nextEntry (HEntry): The next entry to focus on
# Outputs:  None
def validate_username(nextEntry:HEntry):
    # Validation
    username = entry_name.entry.get()
    if not username:
        messagebox.showwarning(title="Warning", message="Username cannot be empty!", icon="warning")
        entry_name.entry.focus()
        return
    # Move user's cursor
    nextEntry.entry.focus()
    return

# Function: try_signin
# Desc:     Attempt to sign in a user
# Inputs:   app (ctk.CTk): The main app instance
#           frame (ctk.CTkFrame): The main frame of the signin screen
# Outputs:  None
def try_signin(app:ctk.CTk, frame:ctk.CTkFrame) -> None:
    global entry_pass, entry_name
    if not entry_pass:
        raise Exception("Event called before page finished loading")
    username = entry_name.entry.get()
    password = entry_pass.entry.get()

    # Validate username, password
    if not username:
        messagebox.showwarning(title="Warning", message="Username cannot be empty!", icon="warning")
        return
    if not password:
        messagebox.showwarning(title="Warning", message="Password cannot be empty!", icon="warning")
        return
    
    success, user = account.signin(username, password=password)
    if not success:
        messagebox.showerror(title="Error", message="Incorrect username/password!",icon="error")
        return
    clear_frame(frame)
    sidebar.construct(app, frame)
    frame = calendar.construct(app)

# Function: go_signup
# Desc:     Go to the signup screen
# Inputs:   app (ctk.CTk): The main app instance
#           frame (ctk.CTkFrame): The main frame of the signin screen
# Outputs:  None
def go_signup(app:ctk.CTk, frame:ctk.CTkFrame) -> None:
    clear_frame(frame)
    frame = signup.construct(app)