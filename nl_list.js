const fs = require("fs").promises;
const playwright = require("playwright");
var argv = require("minimist")(process.argv);

const output_f = argv.o;

(async () => {
    const browser = await playwright['chromium'].launch({ headless: false, slowMo: 1000 });
    const context = await browser.newContext();
    const page = await context.newPage();
    // go to user page
    await page.goto("https://reader.substack.com/discover");
    await page.setViewportSize({
        width: 1200,
        height: 800
    });
    // wait 3 seconds for testing
    await page.waitForTimeout(3000);

    // [check for already scraped sections]
    // for each section
        // click section button
        // click `All`
        // scroll to bottom
        // click button/scroll until button disappears
        // collect newsletter name, launch period, author, URL, and description


    await browser.close();
})();

async function autoScroll(page){
    await page.evaluate(async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight){
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}