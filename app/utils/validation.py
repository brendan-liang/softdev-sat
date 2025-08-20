#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         validation.py
# Program:      trackademic
# Desc:         Validation functions for user input in the signup process
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     17-08-2025

# Import UI libraries
from tkinter import messagebox

# Constants
VALID_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
CAPITAL_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWERCASE_LETTERS = "abcdefghijklmnopqrstuvwxyz"
SPECIAL_CHARACTERS = "!@#$%^&*()-_=+[]{}|;:',.<>?/~`\\"

# Function: username
# Desc:     Validate the username input
# Inputs:   username (str): The username to validate
# Outputs:  bool: Whether the username is valid
def username(username: str) -> bool:
    if not username or len(username) < 3 or len(username) > 32 or not all(char in VALID_CHARACTERS for char in username):
        messagebox.showwarning("Warning", "Username must be between 3 and 32 characters long and can only contain letters, numbers, and underscores!", icon="warning")
        return False
    return True

# Function: display_name
# Desc:     Validate the display name input
# Inputs:   display_name (str): The display name to validate
# Outputs:  bool: Whether the display name is valid
def display_name(display_name: str) -> bool:
    if not display_name or len(display_name) < 3 or len(display_name) > 64 or not all(char in VALID_CHARACTERS + " -" for char in display_name):
        messagebox.showwarning("Warning", "Display name must be between 3 and 64 characters long and can only contain letters, numbers, underscores, dashes, and spaces!", icon="warning")
        return False
    return True

# Function: password
# Desc:     Validate the password input
# Inputs:   password (str): The password to validate
# Outputs:  bool: Whether the password is valid
def password(password: str) -> bool:
    if not password or len(password) < 8 or len(password) > 64 or not any(char.isdigit() for char in password) or not any(char in CAPITAL_LETTERS for char in password) or not any(char in LOWERCASE_LETTERS for char in password) or not any(char in SPECIAL_CHARACTERS for char in password) or not all(char in VALID_CHARACTERS+SPECIAL_CHARACTERS for char in password):
        messagebox.showwarning("Warning", "Password must be between 8 and 64 characters long, contain at least one digit, one uppercase letter, one lowercase letter, and one special character! No other symbols are allowed!", icon="warning")
        return False
    return True

# Function: school
# Desc:     Validate the school name input
# Inputs:   school (str): The school name to validate
# Outputs:  bool: Whether the school name is valid
def school(school: str) -> bool:
    if (not school) or (school == "Select school..."):
        messagebox.showwarning("Warning", "Please select a school!", icon="warning")
        return False
    return True