from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import os
import time
import openstack
import datetime
import prometheus_client as prom

openstack_username = os.getenv('OS_USERNAME')
openstack_password = os.getenv('OS_PASSWORD')
api_metrics = prom.Gauge('openstack_horizon_response_seconds', 'Time for horizon login via Chrome.', ['cloud_name'])
api_status = prom.Gauge('openstack_horizon_status', 'Horizon current status. 1 = up 0 = down.',['cloud_name'])

def get_metrics(horizon_url,cloud_name):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver=webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(10)
    
    # driver.get("https://httpstat.us/200")

    # if "200 OK" in driver.page_source:
    #     print('Selenium successfully opened with Chrome (under the Xvfb display) and navigated to "https://httpstat.us/200", you\'re all set!')

    print(f"Attempting to log into Horizon at {horizon_url}")
    timeout = 30
    driver.get(horizon_url)
    try:
        # wait till page loads
        WebDriverWait(driver, timeout).until(EC.title_contains("OpenStack"))
    except TimeoutException:
        print("Timed out waiting for root url to load")
        api_status.labels(cloud_name).set(0)
        return None

    #Print Page
    # the following javascript scrolls down the entire page body.  Since Twitter
    # uses "inifinite scrolling", more content will be added to the bottom of the
    # DOM as you scroll... since it is in the loop, it will scroll down up to 100
    # times.
    for _ in range(100):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # print all of the page source that was loaded
    # print(driver.page_source.encode("utf-8"))

    # Log in
    driver.find_element_by_id("id_username").send_keys(f"{openstack_username}")
    driver.find_element_by_id ("id_password").send_keys(f"{openstack_password}")
    start_time = datetime.datetime.now()
    driver.find_element_by_id("loginBtn").click()

    try:
        WebDriverWait(driver, timeout).until(EC.title_contains("OpenStack"))
        end_time = datetime.datetime.now()
        time_took = end_time - start_time
        seconds_took = time_took.seconds
        print(f"Horizon took {seconds_took} seconds to log in.")
        api_metrics.labels(cloud_name).set(seconds_took)
        api_status.labels(cloud_name).set(1)
    except:
        print("Timed out waiting for login to load")
        api_status.labels(cloud_name).set(1)

    finally:
        driver.quit()