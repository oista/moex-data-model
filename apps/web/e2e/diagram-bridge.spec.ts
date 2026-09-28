import { expect, test } from "@playwright/test";

const DEMO_DBML = "Table Demo {\n  id integer [pk]\n}\n";

async function mockDiagramApi(page: import("@playwright/test").Page) {
  await page.route("**/api/**", async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    // Do not intercept Vite modules under /src/api/
    if (!url.pathname.startsWith("/api/")) {
      await route.continue();
      return;
    }
    const method = req.method();
    const path = url.pathname;

    if (method === "POST" && path === "/api/workspaces") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ id: "ws-workbench", name: "Workbench" }),
      });
      return;
    }

    if (
      method === "GET" &&
      path === "/api/workspaces/ws-workbench/documents/trading"
    ) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          content: "name: trading\n",
          base_digest: "sha256:e2e",
        }),
      });
      return;
    }

    if (
      method === "POST" &&
      path === "/api/workspaces/ws-workbench/diagrams"
    ) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          session_id: "sess-e2e",
          workspace_id: "ws-workbench",
          profile: "logical",
          dbml: DEMO_DBML,
        }),
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({}),
    });
  });
}

test.describe("drawDB bridge", () => {
  test("imports DBML into static-bridge iframe after moex:ready", async ({
    page,
  }) => {
    await mockDiagramApi(page);
    await page.goto("/models/trading/diagram");

    await expect(page.getByRole("heading", { name: /Diagram/i })).toBeVisible({
      timeout: 20_000,
    });
    const iframe = page.locator('iframe[title="drawDB"]');
    await expect(iframe).toBeVisible();

    const bridge = page.frameLocator('iframe[title="drawDB"]');
    await expect(bridge.locator("#moex-dbml-text")).toHaveValue(
      /Table Demo/,
      { timeout: 20_000 },
    );
    await expect(bridge.locator("#moex-status")).toContainText(/imported/i);
  });
});
