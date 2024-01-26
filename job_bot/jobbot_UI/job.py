'''establish connection to sheets
establish connection to internet
initialize all information needed to make connection to internet and stuff '''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService # needed for selenium4
from selenium.webdriver.common.by import By # needed for searching through the web page elements
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import time, gspread, os, sys
import xml.etree.ElementTree as ET
from oauth2client.service_account import ServiceAccountCredentials

scope =  ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('personal_API_key.json', scope) # replace with personal API key 
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
        Example:  {'Indeed': [...], 'LinkedIn':[...]}.
        Technically this function can be removed since we only need one Indeed/Linkedin
        link as opposed to all of them generated from Google, we can just iterate through
        the pages on the individual site instead.'''
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

def signUserIn(driver, signInCheck, jobSite):
    '''This function handles signing in the user (if they have opted to).
    This function also handles both cases of whether the user wants to sign in manually
    (for security reasons) or if they've opted to use the XML format of their credentials.
    TODO: clarify inputs and outputs'''

    userLoggedIn = False # check whether the user or not has been logged in
    isIndeed = jobSite == "Indeed"
    if signInCheck != 0: # check what KIND of sign in the user wants to do, either by XML or manually
        try:
            login = driver.find_element(By.LINK_TEXT, 'Sign in')
            login.click()
        except:
            print("User is most likely signed in already.")
            userLoggedIn = True
        finally:
            print("Moving on...")
    else:
        return
    
    if not userLoggedIn:
        if signInCheck == 1:
            print("doing the manual route with webdriver wait")
            try:
                if isIndeed:
                    element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.NAME, "MyIndeedResume")))
                else:
                    # TODO: check what the linkedin hrefs/whatever are called and update
                    element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "UserEmail")))
                userLoggedIn = True
            except:
                print("Unable to do the WebDriverWait")
            finally:
                driver.refresh()
                print("Manual log in was attempted. Login successful: " + str(userLoggedIn))
        elif signInCheck == 2:
            print("doing the XML route")
            # XML file user can update/store credentials so they don't have to sign in every time;
            # this is better than hard coding a password into code program and forgetting about it later...
            indeedUserInfoTree = ET.parse('jobbot_UI/UserInfo.xml') # or use 'UserInfoExample.xml' if running from repository
            userName = indeedUserInfoTree.find(jobSite).find('Username').text
            userPass = indeedUserInfoTree.find(jobSite).find('Password').text

            userField = driver.find_element(By.NAME, '__email')
            userField.clear()
            userField.send_keys(userName)
    # TODO: find a way to detect random pop-up or spam check?
    driver.refresh()

def applyToJobs(jobsList, driver, signInCheck):
    '''This function actually goes through the indeed pages and handles applying to the jobs'''

    # TODO: update this to section to iterate through all indeed links? or move this higher up
    # so that this function is called for each indeed job link which is technically cleaner code practice
    
    #for eachJobLink in range(1, len(jobsList)):
    if signInCheck == "Indeed":
        # warning! this section most liable to break whenever indeed updates their page infrastructure
        listofjobs = driver.find_elements(By.CLASS_NAME, 'jcs-JobTitle')
    else:
        # TODO: update linkedin as well
        listofjobs = driver.find_elements(By.CSS_SELECTOR, 'lol')
    print('number of jobs on current page' , len(listofjobs))
    for x in range(len(listofjobs)):
        # opens every job posting in a new window, TODO: need to click now/interact with
        currJobLink = listofjobs[x]
        driver.execute_script("window.open('"+ currJobLink.get_attribute('href') + "')")
    print('got to here')
    time.sleep(5)
    # check if already applied to
    '''driver.switch_to.window(driver.window_handles[len(driver.window_handles)-1])
    save = driver.find_element(By.ID, 'saveJobButtonContainer')
    if save == 'Applied':
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        #driver.get(jobsList[eachJobLink]) # gets the next page
    '''
    
def runJobScript():
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
    signUserIn = 1
    driver.get(indeedJobs[0]) # this actually navigates to the indeed page, solves fencepost problem
    signUserIn(driver, signUserIn, "Indeed")
    applyToJobs(indeedJobs, driver, "Indeed")
    driver.get(linkedJobs[0])
    signUserIn(driver, signUserIn, "LinkedIn")
    applyToJobs(linkedJobs, driver, "LinkedIn")

if __name__ == "__main__":
    '''This is the core processes of the actual job bot. This function should:
    
    1)   TODO: create a main UI that contains inputs such as salary, keywords, etc
    1.5) Import the UI code/files and run that first
    2)   Select job websites? Indeed, GlassDoor, Monster, LinkedIn? etc
    2.5) run this backend code that parses the user info and grabs the web data, hook this backend code into the UI
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
    #searchResults = getGoogleResults(driver, userKeywords)
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
    signUserInCase = 1
    driver.get(indeedJobs[0]) # this actually navigates to the indeed page, solves fencepost problem
    '''
    when doing automated stuff like this, websites occasionally/often do a bot check
    there is no (easy?) way to remove this so put a web timer for the user to manually bypass this
    and then return back to automation
    '''
    securityCheckFinished = False
    try:
        findMainLogo = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.ID, "indeed-globalnav-logo")))
        securityCheckFinished = True
    except:
         print("Could not find indeed main logo.")
    finally:
         print("Security check was passed: " + str(securityCheckFinished))
    if securityCheckFinished:
        '''After getting to the indeed page, resize the window because 
        when it is small, the job postings open in a new page as opposed to
        opening within the same page dynamically; this resizing allows for multiple page openings'''
        driver.set_window_size(400, 400)
        signUserIn(driver, signUserInCase, "Indeed")
        applyToJobs(indeedJobs, driver, "Indeed")
        #driver.get(linkedJobs[0])
        #signUserIn(driver, signUserInCase, "LinkedIn")
        #applyToJobs(linkedJobs, driver, "LinkedIn")
