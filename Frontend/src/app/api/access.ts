import { apiFetch, parseJsonResponse } from "./http";

export interface FrontendAccessStatus {
  public_access: boolean;
}

export async function fetchAccessStatus(): Promise<FrontendAccessStatus> {
  const response = await apiFetch("/access/status/");
  if (!response.ok) {
    throw new Error(`Erişim durumu yüklenemedi (${response.status})`);
  }
  return parseJsonResponse<FrontendAccessStatus>(response);
}
