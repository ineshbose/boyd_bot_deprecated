from selenium import webdriver
import os
import selenium.common.exceptions as error
import time, datetime

## Constants
URL = "https://www.gla.ac.uk/apps/timetable/#/login"
chromedriver = 'C:/Users/Inesh/Downloads/chromedriver'
weekdayMapping = {"MONDAY":0, "TUESDAY":1, "WEDNESDAY":2, "THURSDAY":3, "FRIDAY":4}
###

options = webdriver.ChromeOptions()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
browsers = {}

def login(guidd,passww):
    browsers[guidd] = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)
    #browsers[guidd] = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
    browsers[guidd].get(URL)
    browsers[guidd].find_element_by_id("guid").send_keys(guidd)
    browsers[guidd].find_element_by_id("password").send_keys(passww)
    browsers[guidd].find_element_by_xpath("//*[@id='app']/div/main/button").click()
    time.sleep(4)
    try:
        browsers[guidd].find_element_by_xpath("//*[@id='app']/div/div[1]/div[1]/a").click()
        time.sleep(1)
        if browsers[guidd].current_url == "https://www.gla.ac.uk/apps/timetable/#/timetable":
            return 1
    except error.UnexpectedAlertPresentException as e:
        browsers[guidd].quit()
        return 2
    except error.NoSuchElementException as load:
        browsers[guidd].quit()
        return 3

def read_today(guidd):
    message = ""
    time.sleep(1)
    classes = browsers[guidd].find_elements_by_class_name("fc-time-grid-event.fc-event.fc-start.fc-end")
    if classes == []:
        message+= "There seem to be no classes."
    else:
        message+= "You have..\n\n"
        for clas in classes:
            try:
                clas.click()
                time.sleep(1)
                table = browsers[guidd].find_element_by_class_name("dialogueTable")
                message+=table.text+"\n\n"
                browsers[guidd].find_element_by_class_name("close.text-white").click()
            except error.ElementNotInteractableException as e:
                message+="(Unable to fetch class)\n"
                continue
    return message

def specific_day(date_entry, guidd):
    try:
        day, month, year = map(int, date_entry.split('/'))
        date1 = datetime.date(year, month, day)
        message = loop_days((date1 - datetime.date.today()).days, guidd)
        return message
    except:
        return "The date seems invalid."

def loop_days(n,guidd):
    if n < 365:
        for i in range(n):
            browsers[guidd].find_element_by_class_name("fc-next-button.fc-button.fc-button-primary").click()
        message = read_today(guidd)
        browsers[guidd].find_element_by_class_name("fc-today-button.fc-button.fc-button-primary").click()
        return message
    else:
        return "That seems way too far out."

def read_week(day,guidd):
    time.sleep(1)
    browsers[guidd].find_element_by_class_name("fc-listWeek-button.fc-button.fc-button-primary").click()
    time.sleep(1)
    week = browsers[guidd].find_element_by_class_name("fc-list-table")
    data = week.text
    days = []
    days.append(data.split("Tuesday")[0])
    days.append(data.split("Tuesday")[1].split("Wednesday")[0])
    days.append(data.split("Wednesday")[1].split("Thursday")[0])
    days.append(data.split("Thursday")[1].split("Friday")[0])
    days.append(data.split("Friday")[1])
    browsers[guidd].find_element_by_class_name("fc-timeGridDay-button.fc-button.fc-button-primary").click()
    return (days[weekdayMapping[day.upper()]])

def close(guidd):
    browsers[guidd].find_element_by_class_name("btn.btn-primary.btn-block.nav-button.router-link-active").click()
    browsers[guidd].find_element_by_class_name("btn.btn-primary.btn-rounded").click()
    browsers[guidd].quit()