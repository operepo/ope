'use strict';

let redis = require('redis');
let url = require('url');
let typeset = require('./typeset');

class Server  {
  constructor(redisPort, redisHost) {
    this.ts = typeset;
    this.useRedis = !!(redisHost && redisPort);
    if (this.useRedis) {
      this.redisCli = redis.createClient(redisPort, redisHost);
    }
  }

  handleRequest(req, res) {
    if (req.method !== 'GET') {
      this.sendError(res, 405, "Method not allowed.");
      return;
    }
    let uri = url.parse(req.url, true);
    let type = uri.pathname.replace(/^\/+|\/+$/g, "");
    if (type !== 'svg' && type !== 'mml') {
      this.sendError(res, 404, "Not Found");
      return;
    }
    let tex = uri.query.tex;
    if (!tex) {
      this.sendBadRequest(res, "no LaTeX provided.");
      return;
    }
    if (req.headers['if-modified-since']) {
      this.sendNotModified(res);
      return;
    }
    this.sendCachedResponse(res, type, tex);
  }

  sendBadRequest(res, reason) {
    this.sendError(res, 400, "Bad request: " + reason);
  }

  sendError(res, code, message) {
    res.writeHead(code, { 'Content-Type': 'text/plain' });
    res.end(message);
  }

  sendNotModified(res) {
    res.writeHead(304);
    res.end();
  }

  // account for bytesize of unicode characters like '£'
  getByteCount(str) {
    return encodeURI(str).split(/%..|./).length - 1;
  }

  sendResponse(res, type, body) {
    let headers = {'Content-Type': type === 'svg' ? 'image/svg+xml' : 'application/mathml+xml'};
    headers['content-length'] = this.getByteCount(body);
    res.writeHead(200, headers);
    res.end(body);
  }

  sendTypesetResponse(res, type, tex) {
    this.ts(tex, (err, data) => {
      if (err) {
        this.sendBadRequest(res, err.join('\n'));
        return;
      }
      this.sendResponse(res, type, data[type]);
      if (this.useRedis) {
        this.redisCli.mset('mml:' + tex, data['mml'], 'svg:' + tex, data['svg']);
      }
    });
  }

  sendCachedResponse(res, type, tex) {
    if (this.useRedis) {
      this.redisCli.get(type + ':' + tex, (err, reply) => {
        if (err) {
          console.log(err);
          this.sendTypesetResponse(res, type, tex);
          return;
        }
        if (!reply) {
          this.sendTypesetResponse(res, type, tex);
          return;
        }
        this.sendResponse(res, type, reply);
      });
    } else {
      this.sendTypesetResponse(res, type, tex);
    }
  }
}

module.exports = Server;

