#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         signup.py
# Program:      trackademic
# Desc:         Signup screen for new users to create an account
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     17-08-2025

# Import UI libraries
import customtkinter as ctk
from tkinter import messagebox

# Import custom modules
from utils import colour, account, validation, api
from utils.components import HEntry, clear_frame, SelectInput
from screens import signin, sidebar, calendar

# Global variables
entry_name:HEntry = None
entry_display:HEntry = None
entry_pass:HEntry = None
entry_confirm:HEntry = None
entry_school:SelectInput = None

# Function: construct
# Desc:     Build the signup screen
# Inputs:   app (ctk.CTk): The main app instance
# Outputs:  frame_main (ctk.CTkFrame): The main frame of the signup screen
def construct(app:ctk.CTk) -> ctk.CTkFrame:
    global entry_name, entry_display, entry_pass, entry_confirm, entry_school
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
    frame_form.rowconfigure(4, weight=1)
    frame_form.rowconfigure(5, weight=6)

    label_title = ctk.CTkLabel(frame_form, text="SIGN UP", anchor="center", fg_color="transparent", font=("sans-serif", 16, "bold"))
    label_title.grid(row=0, column=0, padx=10, sticky="sew")


    schools = api.get("schools")
    if schools:
        schools = schools.get("schools", [])
    entry_confirm = HEntry(frame_form, "Confirm Password", "Type here...", censor=True, on_submit=lambda: try_signup(app, frame_main))
    entry_confirm.grid(row=4, column=0, sticky="nsew", padx=30)
    entry_pass = HEntry(frame_form, "Password", "Type here...", censor=True, on_submit=entry_confirm.entry.focus)
    entry_pass.grid(row=3, column=0, sticky="nsew", padx=30)
    # Not using display names
    # entry_display = HEntry(frame_form, "Display Name", "Type here...", on_submit=entry_pass.entry.focus)
    # entry_display.grid(row=2, column=0, sticky="nsew", padx=30)
    frame_school = ctk.CTkFrame(frame_form, fg_color="transparent")
    frame_school.grid(row=2, column=0, sticky="nsew", padx=30)
    frame_school.rowconfigure(0, weight=1)
    frame_school.columnconfigure(0, weight=2)
    frame_school.columnconfigure(1, weight=7)

    label_school = ctk.CTkLabel(frame_school, text="School", anchor="e", fg_color="transparent", font=("sans-serif", 14), text_color=colour.TXT)
    label_school.grid(row=0, column=0, sticky="nsew", padx=10)
    entry_school = SelectInput(frame_school, schools, "Select school...")
    entry_school.configure(width=350, height=30)
    entry_school.grid_propagate(False)
    entry_school.label.grid_propagate(False)
    entry_school.grid(row=0, column=1, sticky="nsew")

    entry_name = HEntry(frame_form, "Username", "Type here...", on_submit=entry_pass.entry.focus)
    entry_name.grid(row=1, column=0, sticky="nsew", padx=30)


    button_submit = ctk.CTkButton(frame_form, fg_color=colour.ACC, text_color=colour.BG, text="SIGN UP", command=lambda: try_signup(app, frame_main))
    button_submit.grid(row=5, column=0, sticky="n")

    # Set tab order
    tab_order = (entry_name, entry_pass, entry_confirm)

    for element in tab_order:
        element.lift()

    # Build bottom text
    frame_bottom = ctk.CTkFrame(frame_main, fg_color="transparent")
    frame_bottom.grid(row=2, column=1, sticky="s", pady=10)
    

    label_bottom = ctk.CTkLabel(frame_bottom, text="Already have an account? ", anchor="e", fg_color="transparent", font=("sans-serif", 14))
    label_bottom.pack(side="left")
    
    button_bottom = ctk.CTkButton(frame_bottom, text="Sign in", anchor="w", fg_color="transparent", font=("sans-serif", 14, "underline"), height=14, width=1, text_color=colour.ACC, command=lambda: go_signin(app, frame_main))
    button_bottom.pack(side="left")

    return frame_main

# Function: try_signup
# Desc:     Attempt to sign up a user
# Inputs:   app (ctk.CTk): The main app instance
#           frame (ctk.CTkFrame): The main frame of the signup screen
# Outputs:  None
def try_signup(app:ctk.CTk, frame:ctk.CTkFrame):
    global entry_name, entry_display, entry_pass, entry_confirm, entry_school
    if not entry_pass:
        raise Exception("Event called before page finished loading")
    # display_name = entry_display.entry.get()
    username = entry_name.entry.get()
    password = entry_pass.entry.get()
    confirm_password = entry_confirm.entry.get()
    school = entry_school.get_value()
    
    # Validate username, password, school, and display name
    username_valid = validation.username(username)
    if not username_valid:
        return
    # Check passwords match
    if password != confirm_password:
        messagebox.showwarning(title="Warning", message="Passwords do not match!", icon="warning")
        return
    # display_name_valid = validation.display_name(display_name)
    # if not display_name_valid:
    #     return
    password_valid = validation.password(password)
    if not password_valid:
        return
    school_valid = validation.school(school)
    if not school_valid:
        return
    # Check username availability with API
    username_available = False
    fetched_user = api.get(f"users/{username}")
    print(fetched_user)
    if fetched_user.get("error") == "User not found":
        username_available = True
    elif any(key in fetched_user for key in ("username", "display_name", "password_hash")):
        messagebox.showwarning(title="Warning", message="Username already taken!", icon="warning")
        entry_name.entry.focus()
        return
    else:
        messagebox.showerror(title="Error", message="Network error!", icon="error")
        return

    # Actual signup
    success = account.signup(username, "", password, school)
    if success:
        clear_frame(frame)
        frame = calendar.construct(app)
        sidebar.construct(app, frame)
    else:
        messagebox.showerror(title="Error", message="Network error!",icon="error")
        return
    return

# Function: go_signin
# Desc:     Go to the signin screen
# Inputs:   app (ctk.CTk): The main app instance
#           frame (ctk.CTkFrame): The main frame of the signup screen
# Outputs:  None
def go_signin(app, frame):
    clear_frame(frame)
    frame = signin.construct(app)