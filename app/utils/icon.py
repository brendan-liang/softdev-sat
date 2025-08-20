#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         icon.py
# Program:      trackademic
# Desc:         Icon utility functions for managing application icons
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     17-08-2025

import customtkinter as ctk
from PIL import Image
import os

icons_dict = {}
ICONS_DIR = "icons"

def load_icons():
    global icons_dict, ICONS_DIR

    for filename in os.listdir(ICONS_DIR):
        if filename.endswith(".png"):
            name = os.path.splitext(filename)[0]
            img_path = os.path.join(ICONS_DIR, filename)
            icons_dict[name] = Image.open(img_path)
            print

def icon(name:str):

    if (f"light_{name}" not in icons_dict) or (f"dark_{name}" not in icons_dict): 
        name = "unknown"

    icon = ctk.CTkImage(light_image=icons_dict[f"light_{name}"], dark_image=icons_dict[f"dark_{name}"])

    return icon