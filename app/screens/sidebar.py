#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         sidebar.py
# Program:      trackademic
# Desc:         Sidebar for navigation between screens
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     16-08-2025

# Import UI libraries
import customtkinter as ctk

# Import custom modules
from screens import calendar, groups, settings
from utils import colour, icon
from utils.components import SidebarTab, SplashScreen, clear_frame

# Global variables
frame:ctk.CTkFrame = None
weight = 0

tabs = {}

# Constants
COLLAPSED_WEIGHT = 1
OPEN_WEIGHT = 2

# Function: get_mode
# Desc:     Get the current mode of the sidebar
# Inputs:   None
# Outputs:  str: The current mode of the sidebar ("open", "collapsed", "closed")
def get_mode() -> str:
    global weight
    if weight == 0:
        return "closed"
    elif weight == OPEN_WEIGHT:
        return "open"
    elif weight == COLLAPSED_WEIGHT:
        return "collapsed"

# Function: set_mode
# Desc:     Set the mode of the sidebar
# Inputs:   mode (str): The mode to set the sidebar to ("open", "collapsed", "closed")
#           app (ctk.CTk): The main app instance
# Outputs:  None
def set_mode(mode:str, app:ctk.CTk):
    global weight, frame, tabs

    if mode == "open":
        weight = OPEN_WEIGHT
        for tab in tabs.values():
            tab.collapse(False)
    elif mode == "collapsed":
        weight = COLLAPSED_WEIGHT
        for tab in tabs.values():
            tab.collapse(True)
    elif mode == "closed":
        weight = 0

    app.columnconfigure(0, weight=weight)
    if frame:
        frame.configure(width=weight * 200)

# Function: destroy
# Desc:     Destroy the sidebar frame and clear global variables
# Inputs:   None
# Outputs:  None
def destroy():
    global frame
    if frame:
        frame.destroy()
        frame = None

# Function: go
# Desc:     Navigate to a specific screen and update the sidebar
# Inputs:   screen (module): The screen module to navigate to
#           app (ctk.CTk): The main app instance
#           frame_main (ctk.CTkFrame): The main frame to clear and render
# Outputs:  None
def go(screen, app:ctk.CTk, frame_main:ctk.CTkFrame):
    global frame
    # cover = SplashScreen(frame_main)
    clear_frame(frame_main)
    frame_main = screen.construct(app)
    # Put cover and sidebar on top
    # cover.lift()
    frame.lift()

# Function: collapse_button
# Desc:     Toggle the sidebar between open and collapsed modes
# Inputs:   app (ctk.CTk): The main app instance
# Outputs:  None
def collapse_button(app:ctk.CTk):
    global weight
    if weight == OPEN_WEIGHT:
        print("closing")
        set_mode("collapsed", app)
    else:
        print("opening")
        set_mode("open", app)

# Function: dark_mode_button
# Desc:     Toggle the application between light and dark mode
# Inputs:   None
# Outputs:  None
def dark_mode_button():
    global tabs
    colour.toggle()
    if tabs["mode"]:
        tabs["mode"].configure(text=f"{ctk.get_appearance_mode().capitalize()} mode")

# Function: construct
# Desc:     Construct the sidebar and its elements
# Inputs:   app (ctk.CTk): The main app instance
#           frame_main (ctk.CTkFrame): The main frame to render the sidebar
# Outputs:  ctk.CTkFrame: The constructed sidebar frame
def construct(app:ctk.CTk, frame_main:ctk.CTkFrame) -> ctk.CTkFrame:
    global frame, tabs
    frame = ctk.CTkFrame(app, fg_color=colour.BG)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.grid_propagate(False)
    # Configure rows/columns

    # Build elements
    button_collapse = ctk.CTkButton(frame, image=icon.icon("menu"), text="", command=lambda: collapse_button(app), width=10, fg_color="transparent", height=50)
    button_collapse.pack(side="top", anchor="ne", padx=5, pady=5)
    
    tab_calendar = SidebarTab(frame, "Calendar", "calendar", lambda: go(calendar, app, frame_main))
    tab_calendar.pack(side="top", fill="x", padx=5, pady=5)
    tab_groups = SidebarTab(frame, "Classes", "class", lambda: go(groups, app, frame_main))
    tab_groups.pack(side="top", fill="x", padx=5, pady=5)

    tab_settings = SidebarTab(frame, "Settings","settings", lambda: go(settings, app, frame_main))
    tab_settings.pack(side="bottom", fill="x", padx=5, pady=5)

    tab_mode = SidebarTab(frame, f"{ctk.get_appearance_mode().capitalize()} mode", "mode", dark_mode_button)
    tab_mode.pack(side="bottom", fill="x", padx=5, pady=5)

    tabs["calendar"] = tab_calendar
    tabs["groups"] = tab_groups
    tabs["settings"] = tab_settings
    tabs["mode"] = tab_mode
    
    return frame

# Function: highlight_tab
# Desc:     Highlight a specific tab in the sidebar
# Inputs:   tab (str): The name of the tab to highlight
# Outputs:  bool: Whether the tab was successfully highlighted
def highlight_tab(tab:str):
    global tabs
    if tab in tabs:
        for key in tabs:
            tabs[key].highlight(False)
        tabs[tab].highlight(True)
        return True
    else:
        return False