"use strict";
//https://betterprogramming.pub/creating-chrome-extensions-with-typescript-914873467b65
/* This file is responsible for going to https://neetcode.io/practice
// and webscraping to deal with blind75 and neetcode150 */
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
function loadAndCheckJSON(filePath) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const response = yield (fetch(filePath));
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const jsonData = yield response.json();
            console.log("File Contents:", jsonData);
            return jsonData === 'lol'; // change with counting contents of json
        }
        catch (error) {
            console.error('Error fetching the JSON file:', error);
            return false;
        }
    });
}
function updateJSON(filePath) {
    return __awaiter(this, void 0, void 0, function* () {
        const isBlindEmpty = yield loadAndCheckJSON(filePath);
        const isNeetEmpty = yield loadAndCheckJSON(filePath);
        if (isBlindEmpty) {
            //do extraction for blind75
        }
        if (isNeetEmpty) {
            //do extraction for neet150
        }
    });
}
function fetchLinksFromChrome() {
    return __awaiter(this, void 0, void 0, function* () {
        return new Promise((resolve, reject) => {
            chrome.storage.local.get("storedLinks", (result) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                    return;
                }
                const links = result.storedLinks || [];
                resolve(links);
            });
        });
    });
}
//async function extractData(url:string):Promise<jsonStruct>{}
updateJSON('blind75.json');
updateJSON('neet150.json');
