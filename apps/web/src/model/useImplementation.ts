import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Implementation } from "../api/types";

export type UseImplementationResult = {
  asset: Implementation | undefined;
  editable: boolean;
  isLoading: boolean;
  error: Error | null;
};

export function useImplementation(slug: string | undefined): UseImplementationResult {
  const query = useQuery({
    queryKey: ["implementations"],
    queryFn: api.listImplementations,
  });

  const asset = query.data?.find((row) => row.slug === slug || row.id === slug);

  return {
    asset,
    editable: Boolean(asset?.workbench_editable),
    isLoading: query.isLoading,
    error: (query.error as Error | null) ?? null,
  };
}
