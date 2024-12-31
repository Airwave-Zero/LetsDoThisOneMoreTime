import puppeteer from "puppeteer";
import { Page } from "puppeteer";
import fs from "fs";
import path from "path";

interface jsonObject {
    ProblemName: string;
    URL: string;
}

async function interactNeet(page: Page, pageType: string): Promise<void> {
    const neetSelector =
        "body > app-root > app-pattern-table-list > div > div.flex-container-col.content > div.tabs.is-centered.is-boxed.is-large > ul > li.has-dropdown";
    try {
        await page.waitForSelector(neetSelector, { timeout: 5000 });
        await page.click(neetSelector);

        await page.waitForSelector(neetSelector, { timeout: 5000 });
        const options = await page.$$(neetSelector);
        if (options.length > 0) {
            if(pageType ==="blind75")
                await options[0].click();
            else if(pageType ==="neet150")
                await options[1].click();
            return new Promise(resolve => setTimeout(resolve,1000));
        }
    } catch (error) {
        console.warn("Dropdowninteraction failed:", error);
    }
}

async function extractLinks(page: Page): Promise<jsonObject[]> {
    return await page.evaluate(() => {

        const result: jsonObject[] = [];
        const tableCells = document.querySelectorAll('td');

        tableCells.forEach((cell) => {
            const problemLink = cell.querySelector('a.table-text');
            const problemName = problemLink ? problemLink.textContent?.trim() : 'Unknown';

            const tooltipLink = cell.querySelector('a[data-tooltip]');
            const href = tooltipLink? tooltipLink.getAttribute('href'):null;

            if(problemName && href){
                result.push({
                    ProblemName:problemName,
                    URL:href
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
}

async function saveLinksToFile(
    links: jsonObject[],
    filePath: string
): Promise<void> {
    try {
        const jsonContent = JSON.stringify(links, null, 2);
        await fs.promises.writeFile(filePath, jsonContent, "utf-8");
        console.log(`Links saved to ${filePath}`);
    } catch (error) {
        console.error(`Error writing to file:`, error);
    }
}

(async () => {
    console.log("lol");
    const url = "https://neetcode.io/practice";
    const blind75Path = path.join(__dirname, "blind75.json");
    const neet150Path = path.join(__dirname, "neet150.json");

    await fs.promises.mkdir(__dirname, { recursive: true });

    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    try {
        await page.goto(url, { waitUntil: "networkidle2" });
        await interactNeet(page, "blind75");
        const blindLinks = await extractLinks(page);
        console.log('blind', blindLinks);
        await saveLinksToFile(blindLinks, blind75Path);

        await interactNeet(page, "neet150");
        const neetLinks = await extractLinks(page);
        console.log('neet', neetLinks);
        await saveLinksToFile(neetLinks, neet150Path);
    } catch (error) {
        console.error("Error during extraction process:", error);
    } finally {
        await browser.close();
    }
})();
