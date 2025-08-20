#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:     main.py
# Program:  trackademic
# Desc:     FastAPI application for managing trackademic users, groups, and events.
#
# Author:   Brendan Liang
# Created:  19-07-2025
# Modified: 18-08-2025

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from time import sleep
from hashlib import sha256
import datetime
import json

# Function: lifespan
# Desc:    Manages the lifespan of the FastAPI application (startup & shutdown), loading and saving all data.
# Input:   app (FastAPI): The FastAPI application instance.
# Output:  None
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load users from file
    try:
        with open("users.json", "r") as f:
            app.users = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        app.users = {}
        with open("users.json", "w") as f:
            json.dump(app.users, f, indent=4)
    # Load groups from file
    try:
        with open("groups.json", "r") as f:
            app.groups = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        app.groups = {}
        with open("groups.json", "w") as f:
            json.dump(app.groups, f, indent=4)
    yield

    # Save users to file
    await dump()

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Constants
HOST = "127.0.0.1"
PORT = 8000

# Class:    User
# Desc:     Represents a user with username, display name, and password hash.
# Properties:
#   - username (str): The user's username.
#   - display_name (str): The user's display name.
#   - password_hash (str): The user's password hash.
class User(BaseModel):
    username: str
    display_name: str = ""
    password_hash: str = ""
    school: str = ""
    groups: dict[str, bool] = {}
    events: dict[str, dict] = {}

# Class:    Group
# Desc:     Represents a group with name, description, school, members, and events.
# Properties:
#   - id (str): Unique identifier for the group, generated from name and school.
#   - name (str): The group's name.
#   - description (str): The group's description.
#   - school (str): The school associated with the group.
#   - members (list[str]): List of usernames of group members.
#   - events (list[dict]): List of event details associated with the group.
#   - colour (str): The group's colour, used for UI representation.
class Group(BaseModel):
    id: str=""
    name: str
    description: str
    school: str
    members: list[str]  # List of usernames
    events: dict[str, dict] = {}  # List of event details
    colour: str
    owner: str

class Event(BaseModel):
    id: str = ""
    numerical_id: int = 0
    title: str = ""
    description: str = ""
    type: str = "SAC"
    date: datetime.date = datetime.date.today()
    start_time: int = 0
    end_time: int = 1
    group_id: str = ""
    colour: str = "#7B68EE"
    owner: str = ""
    visible: bool = False

# Globals
app.users = {}
app.groups = {}

# Function: dump
# Desc:    Saves all globals to their respective JSON files.
# Input:   None
# Output:  None
async def dump():
    with open("users.json", "w") as f:
        json.dump(app.users, f, indent=4)
    with open("groups.json", "w") as f:
        json.dump(app.groups, f, indent=4)

# Function: check_user
# Desc:    Checks if a user exists and returns their details, obscuring the password hash.
# Input:   username (str): The username to check.
# Output:  JSON response with user details or an error message if the user does not exist
@app.get("/users/{username}")
async def check_user(username: str):
    # Get user
    user = app.users.get(username)
    if not user:
        return {"error": "User not found"}
    # Obscure password
    user = user.copy()
    user["password_hash"] = ""
    return user

# Function: signin_user
# Desc:     Reads user details from the request body and checks if provided credentials match.
# Input:    user (User): The user details from the request body.
# Output:   JSON response with user details or an error message if credentials do not match
@app.post("/users/signin")
async def signin_user(user: User):
    saved_user = app.users.get(user.username)
    if not saved_user:
        return {"error": "User not found"}
    if saved_user["password_hash"] != user.password_hash:
        return {"error": "Incorrect password"}
    return saved_user

# Function: create_user
# Desc:     Creates a new user with the provided details and saves it to the users file.
# Input:    user (User): The user details from the request body.
# Output:   JSON response indicating success or failure of user creation
@app.post("/users/signup")
async def create_user(user: User):
    app.users[user.username] = {
        "username": user.username,
        "display_name": user.display_name,
        "password_hash": user.password_hash,
        "school": user.school,
        "groups": user.groups,
        "events": user.events
    }

    await dump()
    return {"success": True}

# Function: update_user
# Desc:     Updates an existing user's details with the provided information and saves it to the users file.
# Input:    user (User): The user details from the request body.
# Output:   JSON response indicating success or failure of user update
@app.post("/users/update")
async def update_user(user: User):
    # Check if user exists
    if user.username not in app.users:
        return {"error": "User not found"}
    # Update user details
    app.users[user.username] = {
        "username": user.username,
        "display_name": user.display_name,
        "password_hash": user.password_hash or app.users[user.username]["password_hash"],
        "school": user.school or app.users[user.username]["school"],
        "groups": user.groups or app.users[user.username]["groups"],
        "events": user.events or app.users[user.username]["events"],
    }
    
    await dump()
    return {"success": True}

