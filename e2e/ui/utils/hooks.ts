import { Page } from '@playwright/test';
import { buildUrl } from './uiUrlBuilder';

export async function beforeEach<TPage>(
  page: Page,
  PageObjectParam: new (page: Page) => TPage,
  targetPage: string,
  params?: Record<any, any>
): Promise<TPage> {
  await page.goto(buildUrl(targetPage, params));
  const pageObject = new PageObjectParam(page);
  return pageObject;
}

export default { beforeEach };