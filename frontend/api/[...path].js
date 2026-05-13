const ALB = 'http://defect-alb-1564603409.ap-south-1.elb.amazonaws.com:8080';

export default async function handler(req, res) {
  const target = ALB + req.url;

  const headers = {};
  if (req.headers['content-type']) headers['content-type'] = req.headers['content-type'];
  if (req.headers['authorization']) headers['authorization'] = req.headers['authorization'];

  const init = { method: req.method, headers };
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    init.body = JSON.stringify(req.body);
    headers['content-type'] = 'application/json';
  }

  try {
    const upstream = await fetch(target, init);
    const text = await upstream.text();
    res.status(upstream.status);
    try {
      res.json(JSON.parse(text));
    } catch {
      res.send(text);
    }
  } catch (e) {
    res.status(502).json({ detail: 'Proxy error', error: e.message });
  }
}
