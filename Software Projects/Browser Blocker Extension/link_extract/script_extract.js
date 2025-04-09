"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const puppeteer_1 = __importDefault(require("puppeteer"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
function interactNeet(page, pageType) {
    return __awaiter(this, void 0, void 0, function* () {
        const neetSelector = "body > app-root > app-pattern-table-list > div > div.flex-container-col.content > div.tabs.is-centered.is-boxed.is-large > ul > li.has-dropdown";
        try {
            yield page.waitForSelector(neetSelector, { timeout: 5000 });
            yield page.click(neetSelector);
            yield page.waitForSelector(neetSelector, { timeout: 5000 });
            const options = yield page.$$(neetSelector);
            if (options.length > 0) {
                if (pageType === "blind75")
                    yield options[0].click();
                else if (pageType === "neet150")
                    yield options[1].click();
                return new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        catch (error) {
            console.warn("Dropdowninteraction failed:", error);
        }
    });
}
function extractLinks(page) {
    return __awaiter(this, void 0, void 0, function* () {
        return yield page.evaluate(() => {
            const result = [];
            const tableCells = document.querySelectorAll('td');
            tableCells.forEach((cell) => {
                var _a;
                const problemLink = cell.querySelector('a.table-text');
                const problemName = problemLink ? (_a = problemLink.textContent) === null || _a === void 0 ? void 0 : _a.trim() : 'Unknown';
                const tooltipLink = cell.querySelector('a[data-tooltip]');
                const href = tooltipLink ? tooltipLink.getAttribute('href') : null;
                if (problemName && href) {
                    result.push({
                        ProblemName: problemName,
                        URL: href
                    });
                }
            });
            console.log(result);
            return result;
            /*
            const linkTable = document.querySelectorAll('app-pattern-table');
            let problemSet: jsonObject[] = [];
            linkTable.forEach((table)=> {
                const links = table.querySelectorAll('a[data-tooltip]');
                const names = table.querySelectorAll('a[table-text text-color ng-star-inserted]');
                links.forEach((link, names) => {
                    const href = link.getAttribute('href');
                    const linkname = names.textContent?.trim
                    const problemName = link.textContent?.trim() || 'Unknown Problem';
                    if(href){
                        problemSet.push({
                            ProblemName: problemName,
                            URL: href
                        });
                    }
                });
            });
            console.log(problemSet);
            return problemSet;
            */
            /*
                    <td _ngcontent-emg-c39="" style="width: 350px; overflow-wrap: break-word;"><a _ngcontent-emg-c39="" class="table-text text-color ng-star-inserted" href="/problems/duplicate-integer"> Contains Duplicate </a><a _ngcontent-emg-c39="" target="_blank" data-tooltip="External Link" class="has-tooltip-bottom ng-star-inserted" href="https://leetcode.com/problems/contains-duplicate/">&nbsp; <svg _ngcontent-emg-c39="" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="my-lock"><path _ngcontent-emg-c39="" d="M320 0c-17.7 0-32 14.3-32 32s14.3 32 32 32h82.7L201.4 265.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L448 109.3V192c0 17.7 14.3 32 32 32s32-14.3 32-32V32c0-17.7-14.3-32-32-32H320zM80 32C35.8 32 0 67.8 0 112V432c0 44.2 35.8 80 80 80H400c44.2 0 80-35.8 80-80V320c0-17.7-14.3-32-32-32s-32 14.3-32 32V432c0 8.8-7.2 16-16 16H80c-8.8 0-16-7.2-16-16V112c0-8.8 7.2-16 16-16H192c17.7 0 32-14.3 32-32s-14.3-32-32-32H80z"></path></svg></a><!----><!----><!----></td>
                    });*/
        });
    });
}
function saveLinksToFile(links, filePath) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const jsonContent = JSON.stringify(links, null, 2);
            yield fs_1.default.promises.writeFile(filePath, jsonContent, "utf-8");
            console.log(`Links saved to ${filePath}`);
        }
        catch (error) {
            console.error(`Error writing to file:`, error);
        }
    });
}
(() => __awaiter(void 0, void 0, void 0, function* () {
    console.log("lol");
    const url = "https://neetcode.io/practice";
    const blind75Path = path_1.default.join(__dirname, "blind75.json");
    const neet150Path = path_1.default.join(__dirname, "neet150.json");
    yield fs_1.default.promises.mkdir(__dirname, { recursive: true });
    const browser = yield puppeteer_1.default.launch({ headless: false });
    const page = yield browser.newPage();
    try {
        yield page.goto(url, { waitUntil: "networkidle2" });
        yield interactNeet(page, "blind75");
        const blindLinks = yield extractLinks(page);
        console.log('blind', blindLinks);
        yield saveLinksToFile(blindLinks, blind75Path);
        yield interactNeet(page, "neet150");
        const neetLinks = yield extractLinks(page);
        console.log('neet', neetLinks);
        yield saveLinksToFile(neetLinks, neet150Path);
    }
    catch (error) {
        console.error("Error during extraction process:", error);
    }
    finally {
        yield browser.close();
    }
}))();
