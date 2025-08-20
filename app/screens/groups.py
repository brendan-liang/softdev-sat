#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         groups.py
# Program:      trackademic
# Desc:         Groups screen for managing classes and events
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     16-08-2025

import customtkinter as ctk
from screens import sidebar
from utils import colour, icon, api, account
from utils.components import clear_frame, SelectInput
from tkinter import messagebox, Event

loaded_classes = {}

# Globals
search_entry = None
content_frame = None
filter_select = None

def create_class_tile(parent, class_data, row, col):
    # Main tile frame
    tile_frame = ctk.CTkFrame(parent, fg_color=class_data.get("colour", colour.ACC), corner_radius=10, height=300)
    tile_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
    
    # Configure grid
    tile_frame.columnconfigure(0, weight=1)
    tile_frame.rowconfigure(0, weight=1)
    
    # Content frame (white background)
    content_frame = ctk.CTkFrame(tile_frame, fg_color=colour.BG2, corner_radius=8)
    content_frame.grid(row=1, column=0, sticky="sew", padx=0, pady=(10, 0))
    content_frame.columnconfigure(0, weight=1)
    content_frame.rowconfigure(0, weight=1)
    content_frame.rowconfigure(1, weight=1)
    content_frame.rowconfigure(2, weight=1)
    content_frame.rowconfigure(3, weight=1)
    
    # Class name
    name_label = ctk.CTkLabel(content_frame, text=class_data["name"], 
                             font=("sans-serif", 20, "bold"), 
                             text_color=colour.TXT, anchor="w")
    name_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
    
    # Member info frame
    info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    info_frame.grid(row=1, column=0, sticky="ew", padx=15)
    info_frame.columnconfigure(0, weight=1)
    
    # Members count
    members_label = ctk.CTkLabel(info_frame, 
                                image=icon.icon("group"),
                                compound="left",
                                text=f" {len(class_data.get('members'))} Members", 
                                font=("sans-serif", 12), 
                                text_color=colour.TXT, anchor="w")
    members_label.grid(row=0, column=0, sticky="w")
    
    # School name
    school_label = ctk.CTkLabel(info_frame, 
                                image=icon.icon("class"),
                                compound="left",
                                text=f" {class_data['school']}", 
                                font=("sans-serif", 12), 
                                text_color=colour.TXT, anchor="w")
    school_label.grid(row=1, column=0, sticky="w")
    
    # Description
    desc_text = "..."
    desc_label = ctk.CTkLabel(content_frame, text=desc_text, 
                                font=("sans-serif", 11), 
                                text_color=colour.TXT, anchor="nw", 
                                wraplength=250, justify="left")
    desc_label.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
    
    # Button frame for details and action buttons
    button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    button_frame.grid(row=2, column=0, sticky="e", padx=15, pady=(0, 15))
    
    # Details button
    details_btn = ctk.CTkButton(button_frame, text="DETAILS", 
                               fg_color=colour.GREY, text_color=colour.TXT,
                               corner_radius=5, height=30, width=80,
                               command=lambda: handle_class_details(class_data))
    details_btn.pack(side="left", padx=(0, 10))
    
    # Action button (Join/Leave)
    joined = account.get("username") in class_data.get("members", [])
    button_text = "LEAVE" if joined else "JOIN"
    button_color = "#FF6B6B" if joined else "#4A90E2"
    
    action_btn = ctk.CTkButton(button_frame, text=button_text, 
                              fg_color=button_color, text_color=colour.TXT,
                              corner_radius=5, height=30, width=80,
                              command=lambda: handle_class_action(class_data))
    action_btn.pack(side="left")

def fill_classes(content_frame, classes):
    clear_frame(content_frame)
    for i, class_data in enumerate(classes.values()):
        row = i // 2
        col = i % 2
        create_class_tile(content_frame, class_data, row, col)

def detail_close(details_cover, class_data):
    global loaded_classes
    # Close popup
    details_cover.destroy()
    # Update class group on user (whether to save events or not)
    user = account.get()
    print(user)
    # This is a bool because it used to represent whether to show events or not, but
    # that feature was removed.
    user.get("groups", {})[class_data["id"]] = True
    # Update user in API & locally
    api.post("users/update", user)
    account.pull_updates()

    # Update groups UI
    loaded_classes = api.get("groups")
    # Updated local user
    filter_classes()
    

