 Desktop Library Management System
A local desktop application built with Python to manage book collections, track member records, and read text files stored securely in the cloud.

What It Does
Desktop Interface: Built using wxPython for a clean, responsive native GUI featuring custom panels, search functionality, and dual-view navigation (Home, My Books, Due Books).   

Cloud Storage Integration: Fetches and reads text files dynamically from Cloudinary using authenticated signed URLs so book content loads securely on demand.   

Relational Database: Uses PostgreSQL to persist book records, links, and user associations.

Tech Stack
Language: Python

GUI: wxPython

Database: PostgreSQL

Cloud Storage: Cloudinary (raw authenticated assets)

Networking: Requests

Local Setup:
Clone the repository;

Set up your virtual environment;

Bash
python -m venv .response
.response\Scripts\Activate
Install dependencies:

Code snippet
pip install -r requirements.txt
Configure your environment:
Create a .env file in the root directory and add your PostgreSQL and Cloudinary credentials.

Run the application;

Bash
python librarygui.py
