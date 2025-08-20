#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         screens/calendar.py
# Program:      trackademic
# Desc:         Calendar screen for viewing and managing events
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     17-08-2025

# Import UI libraries
import customtkinter as ctk
from tkinter import Event, messagebox

# Import custom modules
from screens import sidebar
from utils import colour, icon, account, api
from utils.components import HEntry, TimeInput, DateInput, SelectInput, Textbox, CalendarEvent

# Import other libraries
import datetime
from hashlib import sha256

# Declare globals
frame_mini_calendar = None
frame_calendar = None
date_labels = [None] * 7
cur_date = datetime.date.today()
frame_cover = None

visible_events = {}
selected_event = None

inp_title = None
inp_date = None
inp_type = None
inp_start_time = None
inp_end_time = None
inp_date = None
inp_reminder = None
inp_class = None
inp_visibility = None
inp_desc = None

def load_events():
    global visible_events, frame_calendar, cur_date
    # Clear existing events
    for event in visible_events.values():
        event.destroy()
    visible_events.clear()

    # Get events from API
    account.pull_updates()
    user_events = account.get("events")
    
    # Create calendar events
    for event_id, event_data in user_events.items():
        if not event_data.get("date"):
            continue  # Skip events without a date
        date = datetime.date.fromisoformat(event_data["date"])
        
        if not (cur_date - datetime.timedelta(days=cur_date.weekday()) <= date <= cur_date + datetime.timedelta(days=6 - cur_date.weekday())):
            continue # Skip events not in current week
        
        frame_event = CalendarEvent(frame_calendar, event_id, event_data, on_click=lambda e, f: event_clicked(e, f), placeholder=False)
        row = event_data.get("start_time", 0) + 2  # Adjust for header rows
        col = date.weekday() + 1  # +1 for the time marker column
        frame_event.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
    

        visible_events[event_id] = frame_event
        

# Function: select_date
# Desc:     Select a date in the mini calendar and update the main calendar
# Inputs:   selected_date (datetime.date): The date to select
# Outputs:  None
def select_date(selected_date:datetime.date):
    global cur_date, frame_mini_calendar
    cur_date = selected_date
    create_mini_calendar(frame_mini_calendar, cur_date)
    update_date_labels(cur_date)

    # Update main calendar events
    load_events()

# Function: create_mini_calendar
# Desc:     Create a mini calendar widget for selecting dates/weeks
# Inputs:   parent_frame (ctk.CTkFrame): The parent frame to place the calendar in
#           target_date (datetime.date): The date to display in the calendar
def create_mini_calendar(parent_frame:ctk.CTkFrame, target_date:datetime.date=None):
    if target_date is None:
        target_date = datetime.date.today()
    
    if not parent_frame:
        return

    # Clear existing content
    for widget in parent_frame.winfo_children():
        widget.destroy()
    
    # Configure grid
    parent_frame.columnconfigure(tuple(range(7)), weight=1, uniform="day")
    parent_frame.rowconfigure(tuple(range(8)), weight=1, uniform="row")
    
    # Header with month/year and navigation
    frame_header = ctk.CTkFrame(parent_frame, fg_color="transparent")
    frame_header.grid(row=0, column=0, columnspan=7, sticky="ew", pady=(5,0))
    frame_header.columnconfigure(1, weight=1)
    
    # Previous month button
    btn_prev = ctk.CTkButton(frame_header, text="<", width=30, height=25, 
                           fg_color=colour.BG2, text_color=colour.TXT,
                           command=lambda: navigate_month(-1))
    btn_prev.grid(row=0, column=0, sticky="w", padx=2)
    
    # Month/Year label
    month_year_text = target_date.strftime("%B %Y").upper()
    label_month = ctk.CTkLabel(frame_header, text=month_year_text, 
                              font=("sans-serif", 12, "bold"), text_color=colour.TXT)
    label_month.grid(row=0, column=1, sticky="ew")
    
    # Next month button
    btn_next = ctk.CTkButton(frame_header, text=">", width=30, height=25,
                           fg_color=colour.BG2, text_color=colour.TXT,
                           command=lambda: navigate_month(1))
    btn_next.grid(row=0, column=2, sticky="e", padx=2)
    
    # Day headers
    day_headers = ["M", "T", "W", "T", "F", "S", "S"]
    for i, day in enumerate(day_headers):
        label = ctk.CTkLabel(parent_frame, text=day, font=("sans-serif", 10, "bold"),
                           text_color=colour.TXT, fg_color="transparent")
        label.grid(row=1, column=i, sticky="nsew", pady=2)
    
    # Get first day of month and number of days
    first_day = target_date.replace(day=1)
    first_weekday = first_day.weekday()  # Monday = 0
    
    # Get last day of month
    if target_date.month == 12:
        last_day = target_date.replace(year=target_date.year + 1, month=1, day=1) - datetime.timedelta(days=1)
    else:
        last_day = target_date.replace(month=target_date.month + 1, day=1) - datetime.timedelta(days=1)
    
    days_in_month = last_day.day
    
    # Fill calendar dates
    current_day = 1
    today = datetime.date.today()
    
    for week in range(6):  # 6 weeks max
        for day_col in range(7):
            row = week + 2
            
            if week == 0 and day_col < first_weekday:
                # Empty cell before month starts
                continue
            elif current_day > days_in_month:
                # Month ended
                break
            else:
                # Create date button
                date_obj = datetime.date(target_date.year, target_date.month, current_day)
                is_today = date_obj == today
                is_selected = date_obj == cur_date
                
                # Button styling
                if is_today:
                    fg_color = colour.ACC
                    text_color = colour.BG
                    font = ("sans-serif", 10, "bold")
                elif is_selected:
                    fg_color = colour.BG2
                    text_color = colour.ACC
                    font = ("sans-serif", 10, "bold")
                else:
                    fg_color = "transparent"
                    text_color = colour.TXT
                    font = ("sans-serif", 10)
                
                btn_date = ctk.CTkButton(parent_frame, text=str(current_day),
                                       width=25, height=25, corner_radius=50,
                                       fg_color=fg_color, text_color=text_color,
                                       font=font, border_width=0,
                                       command=lambda d=date_obj: select_date(d))
                btn_date.grid(row=row, column=day_col, sticky="nsew", padx=1, pady=1)
                
                current_day += 1

