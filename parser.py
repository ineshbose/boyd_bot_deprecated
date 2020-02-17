import details, expect, scraper

def handleExpect(message):
    if expect.expecting_start == 1 and message.upper()!= "START":
        return "Hello there! Say START to wake me!"
    elif expect.expecting_start == 1 and message.upper() == "START":
        #bot.send_text_message(details.uid, "Hello there!")
        expect.expecting_guid = 1
        expect.expecting_start = 0
        return "Enter GUID."
    elif expect.expecting_guid == 1:
        #bot.send_text_message(details.uid, "Thank you for the GUID.")
        details.guid = message
        #print(details.guid)
        expect.expecting_guid = 0
        expect.expecting_pass = 1
        return "Enter password."
    elif expect.expecting_pass == 1:
        #bot.send_text_message(details.uid, "Thank you for the password. You can delete it.")
        details.passw = message
        #print(details.passw)
        expect.expecting_pass = 0
        #bot.send_text_message(details.uid, "Please wait..")
        result = scraper.login(details.guid, details.passw)
        if result == "success":
            expect.expecting_input = 1
            return "Logged in!\n1 - Today\n2 - This Week\n3 - X days later\n4 - On Specific Day\n5 - Logout & Quit"
        else:
            expect.expecting_guid = 1
            return result+"Enter GUID again."
    elif expect.expecting_input == 1 and expect.expecting_day == 1:
        expect.expecting_day = 0
        return scraper.read_week(message)
    elif expect.expecting_input == 1 and expect.expecting_dayno == 1:
        expect.expecting_dayno = 0
        return scraper.loop_days(int(message))
    elif expect.expecting_input == 1 and expect.expecting_date == 1:
        expect.expecting_date = 0
        return scraper.specific_day(message)
    elif expect.expecting_input == 1:
        if message == "1":
            return scraper.read_today()
        elif message == "2":
            expect.expecting_day = 1
            return "What day?"
        elif message == "3":
            expect.expecting_dayno = 1
            return "How many days?"
        elif message == "4":
            expect.expecting_date = 1
            return "Enter date in DD/MM/YYYY format: "
        elif message == "5":
            expect.expecting_start = 1
            expect.expecting_input = 0
            scraper.close()
            return "Logged out! Goodbye. Say START to wake me. :)"