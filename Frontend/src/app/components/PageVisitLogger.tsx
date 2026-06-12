import { useEffect } from "react";
import { useLocation } from "react-router";

import { logPageVisit } from "../api/security";

export function PageVisitLogger() {
  const location = useLocation();

  useEffect(() => {
    logPageVisit(location.pathname, location.search);
  }, [location.pathname, location.search]);

  return null;
}