def navigate_month(direction:int):
    global cur_date, frame_mini_calendar, selected_event, frame_cover
    selected_event = None
    if not frame_cover.winfo_ismapped():
        frame_cover.place(relx=0, rely=0, relwidth=1, relheight=1)
    if direction > 0:
        # Next month
        if cur_date.month == 12:
            new_date = cur_date.replace(year=cur_date.year + 1, month=1)
        else:
            new_date = cur_date.replace(month=cur_date.month + 1)
    else:
        # Previous month
        if cur_date.month == 1:
            new_date = cur_date.replace(year=cur_date.year - 1, month=12)
        else:
            new_date = cur_date.replace(month=cur_date.month - 1)
    
    cur_date = new_date
    create_mini_calendar(frame_mini_calendar, cur_date)
    update_date_labels(cur_date)

    # Update main calendar events
    load_events()

def form_updated(*args):
    global selected_event, inp_title, inp_date, inp_type, inp_start_time, inp_end_time, inp_reminder, inp_class, inp_visibility, inp_desc
    
    if not selected_event:
        return
    
    # Title
    event_title = inp_title.get() or ""
    # Type
    event_type = inp_type.get_value() or selected_event.event_data.get("type", "SAC")
    # Time
    event_start_str = inp_start_time.get_value()
    start_hour = 0
    if event_start_str != "Start":
        start_hour = int(event_start_str.split(":")[0]) if event_start_str else 0
    
    event_end_str = inp_end_time.get_value()
    end_hour = start_hour + 1
    if event_end_str != "End":
        end_hour = int(event_end_str.split(":")[0]) if event_end_str else 0

    if end_hour <= start_hour:
        messagebox.showwarning(title="Warning", message="End time must be after start time!", icon="warning")
        inp_end_time.set_value(f"{start_hour + 1:02d}:00")
        return
    # # Reminder
    # event_reminder_str = inp_reminder.get_value()
    # event_reminder = 0
    # if event_reminder_str != "None":
    #     event_reminder = int(event_reminder_str.split(" ")[0])
    # Class
    event_class_id = inp_class.get_value()
    # Validate class_id
    result = api.get(f"groups/{event_class_id}")
    if result.get("error"):
        event_class_id = ""
    event_colour = colour.ACC[0]
    if event_class_id and event_class_id != "Select Class":    
        # Get class data
        event_class_data = api.get(f"groups/{event_class_id}")
        if not event_class_data or event_class_data.get("error"):
            messagebox.showerror("Error", "Failed to retrieve class data. Please try again later.", icon="error")
            return
        event_colour = event_class_data.get("colour", colour.ACC[0])
    # Visibility
    event_visibility_str = inp_visibility.get_value() or "Private"
    event_visible = event_visibility_str == "Share with class"
    # Description
    event_desc = inp_desc.get("0.0", "end-1c") or ""

    # Date
    today = datetime.date.today()
    prev_date:datetime.date = selected_event.event_data.get("date", today)
    if type(prev_date) == str:
        prev_date = datetime.date.fromisoformat(prev_date)
    day, month, year = inp_date.get_value()

    day = day or prev_date.day
    month = month or prev_date.month
    year = year or prev_date.year
    inp_date.set_value(day, month, year)

    event_date = str(datetime.date(year, month, day))
    
    # If date has changed, rerender on calendar
    if event_date != prev_date:
        selected_event.grid_forget()
        # Only if new date is within range
        new_date = datetime.date(year, month, day)
        if (cur_date - datetime.timedelta(days=cur_date.weekday()) <= new_date <= cur_date + datetime.timedelta(days=6 - cur_date.weekday())): 
            row = start_hour + 2
            col = datetime.date(year, month, day).weekday() + 1  # +1 for the time marker column
            selected_event.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

    event_data = {
        "id": selected_event.id,
        "title": event_title,
        "start_time": start_hour,
        "end_time": end_hour,
        "date": event_date,
        "type": event_type,
        "group_id": event_class_id,
        "visible": event_visible,
        "description": event_desc,
        "colour": event_colour,
    }

    print("sending: ", event_data)

    if selected_event.placeholder:
        selected_event.placeholder = False
    
    # Save to API
    account.pull_updates()
    user_events = account.get("events")
    # If event already exists, update, else, create new event
    target_event = user_events.get(selected_event.id)
    # print(event_data)
    if target_event:
        # Update existing event
        result = api.post(f"users/{account.get('username')}/events/edit", event_data)
        if result.get("error"):
            messagebox.showerror("Error", "Failed to update event. Please try again later.", icon="error")
            return
    else:
        # Event should already exist
        pass

    selected_event.update_event(event_data)


