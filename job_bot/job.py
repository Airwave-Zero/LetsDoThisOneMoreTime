'''establish connection to sheets
establish connection to internet
initialize all information needed to make connection to internet and stuff '''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService # needed for selenium4
from selenium.webdriver.common.by import By # needed for searching through the web page elements
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager




from bs4 import BeautifulSoup
import time, gspread, os, sys
import xml.etree.ElementTree as ET
from oauth2client.service_account import ServiceAccountCredentials

scope =  ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('dec2023project-da899e9caf46.json', scope)
#creds = ServiceAccountCredentials.from_json_keyfile_name('personal_API_key.json', scope) # replace with personal API key 
client = gspread.authorize(creds)

def initialize():
    '''This function initializes the chrome driver and returns it so that we can use a
    Chrome Window later'''
    userDataDir = 'C:/Users/bboyf/AppData/Local/Google/Chrome/User Data' # user local settings on the machine
    userProfileSettings = webdriver.ChromeOptions()
    userProfileSettings.add_argument(f"--user-data-dir={userDataDir}")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = userProfileSettings)
    return driver

def getGoogleResults(driver, userKeyWords):
    '''This is a function that takes in the web browser and user inputs to return 
     a dictionary of lists with all of the web links, where the key is the website name and the value is all the URLs'''
    
    driver.get('https://www.google.com')
    searchbar = driver.find_element(By.NAME, 'q') # Look for the search bar, this is the div NAME (could also search by ID or other elements)

    searchbar.send_keys(userKeyWords)

    clicksearch = driver.find_element(By.NAME, 'btnK') # the actual submit search button
    clicksearch.submit()

    page_source = driver.page_source

    page_html = BeautifulSoup(page_source, 'html.parser') # convert so that it's simpler to parse through the web data in html format
    allWebLinks = page_html.find_all('a') # returns all of the link divs
    allLinks = filterJobByWebsite(allWebLinks) # returns a dictionary of lists of each posting, does the actual heavy lifting
    return allLinks
    
def filterJobByWebsite(allWebLinks):
    '''This function parses the list of a dictionary of lists, where the key is the website name and the values are the respective links for that website
        Example:  {'Indeed': [...], 'LinkedIn':[...]}'''
    indeedLinks = []
    linkedInLinks = []
    for linkNum in range(len(allWebLinks)):
        currLink = allWebLinks[linkNum].get('href')
        if(type(currLink) == type('str')):
            isIndeed = currLink.startswith('https://www.indeed.com/q-') # includes the q in order to only capture query results and filter out other indeed links
            isLinked = currLink.startswith('https://www.linkedin.com/jobs') # same reasoning as above but different parameter when used from google
        if(isIndeed):
            indeedLinks.append(currLink)
        elif(isLinked):
            linkedInLinks.append(currLink)
    allLinks = dict()
    allLinks['Indeed'] = indeedLinks
    allLinks['LinkedIn'] = linkedInLinks
    return allLinks

def signUserInIndeed(driver, signInCheck):
    '''This function handles signing in the user (if they have opted to).
    This function also handles both cases of whether the user wants to sign in manually
    (for security reasons) or if they've opted to use the XML format of their credentials'''

    if signInCheck != 0:
        login = driver.find_element(By.LINK_TEXT, 'Sign in')
        login.click()
    else:
        return
    
    if signInCheck == 1:
        print("doing the manual route with webdriver wait")
        '''        
        https://stackoverflow.com/questions/16927354/how-can-i-make-selenium-python-wait-for-the-user-to-login-before-continuing-to-r
        https://selenium-python.readthedocs.io/waits.html

        try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "UserEmail"))
        )
        finally:
        driver.quit()
        '''
    elif signInCheck == 2:
        print("doing the XML route")
        # XML file user can update/store credentials so they don't have to sign in every time;
        # this is better than hard coding a password into code program and forgetting about it later...
        indeedUserInfoTree = ET.parse('UserInfo.xml') # or use 'UserInfoExample.xml' if running from repository
        userName = indeedUserInfoTree.find('Indeed').find('Username').text
        userPass = indeedUserInfoTree.find('Indeed').find('Password').text

        userField = driver.find_element(By.NAME, '__email')
        userField.send_keys(userName)

        passwordField = driver.find_element(By.NAME, '__password')
        passwordField.send_keys(userPass)

        sign_inButton = driver.find_element(By.ID, 'login-submit-button')
        sign_inButton.click()
        
    # refresh the page in case random pop-up appears
    # TODO: find a way to detect random pop-up or spam check?
    popup = driver.refresh()

def applyIndeedJobs(indeedJobs, driver, signInCheck):
    '''This function actually goes through the indeed pages and handles applying to the jobs'''

    # TODO: update this to section to iterate through all indeed links? or move this higher up
    # so that this function is called for each indeed job link which is technically cleaner code practice
    driver.get(indeedJobs[0]) # loads in the first web page in the indeed job list

    # handles all cases of signing in the user to indeed, or not signing them in at all
    signUserInIndeed(driver, signInCheck)

    listofjobs = driver.find_elements(By.CSS_SELECTOR, '#pageContent tr td')
    print('length of jobs:' , len(listofjobs))
    for x in range(len(listofjobs)):
        a = listofjobs[x]
        a.click()

    print('got to here')
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    save = driver.find_element(By.ID, 'saveJobButtonContainer')
    if save == 'Applied':
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

def applyLinkedJobs(linedJobs, driver):
    '''This function reads through LinkedIn pages and handles applying to the jobs'''

if __name__ == "__main__":
    '''This is the core processes of the actual job bot. This function should:
    
    1)   TODO: create a main UI that contains inputs such as salary, keywords, etc
    1.5) Import the UI code/files and run that first
    2)   Select job websites? Indeed, GlassDoor, Monster, LinkedIn? etc
    2.5) run this backend code that parses the user info and grabs the web data, hook this backend code into the UI
    2.75) add OAuth instead of grabbing raw user info (big issue if security breach)
    3)   Enter updates the UI and pulls out a list of all the postings
    4)   User can check which ones to apply to/which ones they did
    5)   Export data into sheets
    userInput = input("Please enter keywords to search for, then a comma for salary.\nExample: software jobs, 80000\n").split(',') # get user input, should be an array of keywords + salary range
    if userInput == "":
        sys.exit()
    userKeywords = userInput[0] # used for searching google / the actual job site
    userSalary = userInput[1] # used for filtering by salary on the actual job site
    '''

    print("Now opening Chrome instance...")
    driver = initialize() # creates the chrome window to use
    searchResults = getGoogleResults(driver, "software jobs") # returns a dictionary of lists of all the jobs, currently filtered by job site
    indeedJobs = searchResults['Indeed']
    linkedJobs = searchResults['LinkedIn']
    
    '''
    These are the following cases of how (if at all) a user signs in
    based on what they've selected in the UI:
    TODO: figure out the corresponding UI to regular logic assignment
    case 0: no sign in
    case 1: sign in with manual
    case 2: sign in with XML 
    '''
    signUserIn = 0

    applyIndeedJobs(indeedJobs, driver, signUserIn)
    applyLinkedJobs(linkedJobs, driver, signUserIn)

