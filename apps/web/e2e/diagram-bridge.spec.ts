import { expect, test } from "@playwright/test";

const DEMO_DBML = "Table Demo {\n  id integer [pk]\n}\n";
const MDM_ID = "moex:implementation:mdm:0.1.0";
const MDM_DOC =
  `/api/workspaces/ws-workbench/documents/${encodeURIComponent(MDM_ID)}`;

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

    if (method === "GET" && path === "/api/implementations") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: MDM_ID,
            slug: "mdm",
            title: "Модель данных MDM",
            version: "1.0.0",
            implementation_path: "p",
            implementation_kind: "linkml",
            implementation_profile: "dams-data-model",
            workbench_editable: true,
          },
        ]),
      });
      return;
    }

    if (method === "POST" && path === "/api/workspaces") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ id: "ws-workbench", name: "Workbench" }),
      });
      return;
    }

    if (method === "GET" && path === MDM_DOC) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          content: "name: demo\n",
          base_digest: "sha256:e2e",
          doc_key: MDM_ID,
          workspace_id: "ws-workbench",
          updated_by: "dev",
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
    await page.goto("/models/mdm/diagram");

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
