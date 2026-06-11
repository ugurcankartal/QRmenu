import { FormEvent, useEffect, useState } from "react";
import { useLocation } from "react-router";

import { LoginError } from "../api/auth";
import { useFrontendAuth } from "../context/FrontendAuthContext";
import { useSiteAccess } from "../context/SiteAccessContext";

function formatCountdown(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

export function LoginPage() {
  const { login } = useFrontendAuth();
  const { publicAccess } = useSiteAccess();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [remainingAttempts, setRemainingAttempts] = useState<number | null>(
    null,
  );
  const [lockoutSeconds, setLockoutSeconds] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (lockoutSeconds <= 0) {
      return;
    }

    const timer = window.setInterval(() => {
      setLockoutSeconds((current) => Math.max(0, current - 1));
    }, 1000);

    return () => window.clearInterval(timer);
  }, [lockoutSeconds]);

  if (publicAccess) {
    return null;
  }

  const isLockedOut = lockoutSeconds > 0;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isLockedOut) {
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      await login(username.trim(), password);
      setRemainingAttempts(null);
      setLockoutSeconds(0);
    } catch (err) {
      if (err instanceof LoginError) {
        if (typeof err.remainingAttempts === "number") {
          setRemainingAttempts(err.remainingAttempts);
        }
        if (err.retryAfterSeconds && err.retryAfterSeconds > 0) {
          setLockoutSeconds(err.retryAfterSeconds);
          setRemainingAttempts(0);
        }
        setError(err.message);
      } else {
        setError(err instanceof Error ? err.message : "Giriş başarısız.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  const redirectHint =
    (location.state as { from?: string } | null)?.from &&
    (location.state as { from?: string }).from !== "/login"
      ? ""
      : "Site şu anda yalnızca yetkili kullanıcılara açık.";

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-charcoal-black to-dark-graphite px-4">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-dark-graphite/80 p-8 shadow-2xl backdrop-blur-md">
        <h1 className="mb-2 text-2xl font-semibold text-warm-cream">Giriş</h1>
        <p className="mb-6 text-sm text-warm-cream/70">{redirectHint}</p>

        {isLockedOut ? (
          <p className="mb-4 rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
            Çok fazla başarısız deneme. Lütfen{" "}
            <span className="font-semibold">{formatCountdown(lockoutSeconds)}</span>{" "}
            bekleyin.
          </p>
        ) : null}

        {!isLockedOut && remainingAttempts !== null && remainingAttempts > 0 ? (
          <p className="mb-4 text-sm text-warm-cream/60">
            Kalan deneme hakkı:{" "}
            <span className="font-semibold text-warm-cream">
              {remainingAttempts}
            </span>
          </p>
        ) : null}

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
              disabled={isLockedOut || isSubmitting}
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-charcoal-black/60 px-4 py-3 text-warm-cream outline-none focus:border-copper-gold disabled:opacity-60"
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
              disabled={isLockedOut || isSubmitting}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-charcoal-black/60 px-4 py-3 text-warm-cream outline-none focus:border-copper-gold disabled:opacity-60"
            />
          </div>

          {error ? (
            <p className="rounded-xl border border-deep-red/40 bg-deep-red/10 px-4 py-3 text-sm text-red-200">
              {error}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={isSubmitting || isLockedOut}
            className="w-full rounded-xl bg-copper-gold px-4 py-3 font-semibold text-charcoal-black transition-colors hover:bg-copper-gold/90 disabled:opacity-60"
          >
            {isSubmitting
              ? "Giriş yapılıyor..."
              : isLockedOut
                ? "Geçici olarak kilitli"
                : "Giriş yap"}
          </button>
        </form>
      </div>
    </div>
  );
}
