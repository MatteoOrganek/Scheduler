Scheduler

Scheduler is a web scraper designed to interface with the Harri schedule tool used by my workplace. The program synchronizes my work shifts with Google Calendar by automatically adding or removing events based on my schedule. Ongoing development aims to improve automation and streamline the process further.

Features

Scrapes schedule data from Harri

Modifies Google Calendar by adding or removing shifts

Stores credentials securely for seamless authentication

Generates and manages temporary access tokens

Installation

Prerequisites

Ensure you have the following installed:

Python (latest version recommended)

Required dependencies (install via requirements.txt)

Setup

Clone the repository:

git clone <repository_url>
cd <repository_directory>

Install dependencies:

pip install -r requirements.txt

Create a credentials.py file in the project root with the following variables:

OWRES_USERNAME = "your_username"
OWRES_PASSWORD = "your_password"
HARRI_EMAIL = "your_harri_email"
HARRI_PASSWORD = "your_harri_password"
ID_LINK = "https://gateway.harri.com/team/api/v3/brands/xxxxxxxx"
SCHEDULE_LINK = "https://gateway.harri.com/scheduling/api/v1/brands/xxxxxxxx"

Obtain Google Calendar API credentials:

Follow this guide to create a credentials.json file.

Place credentials.json in the project root.

On first run, a token.json file will be generated to store temporary access and refresh tokens.

Usage

Run the script to sync your schedule with Google Calendar:

python scheduler.py

Future Improvements

Enhance error handling and logging

Implement a user-friendly configuration interface

Improve efficiency in data retrieval and calendar updates

License

This project is for personal use. If you plan to modify or distribute it, please ensure proper acknowledgment.

Contact

For any inquiries or contributions, feel free to reach out.

