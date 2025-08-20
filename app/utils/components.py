#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         utils/components.py
# Program:      trackademic
# Desc:         Custom components for the Trackademic app
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     16-08-2025

# Import UI libraries
import customtkinter as ctk
from tkinter import messagebox, Event

# Import custom modules
from utils import colour, icon, api

# Import other libraries
from collections.abc import Callable
from datetime import date, time
from time import sleep
from threading import Timer
from ctypes import WinDLL

# Function: clear_frame
# Desc:     Clears a ctk Frame
# Inputs:   frame (ctk.CTkFrame): The frame to clear
# Outputs:  None
def clear_frame(frame:ctk.CTkFrame) -> None:
    if not frame:
        return
    
    for widget in frame.winfo_children():
        widget.destroy()

# Class:    HEntry
# Desc:     Horizontal entry with label
# Inherits: ctk.CTkFrame (basic frame class from customtkinter library)
class HEntry(ctk.CTkFrame):
    # Method:   __init__
    # Desc:     Initialise the entry
    # Inputs:   root (ctk.CTkBaseClass): The parent widget
    #           text (str): The label text
    #           placeholder (str): Placeholder text for the entry
    #           *args: Additional arguments for ctk.CTkFrame (also forces followingarguments to be keyword-only)
    #           censor (bool): Whether to censor sensitive input e.g. passwords (default: False)
    #           on_submit (Callable): Function to call when the user submits the entry (default: None)
    #           on_key (Callable): Function to call when a key is pressed in the entry
    # Outputs:  None
    def __init__(self, root:ctk.CTkBaseClass, text:str, placeholder:str, *args, censor:bool=False, on_submit:Callable=None, on_key:Callable=None) -> None:
        super().__init__(root, fg_color="transparent")
        # Configure grid
        self.grid(padx=10)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)

        # Properties
        self.value = ""
        self.censor = censor

        self.on_submit = on_submit
        self.on_key = on_key

        # Elements
        self.label = ctk.CTkLabel(self, text=text, font=("sans-serif", 14), text_color=colour.TXT, width=120, anchor="e")
        self.label.grid(row=0, column=0, padx=5, sticky="e")

        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder, fg_color=colour.BG2, height=14, border_color=colour.GREY, border_width=1)
        if self.censor:
            self.entry.configure(show="*")
    
        self.entry.bind("<KeyPress>", self.handle_update)
        self.entry.grid(row=0, column=1, sticky="nsew", pady=10)

        return
    
    # Method:   handle_update
    # Desc:     Handle key updates in the entry
    # Inputs:   event (Event): The key event
    # Outputs:  None
    def handle_update(self, event:Event) -> None:
        if self.on_key:
            self.on_key(event)
        if event.char in ["\r", "\n"] and self.on_submit:
            self.on_submit()
        return
    
# Class:    SidebarTab
# Desc:     Clickable tab with icon, highlighting and text for the sidebar
# Inherits: ctk.CTkButton (basic button class from customtkinter library)
class SidebarTab(ctk.CTkButton):
    # Method:   __init__
    # Desc:     Initialise the sidebar tab
    # Inputs:   root (ctk.CTkBaseClass): The parent widget
    #           text (str): The text to display on the tab
    #           icon_name (str): The name of the icon to display
    #           handler (Callable): Function to call when the tab is clicked
    # Outputs:  None
    def __init__(self, root:ctk.CTkBaseClass, text:str, icon_name:str, handler):
        # Declare properties
        self.highlighted = False
        self.text = text
        # The GUI part
        self.light_icon = icon.icon(icon_name)
        self.dark_icon = icon.icon(icon_name)
        super().__init__(root,
                         fg_color="transparent",
                         text=text, command=handler, 
                         image=self.light_icon,
                         compound="left",
                         anchor="w", font=("sans-serif", 18),
                         text_color=colour.TXT,
                         height=50,
                         width=1
                        )
        
        self.highlight_tab = ctk.CTkFrame(self, fg_color=colour.ACC, width=5)
        self.highlight_tab.place(x=0,y=0, relheight=1)

        # Not highlighted by default (will be manually set by the page renderer)
        self.highlight(False)
        return
    
    # Method:   highlight
    # Desc:     Highlight / unhighlight this tab (with the accent colour bar)
    # Inputs:   highlight (bool): Whether to highlight the tab
    # Outputs:  None
    def highlight(self, highlight:bool):
        self.highlighted = highlight
        self.highlight_tab.configure(fg_color=(colour.ACC if highlight else "transparent"))

    # Method:   collapse
    # Desc:     Collapse the tab when collapsing the sidebar (icons only)
    # Inputs:   collapsed (bool): Whether to collapse or uncollapse
    def collapse(self, collapsed:bool):
        self.configure(text="" if collapsed else self.text)

