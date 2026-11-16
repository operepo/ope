'use strict';

let typeset = require('./typeset')

exports.handler = function(event, context, cb) {
  console.log('>>> exports.handler')
  console.log(event.tex)
  console.log(event.scale)

  const tex = event.tex
  const scale = parseFloat(event.scale || 1)
  if ( tex && scale ) {
    typeset({tex, scale}, cb)
  } else {
    if ( !tex ) {
        cb("[BadRequest] Missing field `tex`")
    } else if ( !scale ) {
        cb("[BadRequest] invalid scale provided")
    }
  }
}
