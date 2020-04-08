'use strict';

let should = require('chai').should();
let sinon = require('sinon');
let mj = require("mathjax-node/lib/main.js");
let typeset = require('../typeset');
const { JSDOM } = require('jsdom');

describe('typeset', function() {
  let ts;
  this.timeout(10000);

  before(function() {
    sinon.spy(mj, 'start');
    sinon.spy(mj, 'typeset');
  });

  after(function () {
    mj.start.restore();
    mj.typeset.restore();
  });

  afterEach(function() {
    mj.start.resetHistory();
    mj.typeset.resetHistory();
  });

  it('should call mj.typeset with the correct parameters', function(done) {
    this.timeout(10000);
    let sampleTex = "a = b + c";
    typeset(sampleTex, function(err) {
      if (err) {
        return done(err);
      }
      try {
        mj.typeset.calledOnce.should.be.true;
        let param = mj.typeset.lastCall.args[0];
        param.should.be.an('object');
        param.should.have.property('format', 'inline-TeX');
        param.should.have.property('svg', true);
        param.should.have.property('mml', true);
        param.should.have.property('speakText', false);
        param.should.have.property('ex', 6);
        param.should.have.property('width', 100);
        param.should.have.property('linebreaks', true);
        param.should.have.property('math', sampleTex);
      } catch (err) {
        return done(err);
      }
      done();
    });
  });

  it('should return data', function (done) {
    let sampleTex = "a = b + c";
    typeset(sampleTex, function(err, data) {
      try {
        should.not.exist(err);
        data.should.be.an('object');
        data.should.have.property('svg').which.is.a('string').and.is.not.empty;
        data.should.have.property('mml').which.is.a('string').and.is.not.empty;
      } catch (err) {
        return done(err);
      }
      done();
    });
  });

  it('replaces `\\slash` with `/`', function (done) {
    let sampleTex = "5 = 15 \\slash 3";
    typeset(sampleTex, function(err, data) {
      try {
        data.mml.should.not.match(/\\slash/);
      } catch (err) {
        return done(err);
      }
      done();
    });
  });

  it('should fail on bad input', function (done) {
    let sampleTex = "a = \fra{}}";
    typeset(sampleTex, function(err, data) {
      try {
        should.not.exist(data);
        err.should.be.an('array').and.not.empty;
      } catch (err) {
        return done(err);
      }
      done();
    });
  });

  it('should use LaTeX \color commands', function (done) {
    const sampleTex = "\\color\{Red\}hi";
    const sampleLaTeXOutput = "transform=\"translate";
    typeset(sampleTex, function(err, data) {
      try {
        data.should.have.property('svg').which.is.a('string').and.contains(sampleLaTeXOutput)
      } catch (err) {
        return done(err);
      }
      done();
    });
  })

  it('should not fail with color command at the end', function(done) {
    const sampleTex = "hi\\color\{Red\}"
    const sampleLaTeXOutput = "transform=\"translate";
    typeset(sampleTex, function(err, data) {
      try {
        data.should.have.property('svg').which.is.a('string').and.contains(sampleLaTeXOutput)
      } catch (err) {
        return done(err);
      }
      done();
    });
  });

  it('should have a fill for text nodes of unrecognized characters', done => {
    const sampleTex = '£ = a + b';
    typeset(sampleTex, function(err, data) {
      const dom = new JSDOM(data.svg);
      try {
        for (let elem of dom.window.document.getElementsByTagName('text')) {
          elem.hasAttribute('fill').should.equal(true);
          elem.getAttribute('fill').should.equal('currentColor');
        }
      } catch (err) {
        return done(err);
      }
      done();
    });
  })
});
