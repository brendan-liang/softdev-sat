#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File:         utils/api.py
# Program:      trackademic
# Desc:         API utility functions for making HTTP requests
#
# Author:       Brendan Liang
# Created:      19-07-2025
# Modified:     16-08-2025

# Import libraries
import requests
import json
from tkinter import messagebox

# Constants
# Define the host and port for the API server
HOST = "127.0.0.1"
PORT = 8000

# Function: post
# Desc:     Make a POST request to the API
# Inputs:   endpoint (str): The API endpoint to post to
#           data (dict): The data to send in the request body
# Outputs:  dict: The JSON response from the API
def post(endpoint, data) -> dict:
    url = f"http://{HOST}:{PORT}/{endpoint}"
    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            return {"error": "network"}
        return response.json()
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Failed to connect to the server. Please check your network connection.", icon="error")
        return {"error": "network"}
    
# Function: get
# Desc:     Make a GET request to the API
# Inputs:   endpoint (str): The API endpoint to get data from
# Outputs:  dict: The JSON response from the API
def get(endpoint) -> dict:
    url = f"http://{HOST}:{PORT}/{endpoint}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "network"}
        return response.json()
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Error", "Failed to connect to the server. Please check your network connection.", icon="error")
        return {"error": "network"}