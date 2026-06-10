import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  fetchCurrentUser,
  login as loginRequest,
  logout as logoutRequest,
  type FrontendAuthUser,
} from "../api/auth";
import { getStoredAccessToken } from "../api/http";
import { useSiteAccess } from "./SiteAccessContext";

interface FrontendAuthContextValue {
  user: FrontendAuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const FrontendAuthContext = createContext<FrontendAuthContextValue | null>(null);

export function FrontendAuthProvider({ children }: { children: ReactNode }) {
  const { publicAccess } = useSiteAccess();
  const [user, setUser] = useState<FrontendAuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const restoreSession = useCallback(async () => {
    if (publicAccess && !getStoredAccessToken()) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    if (!getStoredAccessToken()) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [publicAccess]);

  useEffect(() => {
    void restoreSession();
  }, [restoreSession, publicAccess]);

  const login = useCallback(async (username: string, password: string) => {
    const loggedInUser = await loginRequest(username, password);
    setUser(loggedInUser);
  }, []);

  const logout = useCallback(() => {
    logoutRequest();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
    }),
    [user, isLoading, login, logout],
  );

  return (
    <FrontendAuthContext.Provider value={value}>
      {children}
    </FrontendAuthContext.Provider>
  );
}

export function useFrontendAuth() {
  const context = useContext(FrontendAuthContext);
  if (!context) {
    throw new Error("useFrontendAuth must be used within FrontendAuthProvider");
  }
  return context;
}
