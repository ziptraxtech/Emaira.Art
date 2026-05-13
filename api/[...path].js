const ALB = 'http://defect-alb-1564603409.ap-south-1.elb.amazonaws.com:8080';

module.exports = async function handler(req, res) {
  const target = ALB + req.url;

  const headers = { 'content-type': 'application/json' };
  if (req.headers['authorization']) headers['authorization'] = req.headers['authorization'];

  const init = { method: req.method, headers };
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    init.body = JSON.stringify(req.body);
  }

  try {
    const upstream = await fetch(target, init);
    const text = await upstream.text();
    res.status(upstream.status);
    try { res.json(JSON.parse(text)); } catch { res.send(text); }
  } catch (e) {
    res.status(502).json({ detail: 'Proxy error', error: e.message });
  }
};
