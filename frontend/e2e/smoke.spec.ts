import { test, expect } from "@playwright/test";

test("home loads and can navigate to events", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("nav-events").click();
  await expect(page).toHaveURL(/\/events$/);
  await expect(page.getByRole("heading", { name: "Events" })).toBeVisible();
});