def event_clicked(clickEvent:Event, event:CalendarEvent):
    global selected_event, frame_cover, inp_title, inp_date, inp_type, inp_start_time, inp_end_time, inp_reminder, inp_class, inp_visibility, inp_desc
    if selected_event:
        selected_event.select(False)
    event.select(True)
    selected_event = event
    print(selected_event.event_data.get("title"))

    print("new event clicked")
    
    # Show form
    if frame_cover.winfo_ismapped():
        frame_cover.place_forget()
    
    # Pre-fill form with event data
    update_form(event.event_data)

def update_form(event_data):
    global inp_title, inp_date, inp_type, inp_start_time, inp_end_time, inp_reminder, inp_class, inp_visibility, inp_desc
    
    print("Updating form")

    inp_title.delete(0, "end")
    if "title" in event_data:
        inp_title.insert(0, event_data.get("title", ""))
    
    inp_start_time.set_value(f"{event_data.get("start_time", 0):02d}:00")
    inp_end_time.set_value(f"{event_data.get("end_time", 0):02d}:00")
    if "date" in event_data:
        # Convert date format
        today = datetime.date.today()
        date = event_data.get("date", today)
        if type(date) == str:
            date = datetime.date.fromisoformat(date)
        inp_date.set_value(date.day, date.month, date.year)
    
    inp_type.set_value(event_data.get("tag", "SAC"))
    
    # reminder = "None"
    # if event_data.get("reminder", 0) > 0:
    #     reminder = f"{event_data.get("reminder", 0)} minutes"
    # inp_reminder.set_value(reminder)
    
    if event_data.get("class"):
        class_id = event_data.get("class", None)
        class_name = "No Class"
        if class_id:
            class_data = api.get(f"groups/{class_id}")
            if not class_data.get("error"):
                class_name = class_data.get("name", "No Class")
        inp_class.set_value(class_name)
    inp_visibility.set_value(event_data.get("visibility", "Private"))
    
    inp_desc.clear()
    if event_data.get("description"):
        inp_desc.focus_in(None)
        inp_desc.delete("0.0", "end")
        inp_desc.insert("0.0", event_data.get("description", ""))

