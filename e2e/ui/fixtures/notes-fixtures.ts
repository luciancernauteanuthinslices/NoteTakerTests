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
        
        if ((await homePage.singleNoteCard.count()) > 0) {
            await homePage.cleanAllNotes();
        } else{
            console.log('No notes found');
        }

        await use(homePage);
    },
});