# Come back if I have time to implement a custom message box (regular tkinter one works for now)
# class MessageBox(ctk.CTkFrame):
#     def __init__(self, root:ctk.CTkBaseClass, title:str, desc:str, icon_name:str, mode:int, handler):
#         super().__init__(root,
#                          fg_color=colour.BG,
#                          bg_color="transparent",
#                          border_color=colour.GREY,
#                          border_width=2,
#                          width=300,
#                          height=350
#                          )
#         self.place(relx=0.5, rely=0.5, anchor="center")

#         self.rowconfigure(0, weight=1)
#         self.rowconfigure(1, weight=1)
#         self.rowconfigure(2, weight=1)
#         self.columnconfigure(0, weight=1)

#         label_title = ctk.CTkLabel(self, text=title)
#         label_title.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# Class:    SplashScreen
# Desc:     Splash screen that appears when the app is rendering
# Inherits: ctk.CTkFrame (basic frame class from customtkinter library)
class SplashScreen(ctk.CTkFrame):
    # doesnt work for some reason
    # when new widgets are being rendered, they render on top of any existing widgets (e.g. splash screen)
    # this means that the splash screen is not visible when the app is loading. fix later, but not a priority.

    # Method:   __init__
    # Desc:     Initialise the splash screen
    # Inputs:   root (ctk.CTkBaseClass): The parent widget
    # Outputs:  None
    def __init__(self, root:ctk.CTkBaseClass):
        super().__init__(root, fg_color=colour.BG, corner_radius=0)
        self.place(relwidth=1,relheight=1,relx=0,rely=0)

        # Create delete thread to close splash screen after a short delay
        self.delete_timer = Timer(0.2, self.delete)
        self.delete_timer.start()

    # Method:   delete
    # Desc:     Delete the splash screen (for use as a thread handler)
    def delete(self):
        self.destroy()

