import { test as base} from "@playwright/test";
import { HomePage } from "../pages/homePage";
import hooks from "../utils/hooks";
import pages from "../utils/pages";


type MyFixture = {
    homePage: HomePage;
}

export const test = base.extend<MyFixture>({
    homePage: async ({ page }, use) => {
        const homePage = await hooks.beforeEach(page, HomePage, pages.homePage);
        
        // Note: Cleanup is disabled because ads on the practice site can intercept clicks
        // and cause navigation issues. Consider using API to clean up notes instead.
        const noteCount = await homePage.singleNoteCard.count();
        if (noteCount > 0) {
            console.log(`Found ${noteCount} existing notes (cleanup skipped due to ad overlay issues)`);
        }

        await use(homePage);
    },
});

