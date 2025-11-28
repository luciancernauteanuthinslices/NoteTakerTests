export function buildUrl(path: string, params?: Record<any, any>) {
  if (!params || Object.keys(params).length === 0) {
    return path;
  }

  const searchParams = new URLSearchParams(
    Object.entries(params).map(([key, value]) => [key, String(value)]),
  );
  return `${path}?${searchParams.toString()}`;
}
