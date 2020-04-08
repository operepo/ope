'use strict';

let Server = require('./server');
let http = require('http');

let server = new Server(process.env.REDIS_PORT, process.env.REDIS_HOST);
http.createServer(server.handleRequest.bind(server)).listen(8000);

