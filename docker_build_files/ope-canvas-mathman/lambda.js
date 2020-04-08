'use strict';

let typeset = require('./typeset');

exports.handler = function(event, context, cb) {
  console.log('>>> exports.handler');
  console.log(event.tex);

  if (event.tex) {
    typeset(event.tex, cb);
  } else {
    cb("[BadRequest] Missing field `tex`");
  };
};
