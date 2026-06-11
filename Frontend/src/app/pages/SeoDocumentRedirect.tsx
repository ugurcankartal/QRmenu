import { useEffect } from "react";
import { useLocation } from "react-router";

/** SPA shell yanlislikla /robots.txt veya /sitemap.xml icin yuklendiyse sunucudan tekrar iste. */
export function SeoDocumentRedirect() {
  const location = useLocation();

  useEffect(() => {
    window.location.replace(location.pathname);
  }, [location.pathname]);

  return null;
}
