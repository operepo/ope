'use strict';

let mj = require("mathjax-node");
mj.config({
  extensions: "TeX/color",
  MathJax: {
    extensions: ["Safe.js"]
  }
});
mj.start();

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

let mjCallback = function(scale, cb) {
  return function(data) {
    if (!data.errors) {
      let svg;
      if (data.svgNode) {
        ensureTextFill(data.svgNode);
        if (scale !== 1) {
          const w = data.svgNode.getAttribute("width").match(/([\d.]+)(.*)/)
          data.svgNode.setAttribute("width", `${w[1] * scale}${w[2]}`)
          const h = data.svgNode.getAttribute("height").match(/([\d.]+)(.*)/)
          data.svgNode.setAttribute("height", `${h[1] * scale}${h[2]}`)
        }
        svg = data.svgNode.outerHTML;
      }
      cb(null, {svg, mml: data.mml});
    } else {
      cb(data.errors);
    }
  }
};

// Public
let typeset = function(opts, cb) {
  opts = opts || {}
  const tex = opts.tex
  const scale = opts.scale || 1
  mj.typeset(typesetConfig(tex), mjCallback(scale, cb));
};

module.exports = typeset;
