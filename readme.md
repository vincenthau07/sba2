# Introduction
A website server for facilities and rooms booking.

# Content
1. [How-to-Get-Started](#how-to-get-started)
2. [Website-Guide](#website-guide)
3. [Folders](#folders)


# How-to-Get-Started

**Make sure you have installed Python with 3.11.0 or above, and Pip with version 24.0 or above**

It might work in older python version but it is **NOT GUARANTEED**.

You can get python installer from: [Python 3.11.0](https://www.python.org/downloads/release/python-3110/)

**Make sure you have installed Module Flask with version 3.0.2 or above**

You can install the required modules with:
```
pip install -r /path/to/requirements.txt
```
You can also specify the hosting IP address and PORT in `setting.py`

## Start-the-Web-Server
Run the command:
```
python main.py
```
You can browse the web server with: (default)

Localhost: 127.0.0.1

LAN: { IP-ADDRESS }


If you wish to browse through WAN, please consider using gunicorn, port forwards, tunneling, etc.

# Website-Guide
## Login
You can login by inputting user ID and password.

Note: It will integrate into new templates in the future.

**Accout for testing:**

UserID: S190377

Password: 12345678

## Home
Home

Note: Notification, clock will be included in the future.

## My records
You can cancel and restone booking records.

## Booking

You can book a room/facility by clicking RID of the room/facility.\
You can also sort the table by clicking the field.

You can check the room usage by selecting a week.

You can get more information by clicking the booked session.


You can add a record by filling the form.\
You can filter school units by selecting a category.

Note: It will integrate into new templates in the future.

**Please note that users who have no permission to edit room/facility records have to let the one who has that permission to approve their booking.**

## Approve
**Your account must have a permission to manage the corresponding table.**

You can approve or deny other's booking.

## Management
**Your account must have a permission to manage the corresponding table.**

You can either delete a record, modify a record or add a record.

## SQL
**This is for administrators only.**

You can get a full control of the database of this website by executing sql commands.

## Dashboard
**This is for administrators only.**

You can monitor cpu usage and ram usage through this website and have a general understanding of room/facility usage.

Note: It will integrate into new templates in the future.

## My Account
You can change your personal information here.

Note: It will integrate into new templates in the future.

## Logout
Logout

# Folders
## /app
Server Application

## /app/helpers.py
Some useful python functions

## /blueprints
Python codes for each webpage.

## /app/templates
Html code for each webpage.

## /app/static
Static elements (photos, css, js) for webpages.

## /database
Database files and schema in python.