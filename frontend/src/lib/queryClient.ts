// TanStack Query 전역 QueryClient — 측정 데이터는 잦은 refetch 불필요하므로 staleTime 보수적.
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
