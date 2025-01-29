import operator
import pathlib
import platform
import random
from datetime import datetime, timedelta
from time import sleep
import time

import requests

from pyvirtualdisplay import Display
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import seleniumwire.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import communicator
import credentials

# pip install blinker==1.7.0

if platform.system() == 'Windows':
    PI = False
else:
    PI = True


# BLOCK = [ID, FIRST NAME, LAST NAME, POSITION, START_SCHEDULE, END_SCHEDULE, NOTE]
class ScheduleBlock:
    def __init__(self, block):
        self.id = block[0]
        self.first_name = block[1]
        self.last_name = block[2]
        self.position = block[3]
        self.start_schedule = block[4]
        self.end_schedule = block[5]
        self.note = block[6]
        self.hours = self.calculate_hours()
        self.shift_type = self.determine_shift_type()

    def calculate_hours(self):
        difference = self.end_schedule - self.start_schedule
        return difference.seconds / 60 / 60

    def determine_shift_type(self):
        if 6 <= self.start_schedule.hour < 15 and self.end_schedule.hour <= 17 and self.hours < 9:
            return "EARLY"
        elif 15 <= self.end_schedule.hour <= 24 and self.hours < 9:
            return "LATE"
        else:
            return "DOUBLE"


def slow_type(element, text, delay_s=0.1, delay_e=0.4):
    """Send a text to an element one character at a time with a delay."""
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(delay_s, delay_e))


def get_driver():
    print("@ Creating new driver session...")
    options = Options()
    script_directory = pathlib.Path().absolute()
    options.add_argument("--disable-extensions")
    options.add_experimental_option('useAutomationExtension', False)

    if PI:
        display = Display(visible=False, size=(3600, 2200))
        display.start()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--use_subprocess")
        options.headless = True
        print("@ Virtual display successfully setup.")
        options.add_argument(f"user-data-dir=chromedriver")
        service = Service(executable_path="/usr/lib/chromium-browser/chromedriver")
        _driver = webdriver.Chrome(seleniumwire_options={'mitm_http2': False}, options=options, service=service)
        print("@ Driver successfully setup.")

    else:
        options.add_argument(f"user-data-dir={script_directory}\\owres")
        _driver = webdriver.Chrome(seleniumwire_options={'mitm_http2': False}, options=options)
        print("@ Driver successfully setup.")

    return _driver


def login(_driver):
    print("* Fetching rota...")
    _driver.get("https://live.harri.com/schedule")

    _iterations = 200

    while _iterations != 0:
        print("\r", end="")
        print(f"* Scanning ... {_iterations}", end="")

        # In Login
        try:
            _driver.find_element(By.XPATH, "//*[contains(text(),'Forgot password?')]")
            print("@ Currently in login page.")
            print("@ Injecting login info...")
            sleep(1.38)
            email_entry = _driver.find_element(By.XPATH, "//input[@name='username']")
            email_entry.clear()
            email_entry.send_keys(credentials.HARRI_EMAIL)
            sleep(1.23)

            print("@ Email OK")
            password_entry = _driver.find_element(By.XPATH, "//input[@name='password']")
            password_entry.clear()
            password_entry.send_keys(credentials.HARRI_PASSWORD)
            sleep(1.35)

            print("@ Password OK")

            login_btn = _driver.find_element(By.XPATH, "//*[contains(text(),'Log in')]")
            _driver.execute_script("arguments[0].click();", login_btn)
            print("@ Login info successfully injected.")

            sleep(10)

        except NoSuchElementException:
            print("", end="")

        # Inside Schedule
        try:
            _driver.find_element(By.XPATH, "//*[contains(text(),'General Manager')]")
            print("\n@ Currently in schedule page.")
            break

        except NoSuchElementException:
            print("", end="")
        sleep(1)
        _iterations -= 1


def get_identification(_driver):
    print("* Fetching identification and cookies... ", end="")
    all_cookies = _driver.get_cookies()
    cookies_dict = {}
    s_cookies = ""
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']
        s_cookies = s_cookies + cookie['name'] + ": " + cookie['value'] + "; "

    ref_page = ""
    auth = ""

    for request in _driver.requests:
        if request.headers["X-REFERRER-PAGE"] is not None:
            ref_page = request.headers["X-REFERRER-PAGE"]
            auth = request.headers["Authorization"]

    _headers = {"Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "Origin": "https://live.harri.com",
                "Referer": "https://live.harri.com",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "X-REFERRER-PAGE": ref_page,
                "Authorization": auth}

    return cookies_dict, _headers


