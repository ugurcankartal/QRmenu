import { FormEvent, useState } from "react";
import { useLocation } from "react-router";

import { useFrontendAuth } from "../context/FrontendAuthContext";
import { useSiteAccess } from "../context/SiteAccessContext";

export function LoginPage() {
  const { login } = useFrontendAuth();
  const { publicAccess } = useSiteAccess();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (publicAccess) {
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(username.trim(), password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Giriş başarısız.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const redirectHint =
    (location.state as { from?: string } | null)?.from &&
    (location.state as { from?: string }).from !== "/login"
      ? "Devam etmek için giriş yapın."
      : "Site şu anda yalnızca yetkili kullanıcılara açık.";

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-charcoal-black to-dark-graphite px-4">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-dark-graphite/80 p-8 shadow-2xl backdrop-blur-md">
        <h1 className="mb-2 text-2xl font-semibold text-warm-cream">Giriş</h1>
        <p className="mb-6 text-sm text-warm-cream/70">{redirectHint}</p>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label
              htmlFor="username"
              className="mb-1 block text-sm font-medium text-warm-cream/80"
            >
              Kullanıcı adı
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-charcoal-black/60 px-4 py-3 text-warm-cream outline-none focus:border-copper-gold"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-1 block text-sm font-medium text-warm-cream/80"
            >
              Şifre
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-charcoal-black/60 px-4 py-3 text-warm-cream outline-none focus:border-copper-gold"
            />
          </div>

          {error ? (
            <p className="rounded-xl border border-deep-red/40 bg-deep-red/10 px-4 py-3 text-sm text-red-200">
              {error}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl bg-copper-gold px-4 py-3 font-semibold text-charcoal-black transition-colors hover:bg-copper-gold/90 disabled:opacity-60"
          >
            {isSubmitting ? "Giriş yapılıyor..." : "Giriş yap"}
          </button>
        </form>

        <p className="mt-6 text-xs text-warm-cream/50">
          Yalnızca admin veya supervisor rolündeki kullanıcılar giriş yapabilir.
        </p>
      </div>
    </div>
  );
}
