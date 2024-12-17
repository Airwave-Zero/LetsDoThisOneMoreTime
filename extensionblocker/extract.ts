//https://betterprogramming.pub/creating-chrome-extensions-with-typescript-914873467b65
/* This file is responsible for going to https://neetcode.io/practice
// and webscraping to deal with blind75 and neetcode150 */

/*
1) go to https://neetcode.io/practice
2) Click on blind75 // neetcode 150
3) //iterate through each section of "ng-star-inserted" class, grab the leetcode href and table text
4) store in jsonFile appropriately

document.querySelector("body > app-root > app-pattern-table-list > div > div.flex-container-col.content.ng-star-inserted > app-pattern-table:nth-child(6) > app-accordion > div > div > app-table > div > table > tbody > tr:nth-child(1)")
*/

