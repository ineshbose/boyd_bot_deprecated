from selenium import webdriver
import os
from constants import URL, weekdayMapping, GOOGLE_CHROME_PATH, CHROMEDRIVER_PATH
import details
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException, ElementNotInteractableException
import time, datetime
from getpass import getpass

options = webdriver.ChromeOptions()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options)

def login(guidd,passww):
    browser.get(URL)
    browser.find_element_by_id("guid").send_keys(guidd)
    browser.find_element_by_id("password").send_keys(passww)
    #print("\nLogging in..\n")
    #bot.send_text_message(uid, "Logging in..")
    browser.find_element_by_xpath("//*[@id='app']/div/main/button").click()
    time.sleep(4)
    try:
        #browser.current_url == "https://www.gla.ac.uk/apps/timetable/#/"
        browser.find_element_by_xpath("//*[@id='app']/div/div[1]/div[1]/a").click()
        time.sleep(1)
        if browser.current_url == "https://www.gla.ac.uk/apps/timetable/#/timetable":
            #print("\nLogin successful!\n")
            #bot.send_text_message(uid, "Login successful!")
            details.loggedin = True
            return "success"
            #read_today()
            #read_week()
    except UnexpectedAlertPresentException as e:
        #browser.switch_to_alert().accept()
        #print("\nInvalid credentials! Try again.\n")
        #bot.send_text_message(uid, "Login unsuccessful. Try again.")
        browser.refresh()
        return "Invalid Credentials. "
        #browser.refresh()
        #login()
    except NoSuchElementException as load:
        #print("\nSomething went wrong. Maybe the connection was too slow. Try again.\n")
        #bot.send_text_message(uid, "Something went wrong. Maybe the connection was too slow. Try again.")
        browser.refresh()
        #login()
        return "Something went wrong. Maybe the connection was too slow. "

def read_today():
    message = ""
    time.sleep(1)
    #classes = browser.find_elements_by_class_name("fc-title")
    classes = browser.find_elements_by_class_name("fc-time-grid-event.fc-event.fc-start.fc-end")
    if classes == []:
        #print("Either there are no classes, or something went wrong.")
        #bot.send_text_message(uid, "There seem to be no classes.")
        message+= "There seem to be no classes."
    else:
        #print("\nYou have..")
        #bot.send_text_message(uid, "You have..")
        message+= "You have..\n\n"
        for clas in classes:
            try:
                clas.click()
                time.sleep(1)
                table = browser.find_element_by_class_name("dialogueTable")
                #print(table.text, "\n")
                #bot.send_text_message(uid, table.text)
                message+=table.text+"\n\n"
                browser.find_element_by_class_name("close.text-white").click()
            except ElementNotInteractableException as e:
                #print("(Unable to fetch class)\n")
                #bot.send_text_message(uid, "(Unable to fetch class)")
                message+="(Unable to fetch class)\n"
                continue
    return message
    #for clas in classes:
        #print(clas.text)
        #print(" ")

def specific_day(date_entry):
    #date_entry = input('Enter a date in DD-MM-YYYY format: ')
    day, month, year = map(int, date_entry.split('/'))
    date1 = datetime.date(year, month, day)
    message = loop_days((date1 - datetime.date.today()).days)
    return message

def loop_days(n):
    for i in range(n):
        browser.find_element_by_class_name("fc-next-button.fc-button.fc-button-primary").click()
    message = read_today()
    browser.find_element_by_class_name("fc-today-button.fc-button.fc-button-primary").click()
    return message

def read_week(day):
    time.sleep(1)
    browser.find_element_by_class_name("fc-listWeek-button.fc-button.fc-button-primary").click()
    time.sleep(1)
    week = browser.find_element_by_class_name("fc-list-table")
    data = week.text
    days = []
    days.append(data.split("Tuesday")[0])
    days.append(data.split("Tuesday")[1].split("Wednesday")[0])
    days.append(data.split("Wednesday")[1].split("Thursday")[0])
    days.append(data.split("Thursday")[1].split("Friday")[0])
    days.append(data.split("Friday")[1])
    browser.find_element_by_class_name("fc-timeGridDay-button.fc-button.fc-button-primary").click()
    return (days[weekdayMapping[day.upper()]])

def main(guid,passw):
    #print("\nHello! Give me a minute to initialize..\n")
    #bot.send_text_message(uid, "Hello! Give me a minute to initialize..")
    login(guid,passw)
    quit="n"
    while quit.upper()!="Y":
        print("\nWhat's up?\n1 - Today\n2 - This Week\n3 - X days later\n4 - On Specific Day")
        #bot.send_text_message(uid, "What's up?\n1 - Today\n2 - This Week\n3 - X days later\n4 - On Specific Day")
        choice = int(input("Input: "))
        if choice == 1:
            read_today()
        elif choice == 2:
            read_week()
        elif choice == 3:
            loop_days(int(input("How many days? ")))
        elif choice == 4:
            specific_day()
        else:
            print("Invalid input.")
        quit=input("Quit? [Y/N]: ")

    print("\nClosing browser..\n")
    browser.quit()

def close():
    browser.find_element_by_class_name("btn.btn-primary.btn-block.nav-button.router-link-active").click()
    browser.find_element_by_class_name("btn.btn-primary.btn-rounded").click()
    details.loggedin = False