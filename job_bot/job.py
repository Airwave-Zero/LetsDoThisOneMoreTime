'''establish connection to sheets
establish connection to internet
initialize all information needed to make connection to internet and stuff '''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService # needed for selenium4
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, gspread, os, sys
from oauth2client.service_account import ServiceAccountCredentials

scope =  ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('dec2023project-da899e9caf46.json', scope)
client = gspread.authorize(creds)

def initialize():
    '''This function initializes the chrome driver and returns it so that we can use a
    Chrome Window later'''
    userDataDir = 'C:/Users/bboyf/AppData/Local/Google/Chrome/User Data' # user local settings on the machine
    userProfileSettings = webdriver.ChromeOptions()
    userProfileSettings.add_argument(f"--user-data-dir={userDataDir}")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = userProfileSettings)
    return driver

def getResults(driver, userKeyWords):
    '''This is a function that takes in the web browser and user inputs to return 
     a list of google results for those jobs '''
    
def getIndeedJobs(searchResults):
    '''This function parses the list of search page results and returns all of 
    the Indeed Jobs'''

def applyToJobs(all):
    '''This function actually goes through the web pages and handles applying to the jobs'''

if __name__ == "__main__":
    '''This is the core processes of the actual job bot. This function should:
    1) TODO: create a main UI that contains inputs such as salary, keywords, etc
    2) Select job websites? Indeed, GlassDoor, Monster, LinkedIn? etc
    3) Enter updates the UI and pulls out a list of all the postings
    4) User can check which ones to apply to/which ones they did
    5) Export data into sheets
    '''
    userInput = input("Please enter keywords to search for, then a comma for salary.\nExample: software jobs, 80000\n").split(',') # get user input, should be an array of keywords + salary range
    if userInput == "":
        sys.exit()
    userKeywords = userInput[0] # used for searching google / the actual job site
    userSalary = userInput[1] # used for filtering by salary on the actual job site

    driver = initialize() # creates the chrome window to use
    searchResults = getResults(driver, userKeywords) # returns a list of jobs on google (can be filtered by sites later)
    indeedJobs = getIndeedJobs(searchResults) # opens and returns a list of indeed jobs
    # LinkedinJobs = getLinkedJobs(searchResults)
    allFoundJobs = indeedJobs # + wantedLinkedinJobs + ... etc

    applyToJobs(allFoundJobs)

