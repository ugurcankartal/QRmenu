import { useCallback, useEffect, useRef, useState } from "react";

import { useOptionalCategoryScroll } from "../context/CategoryScrollContext";
import { fetchProductsPage } from "../api/products";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";
import type { Product } from "../types/product";
import { getViewportPageSize } from "../utils/getViewportPageSize";

function useLoadMoreTrigger(
  onLoadMore: () => void,
  enabled: boolean,
  scrollRoot: HTMLElement | null,
  scrollContainerReady: number,
) {
  const ref = useRef<HTMLDivElement>(null);
  const onLoadMoreRef = useRef(onLoadMore);
  onLoadMoreRef.current = onLoadMore;

  useEffect(() => {
    const node = ref.current;
    if (!node || !enabled) {
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          onLoadMoreRef.current();
        }
      },
      { root: scrollRoot, rootMargin: "240px 0px" },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [enabled, scrollRoot, scrollContainerReady]);

  return ref;
}

export function useInfiniteProducts(
  languageCode: string,
  selectedCategory: ActiveCategory,
  searchQuery = "",
) {
  const categoryScroll = useOptionalCategoryScroll();
  const scrollRoot = categoryScroll?.scrollContainerRef.current ?? null;
  const scrollContainerReady = categoryScroll?.scrollContainerReady ?? 0;
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const pageRef = useRef(1);
  const pageSizeRef = useRef(getViewportPageSize());
  const requestIdRef = useRef(0);

  const categoryId =
    selectedCategory === ALL_CATEGORIES ? undefined : selectedCategory;
  const search = searchQuery.trim() || undefined;

  const resetAndLoad = useCallback(async () => {
    const requestId = ++requestIdRef.current;
    pageRef.current = 1;
    pageSizeRef.current = getViewportPageSize();
    setIsLoading(true);
    setIsLoadingMore(false);
    setProducts([]);
    setHasMore(false);

    try {
      const { items, hasMore: more } = await fetchProductsPage({
        languageCode,
        page: 1,
        pageSize: pageSizeRef.current,
        categoryId,
        search,
      });
      if (requestId !== requestIdRef.current) {
        return;
      }
      setProducts(items);
      setHasMore(more);
      pageRef.current = 2;
    } catch {
      if (requestId !== requestIdRef.current) {
        return;
      }
      setProducts([]);
      setHasMore(false);
    } finally {
      if (requestId === requestIdRef.current) {
        setIsLoading(false);
      }
    }
  }, [languageCode, categoryId, search]);

  useEffect(() => {
    void resetAndLoad();
  }, [resetAndLoad]);

  const loadMore = useCallback(async () => {
    if (isLoading || isLoadingMore || !hasMore) {
      return;
    }

    const requestId = requestIdRef.current;
    setIsLoadingMore(true);

    try {
      const { items, hasMore: more } = await fetchProductsPage({
        languageCode,
        page: pageRef.current,
        pageSize: pageSizeRef.current,
        categoryId,
        search,
      });
      if (requestId !== requestIdRef.current) {
        return;
      }
      setProducts((previous) => {
        const existingIds = new Set(previous.map((product) => product.id));
        const uniqueItems = items.filter((product) => !existingIds.has(product.id));
        return [...previous, ...uniqueItems];
      });
      setHasMore(more);
      pageRef.current += 1;
    } catch {
      if (requestId !== requestIdRef.current) {
        return;
      }
      setHasMore(false);
    } finally {
      if (requestId === requestIdRef.current) {
        setIsLoadingMore(false);
      }
    }
  }, [languageCode, categoryId, search, hasMore, isLoading, isLoadingMore]);

  const loadMoreRef = useLoadMoreTrigger(
    () => {
      void loadMore();
    },
    hasMore && !isLoading && !isLoadingMore,
    scrollRoot,
    scrollContainerReady,
  );

  return {
    products,
    isLoading,
    isLoadingMore,
    hasMore,
    loadMoreRef,
  };
}
