/** Ondalık kısmı 2 basamağa keser (yuvarlamaz). */
function truncateFractionToTwoDigits(fraction: string): string {
  return (fraction + "00").slice(0, 2);
}

export function formatMoneyValue(value: string, languageCode: string): string {
  const locale =
    languageCode === "tr" ? "tr-TR" : languageCode === "en" ? "en-US" : undefined;
  const normalized = value.trim();

  if (!normalized) {
    return "0";
  }

  const [whole = "0", fraction = ""] = normalized.split(".");
  const wholeNumber = Number(whole);

  if (!Number.isFinite(wholeNumber)) {
    return "0";
  }

  const formattedWhole = wholeNumber.toLocaleString(locale, {
    maximumFractionDigits: 0,
  });
  const truncatedFraction = truncateFractionToTwoDigits(fraction);
  const hasFraction = !/^0+$/.test(truncatedFraction);

  if (!hasFraction) {
    return formattedWhole;
  }

  const decimalSeparator = locale === "tr-TR" ? "," : ".";
  return `${formattedWhole}${decimalSeparator}${truncatedFraction}`;
}
