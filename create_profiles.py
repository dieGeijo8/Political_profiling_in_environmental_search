from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time
import random
import json
from selenium.webdriver.chrome.service import Service

#########FILES_PART#########

# write the time of the session
def report(file, string, id):

    f = open(file, "a")
    f.write(string + " " + str(id) + ": " + str(datetime.now()) + "\n")


# get the queries
def query_todict(file):

    q_dict={}

    with open(file, encoding='utf-8-sig') as f:

        for line in f:
            if line.startswith(">"):

                header=line.strip(">").strip("\n")
                q_dict[header]=[]
            else:

                q_dict[header].append(line.strip("\n"))

    return q_dict


# obtain usernames and passwords
def users_passwords(file):

    u_p = {}
    u_p.update({'usernames': []})
    u_p.update({'passwords': []})

    with open(file) as f:
        for line in f:

            line = line.replace(" ", "")
            words = line.split('-')

            u_p['usernames'].append(words[0])
            u_p['passwords'].append(words[1].replace('\n', ''))

    return u_p


# create the results file
def create_results(file):

    #create the results dictionary
    u_p = users_passwords(file)
    usernames = u_p['usernames']#usernames list
    passwords = u_p['passwords'] #passwords list
    user_ids = list(range(1, 11)) #userids list

    results = {}

    for id in user_ids:

        id_dict = {'username': usernames[id - 1], 'password': passwords[id - 1]}
        results.update({str(id): id_dict})

    return results
###################


######SELENIUM_PART#########

# set the driver
def set_driver():

    ser = Service("C:\Drivers\chromedriver.exe")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    driver = webdriver.Chrome(service=ser, options=chrome_options)
    driver.implicitly_wait(5)

    return driver

# login and get the bing news page
def login(driver, results, user_id):

    driver.get('https://www.bing.com/?wlexpsignin=1')
    time.sleep(4)

    driver.find_element(By.ID, "id_l").click()
    time.sleep(4)

    driver.find_element(By.NAME, "loginfmt").send_keys(results[user_id]['username'])
    time.sleep(4)

    driver.find_element(By.ID, "idSIButton9").click()
    time.sleep(4)

    driver.find_element(By.NAME, "passwd").send_keys(results[user_id]['password'])
    time.sleep(4)

    driver.find_element(By.ID, "idSIButton9").click()
    time.sleep(4)

    try:

        driver.find_element(By.ID, "iShowSkip").click()
        time.sleep(4)
    except NoSuchElementException:

        print('')

    try:

        driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(4)

    except NoSuchElementException:

        print('')

    try:

        driver.find_element(By.ID, "iCancel").click()
        time.sleep(4)

    except NoSuchElementException:

        print('')

    if (driver.current_url != 'https://www.bing.com/?wlexpsignin=1&wlexpsignin=1'):
        print('login problem')

    return driver


# get the news page, search a query
def search_news(driver, query):

    driver.get("https://www.bing.com/news")

    time.sleep(4)

    q = driver.find_element(By.ID, "sb_form_q")
    q.clear()
    q.send_keys(query)

    time.sleep(2)

    q.send_keys(Keys.ENTER)
    time.sleep(5)


# visit the query search results
def url_navigation(driver, results, query, session_id, user_id):

    starting_url = driver.current_url# get the search page url, to check if we are back there after visiting an url
    links_number = random.randint(2,3)

    allurls = driver.find_elements(By.CLASS_NAME, 'title')
    if(len(allurls) >= 2):

        urls_to_visit = []
        for i in range(links_number):

            urls_to_visit.append(allurls[random.randint(1, len(allurls) - 1)].get_attribute('href'))

        for url in urls_to_visit:

            driver.get(url)
            # stay in the url for some time
            time_for_link = random.randint(10, 15)
            time.sleep(time_for_link)
            # save it in results
            results[user_id][session_id][query].append(url)

            driver.execute_script("window.history.go(-1)")
            time.sleep(2)

            if(driver.current_url != starting_url):
                driver.get(starting_url)
    else:

        # the driver.back didn't work well so I just get the starting link again, I lose one iteration
        driver.get(starting_url)

    time.sleep(3)


# single session of one user
def user_session(results, user_id, session_id, queries):

    driver = login(set_driver(), results, user_id)

    # at this point the driver is in the bing news page, logged
    results[user_id].update({session_id: {}})# add the session to the user in the results dictionary

    for category in list(queries.keys()):

        # work with a copy, to be able to delet visited queries and do not repeat the same query in the same session
        queries_copy = queries[category]
        for i in range(2):
            # randomly select two queries
            if(len(queries_copy) >= 2):

                query = queries_copy[random.randint(0, len(queries_copy) - 1)]
                results[user_id][session_id].update({query: []})# add the query to the session in the results dicitonary
                search_news(driver, query)# search the query
                url_navigation(driver, results, query, session_id, user_id)# explore the results and save the vistited urls

                time.sleep(3)
            else:

                print('problem with len(queries:copy)')

    driver.close()

# single browsing session, 10 users for both rw and lw
def browsing_session(results_rightwing, results_leftwing, q_rw, q_lw, session_id):

    for id in list(range(1, 11)):

        # user of rigth wing
        print("user number:", id, " right wing")
        user_session(results_rightwing, str(id), str(session_id), q_rw)

        #for every user I rewrite the updated dictionary
        with open("results_rw_prov_3.json", "w") as outfile:
            json.dump(results_rightwing, outfile)

        time.sleep(60)

        # user of left wing
        print("user number:", id, " left wing")
        user_session(results_leftwing, str(id), str(session_id), q_lw)

        with open("results_lw_prov_3.json", "w") as outfile:
            json.dump(results_leftwing, outfile)
##########################


#create results, read queries file, launch browsing session
def main():
    #RESULTS, TO RUN JUST IN THE FIRST SESSION, to create the dictionary
    results_rightwing = create_results('users_right.txt')
    results_leftwing = create_results('users_left.txt')

    #we save the dicitionary in a json and we reuploaded it for the next sessions
    #read the partial results, write the new results in a different file to have the
    #cumulative file of each day
    with open('results_rw_prov_2.json') as json_file:
        results_rightwing = json.load(json_file)
    with open('results_lw_prov_2.json') as json_file:
        results_leftwing = json.load(json_file)

    #TRAINING QUERIES
    filelw = "Qleft.txt"
    q_lw = query_todict(filelw)
    filerw = "Qright.txt"
    q_rw = query_todict(filerw)

    #BROWSING SESSION HAVE TO CHANGE JUST THE SESSION_ID
    report("report.txt", "Starting session", 2)
    browsing_session(results_rightwing, results_leftwing, q_rw, q_lw, str(2))
    report("report.txt", "Ending session", 2)

    #save the session results in the results dictionary
    with open("results_rw.json", "w") as outfile:
         json.dump(results_rightwing, outfile)
    with open("results_lw.json", "w") as outfile:
         json.dump(results_leftwing, outfile)

main()


