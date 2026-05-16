const http = require('http');
const PORT = process.env.PORT || 3100;
const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ status: 'alive', port: PORT, node: process.version, ts: new Date().toISOString() }));
});
server.listen(PORT, '0.0.0.0', () => console.log(`Listening on ${PORT}`));
