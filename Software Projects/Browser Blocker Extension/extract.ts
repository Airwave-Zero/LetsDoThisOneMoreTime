//https://betterprogramming.pub/creating-chrome-extensions-with-typescript-914873467b65
/* This file is responsible for going to https://neetcode.io/practice
// and webscraping to deal with blind75 and neetcode150 */

/*

a ->
0) check if blind75.json is empty, if not check if 75 problems
1) go to https://neetcode.io/practice
2) Click on blind75 // neetcode 150
3) //iterate through each section of "ng-star-inserted" class, grab the leetcode href and table text
4) store in jsonFile appropriately

b ->
0) check if neet150 is empty -> if not, dcheck there are 150 problems
1) 


document.querySelector("body > app-root > app-pattern-table-list > div > div.flex-container-col.content.ng-star-inserted > app-pattern-table:nth-child(6) > app-accordion > div > div > app-table > div > table > tbody > tr:nth-child(1)")
*/

interface jsonObject {
    Problem: string;
    URL: string;
}
interface jsonStruct{
    ProblemSet: jsonObject[];
}

async function loadAndCheckJSON(filePath: string): Promise<boolean>{
    try
    {
        const response = await(fetch(filePath));
        if(!response.ok)
        {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const jsonData = await response.json();
        console.log("File Contents:", jsonData);
        return jsonData==='lol'; // change with counting contents of json
    }
    catch(error)
    {
        console.error('Error fetching the JSON file:', error);
        return false;
    }
}

async function updateJSON(filePath:string):Promise<void>{
    
    const isBlindEmpty = await loadAndCheckJSON(filePath);
    const isNeetEmpty = await loadAndCheckJSON(filePath);   

    if (isBlindEmpty)
    {
        //do extraction for blind75
    }
    if(isNeetEmpty)
    {
        //do extraction for neet150
    }
}

async function fetchLinksFromChrome(): Promise<jsonStruct[]>{
    return new Promise((resolve, reject) => {
        chrome.storage.local.get("storedLinks", (result) => {
            if(chrome.runtime.lastError){
                reject(chrome.runtime.lastError);
                return;
            }
            const links:jsonStruct[] = result.storedLinks || [];
            resolve(links);
        });
    });
}
//async function extractData(url:string):Promise<jsonStruct>{}

updateJSON('blind75.json');
updateJSON('neet150.json');