@app.post("/users/{username}/events/create")
async def create_event(username: str, event: Event):
    # Check if user exists
    user = app.users.get(username)
    if not user:
        return {"error": "User not found"}
    
    # Check if event_id was provided
    event_id = event.id
    numerical_id = event.numerical_id
    if not event.id or not numerical_id:
        # Previous event IDs
        previous_event_ids = [e["numerical_id"] for e in user["events"].values()]
        # Create event ID
        numerical_id = max(previous_event_ids, default=0) + 1
        event_id = sha256(f"{username}{numerical_id}".encode()).hexdigest()
    
    # Add event to user
    user["events"][event_id] = {
        "id": event_id,
        "numerical_id": numerical_id,
        "title": event.title,
        "description": event.description,
        "type": event.type,
        "date": event.date.isoformat(),
        "start_time": event.start_time,
        "end_time": event.end_time,
        "group_id": event.group_id,
        "colour": event.colour,
        "owner": username,
        "visible": event.visible,
    }
    # Create event in group if needed
    if event.group_id:
        group = app.groups.get(event.group_id)
        if group:
            if not group.get("events"):
                # Add event to group
                group["events"].append({
                    "id": event_id,
                    "numerical_id": numerical_id,
                    "title": event.title,
                    "description": event.description,
                    "type": event.type,
                    "date": event.date.isoformat(),
                    "start_time": event.start_time,
                    "end_time": event.end_time,
                    "colour": event.colour,
                    "owner": username,
                    "visible": event.visible,
                })
            app.groups[event.group_id] = group
    
    # Save changes
    app.users[username] = user
    await dump()
    
    return {"success": True, "event_id": event_id}

@app.post("/users/{username}/events/edit")
async def edit_event(username: str, event: Event):
    # Check if user exists
    user = app.users.get(username)
    if not user:
        return {"error": "User not found"}
    
    # Find event by ID
    existing_event = user["events"].get(event.id)
    if not existing_event:
        return {"error": "Event not found"}
    
    # Update event details

    new_event = {
        "id": existing_event["id"],
        "numerical_id": existing_event["numerical_id"],
        "title": event.title,
        "description": event.description,
        "type": event.type,
        "date": event.date.isoformat(),
        "start_time": event.start_time,
        "end_time": event.end_time,
        "group_id": event.group_id,
        "colour": event.colour,
        "owner": username,
        "visible": event.visible,
    }

    # Create event in group if needed
    print("hello", event.group_id)
    if event.group_id and event.visible:
        if existing_event.get("group_id") and existing_event["group_id"] != event.group_id:
            # Remove from old group
            old_group = app.groups.get(existing_event["group_id"])
            if old_group:
                old_group["events"] = [e for e in old_group["events"] if e["id"] != event.id]
                app.groups[existing_event["group_id"]] = old_group
        group = app.groups.get(event.group_id)
        if group:
        # Add event to new group if not already present
            if event.id not in group["events"]:
                app.groups[event.group_id]["events"][event.id] = new_event
            else:
                # Update existing group event details
                group_event = group["events"][event.id]
                group_event.update(new_event)
                app.groups[event.group_id]["events"][event.id] = group_event

    print(existing_event)

    # Save changes
    app.users[username]["events"][event.id] = new_event
    await dump()
    
    return {"success": True, "message": "Event updated successfully"}

@app.get("/users/{username}/events/delete/{event_id}")
async def delete_event(username: str, event_id: str):
    # Check if user exists
    user = app.users.get(username)
    if not user:
        return {"error": "User not found"}
    
    # Find event by ID
    event = user["events"].get(event_id)
    if not event:
        return {"error": "Event not found"}
    
    # Remove event from user
    del user["events"][event_id]
    
    # Remove event from group if it exists
    if event.get("group_id"):
        group = app.groups.get(event["group_id"])
        if group:
            group["events"] = [e for e in group["events"] if e["id"] != event_id]
            app.groups[event["group_id"]] = group
    
    # Save changes
    app.users[username] = user
    await dump()
    
    return {"success": True, "message": "Event deleted successfully"}

# Function: create_group
# Desc:     Creates a new group with the provided details and saves it to the groups file.
# Input:    group (Group): The group details from the request body.
# Output:   JSON response indicating success or failure of group creation
@app.post("/groups/create")
async def create_group(group: Group):
    # Check if group exists
    group_id = sha256(f"{group.name}{group.school}".encode()).hexdigest()
    if group_id in app.groups:
        return {"error": "Group already exists"}
    # Create group
    app.groups[group_id] = {
        "id": group_id,
        "name": group.name,
        "description": group.description,
        "school": group.school,
        "members": group.members,
        "events": group.events,
        "colour": group.colour,
        "owner": group.owner
    }
    # Add to user
    for member in group.members:
        app.users[member]["groups"][group_id] = True
    await dump()
    return {"success": True, "group_id": group_id}

