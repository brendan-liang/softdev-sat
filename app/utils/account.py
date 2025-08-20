#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         account.py
# Program:      trackademic
# Desc:         Account management functions for user authentication and signup
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     16-08-2025

# Import libraries
from hashlib import sha256
from utils import api, config

# Function: signin
# Desc:     Sign in a user with username and password
# Inputs:   username (str): The username of the user
#           password_hash (str): The hashed password of the user (optional)
#           password (str): The plaintext password of the user (optional)
# Outputs:  tuple: (success (bool), user (dict)): Whether the signin was successful and the user data if successful
def signin(username, password_hash=None, password=None):
    # Hash password if not already
    if password and not password_hash:
        password_hash = sha256(password.encode("utf-8")).hexdigest()
    elif not password and not password_hash:
        # Corrupted config
        config.write({"loggedIn": False, "loggedInUser": None})
        return False, None

    # Make API request to signin
    result = api.post("users/signin", {
        "username": username,
        "display_name": "",
        "password_hash": password_hash,
        "school": "",
        "groups": {},
        "events": {}
    })

    if result.get("error"):
        print(result.get("error"))
        return False, None
    
    # Save user to config
    data = config.read()
    data["loggedIn"] = True
    data["loggedInUser"] = {
        "username": username,
        "display_name": result.get("display_name", ""),
        "password_hash": password_hash,
        "school": result.get("school", ""),
        "groups": result.get("groups", {}),
        "events": result.get("events", {})
    }
    config.write(data)

    return True, result

# Function: signup
# Desc:     Sign up a new user with username, display name, and password
# Inputs:   username (str): The username of the new user
#           display_name (str): The display name of the new user
#           password (str): The plaintext password of the new user
# Outputs:  bool: Whether the signup was successful
def signup(username, display_name, password, school):
    password_hash = sha256(password.encode("utf-8")).hexdigest()
    result = api.post("users/signup", {
        "username": username,
        "display_name": display_name,
        "password_hash": password_hash,
        "school": school,
        "groups": {},
        "events": {}
    })

    if result.get("error"):
        return False
    
    # Save user to config
    data = config.read()
    data["loggedIn"] = True
    data["loggedInUser"] = {
        "username": username,
        "display_name": display_name,
        "password_hash": password_hash,
        "school": school,
        "groups": {},
        "events": {}
    }
    config.write(data)
    
    return True

# Function: check_signin
# Desc:     Check if a user is signed in
# Inputs:   None
# Outputs:  bool: Whether the user is signed in and if the credentials are valid
def check_signin():
    data = config.read()
    logged_in = data.get("loggedIn")
    logged_in_user = data.get("loggedInUser")
    print(logged_in, logged_in_user)
    if logged_in and logged_in_user:
        # Check that provided credentials work
        success, user = signin(logged_in_user.get("username"), logged_in_user.get("password_hash"))
        if success:
            return True
        else:
            # If credentials don't work, reset config
            data["loggedIn"] = False
            data["loggedInUser"] = None
            config.write(data)
            return False
        
    else:
        data["loggedIn"] = False
        config.write(data)
        return False
    
# Function: get
# Desc:     Get a specific key from the logged in user's data
# Inputs:   key (str): The key to retrieve from the logged in user's data
# Outputs:  str: The value of the key if it exists, None otherwise
def get(key=None):
    data = config.read()
    logged_in_user = data.get("loggedInUser")
    if logged_in_user:
        if key:
            return logged_in_user.get(key)
        return logged_in_user
    return None

# Function: pull_updates
# Desc:     Pull updates for the logged in user from the API
# Inputs:   None
# Outputs:  bool: Whether the pull was successful
def pull_updates():
    user = get()
    if not user:
        return False
    username = user.get("username")
    result = api.get(f"users/{username}")
    if result.get("error"):
        return False
    # Update config with new user data
    data = config.read()
    # Save password hash since API does not return it
    password_hash = data["loggedInUser"].get("password_hash", "")
    result["password_hash"] = password_hash
    # Save updated user data
    data["loggedInUser"] = result
    config.write(data)
    return True

def get_all_events():
    user = get()
    if not user:
        return {}
    username = user.get("username")
    # Get private events