def handle_class_details(class_data):
    global loaded_classes

    # Update class_data
    class_data = api.get(f"groups/{class_data.get('id')}")
    if class_data.get("error") or not class_data:
        messagebox.showerror("Error", "Failed to load class details. Please try again later.", icon="error")
        return

    top_level = content_frame.winfo_toplevel()
    
    # Create modal overlay
    details_cover = ctk.CTkFrame(top_level, fg_color=colour.BG, corner_radius=0)
    details_cover.place(relx=0, rely=0, relwidth=1, relheight=1)
    
    # Main details frame
    details_frame = ctk.CTkFrame(details_cover, fg_color=colour.BG2, corner_radius=10, 
                                border_color=colour.GREY, border_width=2,
                                width=800, height=600)
    details_frame.place(relx=0.5, rely=0.5, anchor="center")
    details_frame.grid_propagate(False)
    
    # Configure grid
    details_frame.columnconfigure(0, weight=1)
    details_frame.rowconfigure(0, weight=1)  # Header
    details_frame.rowconfigure(1, weight=1)  # Info section
    details_frame.rowconfigure(2, weight=3)  # Events section
    details_frame.rowconfigure(3, weight=1)  # Button section
    
    
    # Header with colored background matching class color
    header_frame = ctk.CTkFrame(details_frame, fg_color=class_data.get("colour", colour.ACC), 
                               corner_radius=8)
    header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
    header_frame.columnconfigure(0, weight=1)
    header_frame.columnconfigure(1, weight=1)
    
    # Class title
    title_label = ctk.CTkLabel(header_frame, text=class_data["name"],
                              font=("sans-serif", 28, "bold"),
                              text_color="white")
    title_label.grid(row=0, column=0, sticky="w", padx=30, pady=20)
    
    # Members section in header
    members_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    members_frame.grid(row=0, column=1, sticky="e", padx=30, pady=20)
    
    members_title = ctk.CTkLabel(members_frame, text=f"Members ({len(class_data.get('members', []))})",
                                font=("sans-serif", 16, "bold"), text_color="white")
    members_title.pack(anchor="e", padx=(0, 60))
    
    # Info section
    info_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
    info_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=10)
    info_frame.columnconfigure(0, weight=1)
    info_frame.columnconfigure(1, weight=1)
    
    # Left side - description and school
    left_info = ctk.CTkFrame(info_frame, fg_color="transparent")
    left_info.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
    
    school_label = ctk.CTkLabel(left_info, 
                               image=icon.icon("class"), compound="left",
                               text=f"  {class_data['school']}", 
                               font=("sans-serif", 14), 
                               text_color=colour.TXT, anchor="w")
    school_label.pack(anchor="w", pady=(0, 10))
    
    desc_text = class_data.get('description', 'No description available.')
    desc_label = ctk.CTkLabel(left_info, text=desc_text,
                             font=("sans-serif", 12), 
                             text_color=colour.TXT, anchor="nw", 
                             wraplength=300, justify="left")
    desc_label.pack(anchor="w", fill="x")
    
    # Right side - members list
    right_info = ctk.CTkFrame(info_frame, fg_color=colour.BG, corner_radius=8)
    right_info.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
    
    members_scroll = ctk.CTkScrollableFrame(right_info, fg_color="transparent", height=100)
    members_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add member list
    for member in class_data.get('members', []):
        member_frame = ctk.CTkFrame(members_scroll, fg_color="transparent")
        member_frame.pack(fill="x", pady=2)
        
        member_icon = ctk.CTkLabel(member_frame,
                                  image=icon.icon("group"), 
                                  text="", width=20, height=20)
        member_icon.pack(side="left", padx=(0, 8))
        
        name = member
        if class_data.get("owner") == member:
            name += " (Owner)"
        if member == account.get("username"):
            name += " (You)"
        member_name = ctk.CTkLabel(member_frame, text=name,
                                  font=("sans-serif", 12),
                                  text_color=colour.TXT, anchor="w")
        member_name.pack(side="left", fill="x", expand=True)
    
    # Events section
    events_main_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
    events_main_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=10)
    events_main_frame.columnconfigure(0, weight=1)
    events_main_frame.rowconfigure(0, minsize=30)  # Header
    events_main_frame.rowconfigure(1, weight=1)    # Events list
    
    # Events header with checkbox
    events_header = ctk.CTkFrame(events_main_frame, fg_color="transparent")
    events_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    events_header.columnconfigure(0, weight=1)
    
    events_title = ctk.CTkLabel(events_header, text="Events",
                               font=("sans-serif", 18, "bold"),
                               text_color=colour.TXT, anchor="w")
    events_title.pack(side="left")
    
    user_groups = account.get("groups")
    # show_events = True
    # if user_groups:
    #     show_events = user_groups.get(class_data["id"], True)
    # show_events_var = ctk.BooleanVar(value=show_events)
    # show_events_check = ctk.CTkCheckBox(events_header, text="Show events from this group on calendar?",
    #                                  font=("sans-serif", 12),
    #                                  text_color=colour.TXT,
    #                                  variable=show_events_var)
    # show_events_check.pack(side="right")
    
    
    # Events scrollable frame
    events_frame = ctk.CTkScrollableFrame(events_main_frame, fg_color=colour.BG, 
                                         corner_radius=8, border_width=1, 
                                         border_color=colour.GREY)
    events_frame.grid(row=1, column=0, sticky="nsew")
    events_frame.columnconfigure(0, weight=1)
    
    # Close button
    close_btn = ctk.CTkButton(details_frame, text="✕", width=30, height=30,
                             fg_color="transparent", text_color=colour.TXT,
                             hover_color=colour.GREY, corner_radius=15,
                             command=lambda: detail_close(details_cover, class_data))
    close_btn.place(relx=0.95, rely=0.05, anchor="center")
    
    def create_event_tile(event_data, parent_frame):
        """Create an individual event tile"""
        event_tile = ctk.CTkFrame(parent_frame, fg_color=colour.BG2, corner_radius=5,
                                 border_width=1, border_color=colour.GREY)
        event_tile.pack(fill="x", padx=10, pady=5)
        event_tile.columnconfigure(0, weight=1)
        event_tile.columnconfigure(1, weight=1)
        event_tile.columnconfigure(2, weight=1)
        
        # Event icon and title
        title_frame = ctk.CTkFrame(event_tile, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        
        event_icon = ctk.CTkLabel(title_frame, 
                                 image=icon.icon("calendar"), 
                                 text="", width=20, height=20)
        event_icon.pack(side="left", padx=(0, 10))
        
        title_info = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_info.pack(side="left", fill="x", expand=True)
        
        event_title = ctk.CTkLabel(title_info, text=event_data.get("title", "Untitled Event"),
                                  font=("sans-serif", 14, "bold"),
                                  text_color=colour.TXT, anchor="w")
        event_title.pack(anchor="w")
        
        event_desc = ctk.CTkLabel(title_info, text=event_data.get("description", "No description"),
                                 font=("sans-serif", 10),
                                 text_color=colour.TXT, anchor="w")
        event_desc.pack(anchor="w")
        
        event_author = ctk.CTkLabel(title_info, text=f"Posted by {event_data.get('owner', 'Unknown')}",
                                   font=("sans-serif", 9),
                                   text_color="gray", anchor="w")
        event_author.pack(anchor="w")
        
        # Event type and time
        info_frame = ctk.CTkFrame(event_tile, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=15, pady=10)
        
        # Event type tag
        type_tag = ctk.CTkLabel(info_frame, 
                               image=icon.icon("tag"), compound="left",
                               text=f" {event_data.get('type', 'Event')}",
                               font=("sans-serif", 10),
                               text_color=colour.TXT, corner_radius=10,
                               fg_color=colour.GREY)
        type_tag.pack(anchor="center", pady=(0, 5))
        
        # Time and date
        time_str = f"{event_data.get('start_time', 9)}:00 - {event_data.get('end_time', 10)}:00"
        date_str = event_data.get('date', '01/01/2025')
        time_label = ctk.CTkLabel(info_frame, text=time_str,
                                 font=("sans-serif", 11, "bold"),
                                 text_color=colour.TXT)
        time_label.pack(anchor="center")
        
        date_label = ctk.CTkLabel(info_frame, text=date_str,
                                 font=("sans-serif", 10),
                                 text_color=colour.TXT)
        date_label.pack(anchor="center")
        
        # Action buttons
        button_frame = ctk.CTkFrame(event_tile, fg_color="transparent")
        button_frame.grid(row=0, column=2, sticky="e", padx=15, pady=10)
        
        # Check if event is saved or not
        account.pull_updates()
        user_events = account.get("events")
        if not user_events:
            user_events = {}
        print(f"User events: {user_events}, id: {event_data.get('id')}")
        is_saved = user_events.get(event_data.get("id"), False)
        if not is_saved:
            # Show "SAVE" button for unsaved events (to add to personal calendar)
            save_btn = ctk.CTkButton(button_frame, text="SAVE",
                                    fg_color="#4A90E2", text_color="white",
                                    width=80, height=30, corner_radius=5,
                                    command=lambda: save_event_to_calendar(event_data))
            save_btn.pack(pady=(0, 5))
        else:
            # Show "UNSAVE" button for saved events
            unsave_btn = ctk.CTkButton(button_frame, text="UNSAVE",
                                      fg_color="#FF6B6B", text_color="white",
                                      width=80, height=30, corner_radius=5,
                                      command=lambda: unsave_event(event_data))
            unsave_btn.pack(pady=(0, 5))
    
        delete_btn = ctk.CTkButton(button_frame, text="DELETE",
                                 fg_color="transparent", text_color="#4A90E2",
                                 border_color="#4A90E2", border_width=2,
                                 width=80, height=30, corner_radius=5,
                                 command=lambda: delete_event(event_data))
        # Only show delete button if user is owner
        if account.get("username") == class_data.get("owner"):
            delete_btn.pack(pady=(0, 5))
    
    def save_event_to_calendar(event_data):
        """Save event to user's personal calendar"""
        messagebox.showinfo("Save Event", f"Event '{event_data.get('title')}' saved to your calendar!")
        # Check event is not already saved
        account.pull_updates()
        user_events = account.get("events")
        if not user_events:
            user_events = {}
        if event_data.get("id") in user_events:
            messagebox.showwarning("Save Event", "This event is already saved to your calendar.")
            return
        # Add event to user's personal calendar
        user_events[event_data.get("id")] = event_data
        # Update user data in API
        user = account.get()
        user["events"] = user_events
        api.post("users/update", user)
        # Update local user data
        account.pull_updates()
        # Show success message
        messagebox.showinfo("Save Event", f"Event '{event_data.get('title')}' saved to your calendar!")
        # Reload details to reflect changes
        details_cover.destroy()
        new_event_data = api.get(f"groups/{class_data.get('id')}")
        if new_event_data.get("error") or not new_event_data:
            messagebox.showerror("Error", "Failed to load class details. Please try again later.", icon="error")
            return
        handle_class_details(new_event_data)
        
        return
    
    def unsave_event(event_data):
        """Remove event from user's personal calendar"""
        # Check if event is saved
        account.pull_updates()
        user_events = account.get("events")
        if not user_events or event_data.get("id") not in user_events:
            messagebox.showwarning("Unsave Event", "This event is not saved in your calendar.")
            return
        # Remove event from user's personal calendar
        del user_events[event_data.get("id")]
        # Update user data in API
        user = account.get()
        user["events"] = user_events
        api.post("users/update", user)
        # Update local user data
        account.pull_updates()
        # Show success message
        messagebox.showinfo("Unsave Event", f"Event '{event_data.get('title')}' removed from your calendar!")
        # Reload details to reflect changes
        details_cover.destroy()
        new_event_data = api.get(f"groups/{class_data.get('id')}")
        if new_event_data.get("error") or not new_event_data:
            messagebox.showerror("Error", "Failed to load class details. Please try again later.", icon="error")
            return
        handle_class_details(new_event_data)
        
        return

    def delete_event(event_data):
        delete = messagebox.askokcancel("Delete Event", "Are you sure you want to delete this event?")
        if not delete:
            return
        # Call API to delete event
        group_id = class_data.get("id")
        if not group_id:
            messagebox.showerror("Error", "Could not delete event. Try again later.", icon="error")
            return
        result = api.get(f"groups/{group_id}/events/delete/{event_data.get('id')}")
        if result.get("error"):
            messagebox.showerror("Error", "Could not delete event. Try again later.", icon="error")
            return
        account.pull_updates()
        # Refresh details after deletion
        details_cover.destroy()
        new_data = api.get(f"groups/{class_data.get('id')}")
        if new_data.get("error") or not new_data:
            messagebox.showerror("Error", "Failed to load class details. Please try again later.", icon="error")
            return
        handle_class_details(new_data)
            
    
    # Sample events data (replace with actual API call)
    events_data = class_data.get("events", {})
    
    # Create event tiles
    for event in events_data.values():
        create_event_tile(event, events_frame)
    
    # Bottom button section
    button_section = ctk.CTkFrame(details_frame, fg_color="transparent")
    button_section.grid(row=3, column=0, sticky="ew", padx=30, pady=20)
        
    # Leave/join class button
    def join_leave_handler():
        handle_class_action(class_data)
        # Refresh details after action
        details_cover.destroy()
        new_data = api.get(f"groups/{class_data.get('id')}")
        handle_class_details(new_data)
    joined = account.get("username") in class_data.get("members", [])
    leave_class_btn = ctk.CTkButton(button_section, text=("Leave Class" if joined else "Join Class"),
                                   fg_color=("#FF6B6B" if joined else "#4A90E2"), text_color=colour.TXT,
                                   height=40, width=120, corner_radius=5,
                                   command=join_leave_handler)
    leave_class_btn.pack(side="right", padx=5)
    
    # Delete button for owner
    def delete_class(class_data):
        global loaded_classes
        # Confirm with user
        confirm = messagebox.askokcancel("Delete Class", "Are you sure you want to delete this class for all users? (This action is destructive!)")
        if not confirm:
            return
        # Actually delete class
        result = api.get(f"groups/{class_data["id"]}/delete")
        if result.get("error"):
            messagebox.showwarning("Delete Class", "Could not delete class; try again later.")
        
        # Close details and update API
        account.pull_updates()
        # Close popup
        details_cover.destroy()
        # Update groups UI
        loaded_classes = api.get("groups")
        # Updated local user
        filter_classes()

    if account.get("username") == class_data.get("owner"):
        delete_btn = ctk.CTkButton(button_section, text="Delete Class",
                                  fg_color="#FF6B6B", text_color=colour.TXT,
                                  height=40, width=120, corner_radius=5,
                                  command=lambda: delete_class(class_data))
        delete_btn.pack(side="right", padx=5)
    

def handle_class_action(class_data):
    global loaded_classes
    joined = account.get("username") in class_data.get("members", [])
    if joined:
        # Leaving
        success = api.post(f"groups/{class_data.get('id')}/leave", account.get())
    else:
        # Joining
        success = api.post(f"groups/{class_data.get('id')}/join", account.get())
    # Update groups UI
    loaded_classes = api.get("groups")
    # Updated local user
    account.pull_updates()
    print(account.get("groups"))
    filter_classes()

    

# Function: filter_classes
# Desc:     Filters classes based on search input
# Inputs:   args - Event arguments (not used)
# Outputs:  None
def filter_classes(*args):
    global search_entry, content_frame, loaded_classes, filter_select
    loaded_classes = api.get("groups")
    search_text = search_entry.get().strip().lower()
    classes = []
    final_classes = {}
    # Check for search matches
    for group in loaded_classes.values():
        if search_text in group["name"].lower() or search_text in group["school"].lower():
            classes.append(group)
    # Check for filter matches
    filter_value = filter_select.get_value()
    if filter_value == "My Classes":
        username = account.get("username")
        for group in classes:
            if username in group.get("members", []):
                final_classes[group.get("id")] = group
    elif filter_value == "Same School":
        school = account.get("school")
        print(school)
        for group in classes:
            if group.get("school") == school:
                final_classes[group.get("id")] = group
    # This was code that would overwrite all the filtering previously done
    # for group in classes:
    #     final_classes[group.get("id")] = group
    # Clear and fill content frame with filtered classes
    fill_classes(content_frame, final_classes)
    return

def create_new_class(app:ctk.CTk):
    global loaded_classes
    # Create form cover
    cover = ctk.CTkFrame(app, fg_color=colour.BG, corner_radius=0)
    cover.place(relx=0, rely=0, relwidth=1, relheight=1)
    
    # Main form frame
    form_frame = ctk.CTkFrame(cover, fg_color=colour.BG2, corner_radius=10, 
                             border_color=colour.GREY, border_width=2,
                             width=400, height=500)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")
    form_frame.grid_propagate(False)
    
    # Configure grid
    form_frame.columnconfigure(0, weight=1)
    form_frame.rowconfigure(0, weight=1)
    form_frame.rowconfigure(1, weight=2)
    form_frame.rowconfigure(2, weight=1)
    form_frame.rowconfigure(3, weight=1)
    form_frame.rowconfigure(4, weight=1)
    
    # Close button
    close_btn = ctk.CTkButton(form_frame, text="✕", width=30, height=30,
                             fg_color="transparent", text_color=colour.TXT,
                             hover_color=colour.GREY, corner_radius=15,
                             command=cover.destroy)
    close_btn.place(relx=0.95, rely=0.05, anchor="center")
    
    # Title
    title_label = ctk.CTkLabel(form_frame, text="Create New Class",
                              font=("sans-serif", 24, "bold"),
                              text_color=colour.TXT)
    title_label.grid(row=0, column=0, pady=(30, 10))
    
    # Color selector frame
    color_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    color_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
    
    # Color display (starts blue)
    selected_color = "#4A90E2"
    color_display = ctk.CTkFrame(color_frame, fg_color=selected_color, height=80, corner_radius=10)
    color_display.pack(fill="x", pady=(0, 10))
    
    color_label = ctk.CTkLabel(color_display, text="Click to change colour...",
                              font=("sans-serif", 16), text_color="white")
    color_label.place(relx=0.5, rely=0.5, anchor="center")

    # Subject input
    subject_frame = ctk.CTkFrame(form_frame, fg_color="transparent", height=30, corner_radius=5)
    subject_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=10)

    subjects = api.get("subjects").get("subjects", [])
    subject_input = SelectInput(subject_frame, subjects, "Select Subject")
    subject_input.configure(fg_color=colour.GREY)
    subject_input.place(relx=0.5, rely=0.5, anchor="center", relheight=1, relwidth=0.9)
    
    # Description textbox
    desc_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    desc_frame.grid(row=3, column=0, sticky="ew", padx=30, pady=10)
    
    desc_textbox = ctk.CTkTextbox(desc_frame, height=100, corner_radius=10,
                                 fg_color=colour.BG, border_color=colour.GREY,
                                 border_width=1)
    desc_textbox.pack(fill="x")
    desc_textbox.insert("0.0", "Type description here...")
    
    # Button frame
    button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    button_frame.grid(row=4, column=0, sticky="ew", padx=30, pady=20)
    
    # Cancel button
    cancel_btn = ctk.CTkButton(button_frame, text="CANCEL",
                              fg_color="transparent", text_color=colour.ACC,
                              border_color=colour.ACC, border_width=2,
                              height=40, width=120,
                              command=cover.destroy)
    cancel_btn.pack(side="right", padx=(10, 0))
    
    # Create button
    create_btn = ctk.CTkButton(button_frame, text="CREATE",
                              fg_color=colour.ACC, text_color="white",
                              height=40, width=120,
                              command=lambda: handle_create_class(cover))
    create_btn.pack(side="right")
    
    # Color picker function
    def change_color():
        colors = ["#4A90E2", "#7ED321", "#50E3C2", "#BD10E0", "#F5A623", 
                 "#7B68EE", "#D0021B", "#F8A347", "#9013FE", "#FF5722"]
        import random
        nonlocal selected_color
        selected_color = random.choice(colors)
        color_display.configure(fg_color=selected_color)

    change_color()
    
    # Bind color change
    color_display.bind("<Button-1>", lambda e: change_color())
    color_label.bind("<Button-1>", lambda e: change_color())
    
    def handle_create_class(cover):
        # Get form data
        description = desc_textbox.get("0.0", "end-1c")
        if description == "Type description here...":
            description = ""
        subject = subject_input.get_value()
        # Validate description
        if len(description) > 100:
            messagebox.showerror("Error", "Description cannot exceed 100 characters.")
            return
        if subject == "Select Subject":
            messagebox.showerror("Error", "Please select a subject.")
            subject_input.focus()
            return
        
        # Create new class data (placeholder)
        new_class = {
            "name": subject,
            "members": [account.get("username")],
            "school": account.get("school"),
            "colour": selected_color,
            "description": description,
            "events": {},
            "owner": account.get("username"),
        }
        
        # Send to API
        response = api.post("groups/create", new_class)
        if not response.get("success"):
            if response.get("error") == "Group already exists":
                messagebox.showerror("Error", "Group with the same subject and school already exist.")
            else:
                messagebox.showerror("Error", "Failed to create class. Please try again.")
            return
        loaded_classes = api.get("groups")
        print(new_class)
        # Close the form
        cover.destroy()
        messagebox.showinfo("Success", "Class created successfully!")
        # Refresh
        account.pull_updates()
        global content_frame
        loaded_classes = api.get("groups")
        fill_classes(content_frame, loaded_classes)
        return
        
        