# Class:    SelectInput
# Desc:     Custom combo box with dropdown for selecting options
# Inherits: ctk.CTkFrame (basic frame class from customtkinter library)
class SelectInput(ctk.CTkFrame):
    # Method:   __init__
    # Desc:     Initialise the select input
    # Inputs:   root (ctk.CTkBaseClass): The parent widget
    #           values (list[str]): List of values to display in the dropdown
    #           default_value (str): Default value to display in the input
    #           on_change (Callable): Function to call when the value changes (default: None)
    def __init__(self, root:ctk.CTkBaseClass, values:list[str], default_value:str, on_change:Callable=None, hidden_values:list[str]=None):
        super().__init__(root, fg_color=colour.BG2)

        # Add default callable
        if not on_change:
            on_change = lambda *args: None
        
        # Add alternate values for retrieving
        self.hidden_values = None
        if hidden_values and len(hidden_values) == len(values):
            self.hidden_values= hidden_values

        # Assign properties
        self.value_widgets = []
        self.values = values
        self.on_change = on_change
        self.default_value = default_value

        # UI widgets
        self.scrollable_frame = None  # For dropdown scrolling
        self.label = ctk.CTkLabel(self, text=default_value, text_color=colour.TXT, anchor="w", width=10)
        self.label.pack(side="left", fill="both", expand=True, padx=5, pady=1)
        self.label.bind("<Button-1>", lambda event: self.toggle_dropdown())

        self.button = ctk.CTkButton(self, text="▼", command=self.toggle_dropdown, width=20, bg_color="transparent", fg_color="transparent", text_color=colour.TXT, border_width=0)
        self.button.pack(side="right", fill="y", padx=2, pady=2)

        # Find the top-level window for dropdown placement
        self.top_level = self.winfo_toplevel()

        self.dropdown = ctk.CTkFrame(self.top_level, fg_color=colour.BG2, border_color=colour.GREY, border_width=1, corner_radius=5)
        self.dropdown.bind("")
        self.dropdown.place_forget()
        # Prevent the dropdown from resizing to fit its contents (keep it at calculated size)
        self.dropdown.pack_propagate(False)

        # Bind events to close dropdown
        self._top_level_binds = []
        self._self_binds = []

        self.enabled(True)

        return
    
    def enabled(self, enabled:bool):
        if enabled:
            self.label.configure(state="normal")
            self.button.configure(state="normal")
        else:
            self.label.configure(state="disabled")
            self.button.configure(state="disabled")
    
    # Method:   close_dropdown
    # Desc:     Close the dropdown when clicking outside or pressing escape, and unbind the handlers
    # Inputs:   event (Event): The event that triggered the close
    # Outputs:  None
    def close_dropdown(self, event:Event):
        # Only run if the dropdown is open
        if self.dropdown.winfo_ismapped():
            # Remove widget from screen
            self.dropdown.place_forget()
            # Unbind all handlers
            for bind in self._top_level_binds:
                self.top_level.unbind(bind)
            for bind in self._self_binds:
                self.dropdown.unbind(bind)
            self._top_level_binds.clear()
            self._self_binds.clear()
        return

    # Method:   toggle_dropdown
    # Desc:     Toggle the dropdown visibility
    # Inputs:   None
    # Outputs:  None
    def toggle_dropdown(self):
        if self.dropdown.winfo_ismapped():
            # Close the dropdown if it's already open
            self.close_dropdown(None)
        else:
            # Clear existing value widgets and recreate them
            for widget in self.dropdown.winfo_children():
                widget.destroy()
            self.value_widgets.clear()
            if self.scrollable_frame and self.scrollable_frame.winfo_ismapped():
                self.scrollable_frame.place_forget()
                self.scrollable_frame.destroy()
            self.scrollable_frame = None

            # Calculate position and size for the dropdown
            # I'm not sure why 0.8 is needed, but it works (stops it from being too far down/right)
            # Calculate DPI, as that affects the positioning of root widgets
            user32 = WinDLL("user32")
            dpi = user32.GetDpiForWindow(self.top_level.winfo_id())
            scale_ratio = int((92 / dpi + (1/30)) * 100) / 100
            x = (self.winfo_rootx() - self.top_level.winfo_rootx()) * scale_ratio
            y = (self.winfo_rooty() - self.top_level.winfo_rooty() + self.winfo_height()) * scale_ratio 
            width = self.winfo_width() * scale_ratio
            max_height = self.top_level.winfo_height() * 0.5  # Half screen height
            dropdown_height = len(self.values) * 34  # Approximate height per item

            # Check if we need scrolling
            needs_scrolling = dropdown_height > max_height
            height = min(dropdown_height, max_height)

            if (y + height) / scale_ratio > self.top_level.winfo_height():
                y -= ((y + height) / scale_ratio - self.top_level.winfo_height()) * scale_ratio + 10
            
            # Configure and place the dropdown
            self.dropdown.configure(width=width, height=height)
            self.dropdown.place(x=x, y=y, anchor="nw")
            self.dropdown.lift()

            if needs_scrolling:
                # Create scrollable frame for dropdown items
                self.scrollable_frame = ctk.CTkScrollableFrame(self.dropdown, fg_color=colour.BG2, corner_radius=0)
                self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
                
                # Add values to the scrollable frame
                for value in self.values:
                    value_widget = ctk.CTkButton(self.scrollable_frame, text=value, text_color=colour.TXT, anchor="w", 
                                               command=lambda v=value: self.handle_change(v), width=1, 
                                               fg_color=colour.BG2, corner_radius=0, height=30)
                    self.value_widgets.append(value_widget)
                    value_widget.pack(fill="x", padx=2, pady=2)
            else:
                # Add values directly to the dropdown (no scrolling needed)
                for value in self.values:
                    value_widget = ctk.CTkButton(self.dropdown, text=value, text_color=colour.TXT, anchor="w", 
                                               command=lambda v=value: self.handle_change(v), width=1, 
                                               fg_color=colour.BG2, corner_radius=0, height=30)
                    self.value_widgets.append(value_widget)
                    value_widget.pack(fill="x", padx=2, pady=2)

            self.dropdown.focus_set()

            # Bindings (events that will close the dropdown)
            self._top_level_binds.append(self.top_level.bind("<Button-1>", self.close_dropdown))
            self._self_binds.append(self.dropdown.bind("<FocusOut>", self.close_dropdown))
            self._top_level_binds.append(self.top_level.bind("<Escape>", self.close_dropdown))
        return
    
    # Method:   handle_change
    # Desc:     Handle the change of value when a dropdown item is clicked
    # Inputs:   value (str): The value that was clicked
    # Outputs:  None
    def handle_change(self, value:str):
        self.label.configure(text=value)
        self.on_change()
        self.close_dropdown(None)
        return
    
    # Method:   get_value
    # Desc:     Get the currently selected value
    # Inputs:   None
    # Outputs:  str: The currently selected value
    def get_value(self):
        text = self.label.cget("text")
        if self.hidden_values and text in self.values:
            print("accessing alternate values")
            index = self.values.index(text)
            return self.hidden_values[index]
        return text
    
    # Method:   set_value
    # Desc:     Set the value of the select input
    # Inputs:   value (str): The value to set
    # Outputs:  None
    def set_value(self, value:str):
        if value in self.values:
            self.handle_change(value)
        else:
            raise ValueError(f"Value '{value}' not in available options: {self.values}")
        return

