import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ViewerPage } from "./ViewerPage";

function jsonResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  };
}

describe("ViewerPage", () => {
  afterEach(() => {
    cleanup();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("shows the publication when build info exists", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse({
          commit: "abcdef1234567890",
          built_at: "2026-11-09T00:00:00Z",
        }),
      ),
    );
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-11-09T00:10:00Z"));

    await act(async () => {
      render(<ViewerPage />);
    });

    expect(screen.getByRole("heading", { name: "Viewer" })).toBeTruthy();
    expect(
      screen.getByText(
        "коммит abcdef123456, 2026-11-09 00:00 UTC, собран 10 мин назад",
      ),
    ).toBeTruthy();
    expect(screen.getByRole("link", { name: "Открыть в новой вкладке" }).getAttribute("href")).toBe(
      "/viewer/",
    );
    expect(screen.getByTitle("Viewer").getAttribute("src")).toBe("/viewer/");
  });

  it("explains that the viewer is not built yet", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse({}, 404)),
    );

    await act(async () => {
      render(<ViewerPage />);
    });

    expect(
      screen.getByText("Viewer ещё не собран: модели не подключены"),
    ).toBeTruthy();
    expect(screen.queryByTitle("Viewer")).toBeNull();
  });

  it("reloads the frame when the commit changes", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          commit: "aaaaaaaaaaaa",
          built_at: "2026-11-09T00:00:00Z",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          commit: "bbbbbbbbbbbb",
          built_at: "2026-11-09T00:01:00Z",
        }),
      );
    vi.stubGlobal("fetch", fetchMock);
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-11-09T00:10:00Z"));

    await act(async () => {
      render(<ViewerPage />);
    });

    const first = screen.getByTitle("Viewer");
    expect(screen.getByText(/коммит aaaaaaaaaaaa/)).toBeTruthy();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(30_000);
    });

    const second = screen.getByTitle("Viewer");
    expect(second).not.toBe(first);
    expect(screen.getByText(/коммит bbbbbbbbbbbb/)).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
