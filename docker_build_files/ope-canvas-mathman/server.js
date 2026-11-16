"use strict"

let redis = require("redis")
let url = require("url")
let typeset = require("./typeset")

class Server {
  constructor(redisPort, redisHost) {
    this.ts = typeset
    this.useRedis = !!(redisHost && redisPort)
    if (this.useRedis) {
      this.redisCli = redis.createClient(redisPort, redisHost)
    }
  }

  handleRequest(req, res) {
    if (req.method !== "GET") {
      this.sendError(res, 405, "Method not allowed.")
      return
    }
    let uri = url.parse(req.url, true)
    let type = uri.pathname.replace(/^\/+|\/+$/g, "")
    if (type !== "svg" && type !== "mml") {
      this.sendError(res, 404, "Not Found")
      return
    }
    let tex = uri.query.tex
    if (!tex) {
      this.sendBadRequest(res, "no LaTeX provided.")
      return
    }
    const scale = parseFloat(uri.query.scale || 1)
    if (!scale) {
      this.sendBadRequest(res, "invalid scale provided.")
      return
    }
    if (req.headers["if-modified-since"]) {
      this.sendNotModified(res)
      return
    }
    this.sendCachedResponse(res, type, tex, scale)
  }

  sendBadRequest(res, reason) {
    this.sendError(res, 400, "Bad request: " + reason)
  }

  sendError(res, code, message) {
    res.writeHead(code, { "Content-Type": "text/plain" })
    res.end(message)
  }

  sendNotModified(res) {
    res.writeHead(304)
    res.end()
  }

  // account for bytesize of unicode characters like '£'
  getByteCount(str) {
    return encodeURI(str).split(/%..|./).length - 1
  }

  sendResponse(res, type, body, scale = 1) {
    let headers = {
      "Content-Type":
        type === "svg" ? "image/svg+xml" : "application/mathml+xml",
    }
    headers["content-length"] = this.getByteCount(body)
    res.writeHead(200, headers)
    res.end(body)
  }

  sendTypesetResponse(res, type, tex, scale = 1) {
    this.ts({ tex, scale }, (err, data) => {
      if (err) {
        this.sendBadRequest(res, err.join("\n"))
        return
      }
      this.sendResponse(res, type, data[type], scale)
      if (this.useRedis) {
        this.redisCli.mset(
          "mml:" + tex,
          data["mml"],
          "svg:" + tex + ":" + scale,
          data["svg"]
        )
      }
    })
  }

  sendCachedResponse(res, type, tex, scale = 1) {
    if (this.useRedis) {
      let key = type + ":" + tex
      if (type === 'svg') key = `${key}:${scale}`
      this.redisCli.get(key, (err, reply) => {
        if (err) {
          console.log(err)
          this.sendTypesetResponse(res, type, tex, scale)
          return
        }
        if (!reply) {
          this.sendTypesetResponse(res, type, tex, scale)
          return
        }
        this.sendResponse(res, type, reply, scale)
      })
    } else {
      this.sendTypesetResponse(res, type, tex, scale)
    }
  }
}

module.exports = Server