# Class:    TimeInput
# Desc:     Custom time input with hour, minute and AM/PM selection
# Inherits: ctk.CTkFrame (basic frame class from customtkinter library)
class TimeInput(ctk.CTkFrame):
    # Method:   __init__
    # Desc:     Initialise the time input
    # Inputs:   root (ctk.CTkBaseClass): The parent widget
    # Outputs:  None
    def __init__(self, root:ctk.CTkBaseClass):
        super().__init__(root, fg_color=colour.BG2, corner_radius=10, border_color=colour.GREY, border_width=1, bg_color="transparent")
        # Configure rows and columns
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)
        self.columnconfigure(3, weight=3)

        self.entry_hour = ctk.CTkEntry(self, fg_color=colour.BG2, border_color=colour.BG2, justify="right", width=30)
        self.entry_hour.grid(row=0, column=0, sticky="nsew")
        self.entry_hour.bind("<FocusOut>", self.validate_hour)

        label_colon = ctk.CTkLabel(self, text=":", text_color=colour.TXT)
        label_colon.grid(row=0, column=1, sticky="nsew")

        self.entry_minute = ctk.CTkEntry(self, fg_color=colour.BG2, border_color=colour.BG2, justify="left", width=30)
        self.entry_minute.grid(row=0, column=2, sticky="nsew")
        self.entry_minute.bind("<FocusOut>", self.validate_minute)

        self.entry_am_pm = SelectInput(self, values=["AM", "PM"], default_value="AM")
        self.entry_am_pm.grid(row=0, column=3, sticky="nsew")

        return
    
    # Method:   validate_hour
    # Desc:     Validate the hour entry, and fix its formatting
    # Inputs:   event (Event): The focus out event that triggers validation
    # Outputs:  bool: Whether the hour is valid
    def validate_hour(self, event:Event):
        hour_str = self.entry_hour.get()
        # Validation
        if not hour_str:
            return False
        if not hour_str.isdigit() or not (0 <= int(hour_str) <= 23):
            messagebox.showwarning("Invalid Hour", "Please enter a valid hour (0-23).")
            self.entry_hour.delete(0, "end")
            self.entry_hour.focus_set()
            return False
        # Fix format
        if hour_str >= "12":
            self.entry_am_pm.handle_change("PM")
            self.entry_hour.delete(0, "end")
            self.entry_hour.insert(0, str(int(hour_str) - 12))
            hour_str = self.entry_hour.get()
        if len(hour_str) > 2:
            self.entry_hour.delete(0, (len(hour_str) - 2))
        if len(hour_str) == 1:
            self.entry_hour.insert(0, "0")
        return True

    # Method:   validate_minute
    # Desc:     Validate the minute entry, and fix its formatting
    # Inputs:   event (Event): The focus out event that triggers validation
    # Outputs:  bool: Whether the minute is valid
    def validate_minute(self, event:Event):
        minute_str = self.entry_minute.get()
        # Validation
        if not minute_str:
            return False
        if not minute_str.isdigit() or not (0 <= int(minute_str) <= 59):
            messagebox.showwarning("Invalid Minute", "Please enter a valid minute (0-59).")
            self.entry_minute.delete(0, "end")
            self.entry_minute.focus_set()
            return False
        # Fix format
        if len(minute_str) > 2:
            self.entry_minute.delete(0, (len(minute_str) - 2))
        if len(minute_str) == 1:
            self.entry_minute.insert(0, "0")
        return True
    
    # Not used
    def get_value(self):
        hour = self.entry_hour.get()
        minute = self.entry_minute.get()
        am_pm = self.entry_am_pm.get_value()
        
