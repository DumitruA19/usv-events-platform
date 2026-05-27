import { test, expect } from "@playwright/test";

test("student can sign in via mock login", async ({ page }) => {
  await page.goto("/login/student");
  await page.getByTestId("student-email").fill("student1@student.usv.ro");
  await page.getByTestId("student-mock-login").click();
  await expect(page).toHaveURL(/\/student$/);
  await expect(page.getByRole("heading", { name: "Student dashboard" })).toBeVisible();
});

test("organizer can sign in with username/password", async ({ page }) => {
  await page.goto("/login/organizer");
  await page.getByTestId("organizer-username").fill("organizer1");
  await page.getByTestId("organizer-password").fill("OrganizerPass!234");
  await page.getByTestId("organizer-login").click();
  await expect(page).toHaveURL(/\/organizer$/);
  await expect(page.getByRole("heading", { name: "Organizer dashboard" })).toBeVisible();
});

test("admin can sign in with username/password", async ({ page }) => {
  await page.goto("/login/admin");
  await page.getByTestId("admin-username").fill("admin");
  await page.getByTestId("admin-password").fill("AdminPass!234");
  await page.getByTestId("admin-login").click();
  await expect(page).toHaveURL(/\/admin$/);
  await expect(page.getByRole("heading", { name: "Admin dashboard" })).toBeVisible();
});

