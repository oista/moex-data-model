import yaml from "js-yaml";

export type DraftParseResult = {
  data: Record<string, unknown> | null;
  error: string | null;
};

export function parseDraftYaml(content: string): DraftParseResult {
  if (!content.trim()) {
    return { data: null, error: null };
  }
  try {
    const data = yaml.load(content) as Record<string, unknown> | null;
    if (data !== null && typeof data !== "object") {
      return { data: null, error: "root YAML must be a mapping" };
    }
    return { data: data as Record<string, unknown> | null, error: null };
  } catch (err) {
    return {
      data: null,
      error: err instanceof Error ? err.message : "Invalid YAML",
    };
  }
}

export function serializeDraftYaml(data: Record<string, unknown>): string {
  return yaml.dump(data, {
    lineWidth: 120,
    noRefs: true,
    sortingKeys: false,
  });
}