# Class:    DateInput
# Desc:     Custom date input with day, month and year selection
# Inherits: ctk.CTkFrame (basic frame class from customtkinter library)            
class DateInput(ctk.CTkFrame):
    # Method:   __init__
    # Desc:     Initialise the date input
    # Inputs:   root (ctk.CTkBaseClass): The parent widget
    # Outputs:  None
    def __init__(self, root:ctk.CTkBaseClass, on_change:Callable=None):
        super().__init__(root, fg_color=colour.BG2, corner_radius=10, border_color=colour.GREY, border_width=1, bg_color="transparent")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=3)

        self.entry_day = ctk.CTkEntry(self, fg_color=colour.BG2, border_color=colour.BG2, justify="center", width=30)
        self.entry_day.grid(row=0, column=0, sticky="nsew")
        self.entry_day.bind("<FocusOut>", self.validate_day)

        label_slash1 = ctk.CTkLabel(self, text="/", text_color=colour.TXT)
        label_slash1.grid(row=0, column=1, sticky="nsew")

        self.entry_month = ctk.CTkEntry(self, fg_color=colour.BG2, border_color=colour.BG2, justify="center", width=30)
        self.entry_month.grid(row=0, column=2, sticky="nsew")
        self.entry_month.bind("<FocusOut>", self.validate_month)

        label_slash2 = ctk.CTkLabel(self, text="/", text_color=colour.TXT)
        label_slash2.grid(row=0, column=3, sticky="nsew")

        self.entry_year = ctk.CTkEntry(self, fg_color=colour.BG2, border_color=colour.BG2, justify="center", width=30)
        self.entry_year.grid(row=0, column=4, sticky="nsew")
        self.entry_year.bind("<FocusOut>", self.validate_year)

        self.on_change = on_change

    # Method:   validate_day
    # Desc:     Validate the day entry, and fix its formatting.
    # Inputs:   event (Event): The focus out event that triggers validation
    # Outputs:  bool: Whether the day is valid
    def validate_day(self, event:Event):
        day_str = self.entry_day.get()
        # Validation
        if not day_str:
            self.on_change()
            return False
        if not day_str.isdigit() or not (1 <= int(day_str) <= 31):
            messagebox.showwarning("Invalid Day", "Please enter a valid day (1-31).")
            self.entry_day.delete(0, "end")
            self.entry_day.focus_set()
            return False
        # Fix format
        if len(day_str) == 1:
            self.entry_day.insert(0, 0)
        self.on_change()
        return True

    # Method:   validate_month
    # Desc:     Validate the month entry, and fix its formatting.
    # Inputs:   event (Event): The focus out event that triggers validation
    # Outputs:  bool: Whether the month is valid
    def validate_month(self, event:Event):
        month_str = self.entry_month.get()
        # Validation
        if not month_str:
            self.on_change()
            return False
        if not month_str.isdigit() or not (1 <= int(month_str) <= 12):
            messagebox.showwarning("Invalid Month", "Please enter a valid month (1-12).")
            self.entry_month.delete(0, "end")
            self.entry_month.focus_set()
            return False
        # Fix format
        if len(month_str) == 1:
            self.entry_month.insert(0, "0")
        self.on_change()
        return True
    
    # Method:   validate_year
    # Desc:     Validate the year entry, and fix its formatting.
    # Inputs:   event (Event): The focus out event that triggers validation
    # Outputs:  bool: Whether the year is valid
    def validate_year(self, event:Event):
        year_str = self.entry_year.get()
        # Validation
        if not year_str:
            self.on_change()
            return False
        if not year_str.isdigit() or len(year_str) != 4 or not (2024 <= int(year_str) <= 2100):
            messagebox.showwarning("Invalid Year", "Please enter a valid year (2024 - 2100).")
            self.entry_year.delete(0, "end")
            self.entry_year.focus_set()
            return False
        self.on_change()
        return True
    
    # Method:   get_value
    # Desc:     Get the currently selected date as a string in the format "DD/MM/YYYY"
    # Inputs:   None
    # Outputs:  tuple: (day, month, year)
    def get_value(self):
        day = self.entry_day.get()
        month = self.entry_month.get()
        year = self.entry_year.get()
        return int(day or 0), int(month or 0), int(year or 0)
    
    def set_value(self, day:int, month:int, year:int):
        if not (1 <= day <= 31 and 1 <= month <= 12 and 2024 <= year <= 2100):
            raise ValueError(f"Invalid date: {day}/{month}/{year}. Must be in the range 1-31 for day, 1-12 for month, and 2024-2100 for year.")
        self.entry_day.delete(0, "end")
        self.entry_day.insert(0, str(day).zfill(2))
        self.entry_month.delete(0, "end")
        self.entry_month.insert(0, str(month).zfill(2))
        self.entry_year.delete(0, "end")
        self.entry_year.insert(0, str(year))
        return
    
