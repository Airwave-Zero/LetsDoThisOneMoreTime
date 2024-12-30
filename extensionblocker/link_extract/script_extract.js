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
        const neetSelector = 'body > app-root > app-pattern-table-list > div > div.flex-container-col.content > div.tabs.is-centered.is-boxed.is-large > ul > li.has-dropdown.is-active-tab > a';
        try {
            yield page.waitForSelector(neetSelector, { timeout: 5000 });
            yield page.click(neetSelector);
            yield page.waitForSelector(neetSelector, { timeout: 5000 });
            const options = yield page.$$(neetSelector);
            if (options.length > 0) {
                yield options[0].click();
            }
        }
        catch (error) {
            console.warn('Dropdowninteraction failed:', error);
        }
    });
}
function extractLinks(page) {
    return __awaiter(this, void 0, void 0, function* () {
        return yield page.evaluate(() => {
            const links = Array.from(document.querySelectorAll('a[href]'));
            const now = new Date().toISOString();
            return links.map((anchor) => {
                var _a;
                const linkElement = anchor;
                return {
                    ProblemName: ((_a = linkElement.textContent) === null || _a === void 0 ? void 0 : _a.trim()) || '',
                    URL: linkElement.href,
                };
            });
        });
    });
}
function saveLinksToFile(links, filePath) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const jsonContent = JSON.stringify(links, null, 2);
            yield fs_1.default.promises.writeFile(filePath, jsonContent, 'utf-8');
            console.log(`Links saved to ${filePath}`);
        }
        catch (error) {
            console.error(`Error writing to file:`, error);
        }
    });
}
(() => __awaiter(void 0, void 0, void 0, function* () {
    const url = 'https://neetcode.io/practice';
    const sharedDir = path_1.default.join(__dirname, 'shared');
    const blind75Path = path_1.default.join(sharedDir, 'blind75.json');
    const neet150Path = path_1.default.join(sharedDir, 'neet150.json');
    yield fs_1.default.promises.mkdir(sharedDir, { recursive: true });
    const browser = yield puppeteer_1.default.launch({ headless: false });
    const page = yield browser.newPage();
    try {
        yield page.goto(url, { waitUntil: 'networkidle2' });
        yield interactNeet(page, 'blind75');
        const blindLinks = yield extractLinks(page);
        yield saveLinksToFile(blindLinks, blind75Path);
        yield interactNeet(page, 'neet150');
        const neetLinks = yield extractLinks(page);
        yield saveLinksToFile(neetLinks, neet150Path);
    }
    catch (error) {
        console.error('Error during extraction process:', error);
    }
    finally {
        yield browser.close();
    }
}));
