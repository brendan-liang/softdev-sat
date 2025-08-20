#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         colour.py
# Program:      trackademic
# Desc:         Colour utility functions for managing application themes
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     17-08-2025

# Import libraries
import customtkinter as ctk

# Function: toggle
# Desc:     Toggle the application between light and dark mode
# Inputs:   None
# Outputs:  None
def toggle():
    if ctk.get_appearance_mode().lower() == "dark":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")

# Values (light, dark)
BG = ("#fbfbfb", "#1a1a1a")
BG2 = ("#ffffff", "#000000")
ACC = ("#36b2ff", "#36b2ff")
TXT = ("#1a1a1a", "#fbfbfb")
TXT2 = ("#000000", "#ffffff")
GREY = ("#eaeaea", "#3f3f3f")