# Class:    NumberInput
# Desc:     Custom number input with increment and decrement buttons (not being used)
# Inherits: ctk.CTkFrame (basic frame class from customtkinter library
class NumberInput(ctk.CTkFrame):
    def __init__(self, root:ctk.CTkBaseClass):
        super().__init__(root, fg_color="transparent")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=1)

        self.entry = ctk.CTkEntry(self, fg_color=colour.BG2)
        self.entry.grid(row=0, column=0, sticky="nsew")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=0, column=1, sticky="nsew")
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)

        self.button_up = ctk.CTkButton(self.button_frame, text="▲", command=self.increment)
        self.button_up.grid(row=0, column=0, sticky="nsew")

        self.button_down = ctk.CTkButton(self.button_frame, text="▼", command=self.decrement)
        self.button_down.grid(row=1, column=0, sticky="nsew")

        return

    def increment(self):
        return
    
    def decrement(self):
        return
    
# Class:    Textbox
# Desc:     Custom textbox with placeholder text
# Inherits: ctk.CTkTextbox (basic textbox class from customtkinter library
class Textbox(ctk.CTkTextbox):
    # Method:   __init__
    # Desc:     Initialise the textbox with placeholder text
    # Inputs:   root (ctk.CTkBaseClass): The parent widget
    #           placeholder_text (str): The placeholder text to display when the textbox is empty
    #           *args: Additional arguments for ctk.CTkTextbox (also forces following arguments to be keyword-only)
    #           **kwargs: Additional keyword arguments for ctk.CTkTextbox
    # Outputs:  None
    def __init__(self, root:ctk.CTkBaseClass, placeholder_text, *args, **kwargs):
        super().__init__(root, fg_color=colour.BG2, border_color=colour.GREY, border_width=1, text_color=colour.TXT, *args, **kwargs)
        self.configure(height=40)  # Default height

        # Configure placeholder
        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)
        self.placeholder_text = placeholder_text
        self.placeholdering = True
        self.insert_placeholder()

        return

    # Method:   clear
    # Desc:     Clear the textbox and insert the placeholder text
    # Inputs:   None
    # Outputs:  None
    def clear(self):
        self.delete("0.0", "end")
        self.insert_placeholder()
        return
    
    # Method:   focus_out
    # Desc:     Handle when users leave the textbox, and insert placeholder if the textbox is empty
    # Inputs:   event (Event): The focus out event
    # Outputs:  None
    def focus_out(self, event:Event):
        if not self.placeholdering and not self.get("0.0", "end-1c").strip():
            self.insert_placeholder()
        return
    
    # Method:   focus_in
    # Desc:     Handle when users click the textbox, and clear placeholder text if it is currently displayed
    # Inputs:   event (Event): The focus in event
    # Outputs:  None
    def focus_in(self, event:Event):
        # print(self.placeholdering)
        if self.placeholdering:
            self.configure(state="normal")
            self.delete("0.0", "end")
            self.placeholdering = False
        return

    # Method:   insert_placeholder
    # Desc:     Insert the placeholder text into the textbox and disable editing
    # Inputs:   None
    # Outputs:  None
    def insert_placeholder(self):
        self.insert("0.0", self.placeholder_text)
        self.configure(state="disabled")
        self.placeholdering = True

