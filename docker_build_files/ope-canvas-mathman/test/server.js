'use strict';

let should = require('chai').should();
let sinon = require('sinon');
let Server = require('../server');
let redis = require('redis');
let url = require('url');
let typeset = require('../typeset');
// run the typeset tests first.

describe('server', function () {
  describe('#constructur', function () {
    before(function () {
      sinon.stub(redis, 'createClient');
    });

    after(function () {
      redis.createClient.restore();
    });

    afterEach(function () {
      redis.createClient.resetHistory();
    });

    it('should not use redis when host and port not passed', function () {
      let server = new Server;
      server.useRedis.should.be.false;
      server = new Server(1234);
      server.useRedis.should.be.false;
      server = new Server(null, 'localhost');
      server.useRedis.should.be.false;
      redis.createClient.called.should.be.false;
    });

    it('should create redis client when host and port are passed', function () {
      let redisCli = {};
      let port = 12345;
      let host = 'test.com';
      redis.createClient.returns(redisCli);
      let server = new Server(port, host);
      redis.createClient.calledOnce.should.be.true;
      let args = redis.createClient.lastCall.args;
      args.should.have.lengthOf(2);
      args[0].should.equal(port);
      args[1].should.equal(host);
      server.redisCli.should.equal(redisCli);
    });
  });

  describe('#sendError', function () {
    let res = {};
    let server;
    before(function () {
    res.writeHead = sinon.spy();
    res.end = sinon.spy();
    });

    beforeEach(function () {
      server = new Server;
    });

    afterEach(function () {
      res.writeHead.resetHistory();
      res.end.resetHistory();
    });

    it('should call writeHead properly', function () {
      let code = 42;
      server.sendError(res, code, "Life, the universe, and everything!");
      res.writeHead.calledOnce.should.be.true;
      let args = res.writeHead.lastCall.args;
      args.should.have.lengthOf(2);
      args[0].should.equal(code);
      args[1].should.be.an('object').and.have.a.property('Content-Type', 'text/plain');
    });

    it('should call end properly', function () {
      let message = "hello world";
      server.sendError(res, 42, message);
      res.end.calledOnce.should.be.true;
      let args = res.end.lastCall.args;
      args.should.have.lengthOf(1);
      args[0].should.equal(message);
    });
  });

  describe('#sendNotModified', function () {
    let res = {};
    let server;
    before(function () {
    res.writeHead = sinon.spy();
    res.end = sinon.spy();
    });

    beforeEach(function () {
      server = new Server;
    });

    afterEach(function () {
      res.writeHead.resetHistory();
      res.end.resetHistory();
    });

    it('should call writeHead properly', function () {
      server.sendNotModified(res);
      res.writeHead.calledOnce.should.be.true;
      let args = res.writeHead.lastCall.args;
      args.should.have.lengthOf(1);
      args[0].should.equal(304);
    });

    it('should call end properly', function () {
      server.sendNotModified(res);
      res.end.calledOnce.should.be.true;
      let args = res.end.lastCall.args;
      args.should.have.lengthOf(0);
    });
  });

  describe('#sendBadRequest', function () {
    let server;
    beforeEach(function () {
      server = new Server;
      sinon.stub(server, 'sendError');
    });

    it('should call sendError properly', function () {
      let reason = "Message redacted.";
      let res = {};
      server.sendBadRequest(res, reason);
      server.sendError.calledOnce.should.be.true;
      let args = server.sendError.lastCall.args;
      args.should.have.lengthOf(3);
      args[0].should.equal(res);
      args[1].should.equal(400);
      args[2].should.equal("Bad request: " + reason);
    });
  });

  describe('#sendResponse', function () {
    let res = {};
    let server;
    let body = "Merry Christmas from Chiron Beta Prime";

    before(function () {
    res.writeHead = sinon.spy();
    res.end = sinon.spy();
    });

    beforeEach(function () {
      server = new Server;
    });

    afterEach(function () {
      res.writeHead.resetHistory();
      res.end.resetHistory();
    });

    it('should send SVG content-type header', function () {
      server.sendResponse(res, 'svg', body);
      res.writeHead.calledOnce.should.be.true;
      let args = res.writeHead.lastCall.args;
      args.should.have.lengthOf(2);
      args[0].should.equal(200);
      args[1].should.be.an('object').and.have.a.property('Content-Type', 'image/svg+xml');
      args[1].should.have.a.property('content-length', body.length);
    });

    it('should send MathML content-type header', function () {
      server.sendResponse(res, 'mml', body);
      res.writeHead.calledOnce.should.be.true;
      let args = res.writeHead.lastCall.args;
      args.should.have.lengthOf(2);
      args[0].should.equal(200);
      args[1].should.be.an('object').and.have.a.property('Content-Type', 'application/mathml+xml');
      args[1].should.have.a.property('content-length', body.length);
    });

    it('should call end properly', function () {
      server.sendResponse(res, 'svg', body);
      res.end.calledOnce.should.be.true;
      let args = res.end.lastCall.args;
      args.should.have.lengthOf(1);
      args[0].should.equal(body);
    });

    it('should account for unicode character sizes in content-length', function () {
      body = 'i look down in my red \uD83D\uDCA9';
      const expectedHeaders = {
        'Content-Type': 'image/svg+xml',
        'content-length': 26
      }
      server.sendResponse(res, 'svg', body);
      res.writeHead.calledWith(200, expectedHeaders).should.be.true;
    })
  });

  describe('#sendTypesetResponse', function () {
    let server;
    let res = {};
    let type = 'svg';
    let tex = 'z_3 = z_{2}^{2} + c';
    let typesetData = {
      mml: "a day-glo Pterodactyl",
      svg: "a heart-shaped box of springs and wires"
    };

    beforeEach(function () {
      server = new Server;
      sinon.stub(server, 'sendBadRequest');
      sinon.stub(server, 'sendResponse');
      sinon.stub(server, 'ts');
      server.redisCli = {mset: sinon.stub()};
    });

    it('should send error on typeset failure', function () {
      let errors = [
        "She'll look the same except for bionic eyes.",
        "She lost the real ones in the robot wars."
      ];
      server.ts.callsArgWith(1, errors);
      server.sendTypesetResponse(res, type, tex);
      server.ts.calledOnce.should.be.true;
      let typesetArgs = server.ts.lastCall.args;
      typesetArgs.should.have.lengthOf(2);
      typesetArgs[0].should.equal(tex);
      typesetArgs[1].should.be.a('function');
      server.sendBadRequest.calledOnce.should.be.true;
      server.sendResponse.called.should.be.false;
      server.redisCli.mset.called.should.be.false;
      let sendBadRequestArgs = server.sendBadRequest.lastCall.args;
      sendBadRequestArgs.should.have.lengthOf(2);
      sendBadRequestArgs[0].should.be.equal(res);
      sendBadRequestArgs[1].should.equal(errors.join('\n'));
    });

    it('should send response on typeset success', function () {
      server.ts.callsArgWith(1, null, typesetData);
      server.sendTypesetResponse(res, type, tex);
      server.ts.calledOnce.should.be.true;
      let typesetArgs = server.ts.lastCall.args;
      typesetArgs.should.have.lengthOf(2);
      typesetArgs[0].should.equal(tex);
      typesetArgs[1].should.be.a('function');
      server.sendBadRequest.called.should.be.false;
      server.sendResponse.calledOnce.should.be.true;
      server.redisCli.mset.called.should.be.false;
      let sendResponseArgs = server.sendResponse.lastCall.args;
      sendResponseArgs.should.have.lengthOf(3);
      sendResponseArgs[0].should.be.equal(res);
      sendResponseArgs[1].should.equal(type);
      sendResponseArgs[2].should.equal(typesetData[type]);
    });

    it('should cache response on typeset success', function () {
      server.ts.callsArgWith(1, null, typesetData);
      server.useRedis = true;
      server.sendTypesetResponse(res, type, tex);
      server.ts.calledOnce.should.be.true;
      let typesetArgs = server.ts.lastCall.args;
      typesetArgs.should.have.lengthOf(2);
      typesetArgs[0].should.equal(tex);
      typesetArgs[1].should.be.a('function');
      server.sendBadRequest.called.should.be.false;
      server.sendResponse.calledOnce.should.be.true;
      server.redisCli.mset.calledOnce.should.be.true;
      let msetArgs = server.redisCli.mset.lastCall.args;
      msetArgs.should.have.lengthOf(4);
      msetArgs[0].should.equal('mml:' + tex);
      msetArgs[1].should.equal(typesetData['mml']);
      msetArgs[2].should.equal('svg:' + tex);
      msetArgs[3].should.equal(typesetData['svg']);
    });
  });

  describe('#sendCachedResponse', function () {
    let server;
    let res = {};
    let type = 'svg';
    let tex = 'z_3 = z_{2}^{2} + c';

    beforeEach(function () {
      server = new Server;
      sinon.stub(server, 'sendTypesetResponse');
      sinon.stub(server, 'sendResponse');
      server.redisCli = {get: sinon.stub()};
    });

    it('defers to sendTypesetResponse if redis is not available', function () {
      server.sendCachedResponse(res, type, tex);
      server.sendTypesetResponse.calledOnce.should.be.true;
      server.sendResponse.called.should.be.false;
      let args = server.sendTypesetResponse.lastCall.args;
      args.should.have.lengthOf(3);
      args[0].should.equal(res);
      args[1].should.equal(type);
      args[2].should.equal(tex);
    });

    it('defers to sendTypesetResponse on redis error', function () {
      server.useRedis = true;
      let err = "I'm not a monster Tom--well technically I am.";
      server.redisCli.get.callsArgWith(1, err);
      server.sendCachedResponse(res, type, tex);
      server.redisCli.get.calledOnce.should.be.true;
      let getArgs = server.redisCli.get.lastCall.args;
      getArgs.should.have.lengthOf(2);
      getArgs[0].should.equal(type + ':' + tex);
      server.sendTypesetResponse.calledOnce.should.be.true;
      server.sendResponse.called.should.be.false;
      let sendArgs = server.sendTypesetResponse.lastCall.args;
      sendArgs.should.have.lengthOf(3);
      sendArgs[0].should.equal(res);
      sendArgs[1].should.equal(type);
      sendArgs[2].should.equal(tex);
    });

    it('defers to sendTypesetResponse on empty redis reply', function () {
      server.useRedis = true;
      let reply = "";
      server.redisCli.get.callsArgWith(1, null, reply);
      server.sendCachedResponse(res, type, tex);
      server.redisCli.get.calledOnce.should.be.true;
      let getArgs = server.redisCli.get.lastCall.args;
      getArgs.should.have.lengthOf(2);
      getArgs[0].should.equal(type + ':' + tex);
      server.sendTypesetResponse.calledOnce.should.be.true;
      server.sendResponse.called.should.be.false;
      let sendArgs = server.sendTypesetResponse.lastCall.args;
      sendArgs.should.have.lengthOf(3);
      sendArgs[0].should.equal(res);
      sendArgs[1].should.equal(type);
      sendArgs[2].should.equal(tex);
    });

    it('defers to sendResponse on cache hit', function () {
      server.useRedis = true;
      let reply = "because it's loud with the shop vac on.";
      server.redisCli.get.callsArgWith(1, null, reply);
      server.sendCachedResponse(res, type, tex);
      server.redisCli.get.calledOnce.should.be.true;
      let getArgs = server.redisCli.get.lastCall.args;
      getArgs.should.have.lengthOf(2);
      getArgs[0].should.equal(type + ':' + tex);
      server.sendTypesetResponse.called.should.be.false;
      server.sendResponse.calledOnce.should.be.true;
      let sendArgs = server.sendResponse.lastCall.args;
      sendArgs.should.have.lengthOf(3);
      sendArgs[0].should.equal(res);
      sendArgs[1].should.equal(type);
      sendArgs[2].should.equal(reply);
    });
  });

  describe('#handleRequest', function () {
    let server;
    let res = {};
    let escapedTex = 'z%5f3%20%3d%20z%5f%7b2%7d%5e%7b2%7d%20%2b%20c';

    beforeEach(function () {
      server = new Server;
      sinon.stub(server, 'sendCachedResponse');
      sinon.stub(server, 'sendError');
      sinon.stub(server, 'sendBadRequest');
      sinon.stub(server, 'sendNotModified');
      sinon.spy(url, 'parse');
    });

    afterEach(function () {
      url.parse.restore();
    });

    it('should fail on non-get request type', function() {
      let invalidRequestTypes = ['', 'HEAD', 'POST', 'DELETE','z'];
      for (let requestType of invalidRequestTypes) {
        server.handleRequest({method: requestType}, res);
        server.sendError.calledOnce.should.be.true;
        let args = server.sendError.lastCall.args;
        args.should.have.lengthOf(3);
        args[0].should.equal(res);
        args[1].should.equal(405);
        args[2].should.equal("Method not allowed.");
        server.sendError.resetHistory();
      }
      let req = {
        url: `http://localhost/svg/?tex=${escapedTex}`,
        method: 'GET',
        headers: {}
      };
      server.handleRequest(req, res);
      server.sendError.calledOnce.should.be.false;
    });

    it('should fail on invalid type', function () {
      let invalidTypes = ['', 'mathml', 'svgs', 'something', ''];
      for (let type of invalidTypes) {
        server.handleRequest({method: 'GET', url: `https://localhost/${type}?tex=5`}, res);
        server.sendError.calledOnce.should.be.true;
        let args = server.sendError.lastCall.args;
        args.should.have.lengthOf(3);
        args[0].should.equal(res);
        args[1].should.equal(404);
        args[2].should.equal("Not Found");
        server.sendError.resetHistory();
      }
      let validTypes = ['svg', 'mml'];
      for (let type of validTypes) {
      let req = {
        url: `http://localhost/${type}?tex=${escapedTex}`,
        method: 'GET',
        headers: {}
      };
      server.handleRequest(req, res);
      console.dir(server.sendError.args);
      server.sendError.calledOnce.should.be.false;
      server.sendError.resetHistory();
      }
    });

    it('should send bad request on missing tex parameter', function () {
      let req = {
        url: `http://localhost/svg/?broken=${escapedTex}`,
        method: 'GET',
        headers: {}
      };
      server.handleRequest(req, res);
      server.sendBadRequest.calledOnce.should.be.true;
      let args = server.sendBadRequest.lastCall.args;
      args.should.have.lengthOf(2);
      args[0].should.equal(res);
      args[1].should.equal("no LaTeX provided.");
    });

    it('should send not modified header on if-modified-since', function () {
      let req = {
        url: `http://localhost/svg/?tex=${escapedTex}`,
        method: 'GET',
        headers: {'if-modified-since': 'whenever'}
      };
      server.handleRequest(req, res);
      server.sendNotModified.calledOnce.should.be.true;
      let args = server.sendNotModified.lastCall.args;
      args.should.have.lengthOf(1);
      args[0].should.equal(res);
    });

    it('should unescape the tex parameter', function () {
      let req = {
        url: `http://localhost/svg/?tex=${escapedTex}`,
        method: 'GET',
        headers: {}
      };
      server.handleRequest(req, res);
      server.sendCachedResponse.calledOnce.should.be.true;
      let args = server.sendCachedResponse.lastCall.args;
      args.should.have.lengthOf(3);
      args[0].should.equal(res);
      args[1].should.equal('svg');
      args[2].should.equal(decodeURIComponent(escapedTex));
    });
  });
});
