import { useEffect, useState } from 'react';
import { ScanLine } from 'lucide-react';
import { getApiBase } from '@/shared/api';

interface DemoLinksResponse {
  baseUrl: string;
  lanIps: string[];
  port: number;
  mobileDemoUrl: string;
}

function isLoopback(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '::1' || hostname.startsWith('127.');
}

export function DemoQr({ incidentId }: { incidentId: string | null }) {
  const [qrSrc, setQrSrc] = useState<string | null>(null);
  const [demoUrl, setDemoUrl] = useState<string>('');
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${getApiBase()}/demo/links`);
        if (!res.ok) {
          throw new Error('links-failed');
        }
        const data = (await res.json()) as DemoLinksResponse;
        if (cancelled) {
          return;
        }
        // 大屏如果本来就是通过局域网 IP 打开的，直接沿用当前 origin；
        // 否则用后端探测到的局域网地址，保证平板在同一网络内可访问。
        const hostname = window.location.hostname;
        const baseUrl = isLoopback(hostname) ? data.baseUrl : window.location.origin;
        const params = new URLSearchParams();
        if (incidentId) {
          params.set('incidentId', incidentId);
        }
        const query = params.toString();
        const url = `${baseUrl}/mobile-demo${query ? `?${query}` : ''}`;
        setDemoUrl(url);
        setQrSrc(`${getApiBase()}/demo/qr?text=${encodeURIComponent(url)}`);
      } catch {
        if (!cancelled) {
          setFailed(true);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [incidentId]);

  if (failed) {
    return (
      <div className="lra-demo-qr">
        <span style={{ fontSize: 11, color: 'var(--lra-text-faint)' }}>局域网二维码不可用（请确认已启动后端）</span>
      </div>
    );
  }

  return (
    <div className="lra-demo-qr">
      <div className="lra-demo-qr-hint">
        <ScanLine size={13} />
        <span>平板扫码进入四端演示</span>
      </div>
      {qrSrc ? (
        <img className="lra-demo-qr-img" src={qrSrc} alt="四端演示二维码" />
      ) : (
        <div className="lra-demo-qr-img lra-demo-qr-placeholder">二维码生成中…</div>
      )}
      {demoUrl ? <div className="lra-demo-qr-url" title={demoUrl}>{demoUrl}</div> : null}
    </div>
  );
}
