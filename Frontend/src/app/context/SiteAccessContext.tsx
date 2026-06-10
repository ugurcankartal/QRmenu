import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { fetchAccessStatus } from "../api/access";

interface SiteAccessContextValue {
  publicAccess: boolean;
  isLoading: boolean;
  error: string | null;
  refreshAccessStatus: () => Promise<void>;
}

const SiteAccessContext = createContext<SiteAccessContextValue | null>(null);

export function SiteAccessProvider({ children }: { children: ReactNode }) {
  const [publicAccess, setPublicAccess] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshAccessStatus = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const status = await fetchAccessStatus();
      setPublicAccess(status.public_access);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erişim durumu alınamadı.");
      setPublicAccess(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshAccessStatus();
  }, [refreshAccessStatus]);

  const value = useMemo(
    () => ({
      publicAccess,
      isLoading,
      error,
      refreshAccessStatus,
    }),
    [publicAccess, isLoading, error, refreshAccessStatus],
  );

  return (
    <SiteAccessContext.Provider value={value}>{children}</SiteAccessContext.Provider>
  );
}

export function useSiteAccess() {
  const context = useContext(SiteAccessContext);
  if (!context) {
    throw new Error("useSiteAccess must be used within SiteAccessProvider");
  }
  return context;
}
