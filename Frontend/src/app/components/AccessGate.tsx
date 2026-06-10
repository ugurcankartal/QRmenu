import { Navigate, Outlet, useLocation } from "react-router";

import { useFrontendAuth } from "../context/FrontendAuthContext";
import { useSiteAccess } from "../context/SiteAccessContext";

export function AccessGate() {
  const { publicAccess, isLoading: accessLoading } = useSiteAccess();
  const { isAuthenticated, isLoading: authLoading } = useFrontendAuth();
  const location = useLocation();
  const onLoginPage = location.pathname === "/login";

  if (accessLoading || authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-charcoal-black text-warm-cream">
        Yükleniyor...
      </div>
    );
  }

  if (!publicAccess && !isAuthenticated) {
    if (!onLoginPage) {
      return <Navigate to="/login" replace state={{ from: location.pathname }} />;
    }
    return <Outlet />;
  }

  if (onLoginPage && isAuthenticated) {
    const from =
      (location.state as { from?: string } | null)?.from &&
      (location.state as { from?: string }).from !== "/login"
        ? (location.state as { from?: string }).from
        : "/";
    return <Navigate to={from ?? "/"} replace />;
  }

  return <Outlet />;
}
