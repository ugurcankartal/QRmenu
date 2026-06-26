import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";

import {
  CategoryScrollProvider,
  CategoryScrollViewport,
  useCategoryPanelHeight,
  useCategoryScroll,
} from "../context/CategoryScrollContext";
import { useCategoryAutoAdvance } from "../hooks/useCategoryAutoAdvance";
import { useCategoryWheelNavigation } from "../hooks/useCategoryWheelNavigation";
import { CampaignProductGrid } from "./CampaignProductGrid";
import { StickyCategoryNav } from "./StickyCategoryNav";
import type { Category } from "../types/category";
import type { ActiveCategory } from "../types/categorySelection";
import type { Product } from "../types/product";

interface CategoryMenuLayoutProps {
  disabled?: boolean;
  products: Product[];
  isLoading?: boolean;
  isLoadingMore?: boolean;
  hasMore?: boolean;
  loadMoreRef?: React.RefObject<HTMLDivElement | null>;
  emptyMessage?: string;
  navProducts?: Product[];
  onCategoriesLoaded?: (categories: Category[]) => void;
  onSelectedCategoryChange?: (category: ActiveCategory) => void;
  productFilter?: (
    category: ActiveCategory,
    products: Product[],
    categories: Category[],
  ) => Product[];
}

function useApplyCategoryScrollIntent(
  scrollIntent: "forward" | "retreat" | null,
  clearScrollIntent: () => void,
  lockTransitions: () => void,
  isContentReady: boolean,
  contentVersion: string,
) {
  const { scrollToTop, scrollToBottomAfterLayout } = useCategoryScroll();
  const initialScrollAppliedRef = useRef(false);

  useLayoutEffect(() => {
    if (!isContentReady) {
      return;
    }

    if (scrollIntent) {
      if (scrollIntent === "forward") {
        scrollToTop(false);
      } else {
        scrollToBottomAfterLayout(false);
      }

      lockTransitions();
      clearScrollIntent();
      initialScrollAppliedRef.current = true;
      return;
    }

    if (!initialScrollAppliedRef.current) {
      scrollToTop(false);
      initialScrollAppliedRef.current = true;
    }
  }, [
    clearScrollIntent,
    contentVersion,
    isContentReady,
    lockTransitions,
    scrollIntent,
    scrollToBottomAfterLayout,
    scrollToTop,
  ]);
}

function CategoryMenuLayoutInner({
  disabled = false,
  products,
  isLoading = false,
  isLoadingMore = false,
  hasMore = false,
  loadMoreRef,
  emptyMessage,
  navProducts,
  onCategoriesLoaded,
  onSelectedCategoryChange,
  productFilter,
  panelHeight,
}: CategoryMenuLayoutProps & { panelHeight: string }) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [rootCategories, setRootCategories] = useState<Category[]>([]);
  const {
    selectedCategory,
    setSelectedCategory,
    scrollIntent,
    clearScrollIntent,
    lockTransitions,
    handleRootCategoriesChange,
    handleCategoryEndReached,
    handleCategoryStartReached,
    isScrollBlocked,
  } = useCategoryAutoAdvance(disabled);

  useCategoryWheelNavigation({
    disabled,
    isScrollBlocked,
    rootCategories,
    selectedCategory,
    hasMore,
    isLoadingMore,
    isLoading,
    onAdvance: handleCategoryEndReached,
    onRetreat: handleCategoryStartReached,
  });

  const displayProducts = useMemo(() => {
    if (!productFilter) {
      return products;
    }
    return productFilter(selectedCategory, products, categories);
  }, [categories, productFilter, products, selectedCategory]);

  const isContentReady = !isLoading && !isLoadingMore;
  const contentVersion = `${selectedCategory}:${displayProducts.length}:${isLoading}:${isLoadingMore}`;

  useApplyCategoryScrollIntent(
    scrollIntent,
    clearScrollIntent,
    lockTransitions,
    isContentReady,
    contentVersion,
  );

  useEffect(() => {
    onSelectedCategoryChange?.(selectedCategory);
  }, [onSelectedCategoryChange, selectedCategory]);

  const handleCategoriesLoaded = (loaded: Category[]) => {
    setCategories(loaded);
    onCategoriesLoaded?.(loaded);
  };

  const handleRootCategoriesLoaded = (roots: Category[]) => {
    setRootCategories(roots);
    handleRootCategoriesChange(roots);
  };

  return (
    <section data-category-menu-panel className="flex min-h-0 flex-col">
      <StickyCategoryNav
        products={navProducts}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        onCategoriesLoaded={handleCategoriesLoaded}
        onRootCategoriesChange={handleRootCategoriesLoaded}
      />
      <CategoryScrollViewport panelHeight={panelHeight}>
        <CampaignProductGrid
          categoryKey={selectedCategory}
          products={displayProducts}
          isLoading={isLoading}
          isLoadingMore={isLoadingMore}
          hasMore={hasMore}
          loadMoreRef={loadMoreRef}
          emptyMessage={emptyMessage}
        />
      </CategoryScrollViewport>
    </section>
  );
}

export function CategoryMenuLayout(props: CategoryMenuLayoutProps) {
  const panelHeight = useCategoryPanelHeight();

  return (
    <CategoryScrollProvider>
      <CategoryMenuLayoutInner {...props} panelHeight={panelHeight} />
    </CategoryScrollProvider>
  );
}
