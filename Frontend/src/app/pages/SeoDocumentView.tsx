import { useEffect, useState } from "react";
import { useLocation } from "react-router";

const SEO_PATHS = new Set(["/robots.txt", "/sitemap.xml"]);

function isHtmlPayload(text: string): boolean {
  const trimmed = text.trimStart().toLowerCase();
  return trimmed.startsWith("<!doctype html") || trimmed.startsWith("<html");
}

async function fetchSeoDocument(path: string): Promise<string> {
  const candidates = [path, `/api/v1${path}`];

  for (const url of candidates) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      continue;
    }
    const text = await response.text();
    if (!isHtmlPayload(text)) {
      return text;
    }
  }

  throw new Error("SEO dosyasi alinamadi.");
}

export function isSeoDocumentPath(path: string): boolean {
  return SEO_PATHS.has(path);
}

/** CDN/SPA robots.txt veya sitemap.xml isteginde icerigi API'den gosterir. */
export function SeoDocumentView() {
  const location = useLocation();
  const [content, setContent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setContent(null);
    setError(null);

    void fetchSeoDocument(location.pathname)
      .then((text) => {
        if (!cancelled) {
          setContent(text);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "SEO dosyasi yuklenemedi.",
          );
        }
      });

    return () => {
      cancelled = true;
    };
  }, [location.pathname]);

  if (error) {
    return (
      <pre className="m-0 whitespace-pre-wrap p-4 font-mono text-sm text-red-200">
        {error}
      </pre>
    );
  }

  if (content === null) {
    return (
      <pre className="m-0 whitespace-pre-wrap p-4 font-mono text-sm text-warm-cream/70">
        Yukleniyor...
      </pre>
    );
  }

  return (
    <pre className="m-0 min-h-screen whitespace-pre-wrap bg-charcoal-black p-4 font-mono text-sm text-warm-cream">
      {content}
    </pre>
  );
}