def construct(app:ctk.CTk) -> ctk.CTkFrame:
    global search_entry, content_frame, filter_select
    # Configure rows/columns
    frame_main = ctk.CTkFrame(app, fg_color="transparent")
    frame_main.columnconfigure(0, weight=1)
    frame_main.rowconfigure(0, minsize=80)  # Header
    frame_main.rowconfigure(1, weight=1)    # Content
    frame_main.grid(row=0, column=1, sticky="nsew")
    
    # Header section
    header_frame = ctk.CTkFrame(frame_main, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
    header_frame.columnconfigure(0, weight=1)
    header_frame.columnconfigure(1, weight=1)
    header_frame.columnconfigure(2, weight=1)
    
    # Search bar
    search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    search_frame.grid(row=0, column=0, sticky="w")

    search_label = ctk.CTkLabel(search_frame, text="Search Classes:", 
                               text_color=colour.TXT, font=("sans-serif", 16))
    search_label.pack(side="left", padx=(0, 10))

    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search...", 
                               width=300, height=40)
    search_entry.bind("<KeyPress>", filter_classes)
    search_entry.bind("<FocusOut>", filter_classes)
    search_entry.pack(side="left", padx=(0, 10))
    
    # Filter dropdown
    filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    filter_frame.grid(row=0, column=1, sticky="")
    
    filter_label = ctk.CTkLabel(filter_frame, text="Filter by:", 
                               text_color=colour.TXT, font=("sans-serif", 16))
    filter_label.pack(side="left", padx=(0, 10))
    filter_select = SelectInput(filter_frame, ["My Classes", "Same School"], "Same School", filter_classes)
    filter_select.pack_propagate(False)
    filter_select.configure(width=150, height=40)
    filter_select.pack(side="left", padx=(0, 10))
    
    # Create class button
    create_btn = ctk.CTkButton(header_frame, text="Create Class", 
                              fg_color="#4A90E2", text_color="white",
                              height=40, command=lambda: create_new_class(app))
    create_btn.grid(row=0, column=2, sticky="e")
    
    # Content area with scrollable frame
    content_frame = ctk.CTkScrollableFrame(frame_main, fg_color="transparent")
    content_frame.grid(row=1, column=0, sticky="nsew", padx=20)
    content_frame.columnconfigure(0, weight=1)
    content_frame.columnconfigure(1, weight=1)
    
    # Generate class tiles dynamically
    groups = api.get("groups")
    filter_classes()
    
    # Construct sidebar
    sidebar_weight = sidebar.get_mode()
    sidebar.set_mode("open" if sidebar_weight == "closed" else sidebar_weight, app)
    sidebar.highlight_tab("groups")
    return frame_main