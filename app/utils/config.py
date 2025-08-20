#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         config.py
# Program:      trackademic
# Desc:         Configuration management for the application
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     17-08-2025

import json
from os import path

LOCAL_FILE = "config.json"

def read():
    global LOCAL_FILE
    if not path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "w") as file:
            file.write("{}")
    data = None
    with open(LOCAL_FILE, "r") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            return {}
    return data

def write(data:dict):
    global LOCAL_FILE
    with open(LOCAL_FILE, "w") as file:
        json.dump(data, file, indent=4)