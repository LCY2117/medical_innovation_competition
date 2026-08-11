export function downloadJson(filename: string, data: unknown): void {
  downloadText(filename, JSON.stringify(data, null, 2), 'application/json;charset=utf-8');
}

export function downloadText(filename: string, text: string, mimeType = 'text/markdown;charset=utf-8'): void {
  if (typeof document === 'undefined') {
    return;
  }
  const blob = new Blob([text], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export interface BlobDownloadResult {
  filename: string;
  packageSha256: string | null;
}

export async function downloadResponseBlob(
  response: Response,
  fallbackFilename: string,
): Promise<BlobDownloadResult> {
  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const encoded = disposition.match(/filename\*=UTF-8''([^;]+)/)?.[1];
  const plain = disposition.match(/filename="?([^";]+)"?/)?.[1];
  const filename = encoded ? decodeURIComponent(encoded) : plain || fallbackFilename;
  const packageSha256 = response.headers.get('X-LifeReflexArc-Package-Sha256');
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
  return { filename, packageSha256 };
}

export async function copyTextToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}
