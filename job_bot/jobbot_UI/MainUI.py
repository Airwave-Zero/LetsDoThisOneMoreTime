import PySimpleGUI as sg
import xml.etree.ElementTree as ET
import datetime
from job import runJobScript

def updateFileVersion():
    # check and update the version number prior to building/running the UI
    tree = ET.parse('AppVersion.xml') # opens the XML as an ElementTree object
    # set a couple of variables for ease of access
    # fileMajor = tree.find('Major').text #uncomment if needed, currently unused
    # fileMinor = tree.find('Minor').text #uncomment if needed, currently unused
    fileSuperMinor = tree.find('SuperMinor').text
    fileDateString = tree.find('Date').text # returns a string like: '2023-12-11 22:27:56'
    fileDateDTObj = datetime.datetime.strptime(fileDateString, '%Y-%m-%d %H:%M:%S') # turn string into datetime obj to compare versions
    currDT = datetime.datetime.now() # get the current date time for comparison below

    # Update the super minor version number if running new code, only need to
    # that one since realistically not much changes between runs; update
    # minor if there are significant enough changes, can do that manually
    if fileDateDTObj < currDT:
        fileSuperMinor = str(int(fileSuperMinor) + 1)
        tree.find('SuperMinor').text = fileSuperMinor
        tree.find('Date').text = "{:%Y-%m-%d %H:%M:%S}".format(currDT)
        tree.write('AppVersion.xml')

    return tree # return the file in case future access needed
def buildUI(appVersionTitle):
    # Build a UI, set default fields
    sg.theme('GreenMono')
    # TODO: add in a checkbox field for if the user wants to apply with/without signing in to an account
    #       add a second checkbox field for if the user wants to apply using the XML credentials, 
    #       both cannot be checked at the same time

    inputLayout = [ [sg.Text('Job Keywords:'), sg.InputText("(e.g. software jobs)")],
                    [sg.Text('Minimum Salary:'), sg.InputText("(e.g. $40000)")],
                    [sg.Button('Search')]]
    UIWindow = sg.Window(title = appVersionTitle, layout = inputLayout, margins=(300,300))
    return UIWindow

def handleUI(UIWindow):
    runJobScript()
    '''
    while True:
        event, values = UIWindow.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            break
        else:
            print(values)
    UIWindow.close()
    '''

# uncomment this out if running the script directly by itself

if __name__ == "__main__":

    ####### Code that handles the version control for the job bot #######
    fileXMLTree = updateFileVersion()
    fileMajor = fileXMLTree.find('Major').text
    fileMinor = fileXMLTree.find('Minor').text
    fileSuperMinor = fileXMLTree.find('SuperMinor').text

    appVersionTitle = "Job Bot v" + fileMajor + '.' + fileMinor + '.' + fileSuperMinor
    print("Currently running: " + appVersionTitle)

    ####### Code that handles UI generation #######
    UIWindow = buildUI(appVersionTitle)

    handleUI(UIWindow)
    print("end of program")