# Class:    CalendarEvent
# Desc:     Custom calendar event widget that displays event details
# Inherits: ctk.CTkFrame (basic frame class from customtkinter library
class CalendarEvent(ctk.CTkFrame):
    def __init__(self, root:ctk.CTkBaseClass, id:str="", event_data:dict={}, placeholder:bool=True, on_click:Callable=None):
        super().__init__(root, corner_radius=5, border_width=1, width=1, height=1)

        self.event_data = event_data
        self.placeholder = placeholder

        self.id = id

        event_colour = self.event_data.get("colour", colour.ACC)
        if not event_colour:
            event_colour = colour.ACC

        if placeholder:
            self.configure(fg_color=colour.BG, border_color=event_colour, border_width=1)
        else:
            self.configure(fg_color=event_colour, border_color=event_colour, border_width=1)

        # Configure grid

        # Add event details
        self.label_title = ctk.CTkLabel(self, text=event_data.get("title", "No Title"), text_color=colour.TXT, font=("sans-serif", 10, "bold"), width=1, height=1)
        self.label_title.pack(side="top", fill="x", padx=5, pady=(2, 0))
        self.label_title.bind("<Button-1>", lambda e: on_click(e, self))

        class_id = event_data.get("class", None)
        class_name = "No Class"
        if class_id:
            class_data = api.get(f"groups/{class_id}")
            print(class_data)
            if not class_data.get("error"):
                class_name = class_data.get("name", "No Class")

        self.label_class = ctk.CTkLabel(self, text=class_name, text_color=colour.TXT, font=("sans-serif", 8), width=1, height=1, wraplength=80)
        self.label_class.pack(side="top", fill="x", padx=5, pady=(0, 2))
        self.label_class.pack_propagate(False)
        self.label_class.bind("<Button-1>", lambda e: on_click(e, self))

        self.label_type = ctk.CTkLabel(self, text=event_data.get("type", "No Type"), text_color=colour.TXT, font=("sans-serif", 8), width=1, height=1)
        self.label_type.pack(side="top", fill="x", padx=5, pady=(0, 2))
        self.label_type.bind("<Button-1>", lambda e: on_click(e, self))
        
        self.bind("<Button-1>", lambda e: on_click(e, self))

        self.update_event(event_data)

        return

    def select(self, selected:bool):
        if selected:
            self.configure(border_color=colour.ACC, border_width=2)
        else:
            # Delete if no data has been input, and deselected
            if self.placeholder:
                self.destroy()
                return False
            event_colour = self.event_data.get("colour", colour.ACC)
            if not event_colour:
                event_colour = colour.ACC
            self.configure(border_color=event_colour, border_width=1)
        return True

    def update_event(self, event_data:dict):
        self.event_data = event_data
        # Title
        self.label_title.configure(text=event_data.get("title", "No Title"))
        # Type
        self.label_type.configure(text=event_data.get("type", "SAC"))
        # Class
        class_id = event_data.get("class", None)
        class_name = "No Class"
        if class_id:
            class_data = api.get(f"groups/{class_id}")
            print(class_data)
            if not class_data.get("error"):
                class_name = class_data.get("name", "No Class")
        self.label_class.configure(text=class_name)
        # Update visual
        height = self.event_data.get("end_time", 1) - self.event_data.get("start_time", 0)
        self.grid(row=self.event_data.get("start_time", 0) + 2, rowspan=height, sticky="nsew")

        event_colour = self.event_data.get("colour", colour.ACC)
        if not event_colour:
            event_colour = colour.ACC
        
        if self.placeholder:
            self.configure(fg_color=colour.BG, border_color=event_colour, border_width=1)
        else:
            self.configure(fg_color=event_colour, border_color=event_colour, border_width=1)
        
        return