'use strict';

let mj = require("mathjax-node/lib/main.js");
mj.config({
  extensions: "TeX/color"
});


let typesetConfig = function(tex) {
  return {
    math: cleanTex(tex),
    format: "inline-TeX",
    svg: true,
    svgNode: true,
    mml: true,
    speakText: false,
    ex: 6,
    width: 100,
    linebreaks: true
  }
};

let cleanTex = function(tex) {
  return tex.replace(/\\slash/, '/')
};

function ensureTextFill(svg) {
  for (let text of svg.getElementsByTagName('text')) {
    if (!text.hasAttribute('fill')) {
      text.setAttribute('fill', 'currentColor');
    }
  }
}

let mjCallback = function(cb) {
  return function(data) {
    if (!data.errors) {
      let svg;
      if (data.svgNode) {
        ensureTextFill(data.svgNode);
        svg = data.svgNode.outerHTML;
      }
      cb(null, {svg, mml: data.mml});
    } else {
      cb(data.errors);
    }
  }
};

// Public
let typeset = function(tex, cb) {
  mj.typeset(typesetConfig(tex), mjCallback(cb));
};

module.exports = typeset;
