const ALB = 'http://defect-alb-1564603409.ap-south-1.elb.amazonaws.com';

module.exports = async function handler(req, res) {
  const url = new URL(req.url, 'http://x');
  const path = url.searchParams.get('_path') || '';
  url.searchParams.delete('_path');
  const qs = url.searchParams.toString();
  const target = `${ALB}/api/${path}${qs ? '?' + qs : ''}`;

  const headers = {};
  for (const [k, v] of Object.entries(req.headers)) {
    if (['host', 'connection', 'x-forwarded-host', 'x-forwarded-proto', 'x-forwarded-for', 'x-real-ip', 'x-vercel-id', 'x-vercel-deployment-url', 'x-vercel-forwarded-for', 'x-vercel-ip-country', 'x-vercel-ip-country-region', 'x-vercel-ip-city', 'x-vercel-ip-timezone', 'x-vercel-ip-latitude', 'x-vercel-ip-longitude', 'x-vercel-proxy-signature', 'x-vercel-proxy-signature-ts', 'content-length'].includes(k.toLowerCase())) continue;
    headers[k] = v;
  }
  if (!headers['content-type']) headers['content-type'] = 'application/json';

  const init = { method: req.method, headers };
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    init.body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
  }

  try {
    const upstream = await fetch(target, init);
    const setCookie = upstream.headers.getSetCookie ? upstream.headers.getSetCookie() : upstream.headers.raw?.()['set-cookie'];
    if (setCookie && setCookie.length) res.setHeader('set-cookie', setCookie);
    const ct = upstream.headers.get('content-type');
    if (ct) res.setHeader('content-type', ct);
    const text = await upstream.text();
    res.status(upstream.status).send(text);
  } catch (e) {
    res.status(502).json({ detail: 'Proxy error', error: e.message, target });
  }
};