# Function: calendar_clicked
# Desc:     Handle clicking on the calendar to create a new event
# Inputs:   clickEvent (Event): The click event from the calendar
# Outputs:  None
def calendar_clicked(clickEvent:Event):
    global selected_event, visible_events, frame_calendar, frame_cover, inp_title
    # Calculate the time and day based on the click position
    interval_height = clickEvent.widget.winfo_height() / 26
    interval_width = clickEvent.widget.winfo_width() / 7.5 # 7 days + 0.5 for the time marker
    time = int(clickEvent.y / interval_height)
    day = int(clickEvent.x / interval_width - 0.5)
    if time < 2 or time > 25:
        return
    # print(clickEvent, time, day)
    # Check that the spot is free
    for event in visible_events.values():
        if event.grid_info()["row"] == time and event.grid_info()["column"] == day + 1:
            # Spot is taken; event handler for clicking that event should be on the individual calendar entry
            return
    # If currently editing, treat clicking calendar as unselecting the event
    if selected_event:
        # Make event not placeholder if title has been given
        if inp_title.get():
            form_updated()
        keep_event = selected_event.select(False)
        if not keep_event:
            # If the event was deleted, delete it
            delete_event()
        selected_event = None
        if not frame_cover.winfo_ismapped():
            frame_cover.place(relx=0, rely=0, relwidth=1, relheight=1)
        return
    # Everything checks out, proceed
    # Create new event on calendar (UI)
    today = datetime.date.today()
    date = cur_date - datetime.timedelta(days=cur_date.weekday()) + datetime.timedelta(days=day)

    event_data = {
        "start_time": time - 2,
        "end_time": time - 1,
        "date": str(date),
        "type": "SAC",
        "class": None,
        "visible": False,
        "description": ""
    }

    # Generate event_id
    account.pull_updates()
    username = account.get("username")
    user_events = account.get("events")
    numerical_id = max([event.get("numerical_id") for event in user_events.values()] + [0]) + 1
    event_id = sha256(f"{username}{numerical_id}".encode()).hexdigest()
    # Add event_id to event_data
    event_data["id"] = event_id
    event_data["numerical_id"] = numerical_id
    # Push event to API
    api.post(f"users/{username}/events/create", event_data)
    account.pull_updates()
    
    frame_event = CalendarEvent(frame_calendar, event_id, event_data, on_click=lambda e, f: event_clicked(e, f))
    frame_event.grid(row=time, column=day+1, sticky="nsew", padx=1, pady=1)

    update_form(event_data)

    visible_events[frame_event.id] = frame_event
    selected_event = frame_event

    # Pre-fill form
    # Show form
    if frame_cover.winfo_ismapped():
        frame_cover.place_forget()
    return

def delete_event():
    global selected_event, visible_events, frame_cover
    if not selected_event:
        return
    
    # Remove from visible events
    del visible_events[selected_event.id]
    
    # Remove from calendar
    selected_event.destroy()

    # Remove from API
    username = account.get("username")
    api.get(f"users/{username}/events/delete/{selected_event.id}")
    pull_updates = account.pull_updates()
    
    # Reset selected event
    selected_event = None
    
    # Show cover frame again
    if not frame_cover.winfo_ismapped():
        frame_cover.place(relx=0, rely=0, relwidth=1, relheight=1)
    
    return

def update_date_labels(date:datetime.date=datetime.date.today()):
    global date_labels
    today = datetime.date.today()
    # Update date labels to reflect input week
    today_index = today.weekday()
    start_date = date - datetime.timedelta(days=date.weekday())
    for i in range(7):
        date_labels[i].configure(text=(start_date + datetime.timedelta(days=i)).strftime("%d"))
        if i == today_index and start_date <= today <= start_date + datetime.timedelta(days=6):
            date_labels[i].configure(fg_color=colour.ACC, text_color=colour.BG, font=("sans-serif", 16, "bold"))
        else:
            date_labels[i].configure(fg_color=colour.BG, text_color=colour.TXT, font=("sans-serif", 16))