def get_week_blocks(_driver):
    # print(f"* Fetching current price for {object_id}... ", end="")

    cookies_dict, _headers = get_identification(_driver)

    now = datetime.now()
    r = requests.get(
        f"{credentials.SCHEDULE_LINK}/schedule?mode=UNPUBLISHED&week={now.strftime('%b')}+{now.day},+{now.year}",
        headers=_headers,
        cookies=cookies_dict)

    l_ids = []
    l_profiles = []
    blocks = [datetime.strptime(r.json()["data"]["schedule"][0]["start_date"], "%b %d, %Y")]
    for a in r.json()["data"]["schedule"]:
        for role in a["roles"]:
            print(f"Fetching {role["position"]["code"]}...")
            for b in role["role_days"]:
                for c in b["assignees"]:
                    if c["assignee_shifts"]:
                        for d in c["assignee_shifts"]:
                            if c["user_id"] not in l_ids:
                                l_ids.append(c["user_id"])
                                l_profiles.append(get_profile_from_ids([c["user_id"]], _driver))
                            for i in l_profiles:
                                if i[0] == c["user_id"]:
                                    # Format | Jun 06, 2024 10:45
                                    start = datetime.strptime(d["start_time"], "%b %d, %Y %H:%M")
                                    end = datetime.strptime(d["end_time"], "%b %d, %Y %H:%M")
                                    note = None if d["note"] is None else d["note"]["text"]
                                    # BLOCK = [ID, FIRST NAME, LAST NAME, POSITION, START_SCHEDULE, END_SCHEDULE, NOTE]
                                    blocks.append([i[0], i[1], i[2], i[3], start, end, note])
                                    print(f"{i[0]} | {i[1]} {i[2]} {i[3]} | {start} -> {end} | {note}")
    if r.status_code == 200:
        return blocks
    else:
        return []


def get_profile_from_ids(ids, _driver):
    cookies_dict, _headers = get_identification(_driver)
    for _id in ids:
        r = requests.get(
            f"{credentials.ID_LINK}/users?user_ids={_id}",
            headers=_headers,
            cookies=cookies_dict)

        # print(r.content)
        # print(json.dumps(r.json(), indent=4))

        data = r.json()["data"]
        first_name = data[0]["first_name"]
        last_name = data[0]["last_name"]
        position = data[0]["positions"][0]["name"]

        if r.status_code == 200:
            return [_id, first_name, last_name, position]


def fetch_schedule(_driver):
    blocks = get_week_blocks(_driver)

    print(blocks)
    for offset in range(7):
        current_day_start = blocks[0]+timedelta(days=offset)
        current_day_end = blocks[0]+timedelta(days=offset+1)
        print(current_day_start.strftime("%A %d/%m/%Y"))
        list_schedules_day = []
        send_event = False

        for block in blocks[1:]:
            if current_day_start < block[4] < current_day_end:
                schedule_block = ScheduleBlock(block)
                if schedule_block.last_name == "Organek":
                    send_event = True
                # print(f"{schedule_block.first_name} | "
                #       f"{schedule_block.start_schedule.strftime("%H:%M")} -> {schedule_block.end_schedule.strftime("%H:%M")}"
                #       f" ({schedule_block.hours} hours) {schedule_block.shift_type} SHIFT")
                list_schedules_day.append(schedule_block)
        if send_event:
            start_string = ""
            mid_string = ""
            start_event = None
            end_event = None
            list_schedules_day.sort(key=operator.attrgetter('start_schedule'))
            for schedule_block in list_schedules_day:
                if schedule_block.last_name == "Organek":
                    start_string = (f"You will be working a {schedule_block.shift_type.lower()} shift, with a total of {schedule_block.hours} hours ({schedule_block.start_schedule.strftime("%H:%M")} → {schedule_block.end_schedule.strftime("%H:%M")})."
                                    f"\n Below you can find your coworkers' shift:")
                    start_event = schedule_block.start_schedule
                    end_event = schedule_block.end_schedule
                else:
                    mid_string += (f"\n↪ {schedule_block.start_schedule.strftime("%H:%M")} → {schedule_block.end_schedule.strftime("%H:%M")} | "
                            f"{schedule_block.first_name} | ({schedule_block.hours} hours) {schedule_block.shift_type}")
            print(f"\n{start_string+mid_string}")
            communicator.add_calendar_event(start_event, end_event, "Work", start_string + mid_string, 2, True)
            communicator.add_calendar_event(start_event - timedelta(hours=1.2), start_event, "Travel to work", "", 10, False)
            communicator.add_calendar_event(end_event, end_event + timedelta(hours=1.2), "Travel from work", "", 10, False)

if __name__ == "__main__":
    driver = get_driver()
    # login(driver)
    fetch_schedule(driver)