#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         settings.py
# Program:      trackademic
# Desc:         Settings screen for user account management
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     17-08-2025

import customtkinter as ctk
from screens import sidebar, signin
from utils import colour, icon, api, account, validation, config
from utils.components import clear_frame, SelectInput
from tkinter import messagebox

# Globals
entry_username: ctk.CTkEntry = None
entry_school: SelectInput = None

def logout(app:ctk.CTk, frame_main:ctk.CTkFrame):
    # Clear local user data
    config.write({
        "loggedIn": False,
        "loggedInUser": None
    })
    sidebar.set_mode("closed", app)
    sidebar.destroy()
    clear_frame(frame_main)
    frame_main = signin.construct(app)
    # Render login screen
    return

def save_settings():
    global entry_username, entry_school
    new_school = entry_school.get_value()
    # new_username = entry_username.get()

    # Validate username and school
    # username_valid = validation.username(new_username)
    # if not username_valid:
    #     return
    school_valid = validation.school(new_school)
    if not school_valid:
        return
    # Further school validation
    valid_schools = api.get("schools")
    if valid_schools.get("schools"):
        valid_schools = valid_schools.get("schools", [])
    else:
        messagebox.showwarning("Warning", "Error getting schools. Please try again later.", icon="warning")
        return
    
    if new_school not in valid_schools:
        messagebox.showwarning("Warning", "Please select a valid school!", icon="warning")
        return
    # Update user data
    account.pull_updates()
    user_data = account.get()
    user_data["school"] = new_school
    success = api.post("users/update", user_data)
    if not success:
        messagebox.showerror("Error", "Failed to update user data. Please try again later.", icon="error")
        return
    # Update config
    account.pull_updates()

def construct(app:ctk.CTk) -> ctk.CTkFrame:
    global entry_username, entry_school
    # Main frame
    frame_main = ctk.CTkFrame(app, fg_color=colour.BG)
    frame_main.grid(row=0, column=1, sticky="nsew")

    frame_form = ctk.CTkFrame(frame_main, fg_color="transparent", border_color=colour.GREY, border_width=2)
    frame_form.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5)

    # Form widgets
    # label_username = ctk.CTkLabel(frame_form, text="Username", anchor="w", font=("sans-serif", 18, "bold"))
    # label_username.pack(side="top", fill="x", padx=30, pady=(30, 5))
    # entry_username = ctk.CTkEntry(frame_form, placeholder_text="", font=("sans-serif", 18))
    # entry_username.pack(side="top", fill="x", padx=30, pady=5)

    schools = api.get("schools")
    if schools:
        schools = schools.get("schools", [])
    else:
        schools = []
    label_school = ctk.CTkLabel(frame_form, text="School", anchor="w", font=("sans-serif", 18))
    label_school.pack(side="top", fill="x", padx=30, pady=(30, 5))
    entry_school = SelectInput(frame_form, schools, "")
    entry_school.label.configure(font=("sans-serif", 18))
    entry_school.pack(side="top", fill="x", padx=30, pady=5)

    frame_buttons = ctk.CTkFrame(frame_form, fg_color="transparent")
    frame_buttons.pack(side="top", fill="x", padx=30, pady=(5, 30))

    button_save = ctk.CTkButton(frame_buttons, text="Save", command=save_settings, fg_color=colour.ACC, width=100, font=("sans-serif", 16, "bold"))
    button_save.pack(side="right", padx=5)

    button_logout = ctk.CTkButton(frame_buttons, text="Logout", command=lambda: logout(app, frame_main), fg_color="#f44336", width=100, font=("sans-serif", 16, "bold"))
    button_logout.pack(side="right", padx=5)

    # Fill widgets
    user = account.get()
    if user:
        entry_school.set_value(user.get("school", ""))
    # Construct sidebar
    sidebar_weight = sidebar.get_mode()
    sidebar.set_mode("open" if sidebar_weight == "closed" else sidebar_weight, app)
    sidebar.highlight_tab("settings")
    
    return frame_main