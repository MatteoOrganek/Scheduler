# Scheduler

Scheduler is a web scraper designed to interface with the Harri schedule tool used by my workplace. The program synchronizes my work shifts with Google Calendar by automatically adding or removing events based on my schedule.


## Installation

### Prerequisites
Ensure you have the following installed:
- Python (latest version recommended)
- Required dependencies (install via `requirements.txt`)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/MatteoOrganek/Scheduler.git
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Create a `credentials.py` file in the project root with the following variables:
   ```python
   HARRI_EMAIL = "your_harri_email"
   HARRI_PASSWORD = "your_harri_password"
   ID_LINK = "https://gateway.harri.com/team/api/v3/brands/xxxxxxxx"
   SCHEDULE_LINK = "https://gateway.harri.com/scheduling/api/v1/brands/xxxxxxxx"
   ```

4. Obtain Google Calendar API credentials:
   - Follow [this guide](https://developers.google.com/workspace/guides/create-credentials) to create a `credentials.json` file.
   - Place `credentials.json` in the project root.

5. On first run, you will be redirected to grant access to a google account, and, on successful authorization, a `token.json` file will be generated to store temporary access and refresh tokens.

## Usage
Run the script to sync your schedule with Google Calendar:
```sh
python scheduler.py
```

## Future Improvements
- Improve efficiency in calendar updates
- Add Roehampton univerity's Seats schedule tool

## Contact
Feel free to reach out if you have any questions or feedback.

