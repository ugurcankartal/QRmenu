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
  fetchAdisyon,
  removeAdisyonItem,
  toggleAdisyonProduct,
  updateAdisyonItemQuantity,
} from "../api/adisyon";
import { useLanguage } from "./LanguageContext";
import type { Adisyon } from "../types/adisyon";

interface AdisyonContextValue {
  adisyon: Adisyon | null;
  isLoading: boolean;
  error: string | null;
  togglingProductIds: ReadonlySet<number>;
  isInAdisyon: (productId: number | string) => boolean;
  toggleProduct: (productId: number | string) => Promise<void>;
  updateQuantity: (itemId: number, quantity: number) => Promise<void>;
  removeItem: (itemId: number) => Promise<void>;
  refresh: () => Promise<void>;
  itemCount: number;
  lineItemCount: number;
}

const AdisyonContext = createContext<AdisyonContextValue | null>(null);

export function AdisyonProvider({ children }: { children: ReactNode }) {
  const { languageCode } = useLanguage();
  const [adisyon, setAdisyon] = useState<Adisyon | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [togglingProductIds, setTogglingProductIds] = useState<Set<number>>(
    () => new Set(),
  );

  const loadAdisyon = useCallback(async () => {
    if (!languageCode) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchAdisyon(languageCode);
      setAdisyon(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Adisyon yüklenemedi");
    } finally {
      setIsLoading(false);
    }
  }, [languageCode]);

  useEffect(() => {
    void loadAdisyon();
  }, [loadAdisyon]);

  const productIdSet = useMemo(
    () => new Set(adisyon?.product_ids ?? []),
    [adisyon?.product_ids],
  );

  const isInAdisyon = useCallback(
    (productId: number | string) => productIdSet.has(Number(productId)),
    [productIdSet],
  );

  const toggleProduct = useCallback(
    async (productId: number | string) => {
      if (!languageCode) {
        return;
      }

      const id = Number(productId);
      setTogglingProductIds((prev) => new Set(prev).add(id));
      try {
        const data = await toggleAdisyonProduct(id, languageCode);
        setAdisyon(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "İşlem başarısız");
      } finally {
        setTogglingProductIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      }
    },
    [languageCode],
  );

  const updateQuantity = useCallback(
    async (itemId: number, quantity: number) => {
      const data = await updateAdisyonItemQuantity(itemId, quantity, languageCode);
      setAdisyon(data);
      setError(null);
    },
    [languageCode],
  );

  const removeItem = useCallback(
    async (itemId: number) => {
      const data = await removeAdisyonItem(itemId, languageCode);
      setAdisyon(data);
      setError(null);
    },
    [languageCode],
  );

  const itemCount = useMemo(
    () => adisyon?.items.reduce((sum, item) => sum + item.quantity, 0) ?? 0,
    [adisyon?.items],
  );

  const lineItemCount = useMemo(
    () => adisyon?.items.length ?? 0,
    [adisyon?.items],
  );

  const value = useMemo<AdisyonContextValue>(
    () => ({
      adisyon,
      isLoading,
      error,
      togglingProductIds,
      isInAdisyon,
      toggleProduct,
      updateQuantity,
      removeItem,
      refresh: loadAdisyon,
      itemCount,
      lineItemCount,
    }),
    [
      adisyon,
      isLoading,
      error,
      togglingProductIds,
      isInAdisyon,
      toggleProduct,
      updateQuantity,
      removeItem,
      loadAdisyon,
      itemCount,
      lineItemCount,
    ],
  );

  return (
    <AdisyonContext.Provider value={value}>{children}</AdisyonContext.Provider>
  );
}

export function useAdisyon() {
  const context = useContext(AdisyonContext);
  if (!context) {
    throw new Error("useAdisyon must be used within AdisyonProvider");
  }
  return context;
}
