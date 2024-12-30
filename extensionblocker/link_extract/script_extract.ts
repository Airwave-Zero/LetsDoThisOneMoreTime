import puppeteer from "puppeteer";
import {Page} from "puppeteer";
import fs from 'fs';
import path from 'path';

interface jsonObject {
    ProblemName: string;
    URL: string;
}

async function interactNeet(page:Page, pageType: string): Promise<void> {
    const neetSelector = 'body > app-root > app-pattern-table-list > div > div.flex-container-col.content > div.tabs.is-centered.is-boxed.is-large > ul > li.has-dropdown.is-active-tab > a';
    try {
        await page.waitForSelector(neetSelector, {timeout: 5000});
        await page.click(neetSelector);
    
    await page.waitForSelector(neetSelector, {timeout:5000});
    const options = await page.$$(neetSelector);
    if(options.length > 0) 
    {
        await options[0].click();
    }
    }
    catch(error){
        console.warn('Dropdowninteraction failed:', error);
    }
}

async function extractLinks(page: Page): Promise<jsonObject[]>{
    return await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a[href]'));
        const now = new Date().toISOString();

        return links.map((anchor) => {
            const linkElement = anchor as HTMLAnchorElement;
            return {
                ProblemName: linkElement.textContent?.trim()||'',
                URL: linkElement.href,
            };
        });
    });
}

async function saveLinksToFile(links: jsonObject[], filePath: string): Promise<void>{
    try {
        const jsonContent = JSON.stringify(links, null, 2);
        await fs.promises.writeFile(filePath, jsonContent, 'utf-8');
        console.log(`Links saved to ${filePath}`);
    }
    catch(error){
        console.error(`Error writing to file:`, error);
    }
}

(async () => {
    const url = 'https://neetcode.io/practice';
    const sharedDir = path.join(__dirname, 'shared');
    const blind75Path = path.join(sharedDir, 'blind75.json');
    const neet150Path = path.join(sharedDir, 'neet150.json');

    await fs.promises.mkdir(sharedDir, {recursive: true});

    const browser = await puppeteer.launch({headless:false});
    const page = await browser.newPage();

    try {
        await page.goto(url, {waitUntil: 'networkidle2'});
        await interactNeet(page, 'blind75');
        const blindLinks = await extractLinks(page);
        await saveLinksToFile(blindLinks, blind75Path);

        await interactNeet(page, 'neet150');
        const neetLinks = await extractLinks(page);
        await saveLinksToFile(neetLinks, neet150Path);
    }
    catch(error){
        console.error('Error during extraction process:', error);
    }
    finally{
        await browser.close();
    }
})