# Function: get_group
# Desc:     Retrieves a group by its ID and returns its details.
# Input:    group_id (str): The ID of the group to retrieve.
# Output:   JSON response with group details or an error message if the group does not exist
@app.get("/groups/{group_id}")
async def get_group(group_id: str):
    # Get group
    group = app.groups.get(group_id)
    if not group:
        return {"error": "Group not found"}
    return group

# Function: leave_group
# Desc:     Allows a user to leave a group by removing them from the group's members list.
# Input:    group_id (str): The ID of the group to leave.
#           user (User): The user who is leaving the group.
# Output:   JSON response indicating success or failure of leaving the group
@app.post("/groups/{group_id}/leave")
async def leave_group(group_id: str, user: User):
    # Check if group exists
    group = app.groups.get(group_id)
    if not group:
        return {"error": "Group not found"}
    
    # Remove user from group members
    if user.username in group["members"]:
        group["members"].remove(user.username)

    # Remove group from user
    if group_id in app.users.get(user.username, {}).get("groups", {}):
        del app.users[user.username]["groups"][group_id]

    # Change owner if the user leaving is the owner
    if group["owner"] == user.username:
        # Find a new owner (first member in the list)
        if group["members"]:
            group["owner"] = group["members"][0]
        else:
            group["owner"] = None
    
    # Save changes
    app.groups[group_id] = group
    await dump()
    
    return {"success": True, "message": "User left the group successfully"}

# Function: delete_group
# Desc:     Deletes a group by its ID, removing it from the groups file.
# Input:    group_id (str): The ID of the group to delete.
# Output:   JSON response indicating success or failure of group deletion
@app.get("/groups/{group_id}/delete")
async def delete_group(group_id: str):
    group = app.groups.get(group_id)
    if not group:
        return {"error": "Group not found"}
    # Force remove frm all users
    for member in group["members"]:
        if member in app.users:
            user = app.users[member]
            if group_id in user["groups"]:
                print("Removing group from user:", member)
                del user["groups"][group_id]
            app.users[member] = user
    # Remove group
    del app.groups[group_id]
    # Save changes
    await dump()
    return {"success": True, "message": "Group deleted successfully"}

# Function: join_group
# Desc:     Allows a user to join a group by adding them to the group's members list.
# Input:    group_id (str): The ID of the group to join.
#           user (User): The user who is joining the group.
# Output:   JSON response indicating success or failure of joining the group
@app.post("/groups/{group_id}/join")
async def join_group(group_id: str, user: User):
    # Check if group exists
    group = app.groups.get(group_id)
    if not group:
        return {"error": "Group not found"}
    
    # Add group to user
    target_user = app.users.get(user.username)
    if target_user:
        # Check if user is already in the group
        if group_id not in target_user["groups"]:
            target_user["groups"][group_id] = True

    # Add user to group members
    if not user.username in group["members"]:
        group["members"].append(user.username)
    
    # Make user owner if they are the first member
    if len(group["members"]) == 1:
        group["owner"] = user.username
    
    # Save changes
    app.groups[group_id] = group
    app.users[user.username] = target_user
    await dump()
    
    return {"success": True, "message": "User joined the group successfully"}

# Function: get_all_groups
# Desc:     Returns a list of all groups.
# Input:    None
# Output:   JSON response with a list of all groups
@app.get("/groups")
async def get_all_groups():
    # Return all groups
    return app.groups

@app.get("/groups/{group_id}/events/delete/{event_id}")
async def delete_event(group_id: str, event_id: str):
    # Check if group exists
    group = app.groups.get(group_id)
    if not group:
        return {"error": "Group not found"}
    
    # Find event by ID
    event = group["events"].get(event_id)
    if not event:
        return {"error": "Event not found"}
    
    # Remove event from group
    if event_id in group["events"]:
        del group["events"][event_id]
    # Remove event from all users in the group
    for member in group["members"]:
        user = app.users.get(member)
        if user and event_id in user["events"]:
            del user["events"][event_id]
            app.users[member] = user
    
    # Save changes
    app.groups[group_id] = group
    await dump()
    
    return {"success": True, "message": "Event deleted successfully"}

@app.get("/subjects")
async def get_subjects():
    # Load subjects from file
    try:
        with open("subjects.json", "r") as f:
            subjects = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        subjects = []
    
    return {"subjects": subjects}

@app.get("/schools")
async def get_schools():
    # Load schools from file
    try:
        with open("schools.json", "r") as f:
            schools = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        schools = []
    
    return {"schools": schools}

# Function: not_found
# Desc:    Handles requests to a non-existent route, returning a 404 error message.
# Input:   None
# Output:  JSON response with a 404 error message
@app.api_route("/404", methods=["GET", "POST"])
async def not_found():
    return {"error": "404 Not Found"}
            
# 404 Redirecting was disabled so that user not found can be handled by the API
# @app.exception_handler(404)
# async def handle_404(_, __):
#     return RedirectResponse("/404")

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    # Start server
    uvicorn.run("main:app", host=HOST, port=PORT)