# Function: construct
# Desc:     Build the calendar screen
# Inputs:   app (ctk.CTk): The main app instance
# Outputs:  frame_main (ctk.CTkFrame): The main frame of the calendar screen
def construct(app:ctk.CTk) -> ctk.CTkFrame:
    # Import globals
    global date_labels, frame_calendar, frame_mini_calendar, cur_date, frame_cover, \
    inp_title, inp_date, inp_type, inp_start_time, inp_end_time, inp_date, inp_reminder, inp_class, inp_visibility, inp_desc, visible_events

    # Initialize globals
    date_labels = [None] * 7
    frame_calendar = None
    frame_mini_calendar = None
    cur_date = datetime.date.today()
    visible_events = {}

    # Configure rows/columns
    frame_main = ctk.CTkFrame(app, fg_color="transparent")
    frame_main.columnconfigure(0, weight=8)
    frame_main.columnconfigure(1, weight=1)
    frame_main.rowconfigure(0, weight=1)
    frame_main.grid(row=0, column=1, sticky="nsew")
    # Build elements
    frame_calendar = ctk.CTkFrame(frame_main, fg_color=colour.BG)
    frame_calendar.grid(row=0, column=0, sticky="nsew")

    frame_right = ctk.CTkFrame(frame_main, fg_color=colour.BG, width=100)
    frame_right.grid(row=0, column=1, sticky="nsew")

    frame_right.rowconfigure(0, weight=1)
    frame_right.rowconfigure(1, weight=1)
    frame_right.columnconfigure(0, weight=1)

    # Mini calendar
    frame_mini_calendar = ctk.CTkFrame(frame_right, fg_color=colour.BG, border_color=colour.GREY, border_width=1)
    frame_mini_calendar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    create_mini_calendar(frame_mini_calendar, cur_date)

    frame_form = ctk.CTkFrame(frame_right, fg_color=colour.BG)
    frame_form.grid(row=1, column=0, sticky="nsew")

    for i in range(10):
        frame_form.rowconfigure(i, weight=1)
    frame_form.columnconfigure(0, weight=1)
    frame_form.columnconfigure(1, weight=10)

    # Form icons
    icon_type = ctk.CTkLabel(frame_form, image=icon.icon("tag"), text="")
    icon_type.grid(row=1, column=0, sticky="nsew")
    icon_time = ctk.CTkLabel(frame_form, image=icon.icon("time"), text="")
    icon_time.grid(row=2, column=0, sticky="nsew")
    icon_date = ctk.CTkLabel(frame_form, image=icon.icon("date"), text="")
    icon_date.grid(row=3, column=0, sticky="nsew")
    # icon_reminder = ctk.CTkLabel(frame_form, image=icon.icon("reminder"), text="")
    # icon_reminder.grid(row=4, column=0, sticky="nsew")
    icon_class = ctk.CTkLabel(frame_form, image=icon.icon("class"), text="")
    icon_class.grid(row=4, column=0, sticky="nsew")
    icon_visibility = ctk.CTkLabel(frame_form, image=icon.icon("visibility"), text="")
    icon_visibility.grid(row=5, column=0, sticky="nsew")
    
    # Form widgets
    inp_title = ctk.CTkEntry(frame_form, 
                             fg_color=colour.BG2, border_color=colour.GREY, border_width=1,
                             placeholder_text="Title", text_color=colour.TXT
                             )
    inp_title.grid(row=0, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)
    inp_title.bind("<FocusOut>", form_updated)

    inp_type = SelectInput(frame_form, values=["SAC", "Homework", "Exam", "Other"], default_value="SAC", on_change=form_updated)
    inp_type.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
    inp_type.bind("<FocusOut>", form_updated)

    frame_inp_time = ctk.CTkFrame(frame_form, fg_color="transparent")
    frame_inp_time.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
    frame_inp_time.rowconfigure(0, weight=1)
    frame_inp_time.columnconfigure(0, weight=1)
    frame_inp_time.columnconfigure(1, weight=1)
    frame_inp_time.columnconfigure(1, weight=1)
    
    inp_start_time = SelectInput(frame_inp_time, values=[f"{i:02d}:00" for i in range(24)], default_value="Start", on_change=form_updated)
    inp_start_time.grid(row=0, column=0, sticky="nsew")

    label_to = ctk.CTkLabel(frame_inp_time, text="", image=icon.icon("right"), text_color=colour.TXT)
    label_to.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    inp_end_time = SelectInput(frame_inp_time, values=[f"{i+1:02d}:00" for i in range(24)], default_value="End", on_change=form_updated)
    inp_end_time.grid(row=0, column=2, sticky="nsew")

    inp_date = DateInput(frame_form, on_change=form_updated)
    inp_date.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

    # inp_reminder = SelectInput(frame_form, values=["None", "5 minutes", "10 minutes", "30 minutes", "1 hour"], default_value="None", on_change=form_updated)
    # inp_reminder.grid(row=4, column=1, sticky="nsew", padx=5, pady=5)

    # Get classes from account
    account.pull_updates()
    classes = account.get("groups")
    if not classes or classes.get("error"):
        classes = {}
    # Turn classes into list of names
    class_names = []
    class_ids = []
    for group_id in classes.keys():
        group = api.get(f"groups/{group_id}")
        if not group or group.get("error"):
            continue
        class_ids.append(group_id)
        class_names.append(group.get("name"))
    inp_class = SelectInput(frame_form, values=class_names, default_value="Select Class", on_change=form_updated, hidden_values=class_ids)
    inp_class.grid(row=4, column=1, sticky="nsew", padx=5, pady=5)

    inp_visibility = SelectInput(frame_form, values=["Private", "Share with class"], default_value="Private", on_change=form_updated)
    inp_visibility.grid(row=5, column=1, sticky="nsew", padx=5, pady=5)

    inp_desc = Textbox(frame_form, placeholder_text="Description...", height=40)
    inp_desc.insert("0.0", "Description")
    inp_desc.grid(row=6, column=0, sticky="nsew", padx=5, pady=5, columnspan=2, rowspan=2)
    inp_desc.bind("<FocusOut>", form_updated)

    button_frame = ctk.CTkFrame(frame_form, fg_color="transparent")
    button_frame.grid(row=8, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)

    button_frame.rowconfigure(0, weight=1)
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

    button_delete = ctk.CTkButton(button_frame, text="Delete Event", fg_color="#ff4d4d", text_color=colour.TXT, command=delete_event)
    button_delete.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    button_save = ctk.CTkButton(button_frame, text="Save Event", fg_color=colour.ACC, text_color=colour.BG, command=form_updated)
    button_save.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    frame_cover = ctk.CTkFrame(frame_form, fg_color=colour.BG)
    frame_cover.place(relx=0, rely=0, relwidth=1, relheight=1)

    label_warn = ctk.CTkLabel(frame_cover, text="Click on the calendar to create an event", text_color=colour.TXT, fg_color="transparent", font=("sans-serif", 12))
    label_warn.place(relx=0.5, rely=0.5, anchor="center")

    # Main calendar
    # Divide into 1 time marker + 7 day of the week columns
    frame_calendar.columnconfigure(0, weight=1)
    for i in range(7):
        frame_calendar.columnconfigure(i+1, weight=2, uniform="day")
    
    # Divide columns into 24 rows + 2 header rows
    for i in range(26):
        frame_calendar.rowconfigure(i, weight=1, uniform="time")
    
    # Add time markers
    for i in range(24):
        label = ctk.CTkLabel(frame_calendar, text=f"{i:02d}:00", text_color=colour.TXT, anchor="ne", fg_color=colour.BG)
        label.grid(row=i+2, column=0, sticky="nsew", padx=5, pady=5)

    # Add headings
    WEEK_DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    frame_calendar.columnconfigure(0, weight=1)

    # Day / date labels
    for i in range(7):
        # Day of the week
        label_day = ctk.CTkLabel(frame_calendar, text=WEEK_DAYS[i], text_color=colour.TXT, anchor="center", fg_color=colour.BG)
        label_day.grid(row=0, column=i+1, sticky="nsew", pady=5)

        # Date of the month
        label_date = ctk.CTkLabel(frame_calendar, text="", text_color=colour.TXT, anchor="center", corner_radius=100)
        label_date.grid(row=1, column=i+1, sticky="ns", ipadx=0, ipady=5)
        date_labels[i] = label_date

    update_date_labels()

    # Bind click event to create event
    frame_calendar.bind("<Button-1>", calendar_clicked)
    
    # Load existing events
    load_events()
    
    # Construct sidebar
    sidebar_weight = sidebar.get_mode()
    sidebar.set_mode("open" if sidebar_weight == "closed" else sidebar_weight, app)
    sidebar.highlight_tab("calendar")
    return frame_main