import pathlib
import platform
import random
import time

from pyvirtualdisplay import Display
import seleniumwire.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service



# Check if the script is being run by windows
if platform.system() == 'Windows':
    PI = False
else:
    PI = True


def get_driver():
    """
        Function that returns a driver based on the user's OS.
        :return driver
    """
    print("@ Creating new driver session...")
    # Initialize options
    options = Options()
    # Disable extensions
    options.add_argument("--disable-extensions")
    # Disable utilization of automation
    options.add_experimental_option('useAutomationExtension', False)

    # If the OS is not Windows, I am probably using a raspberry pi
    if PI:
        # Setup virtual display (Change False to 0 if any issues arise)
        display = Display(visible=False, size=(1920, 1080))
        # Start VD
        display.start()
        # Add arguments for driver
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--use_subprocess")
        options.headless = True

        print("@ Virtual display successfully setup.")
        # Add directory for browsing data
        options.add_argument(f"user-data-dir=chromedriver")
        # Setup exe path
        service = Service(executable_path="/usr/lib/chromium-browser/chromedriver")
        # Setup driver using selenium_wire to be able to "hide" the nature of this bot
        _driver = webdriver.Chrome(seleniumwire_options={'mitm_http2': False}, options=options, service=service)
        print("@ Driver successfully setup.")

    else:
        # Get current directory
        script_directory = pathlib.Path().absolute()
        # Add directory for browsing data using the current directory
        options.add_argument(f"user-data-dir={script_directory}\\owres")
        # Setup driver using selenium_wire to be able to "hide" the nature of this bot
        _driver = webdriver.Chrome(seleniumwire_options={'mitm_http2': False}, options=options)
        print("@ Driver successfully setup.")

    return _driver


def get_identification(driver):
    """

    :param driver:
    :return: cookies_dict, headers
    """
    print("* Fetching identification and cookies... ", end="")
    all_cookies = driver.get_cookies()
    cookies_dict = {}
    s_cookies = ""
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']
        s_cookies = s_cookies + cookie['name'] + ": " + cookie['value'] + "; "

    ref_page = ""
    auth = ""

    for request in driver.requests:
        if request.headers["X-REFERRER-PAGE"] is not None:
            ref_page = request.headers["X-REFERRER-PAGE"]
            auth = request.headers["Authorization"]

    headers = {"Accept": "application/json",
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

    return cookies_dict, headers

def slow_type(element, text, delay_s=0.1, delay_e=0.4):
    """Send a text to an element one character at a time with a delay."""
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(delay_s, delay_e))


# print(r.content)
# print(json.dumps(r.json(), indent=4))