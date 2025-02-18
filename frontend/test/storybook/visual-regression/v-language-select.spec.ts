import { Page, expect } from "@playwright/test"

import { test } from "~~/test/playwright/utils/test-fixture"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

const expectSnapshot = async (name: string, page: Page) => {
  expect(await page.screenshot()).toMatchSnapshot({ name: `${name}.png` })
}

test.describe("VLanguageSelect", () => {
  test("default", async ({ page }) => {
    await makeGotoWithArgs("components-vlanguageselect--default-story")(page)
    await expectSnapshot("vlanguageselect-default", page)
  })
})
