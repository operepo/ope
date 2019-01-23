/**
 * core-js 2.6.3
 * https://github.com/zloirock/core-js
 * License: http://rock.mit-license.org
 * © 2019 Denis Pushkarev
 */
!function(__e, __g, undefined){
'use strict';
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 129);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

var global = __webpack_require__(2);
var core = __webpack_require__(26);
var hide = __webpack_require__(11);
var redefine = __webpack_require__(12);
var ctx = __webpack_require__(18);
var PROTOTYPE = 'prototype';

var $export = function (type, name, source) {
  var IS_FORCED = type & $export.F;
  var IS_GLOBAL = type & $export.G;
  var IS_STATIC = type & $export.S;
  var IS_PROTO = type & $export.P;
  var IS_BIND = type & $export.B;
  var target = IS_GLOBAL ? global : IS_STATIC ? global[name] || (global[name] = {}) : (global[name] || {})[PROTOTYPE];
  var exports = IS_GLOBAL ? core : core[name] || (core[name] = {});
  var expProto = exports[PROTOTYPE] || (exports[PROTOTYPE] = {});
  var key, own, out, exp;
  if (IS_GLOBAL) source = name;
  for (key in source) {
    // contains in native
    own = !IS_FORCED && target && target[key] !== undefined;
    // export native or passed
    out = (own ? target : source)[key];
    // bind timers to global for call from export context
    exp = IS_BIND && own ? ctx(out, global) : IS_PROTO && typeof out == 'function' ? ctx(Function.call, out) : out;
    // extend global
    if (target) redefine(target, key, out, type & $export.U);
    // export
    if (exports[key] != out) hide(exports, key, exp);
    if (IS_PROTO && expProto[key] != out) expProto[key] = out;
  }
};
global.core = core;
// type bitmap
$export.F = 1;   // forced
$export.G = 2;   // global
$export.S = 4;   // static
$export.P = 8;   // proto
$export.B = 16;  // bind
$export.W = 32;  // wrap
$export.U = 64;  // safe
$export.R = 128; // real proto method for `library`
module.exports = $export;


/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

var isObject = __webpack_require__(4);
module.exports = function (it) {
  if (!isObject(it)) throw TypeError(it + ' is not an object!');
  return it;
};


/***/ }),
/* 2 */
/***/ (function(module, exports) {

// https://github.com/zloirock/core-js/issues/86#issuecomment-115759028
var global = module.exports = typeof window != 'undefined' && window.Math == Math
  ? window : typeof self != 'undefined' && self.Math == Math ? self
  // eslint-disable-next-line no-new-func
  : Function('return this')();
if (typeof __g == 'number') __g = global; // eslint-disable-line no-undef


/***/ }),
/* 3 */
/***/ (function(module, exports) {

module.exports = function (exec) {
  try {
    return !!exec();
  } catch (e) {
    return true;
  }
};


/***/ }),
/* 4 */
/***/ (function(module, exports) {

module.exports = function (it) {
  return typeof it === 'object' ? it !== null : typeof it === 'function';
};


/***/ }),
/* 5 */
/***/ (function(module, exports, __webpack_require__) {

var store = __webpack_require__(51)('wks');
var uid = __webpack_require__(33);
var Symbol = __webpack_require__(2).Symbol;
var USE_SYMBOL = typeof Symbol == 'function';

var $exports = module.exports = function (name) {
  return store[name] || (store[name] =
    USE_SYMBOL && Symbol[name] || (USE_SYMBOL ? Symbol : uid)('Symbol.' + name));
};

$exports.store = store;


/***/ }),
/* 6 */
/***/ (function(module, exports, __webpack_require__) {

// 7.1.15 ToLength
var toInteger = __webpack_require__(20);
var min = Math.min;
module.exports = function (it) {
  return it > 0 ? min(toInteger(it), 0x1fffffffffffff) : 0; // pow(2, 53) - 1 == 9007199254740991
};


/***/ }),
/* 7 */
/***/ (function(module, exports, __webpack_require__) {

// Thank's IE8 for his funny defineProperty
module.exports = !__webpack_require__(3)(function () {
  return Object.defineProperty({}, 'a', { get: function () { return 7; } }).a != 7;
});


/***/ }),
/* 8 */
/***/ (function(module, exports, __webpack_require__) {

var anObject = __webpack_require__(1);
var IE8_DOM_DEFINE = __webpack_require__(93);
var toPrimitive = __webpack_require__(22);
var dP = Object.defineProperty;

exports.f = __webpack_require__(7) ? Object.defineProperty : function defineProperty(O, P, Attributes) {
  anObject(O);
  P = toPrimitive(P, true);
  anObject(Attributes);
  if (IE8_DOM_DEFINE) try {
    return dP(O, P, Attributes);
  } catch (e) { /* empty */ }
  if ('get' in Attributes || 'set' in Attributes) throw TypeError('Accessors not supported!');
  if ('value' in Attributes) O[P] = Attributes.value;
  return O;
};


/***/ }),
/* 9 */
/***/ (function(module, exports, __webpack_require__) {

// 7.1.13 ToObject(argument)
var defined = __webpack_require__(23);
module.exports = function (it) {
  return Object(defined(it));
};


/***/ }),
/* 10 */
/***/ (function(module, exports) {

module.exports = function (it) {
  if (typeof it != 'function') throw TypeError(it + ' is not a function!');
  return it;
};


/***/ }),
/* 11 */
/***/ (function(module, exports, __webpack_require__) {

var dP = __webpack_require__(8);
var createDesc = __webpack_require__(32);
module.exports = __webpack_require__(7) ? function (object, key, value) {
  return dP.f(object, key, createDesc(1, value));
} : function (object, key, value) {
  object[key] = value;
  return object;
};


/***/ }),
/* 12 */
/***/ (function(module, exports, __webpack_require__) {

var global = __webpack_require__(2);
var hide = __webpack_require__(11);
var has = __webpack_require__(14);
var SRC = __webpack_require__(33)('src');
var TO_STRING = 'toString';
var $toString = Function[TO_STRING];
var TPL = ('' + $toString).split(TO_STRING);

__webpack_require__(26).inspectSource = function (it) {
  return $toString.call(it);
};

(module.exports = function (O, key, val, safe) {
  var isFunction = typeof val == 'function';
  if (isFunction) has(val, 'name') || hide(val, 'name', key);
  if (O[key] === val) return;
  if (isFunction) has(val, SRC) || hide(val, SRC, O[key] ? '' + O[key] : TPL.join(String(key)));
  if (O === global) {
    O[key] = val;
  } else if (!safe) {
    delete O[key];
    hide(O, key, val);
  } else if (O[key]) {
    O[key] = val;
  } else {
    hide(O, key, val);
  }
// add fake Function#toString for correct work wrapped methods / constructors with methods like LoDash isNative
})(Function.prototype, TO_STRING, function toString() {
  return typeof this == 'function' && this[SRC] || $toString.call(this);
});


/***/ }),
/* 13 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var fails = __webpack_require__(3);
var defined = __webpack_require__(23);
var quot = /"/g;
// B.2.3.2.1 CreateHTML(string, tag, attribute, value)
var createHTML = function (string, tag, attribute, value) {
  var S = String(defined(string));
  var p1 = '<' + tag;
  if (attribute !== '') p1 += ' ' + attribute + '="' + String(value).replace(quot, '&quot;') + '"';
  return p1 + '>' + S + '</' + tag + '>';
};
module.exports = function (NAME, exec) {
  var O = {};
  O[NAME] = exec(createHTML);
  $export($export.P + $export.F * fails(function () {
    var test = ''[NAME]('"');
    return test !== test.toLowerCase() || test.split('"').length > 3;
  }), 'String', O);
};


/***/ }),
/* 14 */
/***/ (function(module, exports) {

var hasOwnProperty = {}.hasOwnProperty;
module.exports = function (it, key) {
  return hasOwnProperty.call(it, key);
};


/***/ }),
/* 15 */
/***/ (function(module, exports, __webpack_require__) {

// to indexed object, toObject with fallback for non-array-like ES3 strings
var IObject = __webpack_require__(47);
var defined = __webpack_require__(23);
module.exports = function (it) {
  return IObject(defined(it));
};


/***/ }),
/* 16 */
/***/ (function(module, exports, __webpack_require__) {

var pIE = __webpack_require__(48);
var createDesc = __webpack_require__(32);
var toIObject = __webpack_require__(15);
var toPrimitive = __webpack_require__(22);
var has = __webpack_require__(14);
var IE8_DOM_DEFINE = __webpack_require__(93);
var gOPD = Object.getOwnPropertyDescriptor;

exports.f = __webpack_require__(7) ? gOPD : function getOwnPropertyDescriptor(O, P) {
  O = toIObject(O);
  P = toPrimitive(P, true);
  if (IE8_DOM_DEFINE) try {
    return gOPD(O, P);
  } catch (e) { /* empty */ }
  if (has(O, P)) return createDesc(!pIE.f.call(O, P), O[P]);
};


/***/ }),
/* 17 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.9 / 15.2.3.2 Object.getPrototypeOf(O)
var has = __webpack_require__(14);
var toObject = __webpack_require__(9);
var IE_PROTO = __webpack_require__(68)('IE_PROTO');
var ObjectProto = Object.prototype;

module.exports = Object.getPrototypeOf || function (O) {
  O = toObject(O);
  if (has(O, IE_PROTO)) return O[IE_PROTO];
  if (typeof O.constructor == 'function' && O instanceof O.constructor) {
    return O.constructor.prototype;
  } return O instanceof Object ? ObjectProto : null;
};


/***/ }),
/* 18 */
/***/ (function(module, exports, __webpack_require__) {

// optional / simple context binding
var aFunction = __webpack_require__(10);
module.exports = function (fn, that, length) {
  aFunction(fn);
  if (that === undefined) return fn;
  switch (length) {
    case 1: return function (a) {
      return fn.call(that, a);
    };
    case 2: return function (a, b) {
      return fn.call(that, a, b);
    };
    case 3: return function (a, b, c) {
      return fn.call(that, a, b, c);
    };
  }
  return function (/* ...args */) {
    return fn.apply(that, arguments);
  };
};


/***/ }),
/* 19 */
/***/ (function(module, exports) {

var toString = {}.toString;

module.exports = function (it) {
  return toString.call(it).slice(8, -1);
};


/***/ }),
/* 20 */
/***/ (function(module, exports) {

// 7.1.4 ToInteger
var ceil = Math.ceil;
var floor = Math.floor;
module.exports = function (it) {
  return isNaN(it = +it) ? 0 : (it > 0 ? floor : ceil)(it);
};


/***/ }),
/* 21 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var fails = __webpack_require__(3);

module.exports = function (method, arg) {
  return !!method && fails(function () {
    // eslint-disable-next-line no-useless-call
    arg ? method.call(null, function () { /* empty */ }, 1) : method.call(null);
  });
};


/***/ }),
/* 22 */
/***/ (function(module, exports, __webpack_require__) {

// 7.1.1 ToPrimitive(input [, PreferredType])
var isObject = __webpack_require__(4);
// instead of the ES6 spec version, we didn't implement @@toPrimitive case
// and the second argument - flag - preferred type is a string
module.exports = function (it, S) {
  if (!isObject(it)) return it;
  var fn, val;
  if (S && typeof (fn = it.toString) == 'function' && !isObject(val = fn.call(it))) return val;
  if (typeof (fn = it.valueOf) == 'function' && !isObject(val = fn.call(it))) return val;
  if (!S && typeof (fn = it.toString) == 'function' && !isObject(val = fn.call(it))) return val;
  throw TypeError("Can't convert object to primitive value");
};


/***/ }),
/* 23 */
/***/ (function(module, exports) {

// 7.2.1 RequireObjectCoercible(argument)
module.exports = function (it) {
  if (it == undefined) throw TypeError("Can't call method on  " + it);
  return it;
};


/***/ }),
/* 24 */
/***/ (function(module, exports, __webpack_require__) {

// most Object methods by ES6 should accept primitives
var $export = __webpack_require__(0);
var core = __webpack_require__(26);
var fails = __webpack_require__(3);
module.exports = function (KEY, exec) {
  var fn = (core.Object || {})[KEY] || Object[KEY];
  var exp = {};
  exp[KEY] = exec(fn);
  $export($export.S + $export.F * fails(function () { fn(1); }), 'Object', exp);
};


/***/ }),
/* 25 */
/***/ (function(module, exports, __webpack_require__) {

// 0 -> Array#forEach
// 1 -> Array#map
// 2 -> Array#filter
// 3 -> Array#some
// 4 -> Array#every
// 5 -> Array#find
// 6 -> Array#findIndex
var ctx = __webpack_require__(18);
var IObject = __webpack_require__(47);
var toObject = __webpack_require__(9);
var toLength = __webpack_require__(6);
var asc = __webpack_require__(84);
module.exports = function (TYPE, $create) {
  var IS_MAP = TYPE == 1;
  var IS_FILTER = TYPE == 2;
  var IS_SOME = TYPE == 3;
  var IS_EVERY = TYPE == 4;
  var IS_FIND_INDEX = TYPE == 6;
  var NO_HOLES = TYPE == 5 || IS_FIND_INDEX;
  var create = $create || asc;
  return function ($this, callbackfn, that) {
    var O = toObject($this);
    var self = IObject(O);
    var f = ctx(callbackfn, that, 3);
    var length = toLength(self.length);
    var index = 0;
    var result = IS_MAP ? create($this, length) : IS_FILTER ? create($this, 0) : undefined;
    var val, res;
    for (;length > index; index++) if (NO_HOLES || index in self) {
      val = self[index];
      res = f(val, index, O);
      if (TYPE) {
        if (IS_MAP) result[index] = res;   // map
        else if (res) switch (TYPE) {
          case 3: return true;             // some
          case 5: return val;              // find
          case 6: return index;            // findIndex
          case 2: result.push(val);        // filter
        } else if (IS_EVERY) return false; // every
      }
    }
    return IS_FIND_INDEX ? -1 : IS_SOME || IS_EVERY ? IS_EVERY : result;
  };
};


/***/ }),
/* 26 */
/***/ (function(module, exports) {

var core = module.exports = { version: '2.6.3' };
if (typeof __e == 'number') __e = core; // eslint-disable-line no-undef


/***/ }),
/* 27 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

if (__webpack_require__(7)) {
  var LIBRARY = __webpack_require__(30);
  var global = __webpack_require__(2);
  var fails = __webpack_require__(3);
  var $export = __webpack_require__(0);
  var $typed = __webpack_require__(62);
  var $buffer = __webpack_require__(92);
  var ctx = __webpack_require__(18);
  var anInstance = __webpack_require__(39);
  var propertyDesc = __webpack_require__(32);
  var hide = __webpack_require__(11);
  var redefineAll = __webpack_require__(41);
  var toInteger = __webpack_require__(20);
  var toLength = __webpack_require__(6);
  var toIndex = __webpack_require__(122);
  var toAbsoluteIndex = __webpack_require__(35);
  var toPrimitive = __webpack_require__(22);
  var has = __webpack_require__(14);
  var classof = __webpack_require__(43);
  var isObject = __webpack_require__(4);
  var toObject = __webpack_require__(9);
  var isArrayIter = __webpack_require__(81);
  var create = __webpack_require__(36);
  var getPrototypeOf = __webpack_require__(17);
  var gOPN = __webpack_require__(37).f;
  var getIterFn = __webpack_require__(83);
  var uid = __webpack_require__(33);
  var wks = __webpack_require__(5);
  var createArrayMethod = __webpack_require__(25);
  var createArrayIncludes = __webpack_require__(52);
  var speciesConstructor = __webpack_require__(50);
  var ArrayIterators = __webpack_require__(86);
  var Iterators = __webpack_require__(45);
  var $iterDetect = __webpack_require__(57);
  var setSpecies = __webpack_require__(38);
  var arrayFill = __webpack_require__(85);
  var arrayCopyWithin = __webpack_require__(110);
  var $DP = __webpack_require__(8);
  var $GOPD = __webpack_require__(16);
  var dP = $DP.f;
  var gOPD = $GOPD.f;
  var RangeError = global.RangeError;
  var TypeError = global.TypeError;
  var Uint8Array = global.Uint8Array;
  var ARRAY_BUFFER = 'ArrayBuffer';
  var SHARED_BUFFER = 'Shared' + ARRAY_BUFFER;
  var BYTES_PER_ELEMENT = 'BYTES_PER_ELEMENT';
  var PROTOTYPE = 'prototype';
  var ArrayProto = Array[PROTOTYPE];
  var $ArrayBuffer = $buffer.ArrayBuffer;
  var $DataView = $buffer.DataView;
  var arrayForEach = createArrayMethod(0);
  var arrayFilter = createArrayMethod(2);
  var arraySome = createArrayMethod(3);
  var arrayEvery = createArrayMethod(4);
  var arrayFind = createArrayMethod(5);
  var arrayFindIndex = createArrayMethod(6);
  var arrayIncludes = createArrayIncludes(true);
  var arrayIndexOf = createArrayIncludes(false);
  var arrayValues = ArrayIterators.values;
  var arrayKeys = ArrayIterators.keys;
  var arrayEntries = ArrayIterators.entries;
  var arrayLastIndexOf = ArrayProto.lastIndexOf;
  var arrayReduce = ArrayProto.reduce;
  var arrayReduceRight = ArrayProto.reduceRight;
  var arrayJoin = ArrayProto.join;
  var arraySort = ArrayProto.sort;
  var arraySlice = ArrayProto.slice;
  var arrayToString = ArrayProto.toString;
  var arrayToLocaleString = ArrayProto.toLocaleString;
  var ITERATOR = wks('iterator');
  var TAG = wks('toStringTag');
  var TYPED_CONSTRUCTOR = uid('typed_constructor');
  var DEF_CONSTRUCTOR = uid('def_constructor');
  var ALL_CONSTRUCTORS = $typed.CONSTR;
  var TYPED_ARRAY = $typed.TYPED;
  var VIEW = $typed.VIEW;
  var WRONG_LENGTH = 'Wrong length!';

  var $map = createArrayMethod(1, function (O, length) {
    return allocate(speciesConstructor(O, O[DEF_CONSTRUCTOR]), length);
  });

  var LITTLE_ENDIAN = fails(function () {
    // eslint-disable-next-line no-undef
    return new Uint8Array(new Uint16Array([1]).buffer)[0] === 1;
  });

  var FORCED_SET = !!Uint8Array && !!Uint8Array[PROTOTYPE].set && fails(function () {
    new Uint8Array(1).set({});
  });

  var toOffset = function (it, BYTES) {
    var offset = toInteger(it);
    if (offset < 0 || offset % BYTES) throw RangeError('Wrong offset!');
    return offset;
  };

  var validate = function (it) {
    if (isObject(it) && TYPED_ARRAY in it) return it;
    throw TypeError(it + ' is not a typed array!');
  };

  var allocate = function (C, length) {
    if (!(isObject(C) && TYPED_CONSTRUCTOR in C)) {
      throw TypeError('It is not a typed array constructor!');
    } return new C(length);
  };

  var speciesFromList = function (O, list) {
    return fromList(speciesConstructor(O, O[DEF_CONSTRUCTOR]), list);
  };

  var fromList = function (C, list) {
    var index = 0;
    var length = list.length;
    var result = allocate(C, length);
    while (length > index) result[index] = list[index++];
    return result;
  };

  var addGetter = function (it, key, internal) {
    dP(it, key, { get: function () { return this._d[internal]; } });
  };

  var $from = function from(source /* , mapfn, thisArg */) {
    var O = toObject(source);
    var aLen = arguments.length;
    var mapfn = aLen > 1 ? arguments[1] : undefined;
    var mapping = mapfn !== undefined;
    var iterFn = getIterFn(O);
    var i, length, values, result, step, iterator;
    if (iterFn != undefined && !isArrayIter(iterFn)) {
      for (iterator = iterFn.call(O), values = [], i = 0; !(step = iterator.next()).done; i++) {
        values.push(step.value);
      } O = values;
    }
    if (mapping && aLen > 2) mapfn = ctx(mapfn, arguments[2], 2);
    for (i = 0, length = toLength(O.length), result = allocate(this, length); length > i; i++) {
      result[i] = mapping ? mapfn(O[i], i) : O[i];
    }
    return result;
  };

  var $of = function of(/* ...items */) {
    var index = 0;
    var length = arguments.length;
    var result = allocate(this, length);
    while (length > index) result[index] = arguments[index++];
    return result;
  };

  // iOS Safari 6.x fails here
  var TO_LOCALE_BUG = !!Uint8Array && fails(function () { arrayToLocaleString.call(new Uint8Array(1)); });

  var $toLocaleString = function toLocaleString() {
    return arrayToLocaleString.apply(TO_LOCALE_BUG ? arraySlice.call(validate(this)) : validate(this), arguments);
  };

  var proto = {
    copyWithin: function copyWithin(target, start /* , end */) {
      return arrayCopyWithin.call(validate(this), target, start, arguments.length > 2 ? arguments[2] : undefined);
    },
    every: function every(callbackfn /* , thisArg */) {
      return arrayEvery(validate(this), callbackfn, arguments.length > 1 ? arguments[1] : undefined);
    },
    fill: function fill(value /* , start, end */) { // eslint-disable-line no-unused-vars
      return arrayFill.apply(validate(this), arguments);
    },
    filter: function filter(callbackfn /* , thisArg */) {
      return speciesFromList(this, arrayFilter(validate(this), callbackfn,
        arguments.length > 1 ? arguments[1] : undefined));
    },
    find: function find(predicate /* , thisArg */) {
      return arrayFind(validate(this), predicate, arguments.length > 1 ? arguments[1] : undefined);
    },
    findIndex: function findIndex(predicate /* , thisArg */) {
      return arrayFindIndex(validate(this), predicate, arguments.length > 1 ? arguments[1] : undefined);
    },
    forEach: function forEach(callbackfn /* , thisArg */) {
      arrayForEach(validate(this), callbackfn, arguments.length > 1 ? arguments[1] : undefined);
    },
    indexOf: function indexOf(searchElement /* , fromIndex */) {
      return arrayIndexOf(validate(this), searchElement, arguments.length > 1 ? arguments[1] : undefined);
    },
    includes: function includes(searchElement /* , fromIndex */) {
      return arrayIncludes(validate(this), searchElement, arguments.length > 1 ? arguments[1] : undefined);
    },
    join: function join(separator) { // eslint-disable-line no-unused-vars
      return arrayJoin.apply(validate(this), arguments);
    },
    lastIndexOf: function lastIndexOf(searchElement /* , fromIndex */) { // eslint-disable-line no-unused-vars
      return arrayLastIndexOf.apply(validate(this), arguments);
    },
    map: function map(mapfn /* , thisArg */) {
      return $map(validate(this), mapfn, arguments.length > 1 ? arguments[1] : undefined);
    },
    reduce: function reduce(callbackfn /* , initialValue */) { // eslint-disable-line no-unused-vars
      return arrayReduce.apply(validate(this), arguments);
    },
    reduceRight: function reduceRight(callbackfn /* , initialValue */) { // eslint-disable-line no-unused-vars
      return arrayReduceRight.apply(validate(this), arguments);
    },
    reverse: function reverse() {
      var that = this;
      var length = validate(that).length;
      var middle = Math.floor(length / 2);
      var index = 0;
      var value;
      while (index < middle) {
        value = that[index];
        that[index++] = that[--length];
        that[length] = value;
      } return that;
    },
    some: function some(callbackfn /* , thisArg */) {
      return arraySome(validate(this), callbackfn, arguments.length > 1 ? arguments[1] : undefined);
    },
    sort: function sort(comparefn) {
      return arraySort.call(validate(this), comparefn);
    },
    subarray: function subarray(begin, end) {
      var O = validate(this);
      var length = O.length;
      var $begin = toAbsoluteIndex(begin, length);
      return new (speciesConstructor(O, O[DEF_CONSTRUCTOR]))(
        O.buffer,
        O.byteOffset + $begin * O.BYTES_PER_ELEMENT,
        toLength((end === undefined ? length : toAbsoluteIndex(end, length)) - $begin)
      );
    }
  };

  var $slice = function slice(start, end) {
    return speciesFromList(this, arraySlice.call(validate(this), start, end));
  };

  var $set = function set(arrayLike /* , offset */) {
    validate(this);
    var offset = toOffset(arguments[1], 1);
    var length = this.length;
    var src = toObject(arrayLike);
    var len = toLength(src.length);
    var index = 0;
    if (len + offset > length) throw RangeError(WRONG_LENGTH);
    while (index < len) this[offset + index] = src[index++];
  };

  var $iterators = {
    entries: function entries() {
      return arrayEntries.call(validate(this));
    },
    keys: function keys() {
      return arrayKeys.call(validate(this));
    },
    values: function values() {
      return arrayValues.call(validate(this));
    }
  };

  var isTAIndex = function (target, key) {
    return isObject(target)
      && target[TYPED_ARRAY]
      && typeof key != 'symbol'
      && key in target
      && String(+key) == String(key);
  };
  var $getDesc = function getOwnPropertyDescriptor(target, key) {
    return isTAIndex(target, key = toPrimitive(key, true))
      ? propertyDesc(2, target[key])
      : gOPD(target, key);
  };
  var $setDesc = function defineProperty(target, key, desc) {
    if (isTAIndex(target, key = toPrimitive(key, true))
      && isObject(desc)
      && has(desc, 'value')
      && !has(desc, 'get')
      && !has(desc, 'set')
      // TODO: add validation descriptor w/o calling accessors
      && !desc.configurable
      && (!has(desc, 'writable') || desc.writable)
      && (!has(desc, 'enumerable') || desc.enumerable)
    ) {
      target[key] = desc.value;
      return target;
    } return dP(target, key, desc);
  };

  if (!ALL_CONSTRUCTORS) {
    $GOPD.f = $getDesc;
    $DP.f = $setDesc;
  }

  $export($export.S + $export.F * !ALL_CONSTRUCTORS, 'Object', {
    getOwnPropertyDescriptor: $getDesc,
    defineProperty: $setDesc
  });

  if (fails(function () { arrayToString.call({}); })) {
    arrayToString = arrayToLocaleString = function toString() {
      return arrayJoin.call(this);
    };
  }

  var $TypedArrayPrototype$ = redefineAll({}, proto);
  redefineAll($TypedArrayPrototype$, $iterators);
  hide($TypedArrayPrototype$, ITERATOR, $iterators.values);
  redefineAll($TypedArrayPrototype$, {
    slice: $slice,
    set: $set,
    constructor: function () { /* noop */ },
    toString: arrayToString,
    toLocaleString: $toLocaleString
  });
  addGetter($TypedArrayPrototype$, 'buffer', 'b');
  addGetter($TypedArrayPrototype$, 'byteOffset', 'o');
  addGetter($TypedArrayPrototype$, 'byteLength', 'l');
  addGetter($TypedArrayPrototype$, 'length', 'e');
  dP($TypedArrayPrototype$, TAG, {
    get: function () { return this[TYPED_ARRAY]; }
  });

  // eslint-disable-next-line max-statements
  module.exports = function (KEY, BYTES, wrapper, CLAMPED) {
    CLAMPED = !!CLAMPED;
    var NAME = KEY + (CLAMPED ? 'Clamped' : '') + 'Array';
    var GETTER = 'get' + KEY;
    var SETTER = 'set' + KEY;
    var TypedArray = global[NAME];
    var Base = TypedArray || {};
    var TAC = TypedArray && getPrototypeOf(TypedArray);
    var FORCED = !TypedArray || !$typed.ABV;
    var O = {};
    var TypedArrayPrototype = TypedArray && TypedArray[PROTOTYPE];
    var getter = function (that, index) {
      var data = that._d;
      return data.v[GETTER](index * BYTES + data.o, LITTLE_ENDIAN);
    };
    var setter = function (that, index, value) {
      var data = that._d;
      if (CLAMPED) value = (value = Math.round(value)) < 0 ? 0 : value > 0xff ? 0xff : value & 0xff;
      data.v[SETTER](index * BYTES + data.o, value, LITTLE_ENDIAN);
    };
    var addElement = function (that, index) {
      dP(that, index, {
        get: function () {
          return getter(this, index);
        },
        set: function (value) {
          return setter(this, index, value);
        },
        enumerable: true
      });
    };
    if (FORCED) {
      TypedArray = wrapper(function (that, data, $offset, $length) {
        anInstance(that, TypedArray, NAME, '_d');
        var index = 0;
        var offset = 0;
        var buffer, byteLength, length, klass;
        if (!isObject(data)) {
          length = toIndex(data);
          byteLength = length * BYTES;
          buffer = new $ArrayBuffer(byteLength);
        } else if (data instanceof $ArrayBuffer || (klass = classof(data)) == ARRAY_BUFFER || klass == SHARED_BUFFER) {
          buffer = data;
          offset = toOffset($offset, BYTES);
          var $len = data.byteLength;
          if ($length === undefined) {
            if ($len % BYTES) throw RangeError(WRONG_LENGTH);
            byteLength = $len - offset;
            if (byteLength < 0) throw RangeError(WRONG_LENGTH);
          } else {
            byteLength = toLength($length) * BYTES;
            if (byteLength + offset > $len) throw RangeError(WRONG_LENGTH);
          }
          length = byteLength / BYTES;
        } else if (TYPED_ARRAY in data) {
          return fromList(TypedArray, data);
        } else {
          return $from.call(TypedArray, data);
        }
        hide(that, '_d', {
          b: buffer,
          o: offset,
          l: byteLength,
          e: length,
          v: new $DataView(buffer)
        });
        while (index < length) addElement(that, index++);
      });
      TypedArrayPrototype = TypedArray[PROTOTYPE] = create($TypedArrayPrototype$);
      hide(TypedArrayPrototype, 'constructor', TypedArray);
    } else if (!fails(function () {
      TypedArray(1);
    }) || !fails(function () {
      new TypedArray(-1); // eslint-disable-line no-new
    }) || !$iterDetect(function (iter) {
      new TypedArray(); // eslint-disable-line no-new
      new TypedArray(null); // eslint-disable-line no-new
      new TypedArray(1.5); // eslint-disable-line no-new
      new TypedArray(iter); // eslint-disable-line no-new
    }, true)) {
      TypedArray = wrapper(function (that, data, $offset, $length) {
        anInstance(that, TypedArray, NAME);
        var klass;
        // `ws` module bug, temporarily remove validation length for Uint8Array
        // https://github.com/websockets/ws/pull/645
        if (!isObject(data)) return new Base(toIndex(data));
        if (data instanceof $ArrayBuffer || (klass = classof(data)) == ARRAY_BUFFER || klass == SHARED_BUFFER) {
          return $length !== undefined
            ? new Base(data, toOffset($offset, BYTES), $length)
            : $offset !== undefined
              ? new Base(data, toOffset($offset, BYTES))
              : new Base(data);
        }
        if (TYPED_ARRAY in data) return fromList(TypedArray, data);
        return $from.call(TypedArray, data);
      });
      arrayForEach(TAC !== Function.prototype ? gOPN(Base).concat(gOPN(TAC)) : gOPN(Base), function (key) {
        if (!(key in TypedArray)) hide(TypedArray, key, Base[key]);
      });
      TypedArray[PROTOTYPE] = TypedArrayPrototype;
      if (!LIBRARY) TypedArrayPrototype.constructor = TypedArray;
    }
    var $nativeIterator = TypedArrayPrototype[ITERATOR];
    var CORRECT_ITER_NAME = !!$nativeIterator
      && ($nativeIterator.name == 'values' || $nativeIterator.name == undefined);
    var $iterator = $iterators.values;
    hide(TypedArray, TYPED_CONSTRUCTOR, true);
    hide(TypedArrayPrototype, TYPED_ARRAY, NAME);
    hide(TypedArrayPrototype, VIEW, true);
    hide(TypedArrayPrototype, DEF_CONSTRUCTOR, TypedArray);

    if (CLAMPED ? new TypedArray(1)[TAG] != NAME : !(TAG in TypedArrayPrototype)) {
      dP(TypedArrayPrototype, TAG, {
        get: function () { return NAME; }
      });
    }

    O[NAME] = TypedArray;

    $export($export.G + $export.W + $export.F * (TypedArray != Base), O);

    $export($export.S, NAME, {
      BYTES_PER_ELEMENT: BYTES
    });

    $export($export.S + $export.F * fails(function () { Base.of.call(TypedArray, 1); }), NAME, {
      from: $from,
      of: $of
    });

    if (!(BYTES_PER_ELEMENT in TypedArrayPrototype)) hide(TypedArrayPrototype, BYTES_PER_ELEMENT, BYTES);

    $export($export.P, NAME, proto);

    setSpecies(NAME);

    $export($export.P + $export.F * FORCED_SET, NAME, { set: $set });

    $export($export.P + $export.F * !CORRECT_ITER_NAME, NAME, $iterators);

    if (!LIBRARY && TypedArrayPrototype.toString != arrayToString) TypedArrayPrototype.toString = arrayToString;

    $export($export.P + $export.F * fails(function () {
      new TypedArray(1).slice();
    }), NAME, { slice: $slice });

    $export($export.P + $export.F * (fails(function () {
      return [1, 2].toLocaleString() != new TypedArray([1, 2]).toLocaleString();
    }) || !fails(function () {
      TypedArrayPrototype.toLocaleString.call([1, 2]);
    })), NAME, { toLocaleString: $toLocaleString });

    Iterators[NAME] = CORRECT_ITER_NAME ? $nativeIterator : $iterator;
    if (!LIBRARY && !CORRECT_ITER_NAME) hide(TypedArrayPrototype, ITERATOR, $iterator);
  };
} else module.exports = function () { /* empty */ };


/***/ }),
/* 28 */
/***/ (function(module, exports, __webpack_require__) {

var Map = __webpack_require__(116);
var $export = __webpack_require__(0);
var shared = __webpack_require__(51)('metadata');
var store = shared.store || (shared.store = new (__webpack_require__(119))());

var getOrCreateMetadataMap = function (target, targetKey, create) {
  var targetMetadata = store.get(target);
  if (!targetMetadata) {
    if (!create) return undefined;
    store.set(target, targetMetadata = new Map());
  }
  var keyMetadata = targetMetadata.get(targetKey);
  if (!keyMetadata) {
    if (!create) return undefined;
    targetMetadata.set(targetKey, keyMetadata = new Map());
  } return keyMetadata;
};
var ordinaryHasOwnMetadata = function (MetadataKey, O, P) {
  var metadataMap = getOrCreateMetadataMap(O, P, false);
  return metadataMap === undefined ? false : metadataMap.has(MetadataKey);
};
var ordinaryGetOwnMetadata = function (MetadataKey, O, P) {
  var metadataMap = getOrCreateMetadataMap(O, P, false);
  return metadataMap === undefined ? undefined : metadataMap.get(MetadataKey);
};
var ordinaryDefineOwnMetadata = function (MetadataKey, MetadataValue, O, P) {
  getOrCreateMetadataMap(O, P, true).set(MetadataKey, MetadataValue);
};
var ordinaryOwnMetadataKeys = function (target, targetKey) {
  var metadataMap = getOrCreateMetadataMap(target, targetKey, false);
  var keys = [];
  if (metadataMap) metadataMap.forEach(function (_, key) { keys.push(key); });
  return keys;
};
var toMetaKey = function (it) {
  return it === undefined || typeof it == 'symbol' ? it : String(it);
};
var exp = function (O) {
  $export($export.S, 'Reflect', O);
};

module.exports = {
  store: store,
  map: getOrCreateMetadataMap,
  has: ordinaryHasOwnMetadata,
  get: ordinaryGetOwnMetadata,
  set: ordinaryDefineOwnMetadata,
  keys: ordinaryOwnMetadataKeys,
  key: toMetaKey,
  exp: exp
};


/***/ }),
/* 29 */
/***/ (function(module, exports, __webpack_require__) {

var META = __webpack_require__(33)('meta');
var isObject = __webpack_require__(4);
var has = __webpack_require__(14);
var setDesc = __webpack_require__(8).f;
var id = 0;
var isExtensible = Object.isExtensible || function () {
  return true;
};
var FREEZE = !__webpack_require__(3)(function () {
  return isExtensible(Object.preventExtensions({}));
});
var setMeta = function (it) {
  setDesc(it, META, { value: {
    i: 'O' + ++id, // object ID
    w: {}          // weak collections IDs
  } });
};
var fastKey = function (it, create) {
  // return primitive with prefix
  if (!isObject(it)) return typeof it == 'symbol' ? it : (typeof it == 'string' ? 'S' : 'P') + it;
  if (!has(it, META)) {
    // can't set metadata to uncaught frozen object
    if (!isExtensible(it)) return 'F';
    // not necessary to add metadata
    if (!create) return 'E';
    // add missing metadata
    setMeta(it);
  // return object ID
  } return it[META].i;
};
var getWeak = function (it, create) {
  if (!has(it, META)) {
    // can't set metadata to uncaught frozen object
    if (!isExtensible(it)) return true;
    // not necessary to add metadata
    if (!create) return false;
    // add missing metadata
    setMeta(it);
  // return hash weak collections IDs
  } return it[META].w;
};
// add metadata on freeze-family methods calling
var onFreeze = function (it) {
  if (FREEZE && meta.NEED && isExtensible(it) && !has(it, META)) setMeta(it);
  return it;
};
var meta = module.exports = {
  KEY: META,
  NEED: false,
  fastKey: fastKey,
  getWeak: getWeak,
  onFreeze: onFreeze
};


/***/ }),
/* 30 */
/***/ (function(module, exports) {

module.exports = false;


/***/ }),
/* 31 */
/***/ (function(module, exports, __webpack_require__) {

// 22.1.3.31 Array.prototype[@@unscopables]
var UNSCOPABLES = __webpack_require__(5)('unscopables');
var ArrayProto = Array.prototype;
if (ArrayProto[UNSCOPABLES] == undefined) __webpack_require__(11)(ArrayProto, UNSCOPABLES, {});
module.exports = function (key) {
  ArrayProto[UNSCOPABLES][key] = true;
};


/***/ }),
/* 32 */
/***/ (function(module, exports) {

module.exports = function (bitmap, value) {
  return {
    enumerable: !(bitmap & 1),
    configurable: !(bitmap & 2),
    writable: !(bitmap & 4),
    value: value
  };
};


/***/ }),
/* 33 */
/***/ (function(module, exports) {

var id = 0;
var px = Math.random();
module.exports = function (key) {
  return 'Symbol('.concat(key === undefined ? '' : key, ')_', (++id + px).toString(36));
};


/***/ }),
/* 34 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.14 / 15.2.3.14 Object.keys(O)
var $keys = __webpack_require__(95);
var enumBugKeys = __webpack_require__(69);

module.exports = Object.keys || function keys(O) {
  return $keys(O, enumBugKeys);
};


/***/ }),
/* 35 */
/***/ (function(module, exports, __webpack_require__) {

var toInteger = __webpack_require__(20);
var max = Math.max;
var min = Math.min;
module.exports = function (index, length) {
  index = toInteger(index);
  return index < 0 ? max(index + length, 0) : min(index, length);
};


/***/ }),
/* 36 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.2 / 15.2.3.5 Object.create(O [, Properties])
var anObject = __webpack_require__(1);
var dPs = __webpack_require__(96);
var enumBugKeys = __webpack_require__(69);
var IE_PROTO = __webpack_require__(68)('IE_PROTO');
var Empty = function () { /* empty */ };
var PROTOTYPE = 'prototype';

// Create object with fake `null` prototype: use iframe Object with cleared prototype
var createDict = function () {
  // Thrash, waste and sodomy: IE GC bug
  var iframe = __webpack_require__(66)('iframe');
  var i = enumBugKeys.length;
  var lt = '<';
  var gt = '>';
  var iframeDocument;
  iframe.style.display = 'none';
  __webpack_require__(70).appendChild(iframe);
  iframe.src = 'javascript:'; // eslint-disable-line no-script-url
  // createDict = iframe.contentWindow.Object;
  // html.removeChild(iframe);
  iframeDocument = iframe.contentWindow.document;
  iframeDocument.open();
  iframeDocument.write(lt + 'script' + gt + 'document.F=Object' + lt + '/script' + gt);
  iframeDocument.close();
  createDict = iframeDocument.F;
  while (i--) delete createDict[PROTOTYPE][enumBugKeys[i]];
  return createDict();
};

module.exports = Object.create || function create(O, Properties) {
  var result;
  if (O !== null) {
    Empty[PROTOTYPE] = anObject(O);
    result = new Empty();
    Empty[PROTOTYPE] = null;
    // add "__proto__" for Object.getPrototypeOf polyfill
    result[IE_PROTO] = O;
  } else result = createDict();
  return Properties === undefined ? result : dPs(result, Properties);
};


/***/ }),
/* 37 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.7 / 15.2.3.4 Object.getOwnPropertyNames(O)
var $keys = __webpack_require__(95);
var hiddenKeys = __webpack_require__(69).concat('length', 'prototype');

exports.f = Object.getOwnPropertyNames || function getOwnPropertyNames(O) {
  return $keys(O, hiddenKeys);
};


/***/ }),
/* 38 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var global = __webpack_require__(2);
var dP = __webpack_require__(8);
var DESCRIPTORS = __webpack_require__(7);
var SPECIES = __webpack_require__(5)('species');

module.exports = function (KEY) {
  var C = global[KEY];
  if (DESCRIPTORS && C && !C[SPECIES]) dP.f(C, SPECIES, {
    configurable: true,
    get: function () { return this; }
  });
};


/***/ }),
/* 39 */
/***/ (function(module, exports) {

module.exports = function (it, Constructor, name, forbiddenField) {
  if (!(it instanceof Constructor) || (forbiddenField !== undefined && forbiddenField in it)) {
    throw TypeError(name + ': incorrect invocation!');
  } return it;
};


/***/ }),
/* 40 */
/***/ (function(module, exports, __webpack_require__) {

var ctx = __webpack_require__(18);
var call = __webpack_require__(108);
var isArrayIter = __webpack_require__(81);
var anObject = __webpack_require__(1);
var toLength = __webpack_require__(6);
var getIterFn = __webpack_require__(83);
var BREAK = {};
var RETURN = {};
var exports = module.exports = function (iterable, entries, fn, that, ITERATOR) {
  var iterFn = ITERATOR ? function () { return iterable; } : getIterFn(iterable);
  var f = ctx(fn, that, entries ? 2 : 1);
  var index = 0;
  var length, step, iterator, result;
  if (typeof iterFn != 'function') throw TypeError(iterable + ' is not iterable!');
  // fast case for arrays with default iterator
  if (isArrayIter(iterFn)) for (length = toLength(iterable.length); length > index; index++) {
    result = entries ? f(anObject(step = iterable[index])[0], step[1]) : f(iterable[index]);
    if (result === BREAK || result === RETURN) return result;
  } else for (iterator = iterFn.call(iterable); !(step = iterator.next()).done;) {
    result = call(iterator, f, step.value, entries);
    if (result === BREAK || result === RETURN) return result;
  }
};
exports.BREAK = BREAK;
exports.RETURN = RETURN;


/***/ }),
/* 41 */
/***/ (function(module, exports, __webpack_require__) {

var redefine = __webpack_require__(12);
module.exports = function (target, src, safe) {
  for (var key in src) redefine(target, key, src[key], safe);
  return target;
};


/***/ }),
/* 42 */
/***/ (function(module, exports, __webpack_require__) {

var def = __webpack_require__(8).f;
var has = __webpack_require__(14);
var TAG = __webpack_require__(5)('toStringTag');

module.exports = function (it, tag, stat) {
  if (it && !has(it = stat ? it : it.prototype, TAG)) def(it, TAG, { configurable: true, value: tag });
};


/***/ }),
/* 43 */
/***/ (function(module, exports, __webpack_require__) {

// getting tag from 19.1.3.6 Object.prototype.toString()
var cof = __webpack_require__(19);
var TAG = __webpack_require__(5)('toStringTag');
// ES3 wrong here
var ARG = cof(function () { return arguments; }()) == 'Arguments';

// fallback for IE11 Script Access Denied error
var tryGet = function (it, key) {
  try {
    return it[key];
  } catch (e) { /* empty */ }
};

module.exports = function (it) {
  var O, T, B;
  return it === undefined ? 'Undefined' : it === null ? 'Null'
    // @@toStringTag case
    : typeof (T = tryGet(O = Object(it), TAG)) == 'string' ? T
    // builtinTag case
    : ARG ? cof(O)
    // ES3 arguments fallback
    : (B = cof(O)) == 'Object' && typeof O.callee == 'function' ? 'Arguments' : B;
};


/***/ }),
/* 44 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var defined = __webpack_require__(23);
var fails = __webpack_require__(3);
var spaces = __webpack_require__(73);
var space = '[' + spaces + ']';
var non = '\u200b\u0085';
var ltrim = RegExp('^' + space + space + '*');
var rtrim = RegExp(space + space + '*$');

var exporter = function (KEY, exec, ALIAS) {
  var exp = {};
  var FORCE = fails(function () {
    return !!spaces[KEY]() || non[KEY]() != non;
  });
  var fn = exp[KEY] = FORCE ? exec(trim) : spaces[KEY];
  if (ALIAS) exp[ALIAS] = fn;
  $export($export.P + $export.F * FORCE, 'String', exp);
};

// 1 -> String#trimLeft
// 2 -> String#trimRight
// 3 -> String#trim
var trim = exporter.trim = function (string, TYPE) {
  string = String(defined(string));
  if (TYPE & 1) string = string.replace(ltrim, '');
  if (TYPE & 2) string = string.replace(rtrim, '');
  return string;
};

module.exports = exporter;


/***/ }),
/* 45 */
/***/ (function(module, exports) {

module.exports = {};


/***/ }),
/* 46 */
/***/ (function(module, exports, __webpack_require__) {

var isObject = __webpack_require__(4);
module.exports = function (it, TYPE) {
  if (!isObject(it) || it._t !== TYPE) throw TypeError('Incompatible receiver, ' + TYPE + ' required!');
  return it;
};


/***/ }),
/* 47 */
/***/ (function(module, exports, __webpack_require__) {

// fallback for non-array-like ES3 and non-enumerable old V8 strings
var cof = __webpack_require__(19);
// eslint-disable-next-line no-prototype-builtins
module.exports = Object('z').propertyIsEnumerable(0) ? Object : function (it) {
  return cof(it) == 'String' ? it.split('') : Object(it);
};


/***/ }),
/* 48 */
/***/ (function(module, exports) {

exports.f = {}.propertyIsEnumerable;


/***/ }),
/* 49 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 21.2.5.3 get RegExp.prototype.flags
var anObject = __webpack_require__(1);
module.exports = function () {
  var that = anObject(this);
  var result = '';
  if (that.global) result += 'g';
  if (that.ignoreCase) result += 'i';
  if (that.multiline) result += 'm';
  if (that.unicode) result += 'u';
  if (that.sticky) result += 'y';
  return result;
};


/***/ }),
/* 50 */
/***/ (function(module, exports, __webpack_require__) {

// 7.3.20 SpeciesConstructor(O, defaultConstructor)
var anObject = __webpack_require__(1);
var aFunction = __webpack_require__(10);
var SPECIES = __webpack_require__(5)('species');
module.exports = function (O, D) {
  var C = anObject(O).constructor;
  var S;
  return C === undefined || (S = anObject(C)[SPECIES]) == undefined ? D : aFunction(S);
};


/***/ }),
/* 51 */
/***/ (function(module, exports, __webpack_require__) {

var core = __webpack_require__(26);
var global = __webpack_require__(2);
var SHARED = '__core-js_shared__';
var store = global[SHARED] || (global[SHARED] = {});

(module.exports = function (key, value) {
  return store[key] || (store[key] = value !== undefined ? value : {});
})('versions', []).push({
  version: core.version,
  mode: __webpack_require__(30) ? 'pure' : 'global',
  copyright: '© 2019 Denis Pushkarev (zloirock.ru)'
});


/***/ }),
/* 52 */
/***/ (function(module, exports, __webpack_require__) {

// false -> Array#indexOf
// true  -> Array#includes
var toIObject = __webpack_require__(15);
var toLength = __webpack_require__(6);
var toAbsoluteIndex = __webpack_require__(35);
module.exports = function (IS_INCLUDES) {
  return function ($this, el, fromIndex) {
    var O = toIObject($this);
    var length = toLength(O.length);
    var index = toAbsoluteIndex(fromIndex, length);
    var value;
    // Array#includes uses SameValueZero equality algorithm
    // eslint-disable-next-line no-self-compare
    if (IS_INCLUDES && el != el) while (length > index) {
      value = O[index++];
      // eslint-disable-next-line no-self-compare
      if (value != value) return true;
    // Array#indexOf ignores holes, Array#includes - not
    } else for (;length > index; index++) if (IS_INCLUDES || index in O) {
      if (O[index] === el) return IS_INCLUDES || index || 0;
    } return !IS_INCLUDES && -1;
  };
};


/***/ }),
/* 53 */
/***/ (function(module, exports) {

exports.f = Object.getOwnPropertySymbols;


/***/ }),
/* 54 */
/***/ (function(module, exports, __webpack_require__) {

// 7.2.2 IsArray(argument)
var cof = __webpack_require__(19);
module.exports = Array.isArray || function isArray(arg) {
  return cof(arg) == 'Array';
};


/***/ }),
/* 55 */
/***/ (function(module, exports, __webpack_require__) {

var toInteger = __webpack_require__(20);
var defined = __webpack_require__(23);
// true  -> String#at
// false -> String#codePointAt
module.exports = function (TO_STRING) {
  return function (that, pos) {
    var s = String(defined(that));
    var i = toInteger(pos);
    var l = s.length;
    var a, b;
    if (i < 0 || i >= l) return TO_STRING ? '' : undefined;
    a = s.charCodeAt(i);
    return a < 0xd800 || a > 0xdbff || i + 1 === l || (b = s.charCodeAt(i + 1)) < 0xdc00 || b > 0xdfff
      ? TO_STRING ? s.charAt(i) : a
      : TO_STRING ? s.slice(i, i + 2) : (a - 0xd800 << 10) + (b - 0xdc00) + 0x10000;
  };
};


/***/ }),
/* 56 */
/***/ (function(module, exports, __webpack_require__) {

// 7.2.8 IsRegExp(argument)
var isObject = __webpack_require__(4);
var cof = __webpack_require__(19);
var MATCH = __webpack_require__(5)('match');
module.exports = function (it) {
  var isRegExp;
  return isObject(it) && ((isRegExp = it[MATCH]) !== undefined ? !!isRegExp : cof(it) == 'RegExp');
};


/***/ }),
/* 57 */
/***/ (function(module, exports, __webpack_require__) {

var ITERATOR = __webpack_require__(5)('iterator');
var SAFE_CLOSING = false;

try {
  var riter = [7][ITERATOR]();
  riter['return'] = function () { SAFE_CLOSING = true; };
  // eslint-disable-next-line no-throw-literal
  Array.from(riter, function () { throw 2; });
} catch (e) { /* empty */ }

module.exports = function (exec, skipClosing) {
  if (!skipClosing && !SAFE_CLOSING) return false;
  var safe = false;
  try {
    var arr = [7];
    var iter = arr[ITERATOR]();
    iter.next = function () { return { done: safe = true }; };
    arr[ITERATOR] = function () { return iter; };
    exec(arr);
  } catch (e) { /* empty */ }
  return safe;
};


/***/ }),
/* 58 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var classof = __webpack_require__(43);
var builtinExec = RegExp.prototype.exec;

 // `RegExpExec` abstract operation
// https://tc39.github.io/ecma262/#sec-regexpexec
module.exports = function (R, S) {
  var exec = R.exec;
  if (typeof exec === 'function') {
    var result = exec.call(R, S);
    if (typeof result !== 'object') {
      throw new TypeError('RegExp exec method returned something other than an Object or null');
    }
    return result;
  }
  if (classof(R) !== 'RegExp') {
    throw new TypeError('RegExp#exec called on incompatible receiver');
  }
  return builtinExec.call(R, S);
};


/***/ }),
/* 59 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

__webpack_require__(112);
var redefine = __webpack_require__(12);
var hide = __webpack_require__(11);
var fails = __webpack_require__(3);
var defined = __webpack_require__(23);
var wks = __webpack_require__(5);
var regexpExec = __webpack_require__(87);

var SPECIES = wks('species');

var REPLACE_SUPPORTS_NAMED_GROUPS = !fails(function () {
  // #replace needs built-in support for named groups.
  // #match works fine because it just return the exec results, even if it has
  // a "grops" property.
  var re = /./;
  re.exec = function () {
    var result = [];
    result.groups = { a: '7' };
    return result;
  };
  return ''.replace(re, '$<a>') !== '7';
});

var SPLIT_WORKS_WITH_OVERWRITTEN_EXEC = (function () {
  // Chrome 51 has a buggy "split" implementation when RegExp#exec !== nativeExec
  var re = /(?:)/;
  var originalExec = re.exec;
  re.exec = function () { return originalExec.apply(this, arguments); };
  var result = 'ab'.split(re);
  return result.length === 2 && result[0] === 'a' && result[1] === 'b';
})();

module.exports = function (KEY, length, exec) {
  var SYMBOL = wks(KEY);

  var DELEGATES_TO_SYMBOL = !fails(function () {
    // String methods call symbol-named RegEp methods
    var O = {};
    O[SYMBOL] = function () { return 7; };
    return ''[KEY](O) != 7;
  });

  var DELEGATES_TO_EXEC = DELEGATES_TO_SYMBOL ? !fails(function () {
    // Symbol-named RegExp methods call .exec
    var execCalled = false;
    var re = /a/;
    re.exec = function () { execCalled = true; return null; };
    if (KEY === 'split') {
      // RegExp[@@split] doesn't call the regex's exec method, but first creates
      // a new one. We need to return the patched regex when creating the new one.
      re.constructor = {};
      re.constructor[SPECIES] = function () { return re; };
    }
    re[SYMBOL]('');
    return !execCalled;
  }) : undefined;

  if (
    !DELEGATES_TO_SYMBOL ||
    !DELEGATES_TO_EXEC ||
    (KEY === 'replace' && !REPLACE_SUPPORTS_NAMED_GROUPS) ||
    (KEY === 'split' && !SPLIT_WORKS_WITH_OVERWRITTEN_EXEC)
  ) {
    var nativeRegExpMethod = /./[SYMBOL];
    var fns = exec(
      defined,
      SYMBOL,
      ''[KEY],
      function maybeCallNative(nativeMethod, regexp, str, arg2, forceStringMethod) {
        if (regexp.exec === regexpExec) {
          if (DELEGATES_TO_SYMBOL && !forceStringMethod) {
            // The native String method already delegates to @@method (this
            // polyfilled function), leasing to infinite recursion.
            // We avoid it by directly calling the native @@method method.
            return { done: true, value: nativeRegExpMethod.call(regexp, str, arg2) };
          }
          return { done: true, value: nativeMethod.call(str, regexp, arg2) };
        }
        return { done: false };
      }
    );
    var strfn = fns[0];
    var rxfn = fns[1];

    redefine(String.prototype, KEY, strfn);
    hide(RegExp.prototype, SYMBOL, length == 2
      // 21.2.5.8 RegExp.prototype[@@replace](string, replaceValue)
      // 21.2.5.11 RegExp.prototype[@@split](string, limit)
      ? function (string, arg) { return rxfn.call(string, this, arg); }
      // 21.2.5.6 RegExp.prototype[@@match](string)
      // 21.2.5.9 RegExp.prototype[@@search](string)
      : function (string) { return rxfn.call(string, this); }
    );
  }
};


/***/ }),
/* 60 */
/***/ (function(module, exports, __webpack_require__) {

var global = __webpack_require__(2);
var navigator = global.navigator;

module.exports = navigator && navigator.userAgent || '';


/***/ }),
/* 61 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var global = __webpack_require__(2);
var $export = __webpack_require__(0);
var redefine = __webpack_require__(12);
var redefineAll = __webpack_require__(41);
var meta = __webpack_require__(29);
var forOf = __webpack_require__(40);
var anInstance = __webpack_require__(39);
var isObject = __webpack_require__(4);
var fails = __webpack_require__(3);
var $iterDetect = __webpack_require__(57);
var setToStringTag = __webpack_require__(42);
var inheritIfRequired = __webpack_require__(72);

module.exports = function (NAME, wrapper, methods, common, IS_MAP, IS_WEAK) {
  var Base = global[NAME];
  var C = Base;
  var ADDER = IS_MAP ? 'set' : 'add';
  var proto = C && C.prototype;
  var O = {};
  var fixMethod = function (KEY) {
    var fn = proto[KEY];
    redefine(proto, KEY,
      KEY == 'delete' ? function (a) {
        return IS_WEAK && !isObject(a) ? false : fn.call(this, a === 0 ? 0 : a);
      } : KEY == 'has' ? function has(a) {
        return IS_WEAK && !isObject(a) ? false : fn.call(this, a === 0 ? 0 : a);
      } : KEY == 'get' ? function get(a) {
        return IS_WEAK && !isObject(a) ? undefined : fn.call(this, a === 0 ? 0 : a);
      } : KEY == 'add' ? function add(a) { fn.call(this, a === 0 ? 0 : a); return this; }
        : function set(a, b) { fn.call(this, a === 0 ? 0 : a, b); return this; }
    );
  };
  if (typeof C != 'function' || !(IS_WEAK || proto.forEach && !fails(function () {
    new C().entries().next();
  }))) {
    // create collection constructor
    C = common.getConstructor(wrapper, NAME, IS_MAP, ADDER);
    redefineAll(C.prototype, methods);
    meta.NEED = true;
  } else {
    var instance = new C();
    // early implementations not supports chaining
    var HASNT_CHAINING = instance[ADDER](IS_WEAK ? {} : -0, 1) != instance;
    // V8 ~  Chromium 40- weak-collections throws on primitives, but should return false
    var THROWS_ON_PRIMITIVES = fails(function () { instance.has(1); });
    // most early implementations doesn't supports iterables, most modern - not close it correctly
    var ACCEPT_ITERABLES = $iterDetect(function (iter) { new C(iter); }); // eslint-disable-line no-new
    // for early implementations -0 and +0 not the same
    var BUGGY_ZERO = !IS_WEAK && fails(function () {
      // V8 ~ Chromium 42- fails only with 5+ elements
      var $instance = new C();
      var index = 5;
      while (index--) $instance[ADDER](index, index);
      return !$instance.has(-0);
    });
    if (!ACCEPT_ITERABLES) {
      C = wrapper(function (target, iterable) {
        anInstance(target, C, NAME);
        var that = inheritIfRequired(new Base(), target, C);
        if (iterable != undefined) forOf(iterable, IS_MAP, that[ADDER], that);
        return that;
      });
      C.prototype = proto;
      proto.constructor = C;
    }
    if (THROWS_ON_PRIMITIVES || BUGGY_ZERO) {
      fixMethod('delete');
      fixMethod('has');
      IS_MAP && fixMethod('get');
    }
    if (BUGGY_ZERO || HASNT_CHAINING) fixMethod(ADDER);
    // weak collections should not contains .clear method
    if (IS_WEAK && proto.clear) delete proto.clear;
  }

  setToStringTag(C, NAME);

  O[NAME] = C;
  $export($export.G + $export.W + $export.F * (C != Base), O);

  if (!IS_WEAK) common.setStrong(C, NAME, IS_MAP);

  return C;
};


/***/ }),
/* 62 */
/***/ (function(module, exports, __webpack_require__) {

var global = __webpack_require__(2);
var hide = __webpack_require__(11);
var uid = __webpack_require__(33);
var TYPED = uid('typed_array');
var VIEW = uid('view');
var ABV = !!(global.ArrayBuffer && global.DataView);
var CONSTR = ABV;
var i = 0;
var l = 9;
var Typed;

var TypedArrayConstructors = (
  'Int8Array,Uint8Array,Uint8ClampedArray,Int16Array,Uint16Array,Int32Array,Uint32Array,Float32Array,Float64Array'
).split(',');

while (i < l) {
  if (Typed = global[TypedArrayConstructors[i++]]) {
    hide(Typed.prototype, TYPED, true);
    hide(Typed.prototype, VIEW, true);
  } else CONSTR = false;
}

module.exports = {
  ABV: ABV,
  CONSTR: CONSTR,
  TYPED: TYPED,
  VIEW: VIEW
};


/***/ }),
/* 63 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// Forced replacement prototype accessors methods
module.exports = __webpack_require__(30) || !__webpack_require__(3)(function () {
  var K = Math.random();
  // In FF throws only define methods
  // eslint-disable-next-line no-undef, no-useless-call
  __defineSetter__.call(null, K, function () { /* empty */ });
  delete __webpack_require__(2)[K];
});


/***/ }),
/* 64 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://tc39.github.io/proposal-setmap-offrom/
var $export = __webpack_require__(0);

module.exports = function (COLLECTION) {
  $export($export.S, COLLECTION, { of: function of() {
    var length = arguments.length;
    var A = new Array(length);
    while (length--) A[length] = arguments[length];
    return new this(A);
  } });
};


/***/ }),
/* 65 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://tc39.github.io/proposal-setmap-offrom/
var $export = __webpack_require__(0);
var aFunction = __webpack_require__(10);
var ctx = __webpack_require__(18);
var forOf = __webpack_require__(40);

module.exports = function (COLLECTION) {
  $export($export.S, COLLECTION, { from: function from(source /* , mapFn, thisArg */) {
    var mapFn = arguments[1];
    var mapping, A, n, cb;
    aFunction(this);
    mapping = mapFn !== undefined;
    if (mapping) aFunction(mapFn);
    if (source == undefined) return new this();
    A = [];
    if (mapping) {
      n = 0;
      cb = ctx(mapFn, arguments[2], 2);
      forOf(source, false, function (nextItem) {
        A.push(cb(nextItem, n++));
      });
    } else {
      forOf(source, false, A.push, A);
    }
    return new this(A);
  } });
};


/***/ }),
/* 66 */
/***/ (function(module, exports, __webpack_require__) {

var isObject = __webpack_require__(4);
var document = __webpack_require__(2).document;
// typeof document.createElement is 'object' in old IE
var is = isObject(document) && isObject(document.createElement);
module.exports = function (it) {
  return is ? document.createElement(it) : {};
};


/***/ }),
/* 67 */
/***/ (function(module, exports, __webpack_require__) {

var global = __webpack_require__(2);
var core = __webpack_require__(26);
var LIBRARY = __webpack_require__(30);
var wksExt = __webpack_require__(94);
var defineProperty = __webpack_require__(8).f;
module.exports = function (name) {
  var $Symbol = core.Symbol || (core.Symbol = LIBRARY ? {} : global.Symbol || {});
  if (name.charAt(0) != '_' && !(name in $Symbol)) defineProperty($Symbol, name, { value: wksExt.f(name) });
};


/***/ }),
/* 68 */
/***/ (function(module, exports, __webpack_require__) {

var shared = __webpack_require__(51)('keys');
var uid = __webpack_require__(33);
module.exports = function (key) {
  return shared[key] || (shared[key] = uid(key));
};


/***/ }),
/* 69 */
/***/ (function(module, exports) {

// IE 8- don't enum bug keys
module.exports = (
  'constructor,hasOwnProperty,isPrototypeOf,propertyIsEnumerable,toLocaleString,toString,valueOf'
).split(',');


/***/ }),
/* 70 */
/***/ (function(module, exports, __webpack_require__) {

var document = __webpack_require__(2).document;
module.exports = document && document.documentElement;


/***/ }),
/* 71 */
/***/ (function(module, exports, __webpack_require__) {

// Works with __proto__ only. Old v8 can't work with null proto objects.
/* eslint-disable no-proto */
var isObject = __webpack_require__(4);
var anObject = __webpack_require__(1);
var check = function (O, proto) {
  anObject(O);
  if (!isObject(proto) && proto !== null) throw TypeError(proto + ": can't set as prototype!");
};
module.exports = {
  set: Object.setPrototypeOf || ('__proto__' in {} ? // eslint-disable-line
    function (test, buggy, set) {
      try {
        set = __webpack_require__(18)(Function.call, __webpack_require__(16).f(Object.prototype, '__proto__').set, 2);
        set(test, []);
        buggy = !(test instanceof Array);
      } catch (e) { buggy = true; }
      return function setPrototypeOf(O, proto) {
        check(O, proto);
        if (buggy) O.__proto__ = proto;
        else set(O, proto);
        return O;
      };
    }({}, false) : undefined),
  check: check
};


/***/ }),
/* 72 */
/***/ (function(module, exports, __webpack_require__) {

var isObject = __webpack_require__(4);
var setPrototypeOf = __webpack_require__(71).set;
module.exports = function (that, target, C) {
  var S = target.constructor;
  var P;
  if (S !== C && typeof S == 'function' && (P = S.prototype) !== C.prototype && isObject(P) && setPrototypeOf) {
    setPrototypeOf(that, P);
  } return that;
};


/***/ }),
/* 73 */
/***/ (function(module, exports) {

module.exports = '\x09\x0A\x0B\x0C\x0D\x20\xA0\u1680\u180E\u2000\u2001\u2002\u2003' +
  '\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F\u3000\u2028\u2029\uFEFF';


/***/ }),
/* 74 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var toInteger = __webpack_require__(20);
var defined = __webpack_require__(23);

module.exports = function repeat(count) {
  var str = String(defined(this));
  var res = '';
  var n = toInteger(count);
  if (n < 0 || n == Infinity) throw RangeError("Count can't be negative");
  for (;n > 0; (n >>>= 1) && (str += str)) if (n & 1) res += str;
  return res;
};


/***/ }),
/* 75 */
/***/ (function(module, exports) {

// 20.2.2.28 Math.sign(x)
module.exports = Math.sign || function sign(x) {
  // eslint-disable-next-line no-self-compare
  return (x = +x) == 0 || x != x ? x : x < 0 ? -1 : 1;
};


/***/ }),
/* 76 */
/***/ (function(module, exports) {

// 20.2.2.14 Math.expm1(x)
var $expm1 = Math.expm1;
module.exports = (!$expm1
  // Old FF bug
  || $expm1(10) > 22025.465794806719 || $expm1(10) < 22025.4657948067165168
  // Tor Browser bug
  || $expm1(-2e-17) != -2e-17
) ? function expm1(x) {
  return (x = +x) == 0 ? x : x > -1e-6 && x < 1e-6 ? x + x * x / 2 : Math.exp(x) - 1;
} : $expm1;


/***/ }),
/* 77 */
/***/ (function(module, exports, __webpack_require__) {

// helper for String#{startsWith, endsWith, includes}
var isRegExp = __webpack_require__(56);
var defined = __webpack_require__(23);

module.exports = function (that, searchString, NAME) {
  if (isRegExp(searchString)) throw TypeError('String#' + NAME + " doesn't accept regex!");
  return String(defined(that));
};


/***/ }),
/* 78 */
/***/ (function(module, exports, __webpack_require__) {

var MATCH = __webpack_require__(5)('match');
module.exports = function (KEY) {
  var re = /./;
  try {
    '/./'[KEY](re);
  } catch (e) {
    try {
      re[MATCH] = false;
      return !'/./'[KEY](re);
    } catch (f) { /* empty */ }
  } return true;
};


/***/ }),
/* 79 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var LIBRARY = __webpack_require__(30);
var $export = __webpack_require__(0);
var redefine = __webpack_require__(12);
var hide = __webpack_require__(11);
var Iterators = __webpack_require__(45);
var $iterCreate = __webpack_require__(80);
var setToStringTag = __webpack_require__(42);
var getPrototypeOf = __webpack_require__(17);
var ITERATOR = __webpack_require__(5)('iterator');
var BUGGY = !([].keys && 'next' in [].keys()); // Safari has buggy iterators w/o `next`
var FF_ITERATOR = '@@iterator';
var KEYS = 'keys';
var VALUES = 'values';

var returnThis = function () { return this; };

module.exports = function (Base, NAME, Constructor, next, DEFAULT, IS_SET, FORCED) {
  $iterCreate(Constructor, NAME, next);
  var getMethod = function (kind) {
    if (!BUGGY && kind in proto) return proto[kind];
    switch (kind) {
      case KEYS: return function keys() { return new Constructor(this, kind); };
      case VALUES: return function values() { return new Constructor(this, kind); };
    } return function entries() { return new Constructor(this, kind); };
  };
  var TAG = NAME + ' Iterator';
  var DEF_VALUES = DEFAULT == VALUES;
  var VALUES_BUG = false;
  var proto = Base.prototype;
  var $native = proto[ITERATOR] || proto[FF_ITERATOR] || DEFAULT && proto[DEFAULT];
  var $default = $native || getMethod(DEFAULT);
  var $entries = DEFAULT ? !DEF_VALUES ? $default : getMethod('entries') : undefined;
  var $anyNative = NAME == 'Array' ? proto.entries || $native : $native;
  var methods, key, IteratorPrototype;
  // Fix native
  if ($anyNative) {
    IteratorPrototype = getPrototypeOf($anyNative.call(new Base()));
    if (IteratorPrototype !== Object.prototype && IteratorPrototype.next) {
      // Set @@toStringTag to native iterators
      setToStringTag(IteratorPrototype, TAG, true);
      // fix for some old engines
      if (!LIBRARY && typeof IteratorPrototype[ITERATOR] != 'function') hide(IteratorPrototype, ITERATOR, returnThis);
    }
  }
  // fix Array#{values, @@iterator}.name in V8 / FF
  if (DEF_VALUES && $native && $native.name !== VALUES) {
    VALUES_BUG = true;
    $default = function values() { return $native.call(this); };
  }
  // Define iterator
  if ((!LIBRARY || FORCED) && (BUGGY || VALUES_BUG || !proto[ITERATOR])) {
    hide(proto, ITERATOR, $default);
  }
  // Plug for library
  Iterators[NAME] = $default;
  Iterators[TAG] = returnThis;
  if (DEFAULT) {
    methods = {
      values: DEF_VALUES ? $default : getMethod(VALUES),
      keys: IS_SET ? $default : getMethod(KEYS),
      entries: $entries
    };
    if (FORCED) for (key in methods) {
      if (!(key in proto)) redefine(proto, key, methods[key]);
    } else $export($export.P + $export.F * (BUGGY || VALUES_BUG), NAME, methods);
  }
  return methods;
};


/***/ }),
/* 80 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var create = __webpack_require__(36);
var descriptor = __webpack_require__(32);
var setToStringTag = __webpack_require__(42);
var IteratorPrototype = {};

// 25.1.2.1.1 %IteratorPrototype%[@@iterator]()
__webpack_require__(11)(IteratorPrototype, __webpack_require__(5)('iterator'), function () { return this; });

module.exports = function (Constructor, NAME, next) {
  Constructor.prototype = create(IteratorPrototype, { next: descriptor(1, next) });
  setToStringTag(Constructor, NAME + ' Iterator');
};


/***/ }),
/* 81 */
/***/ (function(module, exports, __webpack_require__) {

// check on default Array iterator
var Iterators = __webpack_require__(45);
var ITERATOR = __webpack_require__(5)('iterator');
var ArrayProto = Array.prototype;

module.exports = function (it) {
  return it !== undefined && (Iterators.Array === it || ArrayProto[ITERATOR] === it);
};


/***/ }),
/* 82 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $defineProperty = __webpack_require__(8);
var createDesc = __webpack_require__(32);

module.exports = function (object, index, value) {
  if (index in object) $defineProperty.f(object, index, createDesc(0, value));
  else object[index] = value;
};


/***/ }),
/* 83 */
/***/ (function(module, exports, __webpack_require__) {

var classof = __webpack_require__(43);
var ITERATOR = __webpack_require__(5)('iterator');
var Iterators = __webpack_require__(45);
module.exports = __webpack_require__(26).getIteratorMethod = function (it) {
  if (it != undefined) return it[ITERATOR]
    || it['@@iterator']
    || Iterators[classof(it)];
};


/***/ }),
/* 84 */
/***/ (function(module, exports, __webpack_require__) {

// 9.4.2.3 ArraySpeciesCreate(originalArray, length)
var speciesConstructor = __webpack_require__(212);

module.exports = function (original, length) {
  return new (speciesConstructor(original))(length);
};


/***/ }),
/* 85 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// 22.1.3.6 Array.prototype.fill(value, start = 0, end = this.length)

var toObject = __webpack_require__(9);
var toAbsoluteIndex = __webpack_require__(35);
var toLength = __webpack_require__(6);
module.exports = function fill(value /* , start = 0, end = @length */) {
  var O = toObject(this);
  var length = toLength(O.length);
  var aLen = arguments.length;
  var index = toAbsoluteIndex(aLen > 1 ? arguments[1] : undefined, length);
  var end = aLen > 2 ? arguments[2] : undefined;
  var endPos = end === undefined ? length : toAbsoluteIndex(end, length);
  while (endPos > index) O[index++] = value;
  return O;
};


/***/ }),
/* 86 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var addToUnscopables = __webpack_require__(31);
var step = __webpack_require__(111);
var Iterators = __webpack_require__(45);
var toIObject = __webpack_require__(15);

// 22.1.3.4 Array.prototype.entries()
// 22.1.3.13 Array.prototype.keys()
// 22.1.3.29 Array.prototype.values()
// 22.1.3.30 Array.prototype[@@iterator]()
module.exports = __webpack_require__(79)(Array, 'Array', function (iterated, kind) {
  this._t = toIObject(iterated); // target
  this._i = 0;                   // next index
  this._k = kind;                // kind
// 22.1.5.2.1 %ArrayIteratorPrototype%.next()
}, function () {
  var O = this._t;
  var kind = this._k;
  var index = this._i++;
  if (!O || index >= O.length) {
    this._t = undefined;
    return step(1);
  }
  if (kind == 'keys') return step(0, index);
  if (kind == 'values') return step(0, O[index]);
  return step(0, [index, O[index]]);
}, 'values');

// argumentsList[@@iterator] is %ArrayProto_values% (9.4.4.6, 9.4.4.7)
Iterators.Arguments = Iterators.Array;

addToUnscopables('keys');
addToUnscopables('values');
addToUnscopables('entries');


/***/ }),
/* 87 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var regexpFlags = __webpack_require__(49);

var nativeExec = RegExp.prototype.exec;
// This always refers to the native implementation, because the
// String#replace polyfill uses ./fix-regexp-well-known-symbol-logic.js,
// which loads this file before patching the method.
var nativeReplace = String.prototype.replace;

var patchedExec = nativeExec;

var LAST_INDEX = 'lastIndex';

var UPDATES_LAST_INDEX_WRONG = (function () {
  var re1 = /a/,
      re2 = /b*/g;
  nativeExec.call(re1, 'a');
  nativeExec.call(re2, 'a');
  return re1[LAST_INDEX] !== 0 || re2[LAST_INDEX] !== 0;
})();

// nonparticipating capturing group, copied from es5-shim's String#split patch.
var NPCG_INCLUDED = /()??/.exec('')[1] !== undefined;

var PATCH = UPDATES_LAST_INDEX_WRONG || NPCG_INCLUDED;

if (PATCH) {
  patchedExec = function exec(str) {
    var re = this;
    var lastIndex, reCopy, match, i;

    if (NPCG_INCLUDED) {
      reCopy = new RegExp('^' + re.source + '$(?!\\s)', regexpFlags.call(re));
    }
    if (UPDATES_LAST_INDEX_WRONG) lastIndex = re[LAST_INDEX];

    match = nativeExec.call(re, str);

    if (UPDATES_LAST_INDEX_WRONG && match) {
      re[LAST_INDEX] = re.global ? match.index + match[0].length : lastIndex;
    }
    if (NPCG_INCLUDED && match && match.length > 1) {
      // Fix browsers whose `exec` methods don't consistently return `undefined`
      // for NPCG, like IE8. NOTE: This doesn' work for /(.?)?/
      // eslint-disable-next-line no-loop-func
      nativeReplace.call(match[0], reCopy, function () {
        for (i = 1; i < arguments.length - 2; i++) {
          if (arguments[i] === undefined) match[i] = undefined;
        }
      });
    }

    return match;
  };
}

module.exports = patchedExec;


/***/ }),
/* 88 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var at = __webpack_require__(55)(true);

 // `AdvanceStringIndex` abstract operation
// https://tc39.github.io/ecma262/#sec-advancestringindex
module.exports = function (S, index, unicode) {
  return index + (unicode ? at(S, index).length : 1);
};


/***/ }),
/* 89 */
/***/ (function(module, exports, __webpack_require__) {

var ctx = __webpack_require__(18);
var invoke = __webpack_require__(101);
var html = __webpack_require__(70);
var cel = __webpack_require__(66);
var global = __webpack_require__(2);
var process = global.process;
var setTask = global.setImmediate;
var clearTask = global.clearImmediate;
var MessageChannel = global.MessageChannel;
var Dispatch = global.Dispatch;
var counter = 0;
var queue = {};
var ONREADYSTATECHANGE = 'onreadystatechange';
var defer, channel, port;
var run = function () {
  var id = +this;
  // eslint-disable-next-line no-prototype-builtins
  if (queue.hasOwnProperty(id)) {
    var fn = queue[id];
    delete queue[id];
    fn();
  }
};
var listener = function (event) {
  run.call(event.data);
};
// Node.js 0.9+ & IE10+ has setImmediate, otherwise:
if (!setTask || !clearTask) {
  setTask = function setImmediate(fn) {
    var args = [];
    var i = 1;
    while (arguments.length > i) args.push(arguments[i++]);
    queue[++counter] = function () {
      // eslint-disable-next-line no-new-func
      invoke(typeof fn == 'function' ? fn : Function(fn), args);
    };
    defer(counter);
    return counter;
  };
  clearTask = function clearImmediate(id) {
    delete queue[id];
  };
  // Node.js 0.8-
  if (__webpack_require__(19)(process) == 'process') {
    defer = function (id) {
      process.nextTick(ctx(run, id, 1));
    };
  // Sphere (JS game engine) Dispatch API
  } else if (Dispatch && Dispatch.now) {
    defer = function (id) {
      Dispatch.now(ctx(run, id, 1));
    };
  // Browsers with MessageChannel, includes WebWorkers
  } else if (MessageChannel) {
    channel = new MessageChannel();
    port = channel.port2;
    channel.port1.onmessage = listener;
    defer = ctx(port.postMessage, port, 1);
  // Browsers with postMessage, skip WebWorkers
  // IE8 has postMessage, but it's sync & typeof its postMessage is 'object'
  } else if (global.addEventListener && typeof postMessage == 'function' && !global.importScripts) {
    defer = function (id) {
      global.postMessage(id + '', '*');
    };
    global.addEventListener('message', listener, false);
  // IE8-
  } else if (ONREADYSTATECHANGE in cel('script')) {
    defer = function (id) {
      html.appendChild(cel('script'))[ONREADYSTATECHANGE] = function () {
        html.removeChild(this);
        run.call(id);
      };
    };
  // Rest old browsers
  } else {
    defer = function (id) {
      setTimeout(ctx(run, id, 1), 0);
    };
  }
}
module.exports = {
  set: setTask,
  clear: clearTask
};


/***/ }),
/* 90 */
/***/ (function(module, exports, __webpack_require__) {

var global = __webpack_require__(2);
var macrotask = __webpack_require__(89).set;
var Observer = global.MutationObserver || global.WebKitMutationObserver;
var process = global.process;
var Promise = global.Promise;
var isNode = __webpack_require__(19)(process) == 'process';

module.exports = function () {
  var head, last, notify;

  var flush = function () {
    var parent, fn;
    if (isNode && (parent = process.domain)) parent.exit();
    while (head) {
      fn = head.fn;
      head = head.next;
      try {
        fn();
      } catch (e) {
        if (head) notify();
        else last = undefined;
        throw e;
      }
    } last = undefined;
    if (parent) parent.enter();
  };

  // Node.js
  if (isNode) {
    notify = function () {
      process.nextTick(flush);
    };
  // browsers with MutationObserver, except iOS Safari - https://github.com/zloirock/core-js/issues/339
  } else if (Observer && !(global.navigator && global.navigator.standalone)) {
    var toggle = true;
    var node = document.createTextNode('');
    new Observer(flush).observe(node, { characterData: true }); // eslint-disable-line no-new
    notify = function () {
      node.data = toggle = !toggle;
    };
  // environments with maybe non-completely correct, but existent Promise
  } else if (Promise && Promise.resolve) {
    // Promise.resolve without an argument throws an error in LG WebOS 2
    var promise = Promise.resolve(undefined);
    notify = function () {
      promise.then(flush);
    };
  // for other environments - macrotask based on:
  // - setImmediate
  // - MessageChannel
  // - window.postMessag
  // - onreadystatechange
  // - setTimeout
  } else {
    notify = function () {
      // strange IE + webpack dev server bug - use .call(global)
      macrotask.call(global, flush);
    };
  }

  return function (fn) {
    var task = { fn: fn, next: undefined };
    if (last) last.next = task;
    if (!head) {
      head = task;
      notify();
    } last = task;
  };
};


/***/ }),
/* 91 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 25.4.1.5 NewPromiseCapability(C)
var aFunction = __webpack_require__(10);

function PromiseCapability(C) {
  var resolve, reject;
  this.promise = new C(function ($$resolve, $$reject) {
    if (resolve !== undefined || reject !== undefined) throw TypeError('Bad Promise constructor');
    resolve = $$resolve;
    reject = $$reject;
  });
  this.resolve = aFunction(resolve);
  this.reject = aFunction(reject);
}

module.exports.f = function (C) {
  return new PromiseCapability(C);
};


/***/ }),
/* 92 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var global = __webpack_require__(2);
var DESCRIPTORS = __webpack_require__(7);
var LIBRARY = __webpack_require__(30);
var $typed = __webpack_require__(62);
var hide = __webpack_require__(11);
var redefineAll = __webpack_require__(41);
var fails = __webpack_require__(3);
var anInstance = __webpack_require__(39);
var toInteger = __webpack_require__(20);
var toLength = __webpack_require__(6);
var toIndex = __webpack_require__(122);
var gOPN = __webpack_require__(37).f;
var dP = __webpack_require__(8).f;
var arrayFill = __webpack_require__(85);
var setToStringTag = __webpack_require__(42);
var ARRAY_BUFFER = 'ArrayBuffer';
var DATA_VIEW = 'DataView';
var PROTOTYPE = 'prototype';
var WRONG_LENGTH = 'Wrong length!';
var WRONG_INDEX = 'Wrong index!';
var $ArrayBuffer = global[ARRAY_BUFFER];
var $DataView = global[DATA_VIEW];
var Math = global.Math;
var RangeError = global.RangeError;
// eslint-disable-next-line no-shadow-restricted-names
var Infinity = global.Infinity;
var BaseBuffer = $ArrayBuffer;
var abs = Math.abs;
var pow = Math.pow;
var floor = Math.floor;
var log = Math.log;
var LN2 = Math.LN2;
var BUFFER = 'buffer';
var BYTE_LENGTH = 'byteLength';
var BYTE_OFFSET = 'byteOffset';
var $BUFFER = DESCRIPTORS ? '_b' : BUFFER;
var $LENGTH = DESCRIPTORS ? '_l' : BYTE_LENGTH;
var $OFFSET = DESCRIPTORS ? '_o' : BYTE_OFFSET;

// IEEE754 conversions based on https://github.com/feross/ieee754
function packIEEE754(value, mLen, nBytes) {
  var buffer = new Array(nBytes);
  var eLen = nBytes * 8 - mLen - 1;
  var eMax = (1 << eLen) - 1;
  var eBias = eMax >> 1;
  var rt = mLen === 23 ? pow(2, -24) - pow(2, -77) : 0;
  var i = 0;
  var s = value < 0 || value === 0 && 1 / value < 0 ? 1 : 0;
  var e, m, c;
  value = abs(value);
  // eslint-disable-next-line no-self-compare
  if (value != value || value === Infinity) {
    // eslint-disable-next-line no-self-compare
    m = value != value ? 1 : 0;
    e = eMax;
  } else {
    e = floor(log(value) / LN2);
    if (value * (c = pow(2, -e)) < 1) {
      e--;
      c *= 2;
    }
    if (e + eBias >= 1) {
      value += rt / c;
    } else {
      value += rt * pow(2, 1 - eBias);
    }
    if (value * c >= 2) {
      e++;
      c /= 2;
    }
    if (e + eBias >= eMax) {
      m = 0;
      e = eMax;
    } else if (e + eBias >= 1) {
      m = (value * c - 1) * pow(2, mLen);
      e = e + eBias;
    } else {
      m = value * pow(2, eBias - 1) * pow(2, mLen);
      e = 0;
    }
  }
  for (; mLen >= 8; buffer[i++] = m & 255, m /= 256, mLen -= 8);
  e = e << mLen | m;
  eLen += mLen;
  for (; eLen > 0; buffer[i++] = e & 255, e /= 256, eLen -= 8);
  buffer[--i] |= s * 128;
  return buffer;
}
function unpackIEEE754(buffer, mLen, nBytes) {
  var eLen = nBytes * 8 - mLen - 1;
  var eMax = (1 << eLen) - 1;
  var eBias = eMax >> 1;
  var nBits = eLen - 7;
  var i = nBytes - 1;
  var s = buffer[i--];
  var e = s & 127;
  var m;
  s >>= 7;
  for (; nBits > 0; e = e * 256 + buffer[i], i--, nBits -= 8);
  m = e & (1 << -nBits) - 1;
  e >>= -nBits;
  nBits += mLen;
  for (; nBits > 0; m = m * 256 + buffer[i], i--, nBits -= 8);
  if (e === 0) {
    e = 1 - eBias;
  } else if (e === eMax) {
    return m ? NaN : s ? -Infinity : Infinity;
  } else {
    m = m + pow(2, mLen);
    e = e - eBias;
  } return (s ? -1 : 1) * m * pow(2, e - mLen);
}

function unpackI32(bytes) {
  return bytes[3] << 24 | bytes[2] << 16 | bytes[1] << 8 | bytes[0];
}
function packI8(it) {
  return [it & 0xff];
}
function packI16(it) {
  return [it & 0xff, it >> 8 & 0xff];
}
function packI32(it) {
  return [it & 0xff, it >> 8 & 0xff, it >> 16 & 0xff, it >> 24 & 0xff];
}
function packF64(it) {
  return packIEEE754(it, 52, 8);
}
function packF32(it) {
  return packIEEE754(it, 23, 4);
}

function addGetter(C, key, internal) {
  dP(C[PROTOTYPE], key, { get: function () { return this[internal]; } });
}

function get(view, bytes, index, isLittleEndian) {
  var numIndex = +index;
  var intIndex = toIndex(numIndex);
  if (intIndex + bytes > view[$LENGTH]) throw RangeError(WRONG_INDEX);
  var store = view[$BUFFER]._b;
  var start = intIndex + view[$OFFSET];
  var pack = store.slice(start, start + bytes);
  return isLittleEndian ? pack : pack.reverse();
}
function set(view, bytes, index, conversion, value, isLittleEndian) {
  var numIndex = +index;
  var intIndex = toIndex(numIndex);
  if (intIndex + bytes > view[$LENGTH]) throw RangeError(WRONG_INDEX);
  var store = view[$BUFFER]._b;
  var start = intIndex + view[$OFFSET];
  var pack = conversion(+value);
  for (var i = 0; i < bytes; i++) store[start + i] = pack[isLittleEndian ? i : bytes - i - 1];
}

if (!$typed.ABV) {
  $ArrayBuffer = function ArrayBuffer(length) {
    anInstance(this, $ArrayBuffer, ARRAY_BUFFER);
    var byteLength = toIndex(length);
    this._b = arrayFill.call(new Array(byteLength), 0);
    this[$LENGTH] = byteLength;
  };

  $DataView = function DataView(buffer, byteOffset, byteLength) {
    anInstance(this, $DataView, DATA_VIEW);
    anInstance(buffer, $ArrayBuffer, DATA_VIEW);
    var bufferLength = buffer[$LENGTH];
    var offset = toInteger(byteOffset);
    if (offset < 0 || offset > bufferLength) throw RangeError('Wrong offset!');
    byteLength = byteLength === undefined ? bufferLength - offset : toLength(byteLength);
    if (offset + byteLength > bufferLength) throw RangeError(WRONG_LENGTH);
    this[$BUFFER] = buffer;
    this[$OFFSET] = offset;
    this[$LENGTH] = byteLength;
  };

  if (DESCRIPTORS) {
    addGetter($ArrayBuffer, BYTE_LENGTH, '_l');
    addGetter($DataView, BUFFER, '_b');
    addGetter($DataView, BYTE_LENGTH, '_l');
    addGetter($DataView, BYTE_OFFSET, '_o');
  }

  redefineAll($DataView[PROTOTYPE], {
    getInt8: function getInt8(byteOffset) {
      return get(this, 1, byteOffset)[0] << 24 >> 24;
    },
    getUint8: function getUint8(byteOffset) {
      return get(this, 1, byteOffset)[0];
    },
    getInt16: function getInt16(byteOffset /* , littleEndian */) {
      var bytes = get(this, 2, byteOffset, arguments[1]);
      return (bytes[1] << 8 | bytes[0]) << 16 >> 16;
    },
    getUint16: function getUint16(byteOffset /* , littleEndian */) {
      var bytes = get(this, 2, byteOffset, arguments[1]);
      return bytes[1] << 8 | bytes[0];
    },
    getInt32: function getInt32(byteOffset /* , littleEndian */) {
      return unpackI32(get(this, 4, byteOffset, arguments[1]));
    },
    getUint32: function getUint32(byteOffset /* , littleEndian */) {
      return unpackI32(get(this, 4, byteOffset, arguments[1])) >>> 0;
    },
    getFloat32: function getFloat32(byteOffset /* , littleEndian */) {
      return unpackIEEE754(get(this, 4, byteOffset, arguments[1]), 23, 4);
    },
    getFloat64: function getFloat64(byteOffset /* , littleEndian */) {
      return unpackIEEE754(get(this, 8, byteOffset, arguments[1]), 52, 8);
    },
    setInt8: function setInt8(byteOffset, value) {
      set(this, 1, byteOffset, packI8, value);
    },
    setUint8: function setUint8(byteOffset, value) {
      set(this, 1, byteOffset, packI8, value);
    },
    setInt16: function setInt16(byteOffset, value /* , littleEndian */) {
      set(this, 2, byteOffset, packI16, value, arguments[2]);
    },
    setUint16: function setUint16(byteOffset, value /* , littleEndian */) {
      set(this, 2, byteOffset, packI16, value, arguments[2]);
    },
    setInt32: function setInt32(byteOffset, value /* , littleEndian */) {
      set(this, 4, byteOffset, packI32, value, arguments[2]);
    },
    setUint32: function setUint32(byteOffset, value /* , littleEndian */) {
      set(this, 4, byteOffset, packI32, value, arguments[2]);
    },
    setFloat32: function setFloat32(byteOffset, value /* , littleEndian */) {
      set(this, 4, byteOffset, packF32, value, arguments[2]);
    },
    setFloat64: function setFloat64(byteOffset, value /* , littleEndian */) {
      set(this, 8, byteOffset, packF64, value, arguments[2]);
    }
  });
} else {
  if (!fails(function () {
    $ArrayBuffer(1);
  }) || !fails(function () {
    new $ArrayBuffer(-1); // eslint-disable-line no-new
  }) || fails(function () {
    new $ArrayBuffer(); // eslint-disable-line no-new
    new $ArrayBuffer(1.5); // eslint-disable-line no-new
    new $ArrayBuffer(NaN); // eslint-disable-line no-new
    return $ArrayBuffer.name != ARRAY_BUFFER;
  })) {
    $ArrayBuffer = function ArrayBuffer(length) {
      anInstance(this, $ArrayBuffer);
      return new BaseBuffer(toIndex(length));
    };
    var ArrayBufferProto = $ArrayBuffer[PROTOTYPE] = BaseBuffer[PROTOTYPE];
    for (var keys = gOPN(BaseBuffer), j = 0, key; keys.length > j;) {
      if (!((key = keys[j++]) in $ArrayBuffer)) hide($ArrayBuffer, key, BaseBuffer[key]);
    }
    if (!LIBRARY) ArrayBufferProto.constructor = $ArrayBuffer;
  }
  // iOS Safari 7.x bug
  var view = new $DataView(new $ArrayBuffer(2));
  var $setInt8 = $DataView[PROTOTYPE].setInt8;
  view.setInt8(0, 2147483648);
  view.setInt8(1, 2147483649);
  if (view.getInt8(0) || !view.getInt8(1)) redefineAll($DataView[PROTOTYPE], {
    setInt8: function setInt8(byteOffset, value) {
      $setInt8.call(this, byteOffset, value << 24 >> 24);
    },
    setUint8: function setUint8(byteOffset, value) {
      $setInt8.call(this, byteOffset, value << 24 >> 24);
    }
  }, true);
}
setToStringTag($ArrayBuffer, ARRAY_BUFFER);
setToStringTag($DataView, DATA_VIEW);
hide($DataView[PROTOTYPE], $typed.VIEW, true);
exports[ARRAY_BUFFER] = $ArrayBuffer;
exports[DATA_VIEW] = $DataView;


/***/ }),
/* 93 */
/***/ (function(module, exports, __webpack_require__) {

module.exports = !__webpack_require__(7) && !__webpack_require__(3)(function () {
  return Object.defineProperty(__webpack_require__(66)('div'), 'a', { get: function () { return 7; } }).a != 7;
});


/***/ }),
/* 94 */
/***/ (function(module, exports, __webpack_require__) {

exports.f = __webpack_require__(5);


/***/ }),
/* 95 */
/***/ (function(module, exports, __webpack_require__) {

var has = __webpack_require__(14);
var toIObject = __webpack_require__(15);
var arrayIndexOf = __webpack_require__(52)(false);
var IE_PROTO = __webpack_require__(68)('IE_PROTO');

module.exports = function (object, names) {
  var O = toIObject(object);
  var i = 0;
  var result = [];
  var key;
  for (key in O) if (key != IE_PROTO) has(O, key) && result.push(key);
  // Don't enum bug & hidden keys
  while (names.length > i) if (has(O, key = names[i++])) {
    ~arrayIndexOf(result, key) || result.push(key);
  }
  return result;
};


/***/ }),
/* 96 */
/***/ (function(module, exports, __webpack_require__) {

var dP = __webpack_require__(8);
var anObject = __webpack_require__(1);
var getKeys = __webpack_require__(34);

module.exports = __webpack_require__(7) ? Object.defineProperties : function defineProperties(O, Properties) {
  anObject(O);
  var keys = getKeys(Properties);
  var length = keys.length;
  var i = 0;
  var P;
  while (length > i) dP.f(O, P = keys[i++], Properties[P]);
  return O;
};


/***/ }),
/* 97 */
/***/ (function(module, exports, __webpack_require__) {

// fallback for IE11 buggy Object.getOwnPropertyNames with iframe and window
var toIObject = __webpack_require__(15);
var gOPN = __webpack_require__(37).f;
var toString = {}.toString;

var windowNames = typeof window == 'object' && window && Object.getOwnPropertyNames
  ? Object.getOwnPropertyNames(window) : [];

var getWindowNames = function (it) {
  try {
    return gOPN(it);
  } catch (e) {
    return windowNames.slice();
  }
};

module.exports.f = function getOwnPropertyNames(it) {
  return windowNames && toString.call(it) == '[object Window]' ? getWindowNames(it) : gOPN(toIObject(it));
};


/***/ }),
/* 98 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 19.1.2.1 Object.assign(target, source, ...)
var getKeys = __webpack_require__(34);
var gOPS = __webpack_require__(53);
var pIE = __webpack_require__(48);
var toObject = __webpack_require__(9);
var IObject = __webpack_require__(47);
var $assign = Object.assign;

// should work with symbols and should have deterministic property order (V8 bug)
module.exports = !$assign || __webpack_require__(3)(function () {
  var A = {};
  var B = {};
  // eslint-disable-next-line no-undef
  var S = Symbol();
  var K = 'abcdefghijklmnopqrst';
  A[S] = 7;
  K.split('').forEach(function (k) { B[k] = k; });
  return $assign({}, A)[S] != 7 || Object.keys($assign({}, B)).join('') != K;
}) ? function assign(target, source) { // eslint-disable-line no-unused-vars
  var T = toObject(target);
  var aLen = arguments.length;
  var index = 1;
  var getSymbols = gOPS.f;
  var isEnum = pIE.f;
  while (aLen > index) {
    var S = IObject(arguments[index++]);
    var keys = getSymbols ? getKeys(S).concat(getSymbols(S)) : getKeys(S);
    var length = keys.length;
    var j = 0;
    var key;
    while (length > j) if (isEnum.call(S, key = keys[j++])) T[key] = S[key];
  } return T;
} : $assign;


/***/ }),
/* 99 */
/***/ (function(module, exports) {

// 7.2.9 SameValue(x, y)
module.exports = Object.is || function is(x, y) {
  // eslint-disable-next-line no-self-compare
  return x === y ? x !== 0 || 1 / x === 1 / y : x != x && y != y;
};


/***/ }),
/* 100 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var aFunction = __webpack_require__(10);
var isObject = __webpack_require__(4);
var invoke = __webpack_require__(101);
var arraySlice = [].slice;
var factories = {};

var construct = function (F, len, args) {
  if (!(len in factories)) {
    for (var n = [], i = 0; i < len; i++) n[i] = 'a[' + i + ']';
    // eslint-disable-next-line no-new-func
    factories[len] = Function('F,a', 'return new F(' + n.join(',') + ')');
  } return factories[len](F, args);
};

module.exports = Function.bind || function bind(that /* , ...args */) {
  var fn = aFunction(this);
  var partArgs = arraySlice.call(arguments, 1);
  var bound = function (/* args... */) {
    var args = partArgs.concat(arraySlice.call(arguments));
    return this instanceof bound ? construct(fn, args.length, args) : invoke(fn, args, that);
  };
  if (isObject(fn.prototype)) bound.prototype = fn.prototype;
  return bound;
};


/***/ }),
/* 101 */
/***/ (function(module, exports) {

// fast apply, http://jsperf.lnkit.com/fast-apply/5
module.exports = function (fn, args, that) {
  var un = that === undefined;
  switch (args.length) {
    case 0: return un ? fn()
                      : fn.call(that);
    case 1: return un ? fn(args[0])
                      : fn.call(that, args[0]);
    case 2: return un ? fn(args[0], args[1])
                      : fn.call(that, args[0], args[1]);
    case 3: return un ? fn(args[0], args[1], args[2])
                      : fn.call(that, args[0], args[1], args[2]);
    case 4: return un ? fn(args[0], args[1], args[2], args[3])
                      : fn.call(that, args[0], args[1], args[2], args[3]);
  } return fn.apply(that, args);
};


/***/ }),
/* 102 */
/***/ (function(module, exports, __webpack_require__) {

var cof = __webpack_require__(19);
module.exports = function (it, msg) {
  if (typeof it != 'number' && cof(it) != 'Number') throw TypeError(msg);
  return +it;
};


/***/ }),
/* 103 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.3 Number.isInteger(number)
var isObject = __webpack_require__(4);
var floor = Math.floor;
module.exports = function isInteger(it) {
  return !isObject(it) && isFinite(it) && floor(it) === it;
};


/***/ }),
/* 104 */
/***/ (function(module, exports, __webpack_require__) {

var $parseFloat = __webpack_require__(2).parseFloat;
var $trim = __webpack_require__(44).trim;

module.exports = 1 / $parseFloat(__webpack_require__(73) + '-0') !== -Infinity ? function parseFloat(str) {
  var string = $trim(String(str), 3);
  var result = $parseFloat(string);
  return result === 0 && string.charAt(0) == '-' ? -0 : result;
} : $parseFloat;


/***/ }),
/* 105 */
/***/ (function(module, exports, __webpack_require__) {

var $parseInt = __webpack_require__(2).parseInt;
var $trim = __webpack_require__(44).trim;
var ws = __webpack_require__(73);
var hex = /^[-+]?0[xX]/;

module.exports = $parseInt(ws + '08') !== 8 || $parseInt(ws + '0x16') !== 22 ? function parseInt(str, radix) {
  var string = $trim(String(str), 3);
  return $parseInt(string, (radix >>> 0) || (hex.test(string) ? 16 : 10));
} : $parseInt;


/***/ }),
/* 106 */
/***/ (function(module, exports) {

// 20.2.2.20 Math.log1p(x)
module.exports = Math.log1p || function log1p(x) {
  return (x = +x) > -1e-8 && x < 1e-8 ? x - x * x / 2 : Math.log(1 + x);
};


/***/ }),
/* 107 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.16 Math.fround(x)
var sign = __webpack_require__(75);
var pow = Math.pow;
var EPSILON = pow(2, -52);
var EPSILON32 = pow(2, -23);
var MAX32 = pow(2, 127) * (2 - EPSILON32);
var MIN32 = pow(2, -126);

var roundTiesToEven = function (n) {
  return n + 1 / EPSILON - 1 / EPSILON;
};

module.exports = Math.fround || function fround(x) {
  var $abs = Math.abs(x);
  var $sign = sign(x);
  var a, result;
  if ($abs < MIN32) return $sign * roundTiesToEven($abs / MIN32 / EPSILON32) * MIN32 * EPSILON32;
  a = (1 + EPSILON32 / EPSILON) * $abs;
  result = a - (a - $abs);
  // eslint-disable-next-line no-self-compare
  if (result > MAX32 || result != result) return $sign * Infinity;
  return $sign * result;
};


/***/ }),
/* 108 */
/***/ (function(module, exports, __webpack_require__) {

// call something on iterator step with safe closing on error
var anObject = __webpack_require__(1);
module.exports = function (iterator, fn, value, entries) {
  try {
    return entries ? fn(anObject(value)[0], value[1]) : fn(value);
  // 7.4.6 IteratorClose(iterator, completion)
  } catch (e) {
    var ret = iterator['return'];
    if (ret !== undefined) anObject(ret.call(iterator));
    throw e;
  }
};


/***/ }),
/* 109 */
/***/ (function(module, exports, __webpack_require__) {

var aFunction = __webpack_require__(10);
var toObject = __webpack_require__(9);
var IObject = __webpack_require__(47);
var toLength = __webpack_require__(6);

module.exports = function (that, callbackfn, aLen, memo, isRight) {
  aFunction(callbackfn);
  var O = toObject(that);
  var self = IObject(O);
  var length = toLength(O.length);
  var index = isRight ? length - 1 : 0;
  var i = isRight ? -1 : 1;
  if (aLen < 2) for (;;) {
    if (index in self) {
      memo = self[index];
      index += i;
      break;
    }
    index += i;
    if (isRight ? index < 0 : length <= index) {
      throw TypeError('Reduce of empty array with no initial value');
    }
  }
  for (;isRight ? index >= 0 : length > index; index += i) if (index in self) {
    memo = callbackfn(memo, self[index], index, O);
  }
  return memo;
};


/***/ }),
/* 110 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// 22.1.3.3 Array.prototype.copyWithin(target, start, end = this.length)

var toObject = __webpack_require__(9);
var toAbsoluteIndex = __webpack_require__(35);
var toLength = __webpack_require__(6);

module.exports = [].copyWithin || function copyWithin(target /* = 0 */, start /* = 0, end = @length */) {
  var O = toObject(this);
  var len = toLength(O.length);
  var to = toAbsoluteIndex(target, len);
  var from = toAbsoluteIndex(start, len);
  var end = arguments.length > 2 ? arguments[2] : undefined;
  var count = Math.min((end === undefined ? len : toAbsoluteIndex(end, len)) - from, len - to);
  var inc = 1;
  if (from < to && to < from + count) {
    inc = -1;
    from += count - 1;
    to += count - 1;
  }
  while (count-- > 0) {
    if (from in O) O[to] = O[from];
    else delete O[to];
    to += inc;
    from += inc;
  } return O;
};


/***/ }),
/* 111 */
/***/ (function(module, exports) {

module.exports = function (done, value) {
  return { value: value, done: !!done };
};


/***/ }),
/* 112 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var regexpExec = __webpack_require__(87);
__webpack_require__(0)({
  target: 'RegExp',
  proto: true,
  forced: regexpExec !== /./.exec
}, {
  exec: regexpExec
});


/***/ }),
/* 113 */
/***/ (function(module, exports, __webpack_require__) {

// 21.2.5.3 get RegExp.prototype.flags()
if (__webpack_require__(7) && /./g.flags != 'g') __webpack_require__(8).f(RegExp.prototype, 'flags', {
  configurable: true,
  get: __webpack_require__(49)
});


/***/ }),
/* 114 */
/***/ (function(module, exports) {

module.exports = function (exec) {
  try {
    return { e: false, v: exec() };
  } catch (e) {
    return { e: true, v: e };
  }
};


/***/ }),
/* 115 */
/***/ (function(module, exports, __webpack_require__) {

var anObject = __webpack_require__(1);
var isObject = __webpack_require__(4);
var newPromiseCapability = __webpack_require__(91);

module.exports = function (C, x) {
  anObject(C);
  if (isObject(x) && x.constructor === C) return x;
  var promiseCapability = newPromiseCapability.f(C);
  var resolve = promiseCapability.resolve;
  resolve(x);
  return promiseCapability.promise;
};


/***/ }),
/* 116 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var strong = __webpack_require__(117);
var validate = __webpack_require__(46);
var MAP = 'Map';

// 23.1 Map Objects
module.exports = __webpack_require__(61)(MAP, function (get) {
  return function Map() { return get(this, arguments.length > 0 ? arguments[0] : undefined); };
}, {
  // 23.1.3.6 Map.prototype.get(key)
  get: function get(key) {
    var entry = strong.getEntry(validate(this, MAP), key);
    return entry && entry.v;
  },
  // 23.1.3.9 Map.prototype.set(key, value)
  set: function set(key, value) {
    return strong.def(validate(this, MAP), key === 0 ? 0 : key, value);
  }
}, strong, true);


/***/ }),
/* 117 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var dP = __webpack_require__(8).f;
var create = __webpack_require__(36);
var redefineAll = __webpack_require__(41);
var ctx = __webpack_require__(18);
var anInstance = __webpack_require__(39);
var forOf = __webpack_require__(40);
var $iterDefine = __webpack_require__(79);
var step = __webpack_require__(111);
var setSpecies = __webpack_require__(38);
var DESCRIPTORS = __webpack_require__(7);
var fastKey = __webpack_require__(29).fastKey;
var validate = __webpack_require__(46);
var SIZE = DESCRIPTORS ? '_s' : 'size';

var getEntry = function (that, key) {
  // fast case
  var index = fastKey(key);
  var entry;
  if (index !== 'F') return that._i[index];
  // frozen object case
  for (entry = that._f; entry; entry = entry.n) {
    if (entry.k == key) return entry;
  }
};

module.exports = {
  getConstructor: function (wrapper, NAME, IS_MAP, ADDER) {
    var C = wrapper(function (that, iterable) {
      anInstance(that, C, NAME, '_i');
      that._t = NAME;         // collection type
      that._i = create(null); // index
      that._f = undefined;    // first entry
      that._l = undefined;    // last entry
      that[SIZE] = 0;         // size
      if (iterable != undefined) forOf(iterable, IS_MAP, that[ADDER], that);
    });
    redefineAll(C.prototype, {
      // 23.1.3.1 Map.prototype.clear()
      // 23.2.3.2 Set.prototype.clear()
      clear: function clear() {
        for (var that = validate(this, NAME), data = that._i, entry = that._f; entry; entry = entry.n) {
          entry.r = true;
          if (entry.p) entry.p = entry.p.n = undefined;
          delete data[entry.i];
        }
        that._f = that._l = undefined;
        that[SIZE] = 0;
      },
      // 23.1.3.3 Map.prototype.delete(key)
      // 23.2.3.4 Set.prototype.delete(value)
      'delete': function (key) {
        var that = validate(this, NAME);
        var entry = getEntry(that, key);
        if (entry) {
          var next = entry.n;
          var prev = entry.p;
          delete that._i[entry.i];
          entry.r = true;
          if (prev) prev.n = next;
          if (next) next.p = prev;
          if (that._f == entry) that._f = next;
          if (that._l == entry) that._l = prev;
          that[SIZE]--;
        } return !!entry;
      },
      // 23.2.3.6 Set.prototype.forEach(callbackfn, thisArg = undefined)
      // 23.1.3.5 Map.prototype.forEach(callbackfn, thisArg = undefined)
      forEach: function forEach(callbackfn /* , that = undefined */) {
        validate(this, NAME);
        var f = ctx(callbackfn, arguments.length > 1 ? arguments[1] : undefined, 3);
        var entry;
        while (entry = entry ? entry.n : this._f) {
          f(entry.v, entry.k, this);
          // revert to the last existing entry
          while (entry && entry.r) entry = entry.p;
        }
      },
      // 23.1.3.7 Map.prototype.has(key)
      // 23.2.3.7 Set.prototype.has(value)
      has: function has(key) {
        return !!getEntry(validate(this, NAME), key);
      }
    });
    if (DESCRIPTORS) dP(C.prototype, 'size', {
      get: function () {
        return validate(this, NAME)[SIZE];
      }
    });
    return C;
  },
  def: function (that, key, value) {
    var entry = getEntry(that, key);
    var prev, index;
    // change existing entry
    if (entry) {
      entry.v = value;
    // create new entry
    } else {
      that._l = entry = {
        i: index = fastKey(key, true), // <- index
        k: key,                        // <- key
        v: value,                      // <- value
        p: prev = that._l,             // <- previous entry
        n: undefined,                  // <- next entry
        r: false                       // <- removed
      };
      if (!that._f) that._f = entry;
      if (prev) prev.n = entry;
      that[SIZE]++;
      // add to index
      if (index !== 'F') that._i[index] = entry;
    } return that;
  },
  getEntry: getEntry,
  setStrong: function (C, NAME, IS_MAP) {
    // add .keys, .values, .entries, [@@iterator]
    // 23.1.3.4, 23.1.3.8, 23.1.3.11, 23.1.3.12, 23.2.3.5, 23.2.3.8, 23.2.3.10, 23.2.3.11
    $iterDefine(C, NAME, function (iterated, kind) {
      this._t = validate(iterated, NAME); // target
      this._k = kind;                     // kind
      this._l = undefined;                // previous
    }, function () {
      var that = this;
      var kind = that._k;
      var entry = that._l;
      // revert to the last existing entry
      while (entry && entry.r) entry = entry.p;
      // get next entry
      if (!that._t || !(that._l = entry = entry ? entry.n : that._t._f)) {
        // or finish the iteration
        that._t = undefined;
        return step(1);
      }
      // return step by kind
      if (kind == 'keys') return step(0, entry.k);
      if (kind == 'values') return step(0, entry.v);
      return step(0, [entry.k, entry.v]);
    }, IS_MAP ? 'entries' : 'values', !IS_MAP, true);

    // add [@@species], 23.1.2.2, 23.2.2.2
    setSpecies(NAME);
  }
};


/***/ }),
/* 118 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var strong = __webpack_require__(117);
var validate = __webpack_require__(46);
var SET = 'Set';

// 23.2 Set Objects
module.exports = __webpack_require__(61)(SET, function (get) {
  return function Set() { return get(this, arguments.length > 0 ? arguments[0] : undefined); };
}, {
  // 23.2.3.1 Set.prototype.add(value)
  add: function add(value) {
    return strong.def(validate(this, SET), value = value === 0 ? 0 : value, value);
  }
}, strong);


/***/ }),
/* 119 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var each = __webpack_require__(25)(0);
var redefine = __webpack_require__(12);
var meta = __webpack_require__(29);
var assign = __webpack_require__(98);
var weak = __webpack_require__(120);
var isObject = __webpack_require__(4);
var fails = __webpack_require__(3);
var validate = __webpack_require__(46);
var WEAK_MAP = 'WeakMap';
var getWeak = meta.getWeak;
var isExtensible = Object.isExtensible;
var uncaughtFrozenStore = weak.ufstore;
var tmp = {};
var InternalMap;

var wrapper = function (get) {
  return function WeakMap() {
    return get(this, arguments.length > 0 ? arguments[0] : undefined);
  };
};

var methods = {
  // 23.3.3.3 WeakMap.prototype.get(key)
  get: function get(key) {
    if (isObject(key)) {
      var data = getWeak(key);
      if (data === true) return uncaughtFrozenStore(validate(this, WEAK_MAP)).get(key);
      return data ? data[this._i] : undefined;
    }
  },
  // 23.3.3.5 WeakMap.prototype.set(key, value)
  set: function set(key, value) {
    return weak.def(validate(this, WEAK_MAP), key, value);
  }
};

// 23.3 WeakMap Objects
var $WeakMap = module.exports = __webpack_require__(61)(WEAK_MAP, wrapper, methods, weak, true, true);

// IE11 WeakMap frozen keys fix
if (fails(function () { return new $WeakMap().set((Object.freeze || Object)(tmp), 7).get(tmp) != 7; })) {
  InternalMap = weak.getConstructor(wrapper, WEAK_MAP);
  assign(InternalMap.prototype, methods);
  meta.NEED = true;
  each(['delete', 'has', 'get', 'set'], function (key) {
    var proto = $WeakMap.prototype;
    var method = proto[key];
    redefine(proto, key, function (a, b) {
      // store frozen objects on internal weakmap shim
      if (isObject(a) && !isExtensible(a)) {
        if (!this._f) this._f = new InternalMap();
        var result = this._f[key](a, b);
        return key == 'set' ? this : result;
      // store all the rest on native weakmap
      } return method.call(this, a, b);
    });
  });
}


/***/ }),
/* 120 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var redefineAll = __webpack_require__(41);
var getWeak = __webpack_require__(29).getWeak;
var anObject = __webpack_require__(1);
var isObject = __webpack_require__(4);
var anInstance = __webpack_require__(39);
var forOf = __webpack_require__(40);
var createArrayMethod = __webpack_require__(25);
var $has = __webpack_require__(14);
var validate = __webpack_require__(46);
var arrayFind = createArrayMethod(5);
var arrayFindIndex = createArrayMethod(6);
var id = 0;

// fallback for uncaught frozen keys
var uncaughtFrozenStore = function (that) {
  return that._l || (that._l = new UncaughtFrozenStore());
};
var UncaughtFrozenStore = function () {
  this.a = [];
};
var findUncaughtFrozen = function (store, key) {
  return arrayFind(store.a, function (it) {
    return it[0] === key;
  });
};
UncaughtFrozenStore.prototype = {
  get: function (key) {
    var entry = findUncaughtFrozen(this, key);
    if (entry) return entry[1];
  },
  has: function (key) {
    return !!findUncaughtFrozen(this, key);
  },
  set: function (key, value) {
    var entry = findUncaughtFrozen(this, key);
    if (entry) entry[1] = value;
    else this.a.push([key, value]);
  },
  'delete': function (key) {
    var index = arrayFindIndex(this.a, function (it) {
      return it[0] === key;
    });
    if (~index) this.a.splice(index, 1);
    return !!~index;
  }
};

module.exports = {
  getConstructor: function (wrapper, NAME, IS_MAP, ADDER) {
    var C = wrapper(function (that, iterable) {
      anInstance(that, C, NAME, '_i');
      that._t = NAME;      // collection type
      that._i = id++;      // collection id
      that._l = undefined; // leak store for uncaught frozen objects
      if (iterable != undefined) forOf(iterable, IS_MAP, that[ADDER], that);
    });
    redefineAll(C.prototype, {
      // 23.3.3.2 WeakMap.prototype.delete(key)
      // 23.4.3.3 WeakSet.prototype.delete(value)
      'delete': function (key) {
        if (!isObject(key)) return false;
        var data = getWeak(key);
        if (data === true) return uncaughtFrozenStore(validate(this, NAME))['delete'](key);
        return data && $has(data, this._i) && delete data[this._i];
      },
      // 23.3.3.4 WeakMap.prototype.has(key)
      // 23.4.3.4 WeakSet.prototype.has(value)
      has: function has(key) {
        if (!isObject(key)) return false;
        var data = getWeak(key);
        if (data === true) return uncaughtFrozenStore(validate(this, NAME)).has(key);
        return data && $has(data, this._i);
      }
    });
    return C;
  },
  def: function (that, key, value) {
    var data = getWeak(anObject(key), true);
    if (data === true) uncaughtFrozenStore(that).set(key, value);
    else data[that._i] = value;
    return that;
  },
  ufstore: uncaughtFrozenStore
};


/***/ }),
/* 121 */
/***/ (function(module, exports, __webpack_require__) {

// all object keys, includes non-enumerable and symbols
var gOPN = __webpack_require__(37);
var gOPS = __webpack_require__(53);
var anObject = __webpack_require__(1);
var Reflect = __webpack_require__(2).Reflect;
module.exports = Reflect && Reflect.ownKeys || function ownKeys(it) {
  var keys = gOPN.f(anObject(it));
  var getSymbols = gOPS.f;
  return getSymbols ? keys.concat(getSymbols(it)) : keys;
};


/***/ }),
/* 122 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/ecma262/#sec-toindex
var toInteger = __webpack_require__(20);
var toLength = __webpack_require__(6);
module.exports = function (it) {
  if (it === undefined) return 0;
  var number = toInteger(it);
  var length = toLength(number);
  if (number !== length) throw RangeError('Wrong length!');
  return length;
};


/***/ }),
/* 123 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://tc39.github.io/proposal-flatMap/#sec-FlattenIntoArray
var isArray = __webpack_require__(54);
var isObject = __webpack_require__(4);
var toLength = __webpack_require__(6);
var ctx = __webpack_require__(18);
var IS_CONCAT_SPREADABLE = __webpack_require__(5)('isConcatSpreadable');

function flattenIntoArray(target, original, source, sourceLen, start, depth, mapper, thisArg) {
  var targetIndex = start;
  var sourceIndex = 0;
  var mapFn = mapper ? ctx(mapper, thisArg, 3) : false;
  var element, spreadable;

  while (sourceIndex < sourceLen) {
    if (sourceIndex in source) {
      element = mapFn ? mapFn(source[sourceIndex], sourceIndex, original) : source[sourceIndex];

      spreadable = false;
      if (isObject(element)) {
        spreadable = element[IS_CONCAT_SPREADABLE];
        spreadable = spreadable !== undefined ? !!spreadable : isArray(element);
      }

      if (spreadable && depth > 0) {
        targetIndex = flattenIntoArray(target, original, element, toLength(element.length), targetIndex, depth - 1) - 1;
      } else {
        if (targetIndex >= 0x1fffffffffffff) throw TypeError();
        target[targetIndex] = element;
      }

      targetIndex++;
    }
    sourceIndex++;
  }
  return targetIndex;
}

module.exports = flattenIntoArray;


/***/ }),
/* 124 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/tc39/proposal-string-pad-start-end
var toLength = __webpack_require__(6);
var repeat = __webpack_require__(74);
var defined = __webpack_require__(23);

module.exports = function (that, maxLength, fillString, left) {
  var S = String(defined(that));
  var stringLength = S.length;
  var fillStr = fillString === undefined ? ' ' : String(fillString);
  var intMaxLength = toLength(maxLength);
  if (intMaxLength <= stringLength || fillStr == '') return S;
  var fillLen = intMaxLength - stringLength;
  var stringFiller = repeat.call(fillStr, Math.ceil(fillLen / fillStr.length));
  if (stringFiller.length > fillLen) stringFiller = stringFiller.slice(0, fillLen);
  return left ? stringFiller + S : S + stringFiller;
};


/***/ }),
/* 125 */
/***/ (function(module, exports, __webpack_require__) {

var getKeys = __webpack_require__(34);
var toIObject = __webpack_require__(15);
var isEnum = __webpack_require__(48).f;
module.exports = function (isEntries) {
  return function (it) {
    var O = toIObject(it);
    var keys = getKeys(O);
    var length = keys.length;
    var i = 0;
    var result = [];
    var key;
    while (length > i) if (isEnum.call(O, key = keys[i++])) {
      result.push(isEntries ? [key, O[key]] : O[key]);
    } return result;
  };
};


/***/ }),
/* 126 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/DavidBruant/Map-Set.prototype.toJSON
var classof = __webpack_require__(43);
var from = __webpack_require__(127);
module.exports = function (NAME) {
  return function toJSON() {
    if (classof(this) != NAME) throw TypeError(NAME + "#toJSON isn't generic");
    return from(this);
  };
};


/***/ }),
/* 127 */
/***/ (function(module, exports, __webpack_require__) {

var forOf = __webpack_require__(40);

module.exports = function (iter, ITERATOR) {
  var result = [];
  forOf(iter, false, result.push, result, ITERATOR);
  return result;
};


/***/ }),
/* 128 */
/***/ (function(module, exports) {

// https://rwaldron.github.io/proposal-math-extensions/
module.exports = Math.scale || function scale(x, inLow, inHigh, outLow, outHigh) {
  if (
    arguments.length === 0
      // eslint-disable-next-line no-self-compare
      || x != x
      // eslint-disable-next-line no-self-compare
      || inLow != inLow
      // eslint-disable-next-line no-self-compare
      || inHigh != inHigh
      // eslint-disable-next-line no-self-compare
      || outLow != outLow
      // eslint-disable-next-line no-self-compare
      || outHigh != outHigh
  ) return NaN;
  if (x === Infinity || x === -Infinity) return x;
  return (x - inLow) * (outHigh - outLow) / (inHigh - inLow) + outLow;
};


/***/ }),
/* 129 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(130);
__webpack_require__(132);
__webpack_require__(133);
__webpack_require__(134);
__webpack_require__(135);
__webpack_require__(136);
__webpack_require__(137);
__webpack_require__(138);
__webpack_require__(139);
__webpack_require__(140);
__webpack_require__(141);
__webpack_require__(142);
__webpack_require__(143);
__webpack_require__(144);
__webpack_require__(145);
__webpack_require__(146);
__webpack_require__(147);
__webpack_require__(148);
__webpack_require__(149);
__webpack_require__(150);
__webpack_require__(151);
__webpack_require__(152);
__webpack_require__(153);
__webpack_require__(154);
__webpack_require__(155);
__webpack_require__(156);
__webpack_require__(157);
__webpack_require__(158);
__webpack_require__(159);
__webpack_require__(160);
__webpack_require__(161);
__webpack_require__(162);
__webpack_require__(163);
__webpack_require__(164);
__webpack_require__(165);
__webpack_require__(166);
__webpack_require__(167);
__webpack_require__(168);
__webpack_require__(169);
__webpack_require__(170);
__webpack_require__(171);
__webpack_require__(172);
__webpack_require__(173);
__webpack_require__(174);
__webpack_require__(175);
__webpack_require__(176);
__webpack_require__(177);
__webpack_require__(178);
__webpack_require__(179);
__webpack_require__(180);
__webpack_require__(181);
__webpack_require__(182);
__webpack_require__(183);
__webpack_require__(184);
__webpack_require__(185);
__webpack_require__(186);
__webpack_require__(187);
__webpack_require__(188);
__webpack_require__(189);
__webpack_require__(190);
__webpack_require__(191);
__webpack_require__(192);
__webpack_require__(193);
__webpack_require__(194);
__webpack_require__(195);
__webpack_require__(196);
__webpack_require__(197);
__webpack_require__(198);
__webpack_require__(199);
__webpack_require__(200);
__webpack_require__(201);
__webpack_require__(202);
__webpack_require__(203);
__webpack_require__(204);
__webpack_require__(205);
__webpack_require__(206);
__webpack_require__(207);
__webpack_require__(208);
__webpack_require__(209);
__webpack_require__(210);
__webpack_require__(211);
__webpack_require__(213);
__webpack_require__(214);
__webpack_require__(215);
__webpack_require__(216);
__webpack_require__(217);
__webpack_require__(218);
__webpack_require__(219);
__webpack_require__(220);
__webpack_require__(221);
__webpack_require__(222);
__webpack_require__(223);
__webpack_require__(224);
__webpack_require__(86);
__webpack_require__(225);
__webpack_require__(226);
__webpack_require__(112);
__webpack_require__(227);
__webpack_require__(113);
__webpack_require__(228);
__webpack_require__(229);
__webpack_require__(230);
__webpack_require__(231);
__webpack_require__(232);
__webpack_require__(116);
__webpack_require__(118);
__webpack_require__(119);
__webpack_require__(233);
__webpack_require__(234);
__webpack_require__(235);
__webpack_require__(236);
__webpack_require__(237);
__webpack_require__(238);
__webpack_require__(239);
__webpack_require__(240);
__webpack_require__(241);
__webpack_require__(242);
__webpack_require__(243);
__webpack_require__(244);
__webpack_require__(245);
__webpack_require__(246);
__webpack_require__(247);
__webpack_require__(248);
__webpack_require__(249);
__webpack_require__(250);
__webpack_require__(252);
__webpack_require__(253);
__webpack_require__(255);
__webpack_require__(256);
__webpack_require__(257);
__webpack_require__(258);
__webpack_require__(259);
__webpack_require__(260);
__webpack_require__(261);
__webpack_require__(262);
__webpack_require__(263);
__webpack_require__(264);
__webpack_require__(265);
__webpack_require__(266);
__webpack_require__(267);
__webpack_require__(268);
__webpack_require__(269);
__webpack_require__(270);
__webpack_require__(271);
__webpack_require__(272);
__webpack_require__(273);
__webpack_require__(274);
__webpack_require__(275);
__webpack_require__(276);
__webpack_require__(277);
__webpack_require__(278);
__webpack_require__(279);
__webpack_require__(280);
__webpack_require__(281);
__webpack_require__(282);
__webpack_require__(283);
__webpack_require__(284);
__webpack_require__(285);
__webpack_require__(286);
__webpack_require__(287);
__webpack_require__(288);
__webpack_require__(289);
__webpack_require__(290);
__webpack_require__(291);
__webpack_require__(292);
__webpack_require__(293);
__webpack_require__(294);
__webpack_require__(295);
__webpack_require__(296);
__webpack_require__(297);
__webpack_require__(298);
__webpack_require__(299);
__webpack_require__(300);
__webpack_require__(301);
__webpack_require__(302);
__webpack_require__(303);
__webpack_require__(304);
__webpack_require__(305);
__webpack_require__(306);
__webpack_require__(307);
__webpack_require__(308);
__webpack_require__(309);
__webpack_require__(310);
__webpack_require__(311);
__webpack_require__(312);
__webpack_require__(313);
__webpack_require__(314);
__webpack_require__(315);
__webpack_require__(316);
__webpack_require__(317);
__webpack_require__(318);
__webpack_require__(319);
__webpack_require__(320);
__webpack_require__(321);
__webpack_require__(322);
__webpack_require__(323);
module.exports = __webpack_require__(324);


/***/ }),
/* 130 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// ECMAScript 6 symbols shim
var global = __webpack_require__(2);
var has = __webpack_require__(14);
var DESCRIPTORS = __webpack_require__(7);
var $export = __webpack_require__(0);
var redefine = __webpack_require__(12);
var META = __webpack_require__(29).KEY;
var $fails = __webpack_require__(3);
var shared = __webpack_require__(51);
var setToStringTag = __webpack_require__(42);
var uid = __webpack_require__(33);
var wks = __webpack_require__(5);
var wksExt = __webpack_require__(94);
var wksDefine = __webpack_require__(67);
var enumKeys = __webpack_require__(131);
var isArray = __webpack_require__(54);
var anObject = __webpack_require__(1);
var isObject = __webpack_require__(4);
var toIObject = __webpack_require__(15);
var toPrimitive = __webpack_require__(22);
var createDesc = __webpack_require__(32);
var _create = __webpack_require__(36);
var gOPNExt = __webpack_require__(97);
var $GOPD = __webpack_require__(16);
var $DP = __webpack_require__(8);
var $keys = __webpack_require__(34);
var gOPD = $GOPD.f;
var dP = $DP.f;
var gOPN = gOPNExt.f;
var $Symbol = global.Symbol;
var $JSON = global.JSON;
var _stringify = $JSON && $JSON.stringify;
var PROTOTYPE = 'prototype';
var HIDDEN = wks('_hidden');
var TO_PRIMITIVE = wks('toPrimitive');
var isEnum = {}.propertyIsEnumerable;
var SymbolRegistry = shared('symbol-registry');
var AllSymbols = shared('symbols');
var OPSymbols = shared('op-symbols');
var ObjectProto = Object[PROTOTYPE];
var USE_NATIVE = typeof $Symbol == 'function';
var QObject = global.QObject;
// Don't use setters in Qt Script, https://github.com/zloirock/core-js/issues/173
var setter = !QObject || !QObject[PROTOTYPE] || !QObject[PROTOTYPE].findChild;

// fallback for old Android, https://code.google.com/p/v8/issues/detail?id=687
var setSymbolDesc = DESCRIPTORS && $fails(function () {
  return _create(dP({}, 'a', {
    get: function () { return dP(this, 'a', { value: 7 }).a; }
  })).a != 7;
}) ? function (it, key, D) {
  var protoDesc = gOPD(ObjectProto, key);
  if (protoDesc) delete ObjectProto[key];
  dP(it, key, D);
  if (protoDesc && it !== ObjectProto) dP(ObjectProto, key, protoDesc);
} : dP;

var wrap = function (tag) {
  var sym = AllSymbols[tag] = _create($Symbol[PROTOTYPE]);
  sym._k = tag;
  return sym;
};

var isSymbol = USE_NATIVE && typeof $Symbol.iterator == 'symbol' ? function (it) {
  return typeof it == 'symbol';
} : function (it) {
  return it instanceof $Symbol;
};

var $defineProperty = function defineProperty(it, key, D) {
  if (it === ObjectProto) $defineProperty(OPSymbols, key, D);
  anObject(it);
  key = toPrimitive(key, true);
  anObject(D);
  if (has(AllSymbols, key)) {
    if (!D.enumerable) {
      if (!has(it, HIDDEN)) dP(it, HIDDEN, createDesc(1, {}));
      it[HIDDEN][key] = true;
    } else {
      if (has(it, HIDDEN) && it[HIDDEN][key]) it[HIDDEN][key] = false;
      D = _create(D, { enumerable: createDesc(0, false) });
    } return setSymbolDesc(it, key, D);
  } return dP(it, key, D);
};
var $defineProperties = function defineProperties(it, P) {
  anObject(it);
  var keys = enumKeys(P = toIObject(P));
  var i = 0;
  var l = keys.length;
  var key;
  while (l > i) $defineProperty(it, key = keys[i++], P[key]);
  return it;
};
var $create = function create(it, P) {
  return P === undefined ? _create(it) : $defineProperties(_create(it), P);
};
var $propertyIsEnumerable = function propertyIsEnumerable(key) {
  var E = isEnum.call(this, key = toPrimitive(key, true));
  if (this === ObjectProto && has(AllSymbols, key) && !has(OPSymbols, key)) return false;
  return E || !has(this, key) || !has(AllSymbols, key) || has(this, HIDDEN) && this[HIDDEN][key] ? E : true;
};
var $getOwnPropertyDescriptor = function getOwnPropertyDescriptor(it, key) {
  it = toIObject(it);
  key = toPrimitive(key, true);
  if (it === ObjectProto && has(AllSymbols, key) && !has(OPSymbols, key)) return;
  var D = gOPD(it, key);
  if (D && has(AllSymbols, key) && !(has(it, HIDDEN) && it[HIDDEN][key])) D.enumerable = true;
  return D;
};
var $getOwnPropertyNames = function getOwnPropertyNames(it) {
  var names = gOPN(toIObject(it));
  var result = [];
  var i = 0;
  var key;
  while (names.length > i) {
    if (!has(AllSymbols, key = names[i++]) && key != HIDDEN && key != META) result.push(key);
  } return result;
};
var $getOwnPropertySymbols = function getOwnPropertySymbols(it) {
  var IS_OP = it === ObjectProto;
  var names = gOPN(IS_OP ? OPSymbols : toIObject(it));
  var result = [];
  var i = 0;
  var key;
  while (names.length > i) {
    if (has(AllSymbols, key = names[i++]) && (IS_OP ? has(ObjectProto, key) : true)) result.push(AllSymbols[key]);
  } return result;
};

// 19.4.1.1 Symbol([description])
if (!USE_NATIVE) {
  $Symbol = function Symbol() {
    if (this instanceof $Symbol) throw TypeError('Symbol is not a constructor!');
    var tag = uid(arguments.length > 0 ? arguments[0] : undefined);
    var $set = function (value) {
      if (this === ObjectProto) $set.call(OPSymbols, value);
      if (has(this, HIDDEN) && has(this[HIDDEN], tag)) this[HIDDEN][tag] = false;
      setSymbolDesc(this, tag, createDesc(1, value));
    };
    if (DESCRIPTORS && setter) setSymbolDesc(ObjectProto, tag, { configurable: true, set: $set });
    return wrap(tag);
  };
  redefine($Symbol[PROTOTYPE], 'toString', function toString() {
    return this._k;
  });

  $GOPD.f = $getOwnPropertyDescriptor;
  $DP.f = $defineProperty;
  __webpack_require__(37).f = gOPNExt.f = $getOwnPropertyNames;
  __webpack_require__(48).f = $propertyIsEnumerable;
  __webpack_require__(53).f = $getOwnPropertySymbols;

  if (DESCRIPTORS && !__webpack_require__(30)) {
    redefine(ObjectProto, 'propertyIsEnumerable', $propertyIsEnumerable, true);
  }

  wksExt.f = function (name) {
    return wrap(wks(name));
  };
}

$export($export.G + $export.W + $export.F * !USE_NATIVE, { Symbol: $Symbol });

for (var es6Symbols = (
  // 19.4.2.2, 19.4.2.3, 19.4.2.4, 19.4.2.6, 19.4.2.8, 19.4.2.9, 19.4.2.10, 19.4.2.11, 19.4.2.12, 19.4.2.13, 19.4.2.14
  'hasInstance,isConcatSpreadable,iterator,match,replace,search,species,split,toPrimitive,toStringTag,unscopables'
).split(','), j = 0; es6Symbols.length > j;)wks(es6Symbols[j++]);

for (var wellKnownSymbols = $keys(wks.store), k = 0; wellKnownSymbols.length > k;) wksDefine(wellKnownSymbols[k++]);

$export($export.S + $export.F * !USE_NATIVE, 'Symbol', {
  // 19.4.2.1 Symbol.for(key)
  'for': function (key) {
    return has(SymbolRegistry, key += '')
      ? SymbolRegistry[key]
      : SymbolRegistry[key] = $Symbol(key);
  },
  // 19.4.2.5 Symbol.keyFor(sym)
  keyFor: function keyFor(sym) {
    if (!isSymbol(sym)) throw TypeError(sym + ' is not a symbol!');
    for (var key in SymbolRegistry) if (SymbolRegistry[key] === sym) return key;
  },
  useSetter: function () { setter = true; },
  useSimple: function () { setter = false; }
});

$export($export.S + $export.F * !USE_NATIVE, 'Object', {
  // 19.1.2.2 Object.create(O [, Properties])
  create: $create,
  // 19.1.2.4 Object.defineProperty(O, P, Attributes)
  defineProperty: $defineProperty,
  // 19.1.2.3 Object.defineProperties(O, Properties)
  defineProperties: $defineProperties,
  // 19.1.2.6 Object.getOwnPropertyDescriptor(O, P)
  getOwnPropertyDescriptor: $getOwnPropertyDescriptor,
  // 19.1.2.7 Object.getOwnPropertyNames(O)
  getOwnPropertyNames: $getOwnPropertyNames,
  // 19.1.2.8 Object.getOwnPropertySymbols(O)
  getOwnPropertySymbols: $getOwnPropertySymbols
});

// 24.3.2 JSON.stringify(value [, replacer [, space]])
$JSON && $export($export.S + $export.F * (!USE_NATIVE || $fails(function () {
  var S = $Symbol();
  // MS Edge converts symbol values to JSON as {}
  // WebKit converts symbol values to JSON as null
  // V8 throws on boxed symbols
  return _stringify([S]) != '[null]' || _stringify({ a: S }) != '{}' || _stringify(Object(S)) != '{}';
})), 'JSON', {
  stringify: function stringify(it) {
    var args = [it];
    var i = 1;
    var replacer, $replacer;
    while (arguments.length > i) args.push(arguments[i++]);
    $replacer = replacer = args[1];
    if (!isObject(replacer) && it === undefined || isSymbol(it)) return; // IE8 returns string on undefined
    if (!isArray(replacer)) replacer = function (key, value) {
      if (typeof $replacer == 'function') value = $replacer.call(this, key, value);
      if (!isSymbol(value)) return value;
    };
    args[1] = replacer;
    return _stringify.apply($JSON, args);
  }
});

// 19.4.3.4 Symbol.prototype[@@toPrimitive](hint)
$Symbol[PROTOTYPE][TO_PRIMITIVE] || __webpack_require__(11)($Symbol[PROTOTYPE], TO_PRIMITIVE, $Symbol[PROTOTYPE].valueOf);
// 19.4.3.5 Symbol.prototype[@@toStringTag]
setToStringTag($Symbol, 'Symbol');
// 20.2.1.9 Math[@@toStringTag]
setToStringTag(Math, 'Math', true);
// 24.3.3 JSON[@@toStringTag]
setToStringTag(global.JSON, 'JSON', true);


/***/ }),
/* 131 */
/***/ (function(module, exports, __webpack_require__) {

// all enumerable object keys, includes symbols
var getKeys = __webpack_require__(34);
var gOPS = __webpack_require__(53);
var pIE = __webpack_require__(48);
module.exports = function (it) {
  var result = getKeys(it);
  var getSymbols = gOPS.f;
  if (getSymbols) {
    var symbols = getSymbols(it);
    var isEnum = pIE.f;
    var i = 0;
    var key;
    while (symbols.length > i) if (isEnum.call(it, key = symbols[i++])) result.push(key);
  } return result;
};


/***/ }),
/* 132 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
// 19.1.2.4 / 15.2.3.6 Object.defineProperty(O, P, Attributes)
$export($export.S + $export.F * !__webpack_require__(7), 'Object', { defineProperty: __webpack_require__(8).f });


/***/ }),
/* 133 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
// 19.1.2.3 / 15.2.3.7 Object.defineProperties(O, Properties)
$export($export.S + $export.F * !__webpack_require__(7), 'Object', { defineProperties: __webpack_require__(96) });


/***/ }),
/* 134 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.6 Object.getOwnPropertyDescriptor(O, P)
var toIObject = __webpack_require__(15);
var $getOwnPropertyDescriptor = __webpack_require__(16).f;

__webpack_require__(24)('getOwnPropertyDescriptor', function () {
  return function getOwnPropertyDescriptor(it, key) {
    return $getOwnPropertyDescriptor(toIObject(it), key);
  };
});


/***/ }),
/* 135 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
// 19.1.2.2 / 15.2.3.5 Object.create(O [, Properties])
$export($export.S, 'Object', { create: __webpack_require__(36) });


/***/ }),
/* 136 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.9 Object.getPrototypeOf(O)
var toObject = __webpack_require__(9);
var $getPrototypeOf = __webpack_require__(17);

__webpack_require__(24)('getPrototypeOf', function () {
  return function getPrototypeOf(it) {
    return $getPrototypeOf(toObject(it));
  };
});


/***/ }),
/* 137 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.14 Object.keys(O)
var toObject = __webpack_require__(9);
var $keys = __webpack_require__(34);

__webpack_require__(24)('keys', function () {
  return function keys(it) {
    return $keys(toObject(it));
  };
});


/***/ }),
/* 138 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.7 Object.getOwnPropertyNames(O)
__webpack_require__(24)('getOwnPropertyNames', function () {
  return __webpack_require__(97).f;
});


/***/ }),
/* 139 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.5 Object.freeze(O)
var isObject = __webpack_require__(4);
var meta = __webpack_require__(29).onFreeze;

__webpack_require__(24)('freeze', function ($freeze) {
  return function freeze(it) {
    return $freeze && isObject(it) ? $freeze(meta(it)) : it;
  };
});


/***/ }),
/* 140 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.17 Object.seal(O)
var isObject = __webpack_require__(4);
var meta = __webpack_require__(29).onFreeze;

__webpack_require__(24)('seal', function ($seal) {
  return function seal(it) {
    return $seal && isObject(it) ? $seal(meta(it)) : it;
  };
});


/***/ }),
/* 141 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.15 Object.preventExtensions(O)
var isObject = __webpack_require__(4);
var meta = __webpack_require__(29).onFreeze;

__webpack_require__(24)('preventExtensions', function ($preventExtensions) {
  return function preventExtensions(it) {
    return $preventExtensions && isObject(it) ? $preventExtensions(meta(it)) : it;
  };
});


/***/ }),
/* 142 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.12 Object.isFrozen(O)
var isObject = __webpack_require__(4);

__webpack_require__(24)('isFrozen', function ($isFrozen) {
  return function isFrozen(it) {
    return isObject(it) ? $isFrozen ? $isFrozen(it) : false : true;
  };
});


/***/ }),
/* 143 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.13 Object.isSealed(O)
var isObject = __webpack_require__(4);

__webpack_require__(24)('isSealed', function ($isSealed) {
  return function isSealed(it) {
    return isObject(it) ? $isSealed ? $isSealed(it) : false : true;
  };
});


/***/ }),
/* 144 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.2.11 Object.isExtensible(O)
var isObject = __webpack_require__(4);

__webpack_require__(24)('isExtensible', function ($isExtensible) {
  return function isExtensible(it) {
    return isObject(it) ? $isExtensible ? $isExtensible(it) : true : false;
  };
});


/***/ }),
/* 145 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.3.1 Object.assign(target, source)
var $export = __webpack_require__(0);

$export($export.S + $export.F, 'Object', { assign: __webpack_require__(98) });


/***/ }),
/* 146 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.3.10 Object.is(value1, value2)
var $export = __webpack_require__(0);
$export($export.S, 'Object', { is: __webpack_require__(99) });


/***/ }),
/* 147 */
/***/ (function(module, exports, __webpack_require__) {

// 19.1.3.19 Object.setPrototypeOf(O, proto)
var $export = __webpack_require__(0);
$export($export.S, 'Object', { setPrototypeOf: __webpack_require__(71).set });


/***/ }),
/* 148 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 19.1.3.6 Object.prototype.toString()
var classof = __webpack_require__(43);
var test = {};
test[__webpack_require__(5)('toStringTag')] = 'z';
if (test + '' != '[object z]') {
  __webpack_require__(12)(Object.prototype, 'toString', function toString() {
    return '[object ' + classof(this) + ']';
  }, true);
}


/***/ }),
/* 149 */
/***/ (function(module, exports, __webpack_require__) {

// 19.2.3.2 / 15.3.4.5 Function.prototype.bind(thisArg, args...)
var $export = __webpack_require__(0);

$export($export.P, 'Function', { bind: __webpack_require__(100) });


/***/ }),
/* 150 */
/***/ (function(module, exports, __webpack_require__) {

var dP = __webpack_require__(8).f;
var FProto = Function.prototype;
var nameRE = /^\s*function ([^ (]*)/;
var NAME = 'name';

// 19.2.4.2 name
NAME in FProto || __webpack_require__(7) && dP(FProto, NAME, {
  configurable: true,
  get: function () {
    try {
      return ('' + this).match(nameRE)[1];
    } catch (e) {
      return '';
    }
  }
});


/***/ }),
/* 151 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var isObject = __webpack_require__(4);
var getPrototypeOf = __webpack_require__(17);
var HAS_INSTANCE = __webpack_require__(5)('hasInstance');
var FunctionProto = Function.prototype;
// 19.2.3.6 Function.prototype[@@hasInstance](V)
if (!(HAS_INSTANCE in FunctionProto)) __webpack_require__(8).f(FunctionProto, HAS_INSTANCE, { value: function (O) {
  if (typeof this != 'function' || !isObject(O)) return false;
  if (!isObject(this.prototype)) return O instanceof this;
  // for environment w/o native `@@hasInstance` logic enough `instanceof`, but add this:
  while (O = getPrototypeOf(O)) if (this.prototype === O) return true;
  return false;
} });


/***/ }),
/* 152 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var global = __webpack_require__(2);
var has = __webpack_require__(14);
var cof = __webpack_require__(19);
var inheritIfRequired = __webpack_require__(72);
var toPrimitive = __webpack_require__(22);
var fails = __webpack_require__(3);
var gOPN = __webpack_require__(37).f;
var gOPD = __webpack_require__(16).f;
var dP = __webpack_require__(8).f;
var $trim = __webpack_require__(44).trim;
var NUMBER = 'Number';
var $Number = global[NUMBER];
var Base = $Number;
var proto = $Number.prototype;
// Opera ~12 has broken Object#toString
var BROKEN_COF = cof(__webpack_require__(36)(proto)) == NUMBER;
var TRIM = 'trim' in String.prototype;

// 7.1.3 ToNumber(argument)
var toNumber = function (argument) {
  var it = toPrimitive(argument, false);
  if (typeof it == 'string' && it.length > 2) {
    it = TRIM ? it.trim() : $trim(it, 3);
    var first = it.charCodeAt(0);
    var third, radix, maxCode;
    if (first === 43 || first === 45) {
      third = it.charCodeAt(2);
      if (third === 88 || third === 120) return NaN; // Number('+0x1') should be NaN, old V8 fix
    } else if (first === 48) {
      switch (it.charCodeAt(1)) {
        case 66: case 98: radix = 2; maxCode = 49; break; // fast equal /^0b[01]+$/i
        case 79: case 111: radix = 8; maxCode = 55; break; // fast equal /^0o[0-7]+$/i
        default: return +it;
      }
      for (var digits = it.slice(2), i = 0, l = digits.length, code; i < l; i++) {
        code = digits.charCodeAt(i);
        // parseInt parses a string to a first unavailable symbol
        // but ToNumber should return NaN if a string contains unavailable symbols
        if (code < 48 || code > maxCode) return NaN;
      } return parseInt(digits, radix);
    }
  } return +it;
};

if (!$Number(' 0o1') || !$Number('0b1') || $Number('+0x1')) {
  $Number = function Number(value) {
    var it = arguments.length < 1 ? 0 : value;
    var that = this;
    return that instanceof $Number
      // check on 1..constructor(foo) case
      && (BROKEN_COF ? fails(function () { proto.valueOf.call(that); }) : cof(that) != NUMBER)
        ? inheritIfRequired(new Base(toNumber(it)), that, $Number) : toNumber(it);
  };
  for (var keys = __webpack_require__(7) ? gOPN(Base) : (
    // ES3:
    'MAX_VALUE,MIN_VALUE,NaN,NEGATIVE_INFINITY,POSITIVE_INFINITY,' +
    // ES6 (in case, if modules with ES6 Number statics required before):
    'EPSILON,isFinite,isInteger,isNaN,isSafeInteger,MAX_SAFE_INTEGER,' +
    'MIN_SAFE_INTEGER,parseFloat,parseInt,isInteger'
  ).split(','), j = 0, key; keys.length > j; j++) {
    if (has(Base, key = keys[j]) && !has($Number, key)) {
      dP($Number, key, gOPD(Base, key));
    }
  }
  $Number.prototype = proto;
  proto.constructor = $Number;
  __webpack_require__(12)(global, NUMBER, $Number);
}


/***/ }),
/* 153 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var toInteger = __webpack_require__(20);
var aNumberValue = __webpack_require__(102);
var repeat = __webpack_require__(74);
var $toFixed = 1.0.toFixed;
var floor = Math.floor;
var data = [0, 0, 0, 0, 0, 0];
var ERROR = 'Number.toFixed: incorrect invocation!';
var ZERO = '0';

var multiply = function (n, c) {
  var i = -1;
  var c2 = c;
  while (++i < 6) {
    c2 += n * data[i];
    data[i] = c2 % 1e7;
    c2 = floor(c2 / 1e7);
  }
};
var divide = function (n) {
  var i = 6;
  var c = 0;
  while (--i >= 0) {
    c += data[i];
    data[i] = floor(c / n);
    c = (c % n) * 1e7;
  }
};
var numToString = function () {
  var i = 6;
  var s = '';
  while (--i >= 0) {
    if (s !== '' || i === 0 || data[i] !== 0) {
      var t = String(data[i]);
      s = s === '' ? t : s + repeat.call(ZERO, 7 - t.length) + t;
    }
  } return s;
};
var pow = function (x, n, acc) {
  return n === 0 ? acc : n % 2 === 1 ? pow(x, n - 1, acc * x) : pow(x * x, n / 2, acc);
};
var log = function (x) {
  var n = 0;
  var x2 = x;
  while (x2 >= 4096) {
    n += 12;
    x2 /= 4096;
  }
  while (x2 >= 2) {
    n += 1;
    x2 /= 2;
  } return n;
};

$export($export.P + $export.F * (!!$toFixed && (
  0.00008.toFixed(3) !== '0.000' ||
  0.9.toFixed(0) !== '1' ||
  1.255.toFixed(2) !== '1.25' ||
  1000000000000000128.0.toFixed(0) !== '1000000000000000128'
) || !__webpack_require__(3)(function () {
  // V8 ~ Android 4.3-
  $toFixed.call({});
})), 'Number', {
  toFixed: function toFixed(fractionDigits) {
    var x = aNumberValue(this, ERROR);
    var f = toInteger(fractionDigits);
    var s = '';
    var m = ZERO;
    var e, z, j, k;
    if (f < 0 || f > 20) throw RangeError(ERROR);
    // eslint-disable-next-line no-self-compare
    if (x != x) return 'NaN';
    if (x <= -1e21 || x >= 1e21) return String(x);
    if (x < 0) {
      s = '-';
      x = -x;
    }
    if (x > 1e-21) {
      e = log(x * pow(2, 69, 1)) - 69;
      z = e < 0 ? x * pow(2, -e, 1) : x / pow(2, e, 1);
      z *= 0x10000000000000;
      e = 52 - e;
      if (e > 0) {
        multiply(0, z);
        j = f;
        while (j >= 7) {
          multiply(1e7, 0);
          j -= 7;
        }
        multiply(pow(10, j, 1), 0);
        j = e - 1;
        while (j >= 23) {
          divide(1 << 23);
          j -= 23;
        }
        divide(1 << j);
        multiply(1, 1);
        divide(2);
        m = numToString();
      } else {
        multiply(0, z);
        multiply(1 << -e, 0);
        m = numToString() + repeat.call(ZERO, f);
      }
    }
    if (f > 0) {
      k = m.length;
      m = s + (k <= f ? '0.' + repeat.call(ZERO, f - k) + m : m.slice(0, k - f) + '.' + m.slice(k - f));
    } else {
      m = s + m;
    } return m;
  }
});


/***/ }),
/* 154 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $fails = __webpack_require__(3);
var aNumberValue = __webpack_require__(102);
var $toPrecision = 1.0.toPrecision;

$export($export.P + $export.F * ($fails(function () {
  // IE7-
  return $toPrecision.call(1, undefined) !== '1';
}) || !$fails(function () {
  // V8 ~ Android 4.3-
  $toPrecision.call({});
})), 'Number', {
  toPrecision: function toPrecision(precision) {
    var that = aNumberValue(this, 'Number#toPrecision: incorrect invocation!');
    return precision === undefined ? $toPrecision.call(that) : $toPrecision.call(that, precision);
  }
});


/***/ }),
/* 155 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.1 Number.EPSILON
var $export = __webpack_require__(0);

$export($export.S, 'Number', { EPSILON: Math.pow(2, -52) });


/***/ }),
/* 156 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.2 Number.isFinite(number)
var $export = __webpack_require__(0);
var _isFinite = __webpack_require__(2).isFinite;

$export($export.S, 'Number', {
  isFinite: function isFinite(it) {
    return typeof it == 'number' && _isFinite(it);
  }
});


/***/ }),
/* 157 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.3 Number.isInteger(number)
var $export = __webpack_require__(0);

$export($export.S, 'Number', { isInteger: __webpack_require__(103) });


/***/ }),
/* 158 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.4 Number.isNaN(number)
var $export = __webpack_require__(0);

$export($export.S, 'Number', {
  isNaN: function isNaN(number) {
    // eslint-disable-next-line no-self-compare
    return number != number;
  }
});


/***/ }),
/* 159 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.5 Number.isSafeInteger(number)
var $export = __webpack_require__(0);
var isInteger = __webpack_require__(103);
var abs = Math.abs;

$export($export.S, 'Number', {
  isSafeInteger: function isSafeInteger(number) {
    return isInteger(number) && abs(number) <= 0x1fffffffffffff;
  }
});


/***/ }),
/* 160 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.6 Number.MAX_SAFE_INTEGER
var $export = __webpack_require__(0);

$export($export.S, 'Number', { MAX_SAFE_INTEGER: 0x1fffffffffffff });


/***/ }),
/* 161 */
/***/ (function(module, exports, __webpack_require__) {

// 20.1.2.10 Number.MIN_SAFE_INTEGER
var $export = __webpack_require__(0);

$export($export.S, 'Number', { MIN_SAFE_INTEGER: -0x1fffffffffffff });


/***/ }),
/* 162 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var $parseFloat = __webpack_require__(104);
// 20.1.2.12 Number.parseFloat(string)
$export($export.S + $export.F * (Number.parseFloat != $parseFloat), 'Number', { parseFloat: $parseFloat });


/***/ }),
/* 163 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var $parseInt = __webpack_require__(105);
// 20.1.2.13 Number.parseInt(string, radix)
$export($export.S + $export.F * (Number.parseInt != $parseInt), 'Number', { parseInt: $parseInt });


/***/ }),
/* 164 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var $parseInt = __webpack_require__(105);
// 18.2.5 parseInt(string, radix)
$export($export.G + $export.F * (parseInt != $parseInt), { parseInt: $parseInt });


/***/ }),
/* 165 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var $parseFloat = __webpack_require__(104);
// 18.2.4 parseFloat(string)
$export($export.G + $export.F * (parseFloat != $parseFloat), { parseFloat: $parseFloat });


/***/ }),
/* 166 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.3 Math.acosh(x)
var $export = __webpack_require__(0);
var log1p = __webpack_require__(106);
var sqrt = Math.sqrt;
var $acosh = Math.acosh;

$export($export.S + $export.F * !($acosh
  // V8 bug: https://code.google.com/p/v8/issues/detail?id=3509
  && Math.floor($acosh(Number.MAX_VALUE)) == 710
  // Tor Browser bug: Math.acosh(Infinity) -> NaN
  && $acosh(Infinity) == Infinity
), 'Math', {
  acosh: function acosh(x) {
    return (x = +x) < 1 ? NaN : x > 94906265.62425156
      ? Math.log(x) + Math.LN2
      : log1p(x - 1 + sqrt(x - 1) * sqrt(x + 1));
  }
});


/***/ }),
/* 167 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.5 Math.asinh(x)
var $export = __webpack_require__(0);
var $asinh = Math.asinh;

function asinh(x) {
  return !isFinite(x = +x) || x == 0 ? x : x < 0 ? -asinh(-x) : Math.log(x + Math.sqrt(x * x + 1));
}

// Tor Browser bug: Math.asinh(0) -> -0
$export($export.S + $export.F * !($asinh && 1 / $asinh(0) > 0), 'Math', { asinh: asinh });


/***/ }),
/* 168 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.7 Math.atanh(x)
var $export = __webpack_require__(0);
var $atanh = Math.atanh;

// Tor Browser bug: Math.atanh(-0) -> 0
$export($export.S + $export.F * !($atanh && 1 / $atanh(-0) < 0), 'Math', {
  atanh: function atanh(x) {
    return (x = +x) == 0 ? x : Math.log((1 + x) / (1 - x)) / 2;
  }
});


/***/ }),
/* 169 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.9 Math.cbrt(x)
var $export = __webpack_require__(0);
var sign = __webpack_require__(75);

$export($export.S, 'Math', {
  cbrt: function cbrt(x) {
    return sign(x = +x) * Math.pow(Math.abs(x), 1 / 3);
  }
});


/***/ }),
/* 170 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.11 Math.clz32(x)
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  clz32: function clz32(x) {
    return (x >>>= 0) ? 31 - Math.floor(Math.log(x + 0.5) * Math.LOG2E) : 32;
  }
});


/***/ }),
/* 171 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.12 Math.cosh(x)
var $export = __webpack_require__(0);
var exp = Math.exp;

$export($export.S, 'Math', {
  cosh: function cosh(x) {
    return (exp(x = +x) + exp(-x)) / 2;
  }
});


/***/ }),
/* 172 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.14 Math.expm1(x)
var $export = __webpack_require__(0);
var $expm1 = __webpack_require__(76);

$export($export.S + $export.F * ($expm1 != Math.expm1), 'Math', { expm1: $expm1 });


/***/ }),
/* 173 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.16 Math.fround(x)
var $export = __webpack_require__(0);

$export($export.S, 'Math', { fround: __webpack_require__(107) });


/***/ }),
/* 174 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.17 Math.hypot([value1[, value2[, … ]]])
var $export = __webpack_require__(0);
var abs = Math.abs;

$export($export.S, 'Math', {
  hypot: function hypot(value1, value2) { // eslint-disable-line no-unused-vars
    var sum = 0;
    var i = 0;
    var aLen = arguments.length;
    var larg = 0;
    var arg, div;
    while (i < aLen) {
      arg = abs(arguments[i++]);
      if (larg < arg) {
        div = larg / arg;
        sum = sum * div * div + 1;
        larg = arg;
      } else if (arg > 0) {
        div = arg / larg;
        sum += div * div;
      } else sum += arg;
    }
    return larg === Infinity ? Infinity : larg * Math.sqrt(sum);
  }
});


/***/ }),
/* 175 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.18 Math.imul(x, y)
var $export = __webpack_require__(0);
var $imul = Math.imul;

// some WebKit versions fails with big numbers, some has wrong arity
$export($export.S + $export.F * __webpack_require__(3)(function () {
  return $imul(0xffffffff, 5) != -5 || $imul.length != 2;
}), 'Math', {
  imul: function imul(x, y) {
    var UINT16 = 0xffff;
    var xn = +x;
    var yn = +y;
    var xl = UINT16 & xn;
    var yl = UINT16 & yn;
    return 0 | xl * yl + ((UINT16 & xn >>> 16) * yl + xl * (UINT16 & yn >>> 16) << 16 >>> 0);
  }
});


/***/ }),
/* 176 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.21 Math.log10(x)
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  log10: function log10(x) {
    return Math.log(x) * Math.LOG10E;
  }
});


/***/ }),
/* 177 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.20 Math.log1p(x)
var $export = __webpack_require__(0);

$export($export.S, 'Math', { log1p: __webpack_require__(106) });


/***/ }),
/* 178 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.22 Math.log2(x)
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  log2: function log2(x) {
    return Math.log(x) / Math.LN2;
  }
});


/***/ }),
/* 179 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.28 Math.sign(x)
var $export = __webpack_require__(0);

$export($export.S, 'Math', { sign: __webpack_require__(75) });


/***/ }),
/* 180 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.30 Math.sinh(x)
var $export = __webpack_require__(0);
var expm1 = __webpack_require__(76);
var exp = Math.exp;

// V8 near Chromium 38 has a problem with very small numbers
$export($export.S + $export.F * __webpack_require__(3)(function () {
  return !Math.sinh(-2e-17) != -2e-17;
}), 'Math', {
  sinh: function sinh(x) {
    return Math.abs(x = +x) < 1
      ? (expm1(x) - expm1(-x)) / 2
      : (exp(x - 1) - exp(-x - 1)) * (Math.E / 2);
  }
});


/***/ }),
/* 181 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.33 Math.tanh(x)
var $export = __webpack_require__(0);
var expm1 = __webpack_require__(76);
var exp = Math.exp;

$export($export.S, 'Math', {
  tanh: function tanh(x) {
    var a = expm1(x = +x);
    var b = expm1(-x);
    return a == Infinity ? 1 : b == Infinity ? -1 : (a - b) / (exp(x) + exp(-x));
  }
});


/***/ }),
/* 182 */
/***/ (function(module, exports, __webpack_require__) {

// 20.2.2.34 Math.trunc(x)
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  trunc: function trunc(it) {
    return (it > 0 ? Math.floor : Math.ceil)(it);
  }
});


/***/ }),
/* 183 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var toAbsoluteIndex = __webpack_require__(35);
var fromCharCode = String.fromCharCode;
var $fromCodePoint = String.fromCodePoint;

// length should be 1, old FF problem
$export($export.S + $export.F * (!!$fromCodePoint && $fromCodePoint.length != 1), 'String', {
  // 21.1.2.2 String.fromCodePoint(...codePoints)
  fromCodePoint: function fromCodePoint(x) { // eslint-disable-line no-unused-vars
    var res = [];
    var aLen = arguments.length;
    var i = 0;
    var code;
    while (aLen > i) {
      code = +arguments[i++];
      if (toAbsoluteIndex(code, 0x10ffff) !== code) throw RangeError(code + ' is not a valid code point');
      res.push(code < 0x10000
        ? fromCharCode(code)
        : fromCharCode(((code -= 0x10000) >> 10) + 0xd800, code % 0x400 + 0xdc00)
      );
    } return res.join('');
  }
});


/***/ }),
/* 184 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var toIObject = __webpack_require__(15);
var toLength = __webpack_require__(6);

$export($export.S, 'String', {
  // 21.1.2.4 String.raw(callSite, ...substitutions)
  raw: function raw(callSite) {
    var tpl = toIObject(callSite.raw);
    var len = toLength(tpl.length);
    var aLen = arguments.length;
    var res = [];
    var i = 0;
    while (len > i) {
      res.push(String(tpl[i++]));
      if (i < aLen) res.push(String(arguments[i]));
    } return res.join('');
  }
});


/***/ }),
/* 185 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 21.1.3.25 String.prototype.trim()
__webpack_require__(44)('trim', function ($trim) {
  return function trim() {
    return $trim(this, 3);
  };
});


/***/ }),
/* 186 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $at = __webpack_require__(55)(false);
$export($export.P, 'String', {
  // 21.1.3.3 String.prototype.codePointAt(pos)
  codePointAt: function codePointAt(pos) {
    return $at(this, pos);
  }
});


/***/ }),
/* 187 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// 21.1.3.6 String.prototype.endsWith(searchString [, endPosition])

var $export = __webpack_require__(0);
var toLength = __webpack_require__(6);
var context = __webpack_require__(77);
var ENDS_WITH = 'endsWith';
var $endsWith = ''[ENDS_WITH];

$export($export.P + $export.F * __webpack_require__(78)(ENDS_WITH), 'String', {
  endsWith: function endsWith(searchString /* , endPosition = @length */) {
    var that = context(this, searchString, ENDS_WITH);
    var endPosition = arguments.length > 1 ? arguments[1] : undefined;
    var len = toLength(that.length);
    var end = endPosition === undefined ? len : Math.min(toLength(endPosition), len);
    var search = String(searchString);
    return $endsWith
      ? $endsWith.call(that, search, end)
      : that.slice(end - search.length, end) === search;
  }
});


/***/ }),
/* 188 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// 21.1.3.7 String.prototype.includes(searchString, position = 0)

var $export = __webpack_require__(0);
var context = __webpack_require__(77);
var INCLUDES = 'includes';

$export($export.P + $export.F * __webpack_require__(78)(INCLUDES), 'String', {
  includes: function includes(searchString /* , position = 0 */) {
    return !!~context(this, searchString, INCLUDES)
      .indexOf(searchString, arguments.length > 1 ? arguments[1] : undefined);
  }
});


/***/ }),
/* 189 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);

$export($export.P, 'String', {
  // 21.1.3.13 String.prototype.repeat(count)
  repeat: __webpack_require__(74)
});


/***/ }),
/* 190 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// 21.1.3.18 String.prototype.startsWith(searchString [, position ])

var $export = __webpack_require__(0);
var toLength = __webpack_require__(6);
var context = __webpack_require__(77);
var STARTS_WITH = 'startsWith';
var $startsWith = ''[STARTS_WITH];

$export($export.P + $export.F * __webpack_require__(78)(STARTS_WITH), 'String', {
  startsWith: function startsWith(searchString /* , position = 0 */) {
    var that = context(this, searchString, STARTS_WITH);
    var index = toLength(Math.min(arguments.length > 1 ? arguments[1] : undefined, that.length));
    var search = String(searchString);
    return $startsWith
      ? $startsWith.call(that, search, index)
      : that.slice(index, index + search.length) === search;
  }
});


/***/ }),
/* 191 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $at = __webpack_require__(55)(true);

// 21.1.3.27 String.prototype[@@iterator]()
__webpack_require__(79)(String, 'String', function (iterated) {
  this._t = String(iterated); // target
  this._i = 0;                // next index
// 21.1.5.2.1 %StringIteratorPrototype%.next()
}, function () {
  var O = this._t;
  var index = this._i;
  var point;
  if (index >= O.length) return { value: undefined, done: true };
  point = $at(O, index);
  this._i += point.length;
  return { value: point, done: false };
});


/***/ }),
/* 192 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.2 String.prototype.anchor(name)
__webpack_require__(13)('anchor', function (createHTML) {
  return function anchor(name) {
    return createHTML(this, 'a', 'name', name);
  };
});


/***/ }),
/* 193 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.3 String.prototype.big()
__webpack_require__(13)('big', function (createHTML) {
  return function big() {
    return createHTML(this, 'big', '', '');
  };
});


/***/ }),
/* 194 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.4 String.prototype.blink()
__webpack_require__(13)('blink', function (createHTML) {
  return function blink() {
    return createHTML(this, 'blink', '', '');
  };
});


/***/ }),
/* 195 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.5 String.prototype.bold()
__webpack_require__(13)('bold', function (createHTML) {
  return function bold() {
    return createHTML(this, 'b', '', '');
  };
});


/***/ }),
/* 196 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.6 String.prototype.fixed()
__webpack_require__(13)('fixed', function (createHTML) {
  return function fixed() {
    return createHTML(this, 'tt', '', '');
  };
});


/***/ }),
/* 197 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.7 String.prototype.fontcolor(color)
__webpack_require__(13)('fontcolor', function (createHTML) {
  return function fontcolor(color) {
    return createHTML(this, 'font', 'color', color);
  };
});


/***/ }),
/* 198 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.8 String.prototype.fontsize(size)
__webpack_require__(13)('fontsize', function (createHTML) {
  return function fontsize(size) {
    return createHTML(this, 'font', 'size', size);
  };
});


/***/ }),
/* 199 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.9 String.prototype.italics()
__webpack_require__(13)('italics', function (createHTML) {
  return function italics() {
    return createHTML(this, 'i', '', '');
  };
});


/***/ }),
/* 200 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.10 String.prototype.link(url)
__webpack_require__(13)('link', function (createHTML) {
  return function link(url) {
    return createHTML(this, 'a', 'href', url);
  };
});


/***/ }),
/* 201 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.11 String.prototype.small()
__webpack_require__(13)('small', function (createHTML) {
  return function small() {
    return createHTML(this, 'small', '', '');
  };
});


/***/ }),
/* 202 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.12 String.prototype.strike()
__webpack_require__(13)('strike', function (createHTML) {
  return function strike() {
    return createHTML(this, 'strike', '', '');
  };
});


/***/ }),
/* 203 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.13 String.prototype.sub()
__webpack_require__(13)('sub', function (createHTML) {
  return function sub() {
    return createHTML(this, 'sub', '', '');
  };
});


/***/ }),
/* 204 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// B.2.3.14 String.prototype.sup()
__webpack_require__(13)('sup', function (createHTML) {
  return function sup() {
    return createHTML(this, 'sup', '', '');
  };
});


/***/ }),
/* 205 */
/***/ (function(module, exports, __webpack_require__) {

// 22.1.2.2 / 15.4.3.2 Array.isArray(arg)
var $export = __webpack_require__(0);

$export($export.S, 'Array', { isArray: __webpack_require__(54) });


/***/ }),
/* 206 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var ctx = __webpack_require__(18);
var $export = __webpack_require__(0);
var toObject = __webpack_require__(9);
var call = __webpack_require__(108);
var isArrayIter = __webpack_require__(81);
var toLength = __webpack_require__(6);
var createProperty = __webpack_require__(82);
var getIterFn = __webpack_require__(83);

$export($export.S + $export.F * !__webpack_require__(57)(function (iter) { Array.from(iter); }), 'Array', {
  // 22.1.2.1 Array.from(arrayLike, mapfn = undefined, thisArg = undefined)
  from: function from(arrayLike /* , mapfn = undefined, thisArg = undefined */) {
    var O = toObject(arrayLike);
    var C = typeof this == 'function' ? this : Array;
    var aLen = arguments.length;
    var mapfn = aLen > 1 ? arguments[1] : undefined;
    var mapping = mapfn !== undefined;
    var index = 0;
    var iterFn = getIterFn(O);
    var length, result, step, iterator;
    if (mapping) mapfn = ctx(mapfn, aLen > 2 ? arguments[2] : undefined, 2);
    // if object isn't iterable or it's array with default iterator - use simple case
    if (iterFn != undefined && !(C == Array && isArrayIter(iterFn))) {
      for (iterator = iterFn.call(O), result = new C(); !(step = iterator.next()).done; index++) {
        createProperty(result, index, mapping ? call(iterator, mapfn, [step.value, index], true) : step.value);
      }
    } else {
      length = toLength(O.length);
      for (result = new C(length); length > index; index++) {
        createProperty(result, index, mapping ? mapfn(O[index], index) : O[index]);
      }
    }
    result.length = index;
    return result;
  }
});


/***/ }),
/* 207 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var createProperty = __webpack_require__(82);

// WebKit Array.of isn't generic
$export($export.S + $export.F * __webpack_require__(3)(function () {
  function F() { /* empty */ }
  return !(Array.of.call(F) instanceof F);
}), 'Array', {
  // 22.1.2.3 Array.of( ...items)
  of: function of(/* ...args */) {
    var index = 0;
    var aLen = arguments.length;
    var result = new (typeof this == 'function' ? this : Array)(aLen);
    while (aLen > index) createProperty(result, index, arguments[index++]);
    result.length = aLen;
    return result;
  }
});


/***/ }),
/* 208 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 22.1.3.13 Array.prototype.join(separator)
var $export = __webpack_require__(0);
var toIObject = __webpack_require__(15);
var arrayJoin = [].join;

// fallback for not array-like strings
$export($export.P + $export.F * (__webpack_require__(47) != Object || !__webpack_require__(21)(arrayJoin)), 'Array', {
  join: function join(separator) {
    return arrayJoin.call(toIObject(this), separator === undefined ? ',' : separator);
  }
});


/***/ }),
/* 209 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var html = __webpack_require__(70);
var cof = __webpack_require__(19);
var toAbsoluteIndex = __webpack_require__(35);
var toLength = __webpack_require__(6);
var arraySlice = [].slice;

// fallback for not array-like ES3 strings and DOM objects
$export($export.P + $export.F * __webpack_require__(3)(function () {
  if (html) arraySlice.call(html);
}), 'Array', {
  slice: function slice(begin, end) {
    var len = toLength(this.length);
    var klass = cof(this);
    end = end === undefined ? len : end;
    if (klass == 'Array') return arraySlice.call(this, begin, end);
    var start = toAbsoluteIndex(begin, len);
    var upTo = toAbsoluteIndex(end, len);
    var size = toLength(upTo - start);
    var cloned = new Array(size);
    var i = 0;
    for (; i < size; i++) cloned[i] = klass == 'String'
      ? this.charAt(start + i)
      : this[start + i];
    return cloned;
  }
});


/***/ }),
/* 210 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var aFunction = __webpack_require__(10);
var toObject = __webpack_require__(9);
var fails = __webpack_require__(3);
var $sort = [].sort;
var test = [1, 2, 3];

$export($export.P + $export.F * (fails(function () {
  // IE8-
  test.sort(undefined);
}) || !fails(function () {
  // V8 bug
  test.sort(null);
  // Old WebKit
}) || !__webpack_require__(21)($sort)), 'Array', {
  // 22.1.3.25 Array.prototype.sort(comparefn)
  sort: function sort(comparefn) {
    return comparefn === undefined
      ? $sort.call(toObject(this))
      : $sort.call(toObject(this), aFunction(comparefn));
  }
});


/***/ }),
/* 211 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $forEach = __webpack_require__(25)(0);
var STRICT = __webpack_require__(21)([].forEach, true);

$export($export.P + $export.F * !STRICT, 'Array', {
  // 22.1.3.10 / 15.4.4.18 Array.prototype.forEach(callbackfn [, thisArg])
  forEach: function forEach(callbackfn /* , thisArg */) {
    return $forEach(this, callbackfn, arguments[1]);
  }
});


/***/ }),
/* 212 */
/***/ (function(module, exports, __webpack_require__) {

var isObject = __webpack_require__(4);
var isArray = __webpack_require__(54);
var SPECIES = __webpack_require__(5)('species');

module.exports = function (original) {
  var C;
  if (isArray(original)) {
    C = original.constructor;
    // cross-realm fallback
    if (typeof C == 'function' && (C === Array || isArray(C.prototype))) C = undefined;
    if (isObject(C)) {
      C = C[SPECIES];
      if (C === null) C = undefined;
    }
  } return C === undefined ? Array : C;
};


/***/ }),
/* 213 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $map = __webpack_require__(25)(1);

$export($export.P + $export.F * !__webpack_require__(21)([].map, true), 'Array', {
  // 22.1.3.15 / 15.4.4.19 Array.prototype.map(callbackfn [, thisArg])
  map: function map(callbackfn /* , thisArg */) {
    return $map(this, callbackfn, arguments[1]);
  }
});


/***/ }),
/* 214 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $filter = __webpack_require__(25)(2);

$export($export.P + $export.F * !__webpack_require__(21)([].filter, true), 'Array', {
  // 22.1.3.7 / 15.4.4.20 Array.prototype.filter(callbackfn [, thisArg])
  filter: function filter(callbackfn /* , thisArg */) {
    return $filter(this, callbackfn, arguments[1]);
  }
});


/***/ }),
/* 215 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $some = __webpack_require__(25)(3);

$export($export.P + $export.F * !__webpack_require__(21)([].some, true), 'Array', {
  // 22.1.3.23 / 15.4.4.17 Array.prototype.some(callbackfn [, thisArg])
  some: function some(callbackfn /* , thisArg */) {
    return $some(this, callbackfn, arguments[1]);
  }
});


/***/ }),
/* 216 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $every = __webpack_require__(25)(4);

$export($export.P + $export.F * !__webpack_require__(21)([].every, true), 'Array', {
  // 22.1.3.5 / 15.4.4.16 Array.prototype.every(callbackfn [, thisArg])
  every: function every(callbackfn /* , thisArg */) {
    return $every(this, callbackfn, arguments[1]);
  }
});


/***/ }),
/* 217 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $reduce = __webpack_require__(109);

$export($export.P + $export.F * !__webpack_require__(21)([].reduce, true), 'Array', {
  // 22.1.3.18 / 15.4.4.21 Array.prototype.reduce(callbackfn [, initialValue])
  reduce: function reduce(callbackfn /* , initialValue */) {
    return $reduce(this, callbackfn, arguments.length, arguments[1], false);
  }
});


/***/ }),
/* 218 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $reduce = __webpack_require__(109);

$export($export.P + $export.F * !__webpack_require__(21)([].reduceRight, true), 'Array', {
  // 22.1.3.19 / 15.4.4.22 Array.prototype.reduceRight(callbackfn [, initialValue])
  reduceRight: function reduceRight(callbackfn /* , initialValue */) {
    return $reduce(this, callbackfn, arguments.length, arguments[1], true);
  }
});


/***/ }),
/* 219 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $indexOf = __webpack_require__(52)(false);
var $native = [].indexOf;
var NEGATIVE_ZERO = !!$native && 1 / [1].indexOf(1, -0) < 0;

$export($export.P + $export.F * (NEGATIVE_ZERO || !__webpack_require__(21)($native)), 'Array', {
  // 22.1.3.11 / 15.4.4.14 Array.prototype.indexOf(searchElement [, fromIndex])
  indexOf: function indexOf(searchElement /* , fromIndex = 0 */) {
    return NEGATIVE_ZERO
      // convert -0 to +0
      ? $native.apply(this, arguments) || 0
      : $indexOf(this, searchElement, arguments[1]);
  }
});


/***/ }),
/* 220 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var toIObject = __webpack_require__(15);
var toInteger = __webpack_require__(20);
var toLength = __webpack_require__(6);
var $native = [].lastIndexOf;
var NEGATIVE_ZERO = !!$native && 1 / [1].lastIndexOf(1, -0) < 0;

$export($export.P + $export.F * (NEGATIVE_ZERO || !__webpack_require__(21)($native)), 'Array', {
  // 22.1.3.14 / 15.4.4.15 Array.prototype.lastIndexOf(searchElement [, fromIndex])
  lastIndexOf: function lastIndexOf(searchElement /* , fromIndex = @[*-1] */) {
    // convert -0 to +0
    if (NEGATIVE_ZERO) return $native.apply(this, arguments) || 0;
    var O = toIObject(this);
    var length = toLength(O.length);
    var index = length - 1;
    if (arguments.length > 1) index = Math.min(index, toInteger(arguments[1]));
    if (index < 0) index = length + index;
    for (;index >= 0; index--) if (index in O) if (O[index] === searchElement) return index || 0;
    return -1;
  }
});


/***/ }),
/* 221 */
/***/ (function(module, exports, __webpack_require__) {

// 22.1.3.3 Array.prototype.copyWithin(target, start, end = this.length)
var $export = __webpack_require__(0);

$export($export.P, 'Array', { copyWithin: __webpack_require__(110) });

__webpack_require__(31)('copyWithin');


/***/ }),
/* 222 */
/***/ (function(module, exports, __webpack_require__) {

// 22.1.3.6 Array.prototype.fill(value, start = 0, end = this.length)
var $export = __webpack_require__(0);

$export($export.P, 'Array', { fill: __webpack_require__(85) });

__webpack_require__(31)('fill');


/***/ }),
/* 223 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 22.1.3.8 Array.prototype.find(predicate, thisArg = undefined)
var $export = __webpack_require__(0);
var $find = __webpack_require__(25)(5);
var KEY = 'find';
var forced = true;
// Shouldn't skip holes
if (KEY in []) Array(1)[KEY](function () { forced = false; });
$export($export.P + $export.F * forced, 'Array', {
  find: function find(callbackfn /* , that = undefined */) {
    return $find(this, callbackfn, arguments.length > 1 ? arguments[1] : undefined);
  }
});
__webpack_require__(31)(KEY);


/***/ }),
/* 224 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 22.1.3.9 Array.prototype.findIndex(predicate, thisArg = undefined)
var $export = __webpack_require__(0);
var $find = __webpack_require__(25)(6);
var KEY = 'findIndex';
var forced = true;
// Shouldn't skip holes
if (KEY in []) Array(1)[KEY](function () { forced = false; });
$export($export.P + $export.F * forced, 'Array', {
  findIndex: function findIndex(callbackfn /* , that = undefined */) {
    return $find(this, callbackfn, arguments.length > 1 ? arguments[1] : undefined);
  }
});
__webpack_require__(31)(KEY);


/***/ }),
/* 225 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(38)('Array');


/***/ }),
/* 226 */
/***/ (function(module, exports, __webpack_require__) {

var global = __webpack_require__(2);
var inheritIfRequired = __webpack_require__(72);
var dP = __webpack_require__(8).f;
var gOPN = __webpack_require__(37).f;
var isRegExp = __webpack_require__(56);
var $flags = __webpack_require__(49);
var $RegExp = global.RegExp;
var Base = $RegExp;
var proto = $RegExp.prototype;
var re1 = /a/g;
var re2 = /a/g;
// "new" creates a new object, old webkit buggy here
var CORRECT_NEW = new $RegExp(re1) !== re1;

if (__webpack_require__(7) && (!CORRECT_NEW || __webpack_require__(3)(function () {
  re2[__webpack_require__(5)('match')] = false;
  // RegExp constructor can alter flags and IsRegExp works correct with @@match
  return $RegExp(re1) != re1 || $RegExp(re2) == re2 || $RegExp(re1, 'i') != '/a/i';
}))) {
  $RegExp = function RegExp(p, f) {
    var tiRE = this instanceof $RegExp;
    var piRE = isRegExp(p);
    var fiU = f === undefined;
    return !tiRE && piRE && p.constructor === $RegExp && fiU ? p
      : inheritIfRequired(CORRECT_NEW
        ? new Base(piRE && !fiU ? p.source : p, f)
        : Base((piRE = p instanceof $RegExp) ? p.source : p, piRE && fiU ? $flags.call(p) : f)
      , tiRE ? this : proto, $RegExp);
  };
  var proxy = function (key) {
    key in $RegExp || dP($RegExp, key, {
      configurable: true,
      get: function () { return Base[key]; },
      set: function (it) { Base[key] = it; }
    });
  };
  for (var keys = gOPN(Base), i = 0; keys.length > i;) proxy(keys[i++]);
  proto.constructor = $RegExp;
  $RegExp.prototype = proto;
  __webpack_require__(12)(global, 'RegExp', $RegExp);
}

__webpack_require__(38)('RegExp');


/***/ }),
/* 227 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

__webpack_require__(113);
var anObject = __webpack_require__(1);
var $flags = __webpack_require__(49);
var DESCRIPTORS = __webpack_require__(7);
var TO_STRING = 'toString';
var $toString = /./[TO_STRING];

var define = function (fn) {
  __webpack_require__(12)(RegExp.prototype, TO_STRING, fn, true);
};

// 21.2.5.14 RegExp.prototype.toString()
if (__webpack_require__(3)(function () { return $toString.call({ source: 'a', flags: 'b' }) != '/a/b'; })) {
  define(function toString() {
    var R = anObject(this);
    return '/'.concat(R.source, '/',
      'flags' in R ? R.flags : !DESCRIPTORS && R instanceof RegExp ? $flags.call(R) : undefined);
  });
// FF44- RegExp#toString has a wrong name
} else if ($toString.name != TO_STRING) {
  define(function toString() {
    return $toString.call(this);
  });
}


/***/ }),
/* 228 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var anObject = __webpack_require__(1);
var toLength = __webpack_require__(6);
var advanceStringIndex = __webpack_require__(88);
var regExpExec = __webpack_require__(58);

// @@match logic
__webpack_require__(59)('match', 1, function (defined, MATCH, $match, maybeCallNative) {
  return [
    // `String.prototype.match` method
    // https://tc39.github.io/ecma262/#sec-string.prototype.match
    function match(regexp) {
      var O = defined(this);
      var fn = regexp == undefined ? undefined : regexp[MATCH];
      return fn !== undefined ? fn.call(regexp, O) : new RegExp(regexp)[MATCH](String(O));
    },
    // `RegExp.prototype[@@match]` method
    // https://tc39.github.io/ecma262/#sec-regexp.prototype-@@match
    function (regexp) {
      var res = maybeCallNative($match, regexp, this);
      if (res.done) return res.value;
      var rx = anObject(regexp);
      var S = String(this);
      if (!rx.global) return regExpExec(rx, S);
      var fullUnicode = rx.unicode;
      rx.lastIndex = 0;
      var A = [];
      var n = 0;
      var result;
      while ((result = regExpExec(rx, S)) !== null) {
        var matchStr = String(result[0]);
        A[n] = matchStr;
        if (matchStr === '') rx.lastIndex = advanceStringIndex(S, toLength(rx.lastIndex), fullUnicode);
        n++;
      }
      return n === 0 ? null : A;
    }
  ];
});


/***/ }),
/* 229 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var anObject = __webpack_require__(1);
var toObject = __webpack_require__(9);
var toLength = __webpack_require__(6);
var toInteger = __webpack_require__(20);
var advanceStringIndex = __webpack_require__(88);
var regExpExec = __webpack_require__(58);
var max = Math.max;
var min = Math.min;
var floor = Math.floor;
var SUBSTITUTION_SYMBOLS = /\$([$&`']|\d\d?|<[^>]*>)/g;
var SUBSTITUTION_SYMBOLS_NO_NAMED = /\$([$&`']|\d\d?)/g;

var maybeToString = function (it) {
  return it === undefined ? it : String(it);
};

// @@replace logic
__webpack_require__(59)('replace', 2, function (defined, REPLACE, $replace, maybeCallNative) {
  return [
    // `String.prototype.replace` method
    // https://tc39.github.io/ecma262/#sec-string.prototype.replace
    function replace(searchValue, replaceValue) {
      var O = defined(this);
      var fn = searchValue == undefined ? undefined : searchValue[REPLACE];
      return fn !== undefined
        ? fn.call(searchValue, O, replaceValue)
        : $replace.call(String(O), searchValue, replaceValue);
    },
    // `RegExp.prototype[@@replace]` method
    // https://tc39.github.io/ecma262/#sec-regexp.prototype-@@replace
    function (regexp, replaceValue) {
      var res = maybeCallNative($replace, regexp, this, replaceValue);
      if (res.done) return res.value;

      var rx = anObject(regexp);
      var S = String(this);
      var functionalReplace = typeof replaceValue === 'function';
      if (!functionalReplace) replaceValue = String(replaceValue);
      var global = rx.global;
      if (global) {
        var fullUnicode = rx.unicode;
        rx.lastIndex = 0;
      }
      var results = [];
      while (true) {
        var result = regExpExec(rx, S);
        if (result === null) break;
        results.push(result);
        if (!global) break;
        var matchStr = String(result[0]);
        if (matchStr === '') rx.lastIndex = advanceStringIndex(S, toLength(rx.lastIndex), fullUnicode);
      }
      var accumulatedResult = '';
      var nextSourcePosition = 0;
      for (var i = 0; i < results.length; i++) {
        result = results[i];
        var matched = String(result[0]);
        var position = max(min(toInteger(result.index), S.length), 0);
        var captures = [];
        // NOTE: This is equivalent to
        //   captures = result.slice(1).map(maybeToString)
        // but for some reason `nativeSlice.call(result, 1, result.length)` (called in
        // the slice polyfill when slicing native arrays) "doesn't work" in safari 9 and
        // causes a crash (https://pastebin.com/N21QzeQA) when trying to debug it.
        for (var j = 1; j < result.length; j++) captures.push(maybeToString(result[j]));
        var namedCaptures = result.groups;
        if (functionalReplace) {
          var replacerArgs = [matched].concat(captures, position, S);
          if (namedCaptures !== undefined) replacerArgs.push(namedCaptures);
          var replacement = String(replaceValue.apply(undefined, replacerArgs));
        } else {
          replacement = getSubstitution(matched, S, position, captures, namedCaptures, replaceValue);
        }
        if (position >= nextSourcePosition) {
          accumulatedResult += S.slice(nextSourcePosition, position) + replacement;
          nextSourcePosition = position + matched.length;
        }
      }
      return accumulatedResult + S.slice(nextSourcePosition);
    }
  ];

    // https://tc39.github.io/ecma262/#sec-getsubstitution
  function getSubstitution(matched, str, position, captures, namedCaptures, replacement) {
    var tailPos = position + matched.length;
    var m = captures.length;
    var symbols = SUBSTITUTION_SYMBOLS_NO_NAMED;
    if (namedCaptures !== undefined) {
      namedCaptures = toObject(namedCaptures);
      symbols = SUBSTITUTION_SYMBOLS;
    }
    return $replace.call(replacement, symbols, function (match, ch) {
      var capture;
      switch (ch.charAt(0)) {
        case '$': return '$';
        case '&': return matched;
        case '`': return str.slice(0, position);
        case "'": return str.slice(tailPos);
        case '<':
          capture = namedCaptures[ch.slice(1, -1)];
          break;
        default: // \d\d?
          var n = +ch;
          if (n === 0) return match;
          if (n > m) {
            var f = floor(n / 10);
            if (f === 0) return match;
            if (f <= m) return captures[f - 1] === undefined ? ch.charAt(1) : captures[f - 1] + ch.charAt(1);
            return match;
          }
          capture = captures[n - 1];
      }
      return capture === undefined ? '' : capture;
    });
  }
});


/***/ }),
/* 230 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var anObject = __webpack_require__(1);
var sameValue = __webpack_require__(99);
var regExpExec = __webpack_require__(58);

// @@search logic
__webpack_require__(59)('search', 1, function (defined, SEARCH, $search, maybeCallNative) {
  return [
    // `String.prototype.search` method
    // https://tc39.github.io/ecma262/#sec-string.prototype.search
    function search(regexp) {
      var O = defined(this);
      var fn = regexp == undefined ? undefined : regexp[SEARCH];
      return fn !== undefined ? fn.call(regexp, O) : new RegExp(regexp)[SEARCH](String(O));
    },
    // `RegExp.prototype[@@search]` method
    // https://tc39.github.io/ecma262/#sec-regexp.prototype-@@search
    function (regexp) {
      var res = maybeCallNative($search, regexp, this);
      if (res.done) return res.value;
      var rx = anObject(regexp);
      var S = String(this);
      var previousLastIndex = rx.lastIndex;
      if (!sameValue(previousLastIndex, 0)) rx.lastIndex = 0;
      var result = regExpExec(rx, S);
      if (!sameValue(rx.lastIndex, previousLastIndex)) rx.lastIndex = previousLastIndex;
      return result === null ? -1 : result.index;
    }
  ];
});


/***/ }),
/* 231 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var isRegExp = __webpack_require__(56);
var anObject = __webpack_require__(1);
var speciesConstructor = __webpack_require__(50);
var advanceStringIndex = __webpack_require__(88);
var toLength = __webpack_require__(6);
var callRegExpExec = __webpack_require__(58);
var regexpExec = __webpack_require__(87);
var fails = __webpack_require__(3);
var $min = Math.min;
var $push = [].push;
var $SPLIT = 'split';
var LENGTH = 'length';
var LAST_INDEX = 'lastIndex';
var MAX_UINT32 = 0xffffffff;

// babel-minify transpiles RegExp('x', 'y') -> /x/y and it causes SyntaxError
var SUPPORTS_Y = !fails(function () { RegExp(MAX_UINT32, 'y'); });

// @@split logic
__webpack_require__(59)('split', 2, function (defined, SPLIT, $split, maybeCallNative) {
  var internalSplit;
  if (
    'abbc'[$SPLIT](/(b)*/)[1] == 'c' ||
    'test'[$SPLIT](/(?:)/, -1)[LENGTH] != 4 ||
    'ab'[$SPLIT](/(?:ab)*/)[LENGTH] != 2 ||
    '.'[$SPLIT](/(.?)(.?)/)[LENGTH] != 4 ||
    '.'[$SPLIT](/()()/)[LENGTH] > 1 ||
    ''[$SPLIT](/.?/)[LENGTH]
  ) {
    // based on es5-shim implementation, need to rework it
    internalSplit = function (separator, limit) {
      var string = String(this);
      if (separator === undefined && limit === 0) return [];
      // If `separator` is not a regex, use native split
      if (!isRegExp(separator)) return $split.call(string, separator, limit);
      var output = [];
      var flags = (separator.ignoreCase ? 'i' : '') +
                  (separator.multiline ? 'm' : '') +
                  (separator.unicode ? 'u' : '') +
                  (separator.sticky ? 'y' : '');
      var lastLastIndex = 0;
      var splitLimit = limit === undefined ? MAX_UINT32 : limit >>> 0;
      // Make `global` and avoid `lastIndex` issues by working with a copy
      var separatorCopy = new RegExp(separator.source, flags + 'g');
      var match, lastIndex, lastLength;
      while (match = regexpExec.call(separatorCopy, string)) {
        lastIndex = separatorCopy[LAST_INDEX];
        if (lastIndex > lastLastIndex) {
          output.push(string.slice(lastLastIndex, match.index));
          if (match[LENGTH] > 1 && match.index < string[LENGTH]) $push.apply(output, match.slice(1));
          lastLength = match[0][LENGTH];
          lastLastIndex = lastIndex;
          if (output[LENGTH] >= splitLimit) break;
        }
        if (separatorCopy[LAST_INDEX] === match.index) separatorCopy[LAST_INDEX]++; // Avoid an infinite loop
      }
      if (lastLastIndex === string[LENGTH]) {
        if (lastLength || !separatorCopy.test('')) output.push('');
      } else output.push(string.slice(lastLastIndex));
      return output[LENGTH] > splitLimit ? output.slice(0, splitLimit) : output;
    };
  // Chakra, V8
  } else if ('0'[$SPLIT](undefined, 0)[LENGTH]) {
    internalSplit = function (separator, limit) {
      return separator === undefined && limit === 0 ? [] : $split.call(this, separator, limit);
    };
  } else {
    internalSplit = $split;
  }

  return [
    // `String.prototype.split` method
    // https://tc39.github.io/ecma262/#sec-string.prototype.split
    function split(separator, limit) {
      var O = defined(this);
      var splitter = separator == undefined ? undefined : separator[SPLIT];
      return splitter !== undefined
        ? splitter.call(separator, O, limit)
        : internalSplit.call(String(O), separator, limit);
    },
    // `RegExp.prototype[@@split]` method
    // https://tc39.github.io/ecma262/#sec-regexp.prototype-@@split
    //
    // NOTE: This cannot be properly polyfilled in engines that don't support
    // the 'y' flag.
    function (regexp, limit) {
      var res = maybeCallNative(internalSplit, regexp, this, limit, internalSplit !== $split);
      if (res.done) return res.value;

      var rx = anObject(regexp);
      var S = String(this);
      var C = speciesConstructor(rx, RegExp);

      var unicodeMatching = rx.unicode;
      var flags = (rx.ignoreCase ? 'i' : '') +
                  (rx.multiline ? 'm' : '') +
                  (rx.unicode ? 'u' : '') +
                  (SUPPORTS_Y ? 'y' : 'g');

      // ^(? + rx + ) is needed, in combination with some S slicing, to
      // simulate the 'y' flag.
      var splitter = new C(SUPPORTS_Y ? rx : '^(?:' + rx.source + ')', flags);
      var lim = limit === undefined ? MAX_UINT32 : limit >>> 0;
      if (lim === 0) return [];
      if (S.length === 0) return callRegExpExec(splitter, S) === null ? [S] : [];
      var p = 0;
      var q = 0;
      var A = [];
      while (q < S.length) {
        splitter.lastIndex = SUPPORTS_Y ? q : 0;
        var z = callRegExpExec(splitter, SUPPORTS_Y ? S : S.slice(q));
        var e;
        if (
          z === null ||
          (e = $min(toLength(splitter.lastIndex + (SUPPORTS_Y ? 0 : q)), S.length)) === p
        ) {
          q = advanceStringIndex(S, q, unicodeMatching);
        } else {
          A.push(S.slice(p, q));
          if (A.length === lim) return A;
          for (var i = 1; i <= z.length - 1; i++) {
            A.push(z[i]);
            if (A.length === lim) return A;
          }
          q = p = e;
        }
      }
      A.push(S.slice(p));
      return A;
    }
  ];
});


/***/ }),
/* 232 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var LIBRARY = __webpack_require__(30);
var global = __webpack_require__(2);
var ctx = __webpack_require__(18);
var classof = __webpack_require__(43);
var $export = __webpack_require__(0);
var isObject = __webpack_require__(4);
var aFunction = __webpack_require__(10);
var anInstance = __webpack_require__(39);
var forOf = __webpack_require__(40);
var speciesConstructor = __webpack_require__(50);
var task = __webpack_require__(89).set;
var microtask = __webpack_require__(90)();
var newPromiseCapabilityModule = __webpack_require__(91);
var perform = __webpack_require__(114);
var userAgent = __webpack_require__(60);
var promiseResolve = __webpack_require__(115);
var PROMISE = 'Promise';
var TypeError = global.TypeError;
var process = global.process;
var versions = process && process.versions;
var v8 = versions && versions.v8 || '';
var $Promise = global[PROMISE];
var isNode = classof(process) == 'process';
var empty = function () { /* empty */ };
var Internal, newGenericPromiseCapability, OwnPromiseCapability, Wrapper;
var newPromiseCapability = newGenericPromiseCapability = newPromiseCapabilityModule.f;

var USE_NATIVE = !!function () {
  try {
    // correct subclassing with @@species support
    var promise = $Promise.resolve(1);
    var FakePromise = (promise.constructor = {})[__webpack_require__(5)('species')] = function (exec) {
      exec(empty, empty);
    };
    // unhandled rejections tracking support, NodeJS Promise without it fails @@species test
    return (isNode || typeof PromiseRejectionEvent == 'function')
      && promise.then(empty) instanceof FakePromise
      // v8 6.6 (Node 10 and Chrome 66) have a bug with resolving custom thenables
      // https://bugs.chromium.org/p/chromium/issues/detail?id=830565
      // we can't detect it synchronously, so just check versions
      && v8.indexOf('6.6') !== 0
      && userAgent.indexOf('Chrome/66') === -1;
  } catch (e) { /* empty */ }
}();

// helpers
var isThenable = function (it) {
  var then;
  return isObject(it) && typeof (then = it.then) == 'function' ? then : false;
};
var notify = function (promise, isReject) {
  if (promise._n) return;
  promise._n = true;
  var chain = promise._c;
  microtask(function () {
    var value = promise._v;
    var ok = promise._s == 1;
    var i = 0;
    var run = function (reaction) {
      var handler = ok ? reaction.ok : reaction.fail;
      var resolve = reaction.resolve;
      var reject = reaction.reject;
      var domain = reaction.domain;
      var result, then, exited;
      try {
        if (handler) {
          if (!ok) {
            if (promise._h == 2) onHandleUnhandled(promise);
            promise._h = 1;
          }
          if (handler === true) result = value;
          else {
            if (domain) domain.enter();
            result = handler(value); // may throw
            if (domain) {
              domain.exit();
              exited = true;
            }
          }
          if (result === reaction.promise) {
            reject(TypeError('Promise-chain cycle'));
          } else if (then = isThenable(result)) {
            then.call(result, resolve, reject);
          } else resolve(result);
        } else reject(value);
      } catch (e) {
        if (domain && !exited) domain.exit();
        reject(e);
      }
    };
    while (chain.length > i) run(chain[i++]); // variable length - can't use forEach
    promise._c = [];
    promise._n = false;
    if (isReject && !promise._h) onUnhandled(promise);
  });
};
var onUnhandled = function (promise) {
  task.call(global, function () {
    var value = promise._v;
    var unhandled = isUnhandled(promise);
    var result, handler, console;
    if (unhandled) {
      result = perform(function () {
        if (isNode) {
          process.emit('unhandledRejection', value, promise);
        } else if (handler = global.onunhandledrejection) {
          handler({ promise: promise, reason: value });
        } else if ((console = global.console) && console.error) {
          console.error('Unhandled promise rejection', value);
        }
      });
      // Browsers should not trigger `rejectionHandled` event if it was handled here, NodeJS - should
      promise._h = isNode || isUnhandled(promise) ? 2 : 1;
    } promise._a = undefined;
    if (unhandled && result.e) throw result.v;
  });
};
var isUnhandled = function (promise) {
  return promise._h !== 1 && (promise._a || promise._c).length === 0;
};
var onHandleUnhandled = function (promise) {
  task.call(global, function () {
    var handler;
    if (isNode) {
      process.emit('rejectionHandled', promise);
    } else if (handler = global.onrejectionhandled) {
      handler({ promise: promise, reason: promise._v });
    }
  });
};
var $reject = function (value) {
  var promise = this;
  if (promise._d) return;
  promise._d = true;
  promise = promise._w || promise; // unwrap
  promise._v = value;
  promise._s = 2;
  if (!promise._a) promise._a = promise._c.slice();
  notify(promise, true);
};
var $resolve = function (value) {
  var promise = this;
  var then;
  if (promise._d) return;
  promise._d = true;
  promise = promise._w || promise; // unwrap
  try {
    if (promise === value) throw TypeError("Promise can't be resolved itself");
    if (then = isThenable(value)) {
      microtask(function () {
        var wrapper = { _w: promise, _d: false }; // wrap
        try {
          then.call(value, ctx($resolve, wrapper, 1), ctx($reject, wrapper, 1));
        } catch (e) {
          $reject.call(wrapper, e);
        }
      });
    } else {
      promise._v = value;
      promise._s = 1;
      notify(promise, false);
    }
  } catch (e) {
    $reject.call({ _w: promise, _d: false }, e); // wrap
  }
};

// constructor polyfill
if (!USE_NATIVE) {
  // 25.4.3.1 Promise(executor)
  $Promise = function Promise(executor) {
    anInstance(this, $Promise, PROMISE, '_h');
    aFunction(executor);
    Internal.call(this);
    try {
      executor(ctx($resolve, this, 1), ctx($reject, this, 1));
    } catch (err) {
      $reject.call(this, err);
    }
  };
  // eslint-disable-next-line no-unused-vars
  Internal = function Promise(executor) {
    this._c = [];             // <- awaiting reactions
    this._a = undefined;      // <- checked in isUnhandled reactions
    this._s = 0;              // <- state
    this._d = false;          // <- done
    this._v = undefined;      // <- value
    this._h = 0;              // <- rejection state, 0 - default, 1 - handled, 2 - unhandled
    this._n = false;          // <- notify
  };
  Internal.prototype = __webpack_require__(41)($Promise.prototype, {
    // 25.4.5.3 Promise.prototype.then(onFulfilled, onRejected)
    then: function then(onFulfilled, onRejected) {
      var reaction = newPromiseCapability(speciesConstructor(this, $Promise));
      reaction.ok = typeof onFulfilled == 'function' ? onFulfilled : true;
      reaction.fail = typeof onRejected == 'function' && onRejected;
      reaction.domain = isNode ? process.domain : undefined;
      this._c.push(reaction);
      if (this._a) this._a.push(reaction);
      if (this._s) notify(this, false);
      return reaction.promise;
    },
    // 25.4.5.1 Promise.prototype.catch(onRejected)
    'catch': function (onRejected) {
      return this.then(undefined, onRejected);
    }
  });
  OwnPromiseCapability = function () {
    var promise = new Internal();
    this.promise = promise;
    this.resolve = ctx($resolve, promise, 1);
    this.reject = ctx($reject, promise, 1);
  };
  newPromiseCapabilityModule.f = newPromiseCapability = function (C) {
    return C === $Promise || C === Wrapper
      ? new OwnPromiseCapability(C)
      : newGenericPromiseCapability(C);
  };
}

$export($export.G + $export.W + $export.F * !USE_NATIVE, { Promise: $Promise });
__webpack_require__(42)($Promise, PROMISE);
__webpack_require__(38)(PROMISE);
Wrapper = __webpack_require__(26)[PROMISE];

// statics
$export($export.S + $export.F * !USE_NATIVE, PROMISE, {
  // 25.4.4.5 Promise.reject(r)
  reject: function reject(r) {
    var capability = newPromiseCapability(this);
    var $$reject = capability.reject;
    $$reject(r);
    return capability.promise;
  }
});
$export($export.S + $export.F * (LIBRARY || !USE_NATIVE), PROMISE, {
  // 25.4.4.6 Promise.resolve(x)
  resolve: function resolve(x) {
    return promiseResolve(LIBRARY && this === Wrapper ? $Promise : this, x);
  }
});
$export($export.S + $export.F * !(USE_NATIVE && __webpack_require__(57)(function (iter) {
  $Promise.all(iter)['catch'](empty);
})), PROMISE, {
  // 25.4.4.1 Promise.all(iterable)
  all: function all(iterable) {
    var C = this;
    var capability = newPromiseCapability(C);
    var resolve = capability.resolve;
    var reject = capability.reject;
    var result = perform(function () {
      var values = [];
      var index = 0;
      var remaining = 1;
      forOf(iterable, false, function (promise) {
        var $index = index++;
        var alreadyCalled = false;
        values.push(undefined);
        remaining++;
        C.resolve(promise).then(function (value) {
          if (alreadyCalled) return;
          alreadyCalled = true;
          values[$index] = value;
          --remaining || resolve(values);
        }, reject);
      });
      --remaining || resolve(values);
    });
    if (result.e) reject(result.v);
    return capability.promise;
  },
  // 25.4.4.4 Promise.race(iterable)
  race: function race(iterable) {
    var C = this;
    var capability = newPromiseCapability(C);
    var reject = capability.reject;
    var result = perform(function () {
      forOf(iterable, false, function (promise) {
        C.resolve(promise).then(capability.resolve, reject);
      });
    });
    if (result.e) reject(result.v);
    return capability.promise;
  }
});


/***/ }),
/* 233 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var weak = __webpack_require__(120);
var validate = __webpack_require__(46);
var WEAK_SET = 'WeakSet';

// 23.4 WeakSet Objects
__webpack_require__(61)(WEAK_SET, function (get) {
  return function WeakSet() { return get(this, arguments.length > 0 ? arguments[0] : undefined); };
}, {
  // 23.4.3.1 WeakSet.prototype.add(value)
  add: function add(value) {
    return weak.def(validate(this, WEAK_SET), value, true);
  }
}, weak, false, true);


/***/ }),
/* 234 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.1 Reflect.apply(target, thisArgument, argumentsList)
var $export = __webpack_require__(0);
var aFunction = __webpack_require__(10);
var anObject = __webpack_require__(1);
var rApply = (__webpack_require__(2).Reflect || {}).apply;
var fApply = Function.apply;
// MS Edge argumentsList argument is optional
$export($export.S + $export.F * !__webpack_require__(3)(function () {
  rApply(function () { /* empty */ });
}), 'Reflect', {
  apply: function apply(target, thisArgument, argumentsList) {
    var T = aFunction(target);
    var L = anObject(argumentsList);
    return rApply ? rApply(T, thisArgument, L) : fApply.call(T, thisArgument, L);
  }
});


/***/ }),
/* 235 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.2 Reflect.construct(target, argumentsList [, newTarget])
var $export = __webpack_require__(0);
var create = __webpack_require__(36);
var aFunction = __webpack_require__(10);
var anObject = __webpack_require__(1);
var isObject = __webpack_require__(4);
var fails = __webpack_require__(3);
var bind = __webpack_require__(100);
var rConstruct = (__webpack_require__(2).Reflect || {}).construct;

// MS Edge supports only 2 arguments and argumentsList argument is optional
// FF Nightly sets third argument as `new.target`, but does not create `this` from it
var NEW_TARGET_BUG = fails(function () {
  function F() { /* empty */ }
  return !(rConstruct(function () { /* empty */ }, [], F) instanceof F);
});
var ARGS_BUG = !fails(function () {
  rConstruct(function () { /* empty */ });
});

$export($export.S + $export.F * (NEW_TARGET_BUG || ARGS_BUG), 'Reflect', {
  construct: function construct(Target, args /* , newTarget */) {
    aFunction(Target);
    anObject(args);
    var newTarget = arguments.length < 3 ? Target : aFunction(arguments[2]);
    if (ARGS_BUG && !NEW_TARGET_BUG) return rConstruct(Target, args, newTarget);
    if (Target == newTarget) {
      // w/o altered newTarget, optimization for 0-4 arguments
      switch (args.length) {
        case 0: return new Target();
        case 1: return new Target(args[0]);
        case 2: return new Target(args[0], args[1]);
        case 3: return new Target(args[0], args[1], args[2]);
        case 4: return new Target(args[0], args[1], args[2], args[3]);
      }
      // w/o altered newTarget, lot of arguments case
      var $args = [null];
      $args.push.apply($args, args);
      return new (bind.apply(Target, $args))();
    }
    // with altered newTarget, not support built-in constructors
    var proto = newTarget.prototype;
    var instance = create(isObject(proto) ? proto : Object.prototype);
    var result = Function.apply.call(Target, instance, args);
    return isObject(result) ? result : instance;
  }
});


/***/ }),
/* 236 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.3 Reflect.defineProperty(target, propertyKey, attributes)
var dP = __webpack_require__(8);
var $export = __webpack_require__(0);
var anObject = __webpack_require__(1);
var toPrimitive = __webpack_require__(22);

// MS Edge has broken Reflect.defineProperty - throwing instead of returning false
$export($export.S + $export.F * __webpack_require__(3)(function () {
  // eslint-disable-next-line no-undef
  Reflect.defineProperty(dP.f({}, 1, { value: 1 }), 1, { value: 2 });
}), 'Reflect', {
  defineProperty: function defineProperty(target, propertyKey, attributes) {
    anObject(target);
    propertyKey = toPrimitive(propertyKey, true);
    anObject(attributes);
    try {
      dP.f(target, propertyKey, attributes);
      return true;
    } catch (e) {
      return false;
    }
  }
});


/***/ }),
/* 237 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.4 Reflect.deleteProperty(target, propertyKey)
var $export = __webpack_require__(0);
var gOPD = __webpack_require__(16).f;
var anObject = __webpack_require__(1);

$export($export.S, 'Reflect', {
  deleteProperty: function deleteProperty(target, propertyKey) {
    var desc = gOPD(anObject(target), propertyKey);
    return desc && !desc.configurable ? false : delete target[propertyKey];
  }
});


/***/ }),
/* 238 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 26.1.5 Reflect.enumerate(target)
var $export = __webpack_require__(0);
var anObject = __webpack_require__(1);
var Enumerate = function (iterated) {
  this._t = anObject(iterated); // target
  this._i = 0;                  // next index
  var keys = this._k = [];      // keys
  var key;
  for (key in iterated) keys.push(key);
};
__webpack_require__(80)(Enumerate, 'Object', function () {
  var that = this;
  var keys = that._k;
  var key;
  do {
    if (that._i >= keys.length) return { value: undefined, done: true };
  } while (!((key = keys[that._i++]) in that._t));
  return { value: key, done: false };
});

$export($export.S, 'Reflect', {
  enumerate: function enumerate(target) {
    return new Enumerate(target);
  }
});


/***/ }),
/* 239 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.6 Reflect.get(target, propertyKey [, receiver])
var gOPD = __webpack_require__(16);
var getPrototypeOf = __webpack_require__(17);
var has = __webpack_require__(14);
var $export = __webpack_require__(0);
var isObject = __webpack_require__(4);
var anObject = __webpack_require__(1);

function get(target, propertyKey /* , receiver */) {
  var receiver = arguments.length < 3 ? target : arguments[2];
  var desc, proto;
  if (anObject(target) === receiver) return target[propertyKey];
  if (desc = gOPD.f(target, propertyKey)) return has(desc, 'value')
    ? desc.value
    : desc.get !== undefined
      ? desc.get.call(receiver)
      : undefined;
  if (isObject(proto = getPrototypeOf(target))) return get(proto, propertyKey, receiver);
}

$export($export.S, 'Reflect', { get: get });


/***/ }),
/* 240 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.7 Reflect.getOwnPropertyDescriptor(target, propertyKey)
var gOPD = __webpack_require__(16);
var $export = __webpack_require__(0);
var anObject = __webpack_require__(1);

$export($export.S, 'Reflect', {
  getOwnPropertyDescriptor: function getOwnPropertyDescriptor(target, propertyKey) {
    return gOPD.f(anObject(target), propertyKey);
  }
});


/***/ }),
/* 241 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.8 Reflect.getPrototypeOf(target)
var $export = __webpack_require__(0);
var getProto = __webpack_require__(17);
var anObject = __webpack_require__(1);

$export($export.S, 'Reflect', {
  getPrototypeOf: function getPrototypeOf(target) {
    return getProto(anObject(target));
  }
});


/***/ }),
/* 242 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.9 Reflect.has(target, propertyKey)
var $export = __webpack_require__(0);

$export($export.S, 'Reflect', {
  has: function has(target, propertyKey) {
    return propertyKey in target;
  }
});


/***/ }),
/* 243 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.10 Reflect.isExtensible(target)
var $export = __webpack_require__(0);
var anObject = __webpack_require__(1);
var $isExtensible = Object.isExtensible;

$export($export.S, 'Reflect', {
  isExtensible: function isExtensible(target) {
    anObject(target);
    return $isExtensible ? $isExtensible(target) : true;
  }
});


/***/ }),
/* 244 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.11 Reflect.ownKeys(target)
var $export = __webpack_require__(0);

$export($export.S, 'Reflect', { ownKeys: __webpack_require__(121) });


/***/ }),
/* 245 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.12 Reflect.preventExtensions(target)
var $export = __webpack_require__(0);
var anObject = __webpack_require__(1);
var $preventExtensions = Object.preventExtensions;

$export($export.S, 'Reflect', {
  preventExtensions: function preventExtensions(target) {
    anObject(target);
    try {
      if ($preventExtensions) $preventExtensions(target);
      return true;
    } catch (e) {
      return false;
    }
  }
});


/***/ }),
/* 246 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.13 Reflect.set(target, propertyKey, V [, receiver])
var dP = __webpack_require__(8);
var gOPD = __webpack_require__(16);
var getPrototypeOf = __webpack_require__(17);
var has = __webpack_require__(14);
var $export = __webpack_require__(0);
var createDesc = __webpack_require__(32);
var anObject = __webpack_require__(1);
var isObject = __webpack_require__(4);

function set(target, propertyKey, V /* , receiver */) {
  var receiver = arguments.length < 4 ? target : arguments[3];
  var ownDesc = gOPD.f(anObject(target), propertyKey);
  var existingDescriptor, proto;
  if (!ownDesc) {
    if (isObject(proto = getPrototypeOf(target))) {
      return set(proto, propertyKey, V, receiver);
    }
    ownDesc = createDesc(0);
  }
  if (has(ownDesc, 'value')) {
    if (ownDesc.writable === false || !isObject(receiver)) return false;
    if (existingDescriptor = gOPD.f(receiver, propertyKey)) {
      if (existingDescriptor.get || existingDescriptor.set || existingDescriptor.writable === false) return false;
      existingDescriptor.value = V;
      dP.f(receiver, propertyKey, existingDescriptor);
    } else dP.f(receiver, propertyKey, createDesc(0, V));
    return true;
  }
  return ownDesc.set === undefined ? false : (ownDesc.set.call(receiver, V), true);
}

$export($export.S, 'Reflect', { set: set });


/***/ }),
/* 247 */
/***/ (function(module, exports, __webpack_require__) {

// 26.1.14 Reflect.setPrototypeOf(target, proto)
var $export = __webpack_require__(0);
var setProto = __webpack_require__(71);

if (setProto) $export($export.S, 'Reflect', {
  setPrototypeOf: function setPrototypeOf(target, proto) {
    setProto.check(target, proto);
    try {
      setProto.set(target, proto);
      return true;
    } catch (e) {
      return false;
    }
  }
});


/***/ }),
/* 248 */
/***/ (function(module, exports, __webpack_require__) {

// 20.3.3.1 / 15.9.4.4 Date.now()
var $export = __webpack_require__(0);

$export($export.S, 'Date', { now: function () { return new Date().getTime(); } });


/***/ }),
/* 249 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var toObject = __webpack_require__(9);
var toPrimitive = __webpack_require__(22);

$export($export.P + $export.F * __webpack_require__(3)(function () {
  return new Date(NaN).toJSON() !== null
    || Date.prototype.toJSON.call({ toISOString: function () { return 1; } }) !== 1;
}), 'Date', {
  // eslint-disable-next-line no-unused-vars
  toJSON: function toJSON(key) {
    var O = toObject(this);
    var pv = toPrimitive(O);
    return typeof pv == 'number' && !isFinite(pv) ? null : O.toISOString();
  }
});


/***/ }),
/* 250 */
/***/ (function(module, exports, __webpack_require__) {

// 20.3.4.36 / 15.9.5.43 Date.prototype.toISOString()
var $export = __webpack_require__(0);
var toISOString = __webpack_require__(251);

// PhantomJS / old WebKit has a broken implementations
$export($export.P + $export.F * (Date.prototype.toISOString !== toISOString), 'Date', {
  toISOString: toISOString
});


/***/ }),
/* 251 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// 20.3.4.36 / 15.9.5.43 Date.prototype.toISOString()
var fails = __webpack_require__(3);
var getTime = Date.prototype.getTime;
var $toISOString = Date.prototype.toISOString;

var lz = function (num) {
  return num > 9 ? num : '0' + num;
};

// PhantomJS / old WebKit has a broken implementations
module.exports = (fails(function () {
  return $toISOString.call(new Date(-5e13 - 1)) != '0385-07-25T07:06:39.999Z';
}) || !fails(function () {
  $toISOString.call(new Date(NaN));
})) ? function toISOString() {
  if (!isFinite(getTime.call(this))) throw RangeError('Invalid time value');
  var d = this;
  var y = d.getUTCFullYear();
  var m = d.getUTCMilliseconds();
  var s = y < 0 ? '-' : y > 9999 ? '+' : '';
  return s + ('00000' + Math.abs(y)).slice(s ? -6 : -4) +
    '-' + lz(d.getUTCMonth() + 1) + '-' + lz(d.getUTCDate()) +
    'T' + lz(d.getUTCHours()) + ':' + lz(d.getUTCMinutes()) +
    ':' + lz(d.getUTCSeconds()) + '.' + (m > 99 ? m : '0' + lz(m)) + 'Z';
} : $toISOString;


/***/ }),
/* 252 */
/***/ (function(module, exports, __webpack_require__) {

var DateProto = Date.prototype;
var INVALID_DATE = 'Invalid Date';
var TO_STRING = 'toString';
var $toString = DateProto[TO_STRING];
var getTime = DateProto.getTime;
if (new Date(NaN) + '' != INVALID_DATE) {
  __webpack_require__(12)(DateProto, TO_STRING, function toString() {
    var value = getTime.call(this);
    // eslint-disable-next-line no-self-compare
    return value === value ? $toString.call(this) : INVALID_DATE;
  });
}


/***/ }),
/* 253 */
/***/ (function(module, exports, __webpack_require__) {

var TO_PRIMITIVE = __webpack_require__(5)('toPrimitive');
var proto = Date.prototype;

if (!(TO_PRIMITIVE in proto)) __webpack_require__(11)(proto, TO_PRIMITIVE, __webpack_require__(254));


/***/ }),
/* 254 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var anObject = __webpack_require__(1);
var toPrimitive = __webpack_require__(22);
var NUMBER = 'number';

module.exports = function (hint) {
  if (hint !== 'string' && hint !== NUMBER && hint !== 'default') throw TypeError('Incorrect hint');
  return toPrimitive(anObject(this), hint != NUMBER);
};


/***/ }),
/* 255 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var $typed = __webpack_require__(62);
var buffer = __webpack_require__(92);
var anObject = __webpack_require__(1);
var toAbsoluteIndex = __webpack_require__(35);
var toLength = __webpack_require__(6);
var isObject = __webpack_require__(4);
var ArrayBuffer = __webpack_require__(2).ArrayBuffer;
var speciesConstructor = __webpack_require__(50);
var $ArrayBuffer = buffer.ArrayBuffer;
var $DataView = buffer.DataView;
var $isView = $typed.ABV && ArrayBuffer.isView;
var $slice = $ArrayBuffer.prototype.slice;
var VIEW = $typed.VIEW;
var ARRAY_BUFFER = 'ArrayBuffer';

$export($export.G + $export.W + $export.F * (ArrayBuffer !== $ArrayBuffer), { ArrayBuffer: $ArrayBuffer });

$export($export.S + $export.F * !$typed.CONSTR, ARRAY_BUFFER, {
  // 24.1.3.1 ArrayBuffer.isView(arg)
  isView: function isView(it) {
    return $isView && $isView(it) || isObject(it) && VIEW in it;
  }
});

$export($export.P + $export.U + $export.F * __webpack_require__(3)(function () {
  return !new $ArrayBuffer(2).slice(1, undefined).byteLength;
}), ARRAY_BUFFER, {
  // 24.1.4.3 ArrayBuffer.prototype.slice(start, end)
  slice: function slice(start, end) {
    if ($slice !== undefined && end === undefined) return $slice.call(anObject(this), start); // FF fix
    var len = anObject(this).byteLength;
    var first = toAbsoluteIndex(start, len);
    var fin = toAbsoluteIndex(end === undefined ? len : end, len);
    var result = new (speciesConstructor(this, $ArrayBuffer))(toLength(fin - first));
    var viewS = new $DataView(this);
    var viewT = new $DataView(result);
    var index = 0;
    while (first < fin) {
      viewT.setUint8(index++, viewS.getUint8(first++));
    } return result;
  }
});

__webpack_require__(38)(ARRAY_BUFFER);


/***/ }),
/* 256 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
$export($export.G + $export.W + $export.F * !__webpack_require__(62).ABV, {
  DataView: __webpack_require__(92).DataView
});


/***/ }),
/* 257 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Int8', 1, function (init) {
  return function Int8Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 258 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Uint8', 1, function (init) {
  return function Uint8Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 259 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Uint8', 1, function (init) {
  return function Uint8ClampedArray(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
}, true);


/***/ }),
/* 260 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Int16', 2, function (init) {
  return function Int16Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 261 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Uint16', 2, function (init) {
  return function Uint16Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 262 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Int32', 4, function (init) {
  return function Int32Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 263 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Uint32', 4, function (init) {
  return function Uint32Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 264 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Float32', 4, function (init) {
  return function Float32Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 265 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(27)('Float64', 8, function (init) {
  return function Float64Array(data, byteOffset, length) {
    return init(this, data, byteOffset, length);
  };
});


/***/ }),
/* 266 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/tc39/Array.prototype.includes
var $export = __webpack_require__(0);
var $includes = __webpack_require__(52)(true);

$export($export.P, 'Array', {
  includes: function includes(el /* , fromIndex = 0 */) {
    return $includes(this, el, arguments.length > 1 ? arguments[1] : undefined);
  }
});

__webpack_require__(31)('includes');


/***/ }),
/* 267 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://tc39.github.io/proposal-flatMap/#sec-Array.prototype.flatMap
var $export = __webpack_require__(0);
var flattenIntoArray = __webpack_require__(123);
var toObject = __webpack_require__(9);
var toLength = __webpack_require__(6);
var aFunction = __webpack_require__(10);
var arraySpeciesCreate = __webpack_require__(84);

$export($export.P, 'Array', {
  flatMap: function flatMap(callbackfn /* , thisArg */) {
    var O = toObject(this);
    var sourceLen, A;
    aFunction(callbackfn);
    sourceLen = toLength(O.length);
    A = arraySpeciesCreate(O, 0);
    flattenIntoArray(A, O, O, sourceLen, 0, 1, callbackfn, arguments[1]);
    return A;
  }
});

__webpack_require__(31)('flatMap');


/***/ }),
/* 268 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://tc39.github.io/proposal-flatMap/#sec-Array.prototype.flatten
var $export = __webpack_require__(0);
var flattenIntoArray = __webpack_require__(123);
var toObject = __webpack_require__(9);
var toLength = __webpack_require__(6);
var toInteger = __webpack_require__(20);
var arraySpeciesCreate = __webpack_require__(84);

$export($export.P, 'Array', {
  flatten: function flatten(/* depthArg = 1 */) {
    var depthArg = arguments[0];
    var O = toObject(this);
    var sourceLen = toLength(O.length);
    var A = arraySpeciesCreate(O, 0);
    flattenIntoArray(A, O, O, sourceLen, 0, depthArg === undefined ? 1 : toInteger(depthArg));
    return A;
  }
});

__webpack_require__(31)('flatten');


/***/ }),
/* 269 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/mathiasbynens/String.prototype.at
var $export = __webpack_require__(0);
var $at = __webpack_require__(55)(true);

$export($export.P, 'String', {
  at: function at(pos) {
    return $at(this, pos);
  }
});


/***/ }),
/* 270 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/tc39/proposal-string-pad-start-end
var $export = __webpack_require__(0);
var $pad = __webpack_require__(124);
var userAgent = __webpack_require__(60);

// https://github.com/zloirock/core-js/issues/280
$export($export.P + $export.F * /Version\/10\.\d+(\.\d+)? Safari\//.test(userAgent), 'String', {
  padStart: function padStart(maxLength /* , fillString = ' ' */) {
    return $pad(this, maxLength, arguments.length > 1 ? arguments[1] : undefined, true);
  }
});


/***/ }),
/* 271 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/tc39/proposal-string-pad-start-end
var $export = __webpack_require__(0);
var $pad = __webpack_require__(124);
var userAgent = __webpack_require__(60);

// https://github.com/zloirock/core-js/issues/280
$export($export.P + $export.F * /Version\/10\.\d+(\.\d+)? Safari\//.test(userAgent), 'String', {
  padEnd: function padEnd(maxLength /* , fillString = ' ' */) {
    return $pad(this, maxLength, arguments.length > 1 ? arguments[1] : undefined, false);
  }
});


/***/ }),
/* 272 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/sebmarkbage/ecmascript-string-left-right-trim
__webpack_require__(44)('trimLeft', function ($trim) {
  return function trimLeft() {
    return $trim(this, 1);
  };
}, 'trimStart');


/***/ }),
/* 273 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/sebmarkbage/ecmascript-string-left-right-trim
__webpack_require__(44)('trimRight', function ($trim) {
  return function trimRight() {
    return $trim(this, 2);
  };
}, 'trimEnd');


/***/ }),
/* 274 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://tc39.github.io/String.prototype.matchAll/
var $export = __webpack_require__(0);
var defined = __webpack_require__(23);
var toLength = __webpack_require__(6);
var isRegExp = __webpack_require__(56);
var getFlags = __webpack_require__(49);
var RegExpProto = RegExp.prototype;

var $RegExpStringIterator = function (regexp, string) {
  this._r = regexp;
  this._s = string;
};

__webpack_require__(80)($RegExpStringIterator, 'RegExp String', function next() {
  var match = this._r.exec(this._s);
  return { value: match, done: match === null };
});

$export($export.P, 'String', {
  matchAll: function matchAll(regexp) {
    defined(this);
    if (!isRegExp(regexp)) throw TypeError(regexp + ' is not a regexp!');
    var S = String(this);
    var flags = 'flags' in RegExpProto ? String(regexp.flags) : getFlags.call(regexp);
    var rx = new RegExp(regexp.source, ~flags.indexOf('g') ? flags : 'g' + flags);
    rx.lastIndex = toLength(regexp.lastIndex);
    return new $RegExpStringIterator(rx, S);
  }
});


/***/ }),
/* 275 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(67)('asyncIterator');


/***/ }),
/* 276 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(67)('observable');


/***/ }),
/* 277 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/tc39/proposal-object-getownpropertydescriptors
var $export = __webpack_require__(0);
var ownKeys = __webpack_require__(121);
var toIObject = __webpack_require__(15);
var gOPD = __webpack_require__(16);
var createProperty = __webpack_require__(82);

$export($export.S, 'Object', {
  getOwnPropertyDescriptors: function getOwnPropertyDescriptors(object) {
    var O = toIObject(object);
    var getDesc = gOPD.f;
    var keys = ownKeys(O);
    var result = {};
    var i = 0;
    var key, desc;
    while (keys.length > i) {
      desc = getDesc(O, key = keys[i++]);
      if (desc !== undefined) createProperty(result, key, desc);
    }
    return result;
  }
});


/***/ }),
/* 278 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/tc39/proposal-object-values-entries
var $export = __webpack_require__(0);
var $values = __webpack_require__(125)(false);

$export($export.S, 'Object', {
  values: function values(it) {
    return $values(it);
  }
});


/***/ }),
/* 279 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/tc39/proposal-object-values-entries
var $export = __webpack_require__(0);
var $entries = __webpack_require__(125)(true);

$export($export.S, 'Object', {
  entries: function entries(it) {
    return $entries(it);
  }
});


/***/ }),
/* 280 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var toObject = __webpack_require__(9);
var aFunction = __webpack_require__(10);
var $defineProperty = __webpack_require__(8);

// B.2.2.2 Object.prototype.__defineGetter__(P, getter)
__webpack_require__(7) && $export($export.P + __webpack_require__(63), 'Object', {
  __defineGetter__: function __defineGetter__(P, getter) {
    $defineProperty.f(toObject(this), P, { get: aFunction(getter), enumerable: true, configurable: true });
  }
});


/***/ }),
/* 281 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var toObject = __webpack_require__(9);
var aFunction = __webpack_require__(10);
var $defineProperty = __webpack_require__(8);

// B.2.2.3 Object.prototype.__defineSetter__(P, setter)
__webpack_require__(7) && $export($export.P + __webpack_require__(63), 'Object', {
  __defineSetter__: function __defineSetter__(P, setter) {
    $defineProperty.f(toObject(this), P, { set: aFunction(setter), enumerable: true, configurable: true });
  }
});


/***/ }),
/* 282 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var toObject = __webpack_require__(9);
var toPrimitive = __webpack_require__(22);
var getPrototypeOf = __webpack_require__(17);
var getOwnPropertyDescriptor = __webpack_require__(16).f;

// B.2.2.4 Object.prototype.__lookupGetter__(P)
__webpack_require__(7) && $export($export.P + __webpack_require__(63), 'Object', {
  __lookupGetter__: function __lookupGetter__(P) {
    var O = toObject(this);
    var K = toPrimitive(P, true);
    var D;
    do {
      if (D = getOwnPropertyDescriptor(O, K)) return D.get;
    } while (O = getPrototypeOf(O));
  }
});


/***/ }),
/* 283 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var $export = __webpack_require__(0);
var toObject = __webpack_require__(9);
var toPrimitive = __webpack_require__(22);
var getPrototypeOf = __webpack_require__(17);
var getOwnPropertyDescriptor = __webpack_require__(16).f;

// B.2.2.5 Object.prototype.__lookupSetter__(P)
__webpack_require__(7) && $export($export.P + __webpack_require__(63), 'Object', {
  __lookupSetter__: function __lookupSetter__(P) {
    var O = toObject(this);
    var K = toPrimitive(P, true);
    var D;
    do {
      if (D = getOwnPropertyDescriptor(O, K)) return D.set;
    } while (O = getPrototypeOf(O));
  }
});


/***/ }),
/* 284 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/DavidBruant/Map-Set.prototype.toJSON
var $export = __webpack_require__(0);

$export($export.P + $export.R, 'Map', { toJSON: __webpack_require__(126)('Map') });


/***/ }),
/* 285 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/DavidBruant/Map-Set.prototype.toJSON
var $export = __webpack_require__(0);

$export($export.P + $export.R, 'Set', { toJSON: __webpack_require__(126)('Set') });


/***/ }),
/* 286 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-map.of
__webpack_require__(64)('Map');


/***/ }),
/* 287 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-set.of
__webpack_require__(64)('Set');


/***/ }),
/* 288 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-weakmap.of
__webpack_require__(64)('WeakMap');


/***/ }),
/* 289 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-weakset.of
__webpack_require__(64)('WeakSet');


/***/ }),
/* 290 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-map.from
__webpack_require__(65)('Map');


/***/ }),
/* 291 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-set.from
__webpack_require__(65)('Set');


/***/ }),
/* 292 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-weakmap.from
__webpack_require__(65)('WeakMap');


/***/ }),
/* 293 */
/***/ (function(module, exports, __webpack_require__) {

// https://tc39.github.io/proposal-setmap-offrom/#sec-weakset.from
__webpack_require__(65)('WeakSet');


/***/ }),
/* 294 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/tc39/proposal-global
var $export = __webpack_require__(0);

$export($export.G, { global: __webpack_require__(2) });


/***/ }),
/* 295 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/tc39/proposal-global
var $export = __webpack_require__(0);

$export($export.S, 'System', { global: __webpack_require__(2) });


/***/ }),
/* 296 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/ljharb/proposal-is-error
var $export = __webpack_require__(0);
var cof = __webpack_require__(19);

$export($export.S, 'Error', {
  isError: function isError(it) {
    return cof(it) === 'Error';
  }
});


/***/ }),
/* 297 */
/***/ (function(module, exports, __webpack_require__) {

// https://rwaldron.github.io/proposal-math-extensions/
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  clamp: function clamp(x, lower, upper) {
    return Math.min(upper, Math.max(lower, x));
  }
});


/***/ }),
/* 298 */
/***/ (function(module, exports, __webpack_require__) {

// https://rwaldron.github.io/proposal-math-extensions/
var $export = __webpack_require__(0);

$export($export.S, 'Math', { DEG_PER_RAD: Math.PI / 180 });


/***/ }),
/* 299 */
/***/ (function(module, exports, __webpack_require__) {

// https://rwaldron.github.io/proposal-math-extensions/
var $export = __webpack_require__(0);
var RAD_PER_DEG = 180 / Math.PI;

$export($export.S, 'Math', {
  degrees: function degrees(radians) {
    return radians * RAD_PER_DEG;
  }
});


/***/ }),
/* 300 */
/***/ (function(module, exports, __webpack_require__) {

// https://rwaldron.github.io/proposal-math-extensions/
var $export = __webpack_require__(0);
var scale = __webpack_require__(128);
var fround = __webpack_require__(107);

$export($export.S, 'Math', {
  fscale: function fscale(x, inLow, inHigh, outLow, outHigh) {
    return fround(scale(x, inLow, inHigh, outLow, outHigh));
  }
});


/***/ }),
/* 301 */
/***/ (function(module, exports, __webpack_require__) {

// https://gist.github.com/BrendanEich/4294d5c212a6d2254703
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  iaddh: function iaddh(x0, x1, y0, y1) {
    var $x0 = x0 >>> 0;
    var $x1 = x1 >>> 0;
    var $y0 = y0 >>> 0;
    return $x1 + (y1 >>> 0) + (($x0 & $y0 | ($x0 | $y0) & ~($x0 + $y0 >>> 0)) >>> 31) | 0;
  }
});


/***/ }),
/* 302 */
/***/ (function(module, exports, __webpack_require__) {

// https://gist.github.com/BrendanEich/4294d5c212a6d2254703
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  isubh: function isubh(x0, x1, y0, y1) {
    var $x0 = x0 >>> 0;
    var $x1 = x1 >>> 0;
    var $y0 = y0 >>> 0;
    return $x1 - (y1 >>> 0) - ((~$x0 & $y0 | ~($x0 ^ $y0) & $x0 - $y0 >>> 0) >>> 31) | 0;
  }
});


/***/ }),
/* 303 */
/***/ (function(module, exports, __webpack_require__) {

// https://gist.github.com/BrendanEich/4294d5c212a6d2254703
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  imulh: function imulh(u, v) {
    var UINT16 = 0xffff;
    var $u = +u;
    var $v = +v;
    var u0 = $u & UINT16;
    var v0 = $v & UINT16;
    var u1 = $u >> 16;
    var v1 = $v >> 16;
    var t = (u1 * v0 >>> 0) + (u0 * v0 >>> 16);
    return u1 * v1 + (t >> 16) + ((u0 * v1 >>> 0) + (t & UINT16) >> 16);
  }
});


/***/ }),
/* 304 */
/***/ (function(module, exports, __webpack_require__) {

// https://rwaldron.github.io/proposal-math-extensions/
var $export = __webpack_require__(0);

$export($export.S, 'Math', { RAD_PER_DEG: 180 / Math.PI });


/***/ }),
/* 305 */
/***/ (function(module, exports, __webpack_require__) {

// https://rwaldron.github.io/proposal-math-extensions/
var $export = __webpack_require__(0);
var DEG_PER_RAD = Math.PI / 180;

$export($export.S, 'Math', {
  radians: function radians(degrees) {
    return degrees * DEG_PER_RAD;
  }
});


/***/ }),
/* 306 */
/***/ (function(module, exports, __webpack_require__) {

// https://rwaldron.github.io/proposal-math-extensions/
var $export = __webpack_require__(0);

$export($export.S, 'Math', { scale: __webpack_require__(128) });


/***/ }),
/* 307 */
/***/ (function(module, exports, __webpack_require__) {

// https://gist.github.com/BrendanEich/4294d5c212a6d2254703
var $export = __webpack_require__(0);

$export($export.S, 'Math', {
  umulh: function umulh(u, v) {
    var UINT16 = 0xffff;
    var $u = +u;
    var $v = +v;
    var u0 = $u & UINT16;
    var v0 = $v & UINT16;
    var u1 = $u >>> 16;
    var v1 = $v >>> 16;
    var t = (u1 * v0 >>> 0) + (u0 * v0 >>> 16);
    return u1 * v1 + (t >>> 16) + ((u0 * v1 >>> 0) + (t & UINT16) >>> 16);
  }
});


/***/ }),
/* 308 */
/***/ (function(module, exports, __webpack_require__) {

// http://jfbastien.github.io/papers/Math.signbit.html
var $export = __webpack_require__(0);

$export($export.S, 'Math', { signbit: function signbit(x) {
  // eslint-disable-next-line no-self-compare
  return (x = +x) != x ? x : x == 0 ? 1 / x == Infinity : x > 0;
} });


/***/ }),
/* 309 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
// https://github.com/tc39/proposal-promise-finally

var $export = __webpack_require__(0);
var core = __webpack_require__(26);
var global = __webpack_require__(2);
var speciesConstructor = __webpack_require__(50);
var promiseResolve = __webpack_require__(115);

$export($export.P + $export.R, 'Promise', { 'finally': function (onFinally) {
  var C = speciesConstructor(this, core.Promise || global.Promise);
  var isFunction = typeof onFinally == 'function';
  return this.then(
    isFunction ? function (x) {
      return promiseResolve(C, onFinally()).then(function () { return x; });
    } : onFinally,
    isFunction ? function (e) {
      return promiseResolve(C, onFinally()).then(function () { throw e; });
    } : onFinally
  );
} });


/***/ }),
/* 310 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/tc39/proposal-promise-try
var $export = __webpack_require__(0);
var newPromiseCapability = __webpack_require__(91);
var perform = __webpack_require__(114);

$export($export.S, 'Promise', { 'try': function (callbackfn) {
  var promiseCapability = newPromiseCapability.f(this);
  var result = perform(callbackfn);
  (result.e ? promiseCapability.reject : promiseCapability.resolve)(result.v);
  return promiseCapability.promise;
} });


/***/ }),
/* 311 */
/***/ (function(module, exports, __webpack_require__) {

var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var toMetaKey = metadata.key;
var ordinaryDefineOwnMetadata = metadata.set;

metadata.exp({ defineMetadata: function defineMetadata(metadataKey, metadataValue, target, targetKey) {
  ordinaryDefineOwnMetadata(metadataKey, metadataValue, anObject(target), toMetaKey(targetKey));
} });


/***/ }),
/* 312 */
/***/ (function(module, exports, __webpack_require__) {

var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var toMetaKey = metadata.key;
var getOrCreateMetadataMap = metadata.map;
var store = metadata.store;

metadata.exp({ deleteMetadata: function deleteMetadata(metadataKey, target /* , targetKey */) {
  var targetKey = arguments.length < 3 ? undefined : toMetaKey(arguments[2]);
  var metadataMap = getOrCreateMetadataMap(anObject(target), targetKey, false);
  if (metadataMap === undefined || !metadataMap['delete'](metadataKey)) return false;
  if (metadataMap.size) return true;
  var targetMetadata = store.get(target);
  targetMetadata['delete'](targetKey);
  return !!targetMetadata.size || store['delete'](target);
} });


/***/ }),
/* 313 */
/***/ (function(module, exports, __webpack_require__) {

var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var getPrototypeOf = __webpack_require__(17);
var ordinaryHasOwnMetadata = metadata.has;
var ordinaryGetOwnMetadata = metadata.get;
var toMetaKey = metadata.key;

var ordinaryGetMetadata = function (MetadataKey, O, P) {
  var hasOwn = ordinaryHasOwnMetadata(MetadataKey, O, P);
  if (hasOwn) return ordinaryGetOwnMetadata(MetadataKey, O, P);
  var parent = getPrototypeOf(O);
  return parent !== null ? ordinaryGetMetadata(MetadataKey, parent, P) : undefined;
};

metadata.exp({ getMetadata: function getMetadata(metadataKey, target /* , targetKey */) {
  return ordinaryGetMetadata(metadataKey, anObject(target), arguments.length < 3 ? undefined : toMetaKey(arguments[2]));
} });


/***/ }),
/* 314 */
/***/ (function(module, exports, __webpack_require__) {

var Set = __webpack_require__(118);
var from = __webpack_require__(127);
var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var getPrototypeOf = __webpack_require__(17);
var ordinaryOwnMetadataKeys = metadata.keys;
var toMetaKey = metadata.key;

var ordinaryMetadataKeys = function (O, P) {
  var oKeys = ordinaryOwnMetadataKeys(O, P);
  var parent = getPrototypeOf(O);
  if (parent === null) return oKeys;
  var pKeys = ordinaryMetadataKeys(parent, P);
  return pKeys.length ? oKeys.length ? from(new Set(oKeys.concat(pKeys))) : pKeys : oKeys;
};

metadata.exp({ getMetadataKeys: function getMetadataKeys(target /* , targetKey */) {
  return ordinaryMetadataKeys(anObject(target), arguments.length < 2 ? undefined : toMetaKey(arguments[1]));
} });


/***/ }),
/* 315 */
/***/ (function(module, exports, __webpack_require__) {

var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var ordinaryGetOwnMetadata = metadata.get;
var toMetaKey = metadata.key;

metadata.exp({ getOwnMetadata: function getOwnMetadata(metadataKey, target /* , targetKey */) {
  return ordinaryGetOwnMetadata(metadataKey, anObject(target)
    , arguments.length < 3 ? undefined : toMetaKey(arguments[2]));
} });


/***/ }),
/* 316 */
/***/ (function(module, exports, __webpack_require__) {

var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var ordinaryOwnMetadataKeys = metadata.keys;
var toMetaKey = metadata.key;

metadata.exp({ getOwnMetadataKeys: function getOwnMetadataKeys(target /* , targetKey */) {
  return ordinaryOwnMetadataKeys(anObject(target), arguments.length < 2 ? undefined : toMetaKey(arguments[1]));
} });


/***/ }),
/* 317 */
/***/ (function(module, exports, __webpack_require__) {

var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var getPrototypeOf = __webpack_require__(17);
var ordinaryHasOwnMetadata = metadata.has;
var toMetaKey = metadata.key;

var ordinaryHasMetadata = function (MetadataKey, O, P) {
  var hasOwn = ordinaryHasOwnMetadata(MetadataKey, O, P);
  if (hasOwn) return true;
  var parent = getPrototypeOf(O);
  return parent !== null ? ordinaryHasMetadata(MetadataKey, parent, P) : false;
};

metadata.exp({ hasMetadata: function hasMetadata(metadataKey, target /* , targetKey */) {
  return ordinaryHasMetadata(metadataKey, anObject(target), arguments.length < 3 ? undefined : toMetaKey(arguments[2]));
} });


/***/ }),
/* 318 */
/***/ (function(module, exports, __webpack_require__) {

var metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var ordinaryHasOwnMetadata = metadata.has;
var toMetaKey = metadata.key;

metadata.exp({ hasOwnMetadata: function hasOwnMetadata(metadataKey, target /* , targetKey */) {
  return ordinaryHasOwnMetadata(metadataKey, anObject(target)
    , arguments.length < 3 ? undefined : toMetaKey(arguments[2]));
} });


/***/ }),
/* 319 */
/***/ (function(module, exports, __webpack_require__) {

var $metadata = __webpack_require__(28);
var anObject = __webpack_require__(1);
var aFunction = __webpack_require__(10);
var toMetaKey = $metadata.key;
var ordinaryDefineOwnMetadata = $metadata.set;

$metadata.exp({ metadata: function metadata(metadataKey, metadataValue) {
  return function decorator(target, targetKey) {
    ordinaryDefineOwnMetadata(
      metadataKey, metadataValue,
      (targetKey !== undefined ? anObject : aFunction)(target),
      toMetaKey(targetKey)
    );
  };
} });


/***/ }),
/* 320 */
/***/ (function(module, exports, __webpack_require__) {

// https://github.com/rwaldron/tc39-notes/blob/master/es6/2014-09/sept-25.md#510-globalasap-for-enqueuing-a-microtask
var $export = __webpack_require__(0);
var microtask = __webpack_require__(90)();
var process = __webpack_require__(2).process;
var isNode = __webpack_require__(19)(process) == 'process';

$export($export.G, {
  asap: function asap(fn) {
    var domain = isNode && process.domain;
    microtask(domain ? domain.bind(fn) : fn);
  }
});


/***/ }),
/* 321 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

// https://github.com/zenparsing/es-observable
var $export = __webpack_require__(0);
var global = __webpack_require__(2);
var core = __webpack_require__(26);
var microtask = __webpack_require__(90)();
var OBSERVABLE = __webpack_require__(5)('observable');
var aFunction = __webpack_require__(10);
var anObject = __webpack_require__(1);
var anInstance = __webpack_require__(39);
var redefineAll = __webpack_require__(41);
var hide = __webpack_require__(11);
var forOf = __webpack_require__(40);
var RETURN = forOf.RETURN;

var getMethod = function (fn) {
  return fn == null ? undefined : aFunction(fn);
};

var cleanupSubscription = function (subscription) {
  var cleanup = subscription._c;
  if (cleanup) {
    subscription._c = undefined;
    cleanup();
  }
};

var subscriptionClosed = function (subscription) {
  return subscription._o === undefined;
};

var closeSubscription = function (subscription) {
  if (!subscriptionClosed(subscription)) {
    subscription._o = undefined;
    cleanupSubscription(subscription);
  }
};

var Subscription = function (observer, subscriber) {
  anObject(observer);
  this._c = undefined;
  this._o = observer;
  observer = new SubscriptionObserver(this);
  try {
    var cleanup = subscriber(observer);
    var subscription = cleanup;
    if (cleanup != null) {
      if (typeof cleanup.unsubscribe === 'function') cleanup = function () { subscription.unsubscribe(); };
      else aFunction(cleanup);
      this._c = cleanup;
    }
  } catch (e) {
    observer.error(e);
    return;
  } if (subscriptionClosed(this)) cleanupSubscription(this);
};

Subscription.prototype = redefineAll({}, {
  unsubscribe: function unsubscribe() { closeSubscription(this); }
});

var SubscriptionObserver = function (subscription) {
  this._s = subscription;
};

SubscriptionObserver.prototype = redefineAll({}, {
  next: function next(value) {
    var subscription = this._s;
    if (!subscriptionClosed(subscription)) {
      var observer = subscription._o;
      try {
        var m = getMethod(observer.next);
        if (m) return m.call(observer, value);
      } catch (e) {
        try {
          closeSubscription(subscription);
        } finally {
          throw e;
        }
      }
    }
  },
  error: function error(value) {
    var subscription = this._s;
    if (subscriptionClosed(subscription)) throw value;
    var observer = subscription._o;
    subscription._o = undefined;
    try {
      var m = getMethod(observer.error);
      if (!m) throw value;
      value = m.call(observer, value);
    } catch (e) {
      try {
        cleanupSubscription(subscription);
      } finally {
        throw e;
      }
    } cleanupSubscription(subscription);
    return value;
  },
  complete: function complete(value) {
    var subscription = this._s;
    if (!subscriptionClosed(subscription)) {
      var observer = subscription._o;
      subscription._o = undefined;
      try {
        var m = getMethod(observer.complete);
        value = m ? m.call(observer, value) : undefined;
      } catch (e) {
        try {
          cleanupSubscription(subscription);
        } finally {
          throw e;
        }
      } cleanupSubscription(subscription);
      return value;
    }
  }
});

var $Observable = function Observable(subscriber) {
  anInstance(this, $Observable, 'Observable', '_f')._f = aFunction(subscriber);
};

redefineAll($Observable.prototype, {
  subscribe: function subscribe(observer) {
    return new Subscription(observer, this._f);
  },
  forEach: function forEach(fn) {
    var that = this;
    return new (core.Promise || global.Promise)(function (resolve, reject) {
      aFunction(fn);
      var subscription = that.subscribe({
        next: function (value) {
          try {
            return fn(value);
          } catch (e) {
            reject(e);
            subscription.unsubscribe();
          }
        },
        error: reject,
        complete: resolve
      });
    });
  }
});

redefineAll($Observable, {
  from: function from(x) {
    var C = typeof this === 'function' ? this : $Observable;
    var method = getMethod(anObject(x)[OBSERVABLE]);
    if (method) {
      var observable = anObject(method.call(x));
      return observable.constructor === C ? observable : new C(function (observer) {
        return observable.subscribe(observer);
      });
    }
    return new C(function (observer) {
      var done = false;
      microtask(function () {
        if (!done) {
          try {
            if (forOf(x, false, function (it) {
              observer.next(it);
              if (done) return RETURN;
            }) === RETURN) return;
          } catch (e) {
            if (done) throw e;
            observer.error(e);
            return;
          } observer.complete();
        }
      });
      return function () { done = true; };
    });
  },
  of: function of() {
    for (var i = 0, l = arguments.length, items = new Array(l); i < l;) items[i] = arguments[i++];
    return new (typeof this === 'function' ? this : $Observable)(function (observer) {
      var done = false;
      microtask(function () {
        if (!done) {
          for (var j = 0; j < items.length; ++j) {
            observer.next(items[j]);
            if (done) return;
          } observer.complete();
        }
      });
      return function () { done = true; };
    });
  }
});

hide($Observable.prototype, OBSERVABLE, function () { return this; });

$export($export.G, { Observable: $Observable });

__webpack_require__(38)('Observable');


/***/ }),
/* 322 */
/***/ (function(module, exports, __webpack_require__) {

var $export = __webpack_require__(0);
var $task = __webpack_require__(89);
$export($export.G + $export.B, {
  setImmediate: $task.set,
  clearImmediate: $task.clear
});


/***/ }),
/* 323 */
/***/ (function(module, exports, __webpack_require__) {

var $iterators = __webpack_require__(86);
var getKeys = __webpack_require__(34);
var redefine = __webpack_require__(12);
var global = __webpack_require__(2);
var hide = __webpack_require__(11);
var Iterators = __webpack_require__(45);
var wks = __webpack_require__(5);
var ITERATOR = wks('iterator');
var TO_STRING_TAG = wks('toStringTag');
var ArrayValues = Iterators.Array;

var DOMIterables = {
  CSSRuleList: true, // TODO: Not spec compliant, should be false.
  CSSStyleDeclaration: false,
  CSSValueList: false,
  ClientRectList: false,
  DOMRectList: false,
  DOMStringList: false,
  DOMTokenList: true,
  DataTransferItemList: false,
  FileList: false,
  HTMLAllCollection: false,
  HTMLCollection: false,
  HTMLFormElement: false,
  HTMLSelectElement: false,
  MediaList: true, // TODO: Not spec compliant, should be false.
  MimeTypeArray: false,
  NamedNodeMap: false,
  NodeList: true,
  PaintRequestList: false,
  Plugin: false,
  PluginArray: false,
  SVGLengthList: false,
  SVGNumberList: false,
  SVGPathSegList: false,
  SVGPointList: false,
  SVGStringList: false,
  SVGTransformList: false,
  SourceBufferList: false,
  StyleSheetList: true, // TODO: Not spec compliant, should be false.
  TextTrackCueList: false,
  TextTrackList: false,
  TouchList: false
};

for (var collections = getKeys(DOMIterables), i = 0; i < collections.length; i++) {
  var NAME = collections[i];
  var explicit = DOMIterables[NAME];
  var Collection = global[NAME];
  var proto = Collection && Collection.prototype;
  var key;
  if (proto) {
    if (!proto[ITERATOR]) hide(proto, ITERATOR, ArrayValues);
    if (!proto[TO_STRING_TAG]) hide(proto, TO_STRING_TAG, NAME);
    Iterators[NAME] = ArrayValues;
    if (explicit) for (key in $iterators) if (!proto[key]) redefine(proto, key, $iterators[key], true);
  }
}


/***/ }),
/* 324 */
/***/ (function(module, exports, __webpack_require__) {

// ie9- setTimeout & setInterval additional parameters fix
var global = __webpack_require__(2);
var $export = __webpack_require__(0);
var userAgent = __webpack_require__(60);
var slice = [].slice;
var MSIE = /MSIE .\./.test(userAgent); // <- dirty ie9- check
var wrap = function (set) {
  return function (fn, time /* , ...args */) {
    var boundArgs = arguments.length > 2;
    var args = boundArgs ? slice.call(arguments, 2) : false;
    return set(boundArgs ? function () {
      // eslint-disable-next-line no-new-func
      (typeof fn == 'function' ? fn : Function(fn)).apply(this, args);
    } : fn, time);
  };
};
$export($export.G + $export.B + $export.F * MSIE, {
  setTimeout: wrap(global.setTimeout),
  setInterval: wrap(global.setInterval)
});


/***/ })
/******/ ]);
// CommonJS export
if (typeof module != 'undefined' && module.exports) module.exports = __e;
// RequireJS export
else if (typeof define == 'function' && define.amd) define(function () { return __e; });
// Export to global object
else __g.core = __e;
}(1, 1);/*
 * this file is part of
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2010-2014, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * Copyright 2015-2017 - Radosław Włodkowski, www.wlodkowski.net, radoslaw@wlodkowski.net
 *
 * under GNU General Public License
 * http://www.projekktor.com/license/
 */

window.projekktor = window.$p = (function (window, document, $) {

    "use strict";

    var projekktors = [];

    // this object is returned in case multiple player's are requested
    function Iterator(arr) {
        this.length = arr.length;
        this.each = function (fn) {
            $.each(arr, fn);
        };
        this.size = function () {
            return arr.length;
        };
    }


    function PPlayer(srcNode, cfg, onReady) {
        this.config = new projekktorConfig();

        this.storage = new projekktorPersistentStorage(this);

        this.env = {
            muted: false,
            volume: 1,
            playerDom: null,
            mediaContainer: null,
            mouseIsOver: false,
            loading: false, // important
            className: '',
            onReady: onReady
        };

        this.media = [];
        this._plugins = [];
        this._pluginCache = {};
        this._queue = [];
        this._cuePoints = {};
        this.listeners = [];
        this.playerModel = {};
        this._isReady = false;
        this._isLive = false;
        this._isFullViewport = false;
        this._maxElapsed = 0;
        this._playlistServer = '';
        this._id = '';
        this._parsers = {};

        this.itemRules = [
            function () {
                return arguments[0].id != null;
            },
            function () {
                return arguments[0].config.active !== false;
            },
            function () {
                return arguments[0].config.maxviews == null || arguments[0].viewcount < arguments[0].config.maxviews;
            }
        ];

        /**
         * Add items to the playlist on provided index
         *
         * @param {array} items - playlist items to add
         * @param {number} [index=this.media.length] - index on which the items should be added
         * @param {boolean} [replace=false] - should the items on specified index be replaced
         * @returns {object} object with affected index, added and replaced (removed) items.
         * For example when nothing was added the object will look like: {added: [], removed: [], index: -1}
         */
        this.addItems = function (items, index, replace) {

            var result = {
                    added: [],
                    removed: [],
                    indexes: [],
                    currentItemAffected: false
                },
                i, l,
                item,
                files,
                itemIds = [],
                currentItem = this.getItem();

            replace = !!replace || false; // default is false

            // constrain index to the range
            index = (typeof index !== 'number') ? this.media.length : index;
            index = (index > this.media.length) ? this.media.length : index;
            index = (index < 0) ? 0 : index;

            // check if there is data to add
            if ($.isEmptyObject(items)) {
                return result;
            }

            // check if items are not the reference to the actual media array (for example when result of getPlaylist() is passed)
            if (items === this.media) {
                items = items.slice(); // clone
            }

            // check if items is an array and if it's not push it to the array
            if (!$.isArray(items)) {
                items = [items];
            }

            // be sure that items are unique and processed
            for (i = 0, l = items.length; i < l; i++) {

                item = items[i];
                files = [];

                $.each(item, function (key, value) {
                    if ($.isNumeric(key)) {
                        files.push(value);
                    }
                });

                // item is not processed by _prepareMedia yet
                if (item.processed !== true) {
                    item = this._processItem({
                        file: files,
                        config: item.config || {}
                    });
                }

                // check if the id is unique in currently added array
                if ($.inArray(item.id, itemIds) > -1) {
                    item.id = item.id + '_' + $p.utils.randomId(8);
                }

                // item is already on the playlist, so provide an unique copy of it
                if (this.getItemById(item.id)) {
                    item = $.extend(true, {}, item);
                    item.id = $p.utils.randomId(8);
                }

                // set cuepoints if there are some
                if (item.hasOwnProperty('cuepoints') && !!item.cuepoints) {
                    this.setCuePoints(item.cuepoints, item.id, true);
                }

                itemIds.push(item.id);
                items[i] = item;
            }

            // add item
            result.added = items;
            result.removed = Array.prototype.splice.apply(this.media, [index,
                (replace === true ? items.length : 0)
            ].concat(items));
            result.indexes = [index];
            result.currentItemAffected = $.inArray(currentItem, result.removed) > -1;

            this._promote('scheduleModified', result);

            return result;
        };

        /**
         * Shortcut function to remove item from playlist at given index
         *
         * @param {number} [index=this.media.length-1] - index of item to remove. Default is the last one on the playlist.
         * @returns {object} - object with affected index, removed item  e.g.: {added: [], removed: [], index: -1}
         */
        this.removeItemAtIndex = function (index) {

            var result = {
                    added: [],
                    removed: [],
                    indexes: [],
                    currentItemAffected: false
                },
                func = function (itm, idx) {
                    return idx === index;
                };

            // check if we could remove something
            if (typeof index !== 'number' ||
                this.media.length === 0 ||
                index > this.media.length - 1 ||
                index < 0) {
                return result;
            }

            // remove item
            result = this.removeItems(func);

            return result;
        };

        /**
         * Shortcut function to remove item by id
         * @param {string} itemId
         * @returns {object}
         */
        this.removeItemById = function (itemId) {
            var result = {
                    added: [],
                    removed: [],
                    indexes: [],
                    currentItemAffected: false
                },
                func = function (itm, idx) {
                    return itm.id === itemId;
                };

            // check if we could remove something
            if (typeof itemId !== 'string' ||
                this.media.length === 0) {
                return result;
            }

            result = this.removeItems(func);

            return result;
        };

        this.removeItemsCategory = function (catName) {
            var result = {
                    added: [],
                    removed: [],
                    indexes: [],
                    currentItemAffected: false
                },
                func = function (itm, idx) {
                    return itm.cat === catName;
                };

            // check if we could remove something
            if (typeof catName !== 'string' ||
                this.media.length === 0) {
                return result;
            }

            result = this.removeItems(func);

            return result;
        };

        /**
         * Remove playlist items which satisfy a filter function. If no function provided then all items are removed
         * @param {function} [which] - function( Object elementOfArray, Integer indexInArray ) => Boolean;
         * The function to process each playlist item against. The first argument to the function is the item,
         * and the second argument is the index. The function should return a Boolean value.
         * @returns {object} - object with affected index, removed item  e.g.: {added: [], removed: [], index: -1}
         */
        this.removeItems = function (which) {

            var result = {
                    added: [], // just for consistency with addItems()
                    removed: [],
                    indexes: [],
                    currentItemAffected: false
                },
                currentItem = this.getItem(),
                toRemove,
                toRemoveIndexes = [],
                i, l;

            if (typeof which === 'undefined') {
                which = function (itm, idx) {
                    return true;
                };
            } else if (!$.isFunction(which)) {
                return result;
            }

            // check if there anything to remove
            if (this.media.length === 0) {
                return result;
            }

            toRemove = $.grep(this.media, which);

            for (i = 0, l = toRemove.length; i < l; i++) {
                toRemoveIndexes.push($.inArray(toRemove[i], this.media));
            }

            for (i = 0, l = toRemoveIndexes.length; i < l; i++) {
                result.removed.push(this.media.splice(toRemoveIndexes[i] - i, 1)[0]);
            }

            result.indexes = toRemoveIndexes;
            result.currentItemAffected = $.inArray(currentItem, result.removed) > -1;

            this._promote('scheduleModified', result);

            return result;
        };

        this.getItemById = function (itemId) {
            return this.media.find(function (item) {
                return (itemId === item.id);
            }) || null;
        };

        this.getItemsByCatName = function (catName) {
            return this.media.filter(function (item) {
                return (catName === item.cat);
            }) || [];
        };

        /**
         * Returns all possible platform names implemented in projekktor which are potentially 
         * able to play the MIME Type specified in the argument. 
         */
        this._canPlayOnPlatforms = function (mimeType) {
            var platformsSet = new Set(),
                mILove = $p.cache.modelsILove || [];

            mILove.forEach(function (iLove) {
                if (iLove.type === mimeType) {
                    iLove.platform.forEach(function (platform) {
                        platformsSet.add(platform);
                    });
                }
            });

            return platformsSet;
        };

        /**
         * Checks if mimeType can be played using specified platform
         */
        this._canPlay = function (mimeType, platform) {

            var platformMimeTypeMap = this.getSupportedPlatforms(),
                pt = (typeof platform === "string") ? platform.toLowerCase() : "browser",
                type = (typeof mimeType === "string") ? mimeType.toLowerCase() : undefined;

            // if mimeType is undefined we have nothing to look for
            if (type === undefined) {
                return false;
            }

            // platform unsupported
            if (!platformMimeTypeMap.has(pt)) {
                return false;
            }

            // everything fine
            // check if specified platform is supporting mimeType we are looking for
            return platformMimeTypeMap.get(pt).has(type);
        };

        this._processItem = function (itemData) {
            var files = itemData.file || [],
                config = itemData.config || {},
                defaultItem = {
                    id: config.id || $p.utils.randomId(8),
                    cat: config.cat || 'clip',
                    file: [],
                    availableFiles: files,
                    platform: 'browser',
                    qualities: [], // available quality keys
                    model: 'NA',
                    errorCode: undefined,
                    viewcount: 0,
                    processed: false,
                    config: config,
                    cuepoints: []
                },
                resultItem = $.extend({}, defaultItem);

            // leave only supported files
            resultItem = this._filterSupportedItemFiles(resultItem);

            if (resultItem.file.length) {
                // In this place we are dealing only with potentially playable files.
                // Now we need to select the best one(s) to play.
                resultItem = this._getBestModelForItem(resultItem);

                // leave only valid files for the selected model/platform
                resultItem = this._filterFiles(resultItem, function (file, idx, files) {
                    return file.type === files[0].type;
                });

                // finally check for available qualities and remove redundant file formats
                resultItem = this._filterQualities(resultItem);
            }

            resultItem.processed = true;

            return resultItem;
        };

        this._processItemFile = function (file) {
            var parsedMimeType,
                resultFile = {
                    src: $p.utils.toAbsoluteURL(file.src),
                    type: 'none/none',
                    originalType: file.type,
                    drm: file.drm || [],
                    codecs: undefined,
                    quality: file.quality || 'auto'
                };

            // check and cleanup provided mimeType
            if (file.type) {
                parsedMimeType = $p.utils.parseMimeType(file.type);
                resultFile.type = parsedMimeType.type + "/" + parsedMimeType.subtype;
                resultFile.codecs = parsedMimeType.parameters.codecs;
            }
            // if type is not set try to get it from file extension
            else {
                resultFile.type = ref._getTypeFromFileExtension(file.src);
            }

            return resultFile;
        };

        this._filterSupportedItemFiles = function (item) {

            var ref = this,
                inFiles = item.availableFiles || [],
                outFiles = [];

            // select only playable files
            inFiles.forEach(function (file) {
                var processedFile = ref._processItemFile(file),
                    mimeType = processedFile.type,
                    drm = processedFile.drm;

                // check if the format is supported
                if (ref.getCanPlay(mimeType)) {
                    // check if there is any DRM system specified 
                    if (drm.length) {
                        // if it is then check if it's supported
                        if (drm.some(function (drmSystem) {
                                return ref.getCanPlayWithDrm(drmSystem, mimeType);
                            })) {
                            // if so add this file to the list
                            outFiles.push(processedFile);
                        }
                        // if it's not then add appropriate error code
                        else {
                            item.errorCode = 300;
                        }
                    }
                    // if it's not then just add the file to the list
                    else {
                        outFiles.push(processedFile);
                    }
                }
                // add error code for unsupported file format
                else {
                    item.errorCode = 5;
                }
            });

            // cleanup errorCode if there are some playable files
            if (outFiles.length) {
                item.errorCode = undefined;
            }

            item.file = outFiles;

            return item;
        };

        this._getBestModelForItem = function (item) {
            var ref = this,
                files = item.file,
                config = item.config || {},
                prioritizeBy = config.prioritizeBy || this.getConfig('prioritizeBy'),
                platformPriorities = Array.from(this.getSupportedPlatforms().keys()),
                resultILoves = [],
                file,
                selectedModel = item.model,
                selectedPlatform = item.platform;

            // select best model based on defined priorities
            if (prioritizeBy === 'sourcesOrder') {
                // in 'sourcesOrder' mode we just need to find a proper model
                // for the first playable file
                file = files[0];
            } else {
                /**
                 * In platformsOrder mode we need to find the first file supported by the 
                 * platform with highest priority.
                 */
                platformPriorities.some(function (pt) {
                    selectedPlatform = pt;
                    file = files.find(function (f) {
                        if (f.drm.length) {
                            return f.drm.some(function (drmSystem) {
                                return ref.getCanPlayWithDrm(drmSystem, f.type, [pt]);
                            });
                        } else {
                            return ref.getCanPlay(f.type, [pt]);
                        }
                    });
                    return file !== undefined;
                });
            }

            /**
             * Get only sensible iLoves in this context
             */
            resultILoves = this._filterModelILoves(file.type, file.drm);

            /**
             * Now resultILoves is filled only with compatible and supported models iLoves
             * but probably in the wrong order. Select first one with the highest priority
             * for supported platforms.
             */

            platformPriorities.some(function (pt) {
                selectedPlatform = pt;
                selectedModel = resultILoves.find(function (iLove) {
                    return (iLove.platform.indexOf(pt) > -1);
                });

                return selectedModel !== undefined;
            });

            // move selected file to the beginning of the array
            item.file = files.splice(files.indexOf(file), 1).concat(files);
            item.model = selectedModel.model;
            item.platform = selectedPlatform;

            return item;
        };

        this._filterModelILoves = function (mimeType, drmSystems) {
            var modelsILoveSupported = $p.cache.modelsILoveSupported,
                drm = drmSystems || [];

            return modelsILoveSupported.filter(function (iLove) {
                return (iLove.type === mimeType &&
                    (!drm.length // no DRM support needed
                        // DRM support needed
                        ||
                        (iLove.drm // model has defined DRM support
                            &&
                            $p.utils.intersect(iLove.drm, drm).length // and this is the DRM support we need
                        )
                    )
                );
            });
        };

        this._filterQualities = function (item) {
            var inFiles = item.file,
                qualityDefinitions = item.config.playbackQualities || this.getConfig('playbackQualities') || [],
                fileQualityKeys = [],
                definedQualityKeys = qualityDefinitions.map(function (q) {
                    return q.key;
                }),
                outFiles = [];

            // always push 'auto' to the definedQualityKeys
            definedQualityKeys.push('auto');

            // collect all quality keys from available files
            inFiles.forEach(function (file) {
                fileQualityKeys.push(file.quality);
            });

            // leave only unique ones
            fileQualityKeys = $p.utils.unique(fileQualityKeys);

            // are there proper definitions for those quality keys?
            // leave only valid ones
            fileQualityKeys = $p.utils.intersect(fileQualityKeys, definedQualityKeys);

            // is there more than one quality
            if (fileQualityKeys.length > 1) {
                // leave only one file for each valid key
                fileQualityKeys.forEach(function (qKey) {
                    outFiles.push(inFiles.find(function (file) {
                        return file.quality === qKey;
                    }));
                });
            }

            // if there is no usable quality file
            // add first file from playable ones and overwrite its quality with 'auto'
            if (outFiles.length === 0) {
                inFiles[0].quality = 'auto';
                outFiles.push(inFiles[0]);
            }

            item.file = outFiles;
            item.qualities = fileQualityKeys;

            return item;
        };

        this._filterFiles = function (item, filterFunc) {
            var files = item.file || [];

            item.file = files.filter(filterFunc);

            return item;
        };

        /********************************************************************************************
         Event Handlers:
         *********************************************************************************************/

        /* Event Handlers */

        this.displayReadyHandler = function () {

            this._syncPlugins('displayready');
        };

        this.modelReadyHandler = function () {

            this._maxElapsed = 0;
            this._promote('item', this.getItemIdx());
        };

        this.pluginsReadyHandler = function (obj) {

            switch (obj.callee) {
                case 'parserscollected':
                    var parser = this.getParser(obj.data[2]);
                    this.setPlaylist(parser(obj.data));
                    if (this.getItemCount() < 1) {
                        this.setPlaylist();
                    }
                    break;

                case 'reelupdate':
                    this._promote('playlistLoaded', this.getPlaylist());
                    this.setActiveItem(0);
                    break;

                case 'displayready':
                    this._addGUIListeners();
                    this._promote('synchronized');
                    if (this.getState('AWAKENING')) {
                        this.playerModel.start();
                    }
                    if (!this._isReady) {
                        this._promote('ready');
                    }
                    break;

                case 'awakening':
                    if (this.getState('AWAKENING')) {
                        this.playerModel.displayItem(true);
                    }
                    break;
            }
        };

        this.synchronizedHandler = function (forceAutoplay) {

            if (this._isReady) {

                if (this.playerModel.init && (this.playerModel._ap === true || forceAutoplay === true) && this.getState('IDLE')) {
                    this.setPlay();
                }
            }
        };

        this.scheduleModifiedHandler = function (event) {
            if (event.currentItemAffected) {
                this.setActiveItem('next');
            }
        };

        this.readyHandler = function () {

            this._isReady = true;

            if (typeof onReady === 'function') {
                onReady(this);
            }

            this.synchronizedHandler(this.getConfig('autoplay'));
        };

        this.stateHandler = function (stateValue) {

            var ref = this;

            // change player css classes in order to reflect current state:
            var classes = $.map(this.getDC().attr("class").split(" "), function (item) {
                return item.indexOf(ref.getConfig('ns') + "state") === -1 ? item : null;
            });

            classes.push(this.getConfig('ns') + "state" + stateValue.toLowerCase());
            this.getDC().attr("class", classes.join(" "));

            switch (stateValue) {
                case 'STARTING':
                    this.getItem().viewcount++;
                    break;

                case 'AWAKENING':
                    this._syncPlugins('awakening');
                    break;

                case 'ERROR':
                    this._addGUIListeners();
                    if (this.getConfig('skipTestcard')) {
                        this.setActiveItem('next');
                    }
                    break;

                case 'COMPLETED':
                    this.setActiveItem('next');
                    break;

                case 'IDLE':
                    if (this.getConfig('leaveFullscreen')) {
                        this.setFullscreen(false);
                    }
                    break;
            }
        };

        this.volumeHandler = function (value) {
            var muted;

            if (value <= 0) {
                muted = true;
            } else {
                muted = false;
            }

            if (muted !== this.env.muted) {
                this.env.muted = muted;
                this.storage.save('muted', muted);
                this._promote('muted', muted);
            }

            this.storage.save('volume', value);
            this.env.volume = value;
        };

        this.playlistHandler = function (value) {
            this.setFile(value.file, value.type);
        };

        this.cuepointsAddHandler = function (value) {
            this._cuepointsChangeEventHandler(value);
        };

        this.cuepointsRemoveHandler = function (value) {
            this._cuepointsChangeEventHandler(value);
        };

        this.fullscreenHandler = function (goFullscreen) {

            if (goFullscreen === true) {
                this._requestFullscreen();
                this.getDC().addClass(this.getNS() + 'fullscreen');
            } else {
                this._exitFullscreen();
                this.getDC().removeClass(this.getNS() + 'fullscreen');
            }
        };

        this.configHandler = function (value) {
            this.setConfig(value);
        };

        this.timeHandler = function (value) {

            if (this._maxElapsed < value) {

                var pct = Math.round(value * 100 / this.getDuration()),
                    evt = false;

                if (pct < 25) {
                    pct = 25;
                }
                if (pct > 25 && pct < 50) {
                    evt = 'firstquartile';
                    pct = 50;
                }
                if (pct > 50 && pct < 75) {
                    evt = 'midpoint';
                    pct = 75;
                }
                if (pct > 75 && pct < 100) {
                    evt = 'thirdquartile';
                    pct = 100;
                }

                if (evt !== false) {
                    this._promote(evt, value);
                }

                this._maxElapsed = (this.getDuration() * pct / 100);
            }
        };

        this.availableQualitiesChangeHandler = function (value) {

            this.getItem().qualities = value;
        };

        this.qualityChangeHandler = function (value) {

            this.setConfig({
                playbackQuality: value
            });
        };

        this.streamTypeChangeHandler = function (value) {

            if (value === 'dvr' || value === 'live') {
                this._isLive = true;
            } else {
                this._isLive = false;
            }

            switch (value) {
                case 'dvr':
                    this.getDC().addClass(this.getNS() + 'dvr');
                    this.getDC().addClass(this.getNS() + 'live');
                    break;
                case 'live':
                    this.getDC().removeClass(this.getNS() + 'dvr');
                    this.getDC().addClass(this.getNS() + 'live');
                    break;
                default:
                    this.getDC().removeClass(this.getNS() + 'dvr');
                    this.getDC().removeClass(this.getNS() + 'live');
                    break;
            }
        };

        this.doneHandler = function () {

            this.setActiveItem(0, false);

            // prevent player-hangup in situations where
            // playlist becomes virtually empty by applied filter rules (e.g. maxviews)
            if (!this.getNextItem()) {
                //this.reset();
            }
        };

        this._syncPlugins = function (callee, data) {

            // wait for all plugins to re-initialize properly
            var ref = this,
                sync = function () {
                    try {
                        if (ref._plugins.length > 0) {
                            for (var i = 0; i < ref._plugins.length; i++) {
                                if (!ref._plugins[i].isReady()) {
                                    setTimeout(sync, 50);
                                    return;
                                }
                            }
                        }
                        ref._promote('pluginsReady', {
                            callee: callee,
                            data: data
                        });
                    } catch (e) {}
                };

            setTimeout(sync, 50);
        };

        /* attach mouse-listeners to GUI elements */
        this._addGUIListeners = function () {

            var ref = this;

            this._removeGUIListeners();

            this.getDC().on("mousedown mousemove mouseenter mouseleave focus blur", function handler(e) {
                ref._playerFocusListener(e);
            });

            $(window)
                .on('resize.projekktor' + this.getId(), function () {
                    ref.setSize();
                })
                .on('touchstart.projekktor' + this.getId(), function (event) {
                    ref._windowTouchListener(event);
                });

            if (this.config.enableKeyboard === true) {
                $(document).off('keydown.pp' + this._id);
                $(document).on('keydown.pp' + this._id, function (evt) {
                    ref._keyListener(evt);
                });
            }
        };

        /* remove mouse-listeners */
        this._removeGUIListeners = function () {

            $("#" + this.getId()).off();
            this.getDC().off();


            $(window).off('touchstart.projekktor' + this.getId());
            $(window).off('resize.projekktor' + this.getId());
        };

        /* add plugin objects to the bubble-event queue */
        this._registerPlugins = function () {

            var plugins = $.merge($.merge([], this.config._plugins), this.config._addplugins),
                pluginName = '',
                pluginNamePrefix = 'projekktor',
                pluginObj = null,
                availablePlugins = $p.plugins,
                i;

            // nothing to do
            if (this._plugins.length > 0 || plugins.length === 0) {
                return;
            }

            for (i = 0; i < plugins.length; i++) {
                pluginName = pluginNamePrefix + plugins[i].charAt(0).toUpperCase() + plugins[i].slice(1);

                if (typeof availablePlugins[pluginName] !== 'function') {
                    $p.utils.log("Projekktor Error: Plugin '" + plugins[i] + "' malicious or not available.");
                    continue;
                }

                pluginObj = $.extend(true, {}, new projekktorPluginInterface(), availablePlugins[pluginName].prototype);
                pluginObj.name = plugins[i].toLowerCase();
                pluginObj.pp = this;
                pluginObj.playerDom = this.env.playerDom;
                pluginObj._init(this.config['plugin_' + plugins[i].toLowerCase()] || {});

                if (this.config['plugin_' + pluginObj.name] == null) {
                    this.config['plugin_' + pluginObj.name] = {};
                }

                this.config['plugin_' + pluginObj.name] = $.extend(true, {}, pluginObj.config || {});

                for (var propName in pluginObj) {

                    if (propName.indexOf('Handler') > 1) {

                        if (!this._pluginCache.hasOwnProperty(propName)) {
                            this._pluginCache[propName] = [];
                        }
                        this._pluginCache[propName].push(pluginObj);
                    }
                }

                this._plugins.push(pluginObj);
            }
        };

        /* removes some or all eventlisteners from registered plugins */
        this.removePlugins = function (rmvPl) {

            if (this._plugins.length === 0) {
                return;
            }

            var pluginsToRemove = rmvPl || $.merge($.merge([], this.config._plugins), this.config._addplugins),
                pluginsRegistered = this._plugins.length;

            for (var j = 0; j < pluginsToRemove.length; j++) {

                for (var k = 0; k < pluginsRegistered; k++) {

                    if (this._plugins[k] !== undefined) {

                        if (this._plugins[k].name === pluginsToRemove[j].toLowerCase()) {
                            this._plugins[k].deconstruct();
                            this._plugins.splice(k, 1);

                            for (var events in this._pluginCache) {

                                if (this._pluginCache.hasOwnProperty(event)) {

                                    for (var shortcuts = 0; shortcuts < this._pluginCache[events].length; shortcuts++) {

                                        if (this._pluginCache[events][shortcuts].name === pluginsToRemove[j].toLowerCase()) {
                                            this._pluginCache[events].splice(shortcuts, 1);
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        };

        this.getPlugins = function () {

            var result = [];

            $.each(this._plugins, function () {
                result.push({
                    name: this.name,
                    ver: this.version || 'unknown'
                });
            });

            return result;
        };

        /* media element update listener */
        this._modelUpdateListener = function (evtName, value) {

            if (this.playerModel.init) {
                this._promote(evtName, value);
            }
        };

        this._promote = function (evt, value) {
            var ref = this;
            this._enqueue(function () {
                try {
                    ref.__promote(evt, value);
                } catch (e) {}
            });
        };

        /* promote an event to all registered plugins */
        this.__promote = function (evt, value) {

            var ref = this,
                event = evt,
                pluginEventHandlersCache = this._pluginCache,
                playerListeners = this.listeners || [],
                pluginsWithHandlers;

            if (typeof event === 'object') {

                if (!event._plugin) {
                    return;
                }
                event = 'plugin_' + event._plugin + $p.utils.ucfirst(event._event.toLowerCase());
            }

            if (event !== 'time' && event !== 'progress' && event !== 'mousemove') {
                $p.utils.log('Event: [' + event + ']', value, playerListeners);
            }

            // fire on plugins
            pluginsWithHandlers = pluginEventHandlersCache[event + 'Handler'] || [];
            pluginsWithHandlers.forEach(function (plugin) {
                try {
                    plugin[event + 'Handler'](value, ref);
                } catch (error) {
                    $p.utils.log(error);
                }
            });

            // universal plugin event handler
            pluginsWithHandlers = pluginEventHandlersCache['eventHandler'] || [];
            pluginsWithHandlers.forEach(function (plugin) {
                try {
                    plugin['eventHandler'](event, value, ref);
                } catch (error) {
                    $p.utils.log(error);
                }
            });

            // fire on custom player listeners
            playerListeners.forEach(function (listener) {
                if (listener.event === event || listener.event === '*') {
                    try {
                        listener.callback(value, ref);
                    } catch (error) {
                        $p.utils.log(error);
                    }
                }
            });

            // fire on self:
            if (ref.hasOwnProperty(event + 'Handler')) {
                try {
                    ref[evt + 'Handler'](value);
                } catch (error) {
                    $p.utils.log(error);
                }
            }
        };

        /* destroy, reset, break down to rebuild */
        this._detachplayerModel = function () {

            this._removeGUIListeners();
            try {
                this.playerModel.destroy();
                this._promote('detach', {});
            } catch (e) {
                // this.playerModel = new playerModel();
                // this.playerModel._init({pp:this, autoplay: false});
            }
        };


        /*******************************
         GUI LISTENERS
         *******************************/
        this._windowTouchListener = function (evt) {

            if (evt.touches) {

                if (evt.touches.length > 0) {
                    if (($(document.elementFromPoint(evt.touches[0].clientX, evt.touches[0].clientY))
                            .attr('id') || '').indexOf(this.getDC().attr('id')) > -1) {

                        if (this.env.mouseIsOver === false) {
                            this._promote('mouseenter', {});
                        }

                        this.env.mouseIsOver = true;

                        this._promote('mousemove', {});
                        evt.stopPropagation();
                    } else if (this.env.mouseIsOver) {
                        this._promote('mouseleave', {});
                        this.env.mouseIsOver = false;
                    }
                }
            }
        };

        this._playerFocusListener = function (evt) {

            var type = evt.type.toLowerCase();

            switch (type) {
                case 'mousedown':

                    if (this.env.mouseIsOver === false) {
                        break;
                    }

                    // make sure we do not mess with input-overlays here:
                    if ("|TEXTAREA|INPUT".indexOf('|' + evt.target.tagName.toUpperCase()) > -1) {
                        return;
                    }

                    // prevent context-menu
                    if (evt.which === 3) {

                        if ($(evt.target).hasClass('context')) {
                            break;
                        }
                        $(document).on('contextmenu', function (evt) {
                            $(document).off('contextmenu');
                            return false;
                        });
                    }
                    break;

                case 'mousemove':

                    if (this.env.mouseX !== evt.clientX && this.env.mouseY !== evt.clientY) {
                        this.env.mouseIsOver = true;
                    }

                    // prevent strange chrome issues with cursor changes:
                    if (this.env.clientX === evt.clientX && this.env.clientY === evt.clientY) {
                        return;
                    }

                    this.env.clientX = evt.clientX;
                    this.env.clientY = evt.clientY;
                    break;

                case 'focus':
                case 'mouseenter':
                    this.env.mouseIsOver = true;
                    break;

                case 'blur':
                case 'mouseleave':
                    this.env.mouseIsOver = false;
                    break;
            }

            this._promote(type, evt);
        };

        this._keyListener = function (evt) {
            if (!this.env.mouseIsOver) {
                return;
            }

            // make sure we do not mess with input-overlays here:
            if ("|TEXTAREA|INPUT".indexOf('|' + evt.target.tagName.toUpperCase()) > -1) {
                return;
            }

            var ref = this,
                set = (this.getConfig('keys').length > 0) ? this.getConfig('keys') : [{
                    13: function (player) {
                        player.setFullscreen(!player.getIsFullscreen());
                    }, // return;
                    32: function (player, evt) {
                        player.setPlayPause();
                        evt.preventDefault();
                    }, // space
                    39: function (player, evt) {
                        player.setPlayhead('+5');
                        evt.preventDefault();
                    }, // cursor right
                    37: function (player, evt) {
                        player.setPlayhead('-5');
                        evt.preventDefault();
                    }, // cursor left
                    38: function (player, evt) {
                        player.setVolume('+0.05');
                        evt.preventDefault();
                    }, // cursor up
                    40: function (player, evt) {
                        player.setVolume('-0.05');
                        evt.preventDefault();
                    }, // cursor down
                    68: function (player) {
                        player.setDebug();
                    }, // D
                    67: function (player) {
                        $p.utils.log('Config Dump', player.config);
                    }, // C
                    80: function (player) {
                        $p.utils.log('Schedule Dump', player.media);
                    }, // P
                    84: function (player) {
                        $p.utils.log('Cuepoints Dump', player.getCuePoints());
                    } // T
                }];

            this._promote('key', evt);

            $.each(set || [], function () {
                try {
                    this[evt.keyCode](ref, evt);
                } catch (e) {}

                try {
                    this['*'](ref);
                } catch (e) {}
            });
        };

        /*******************************
         DOM manipulations
         *******************************/

        /* make player fill actual viewport */
        this._expandView = function (win, target, targetParent) {

            var winBody = $(win[0].document).find('body'),
                overflow = winBody.css('overflow'),
                isSelf = (win[0] === window.self),
                targetWidthAttr = target.attr('width') || '',
                targetHeightAttr = target.attr('height') || '';

            // prepare target:
            target
                .data('fsdata', {
                    scrollTop: win.scrollTop() || 0,
                    scrollLeft: win.scrollLeft() || 0,
                    targetStyle: target.attr('style') || '',
                    targetWidth: target.width(),
                    targetHeight: target.height(),
                    bodyOverflow: (overflow === 'visible') ? 'auto' : overflow, // prevent IE7 crash
                    bodyOverflowX: winBody.css('overflow-x'), // prevent IE7 crash
                    bodyOverflowY: winBody.css('overflow-y'), // prevent IE7 crash
                    iframeWidth: targetWidthAttr.indexOf('%') > -1 ? targetWidthAttr : parseInt(targetWidthAttr) || 0,
                    iframeHeight: targetHeightAttr.indexOf('%') > -1 ? targetHeightAttr : parseInt(targetHeightAttr) || 0
                })
                .removeAttr('width')
                .removeAttr('height')
                .css({
                    position: isSelf && !targetParent ? 'absolute' : 'fixed', // to prevent Android native browser bad 'fixed' positioning when the player is in the iframe mode
                    display: 'block',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    zIndex: 9999999, // that still not guarantee that the target element will be on top. Theoretically we could move the target element to the body but this causing reload of the iframe so it's not an option.
                    margin: 0,
                    padding: 0
                });

            // prepare target parent
            // check if it's not in the iframe mode and if the targetParent is not <body>
            if (!isSelf && !!targetParent && targetParent[0].tagName !== 'BODY') {
                targetParent
                    .data('fsdata', {
                        overflow: targetParent.css('overflow'),
                        overflowX: targetParent.css('overflow-x'),
                        overflowY: targetParent.css('overflow-y'),
                        styles: targetParent.attr('style')
                    })
                    .attr('style', (!targetParent.attr('style') ? '' : targetParent.attr('style') + '; ') + 'overflow: visible!important;'); // that fixes IE issues with visibility of the element
            }

            // prepare parent window
            win.scrollTop(0).scrollLeft(0);

            winBody.css({
                overflow: 'hidden',
                overflowX: 'hidden',
                overflowY: 'hidden'
            });

            return true;
        };

        /* return player to the original size */
        this._collapseView = function (win, target, targetParent) {
            var isSelf = (win[0] === window.self),
                fsData = target ? target.data('fsdata') : null,
                fsTargetParentData = targetParent ? targetParent.data('fsdata') : null;

            // reset
            if (fsData !== null) {

                $(win[0].document.body)
                    .css({
                        overflow: fsData.bodyOverflow,
                        overflowX: fsData.bodyOverflowX,
                        overflowY: fsData.bodyOverflowY
                    });

                // rebuild iframe:
                if (fsData.iframeWidth > 0 && !isSelf) {
                    target
                        .attr('width', fsData.iframeWidth)
                        .attr('height', fsData.iframeHeight);
                } else {
                    target
                        .width(fsData.targetWidth)
                        .height(fsData.targetHeight);
                }

                target
                    .attr('style', (fsData.targetStyle == null) ? '' : fsData.targetStyle)
                    .data('fsdata', null);

                if (!isSelf && !!fsTargetParentData) {
                    targetParent
                        .attr('style', !fsTargetParentData.styles ? '' : fsTargetParentData.styles)
                        .data('fsdata', null);
                }

                // rebuild parent window state
                win.scrollTop(fsData.scrollTop)
                    .scrollLeft(fsData.scrollLeft);

                return true;
            }

            return false;
        };

        this._enterFullViewport = function () {

            var iframeCfg = this.getConfig('iframe'),
                win = iframeCfg ? this.getIframeParent() || $(window) : $(window),
                target = iframeCfg ? this.getIframe() || this.getDC() : this.getDC(),
                targetParent = target.parent() || null,
                winDocument = $(win[0].document);

            // set isFullViewport flag
            this._isFullViewport = true;

            // add class to eventually create more specific rules for site elements with high z-indexes
            winDocument.find('body').addClass(this.getNS() + 'fullviewport');

            // prevent Android 4.x Browser from scrolling
            $(document).on('touchmove.fullviewport', function (e) {
                e.preventDefault();
            });

            this._expandView(win, target, targetParent);

            return true;
        };

        /* exit player from full viewport mode - "full (parent) window viewport" to be specific */
        this._exitFullViewport = function () {

            var iframeCfg = this.getConfig('iframe'),
                win = iframeCfg ? this.getIframeParent() || $(window) : $(window),
                target = iframeCfg ? this.getIframe() || this.getDC() : this.getDC(),
                targetParent = target.parent() || null,
                winDocument = $(win[0].document);

            this._isFullViewport = false;

            winDocument.find('body').removeClass(this.getNS() + 'fullviewport');

            $(document).off('.fullviewport');

            this._collapseView(win, target, targetParent);

            return true;
        };

        /*******************************
         plugin API wrapper
         *******************************/
        this.pluginAPI = function () {

            var args = Array.prototype.slice.call(arguments) || null,
                dest = args.shift(),
                func = args.shift();

            if (dest != null && func != null) {

                for (var j = 0; j < this._plugins.length; j++) {

                    if (this._plugins[j].name === dest) {
                        this._plugins[j][func](args[0]);
                        return;
                    }
                }
            }
        };

        /*******************************
         public (API) methods GETTERS
         *******************************/
        this.getVersion = function () {
            return this.config._version;
        };

        this.getIsLastItem = function () {
            return this.getNextItem() !== false;
        };

        this.getIsFirstItem = function () {
            return this.getPreviousItem() !== false;
        };

        this.getConfig = function () {

            var idx = this.getItemIdx(),
                name = null,
                result = false;

            if (typeof arguments[0] === 'string') {
                name = arguments[0];
                result = (this.config['_' + name] != null) ? this.config['_' + name] : this.config[name];
            } else if (typeof arguments[0] === 'number') {
                idx = arguments[0];
            }

            if (name == null) {
                return this.media[idx]['config'];
            }

            // get value from item-specific config (beats them all)
            if (this.config['_' + name] == undefined) {

                try {
                    if (this.media[idx]['config'][name] !== undefined) {
                        result = this.media[idx]['config'][name];
                    }
                } catch (e) {}
            }

            if (name.indexOf('plugin_') > -1) {

                try {
                    if (this.media[idx]['config'][name]) {
                        result = $.extend(true, {}, this.config[name], this.media[idx]['config'][name]);
                    }
                } catch (e) {}
            }


            if (result == null) {
                return null;
            }

            if (typeof result === 'object' && result.length === null) {
                result = $.extend(true, {}, result || {});
            } else if (typeof result === 'object') {
                result = $.extend(true, [], result || []);
            }

            if (typeof result === 'string') {

                switch (result) {
                    case 'true':
                        result = true;
                        break;

                    case 'false':
                        result = false;
                        break;

                    case 'NaN':
                    case 'undefined':
                    case 'null':
                        result = null;
                        break;
                }
            }

            return result;
        };

        this.getDC = function () {
            return this.env.playerDom;
        };

        this.getState = function (compare) {

            var result = 'IDLE';

            try {
                result = this.playerModel.getState();
            } catch (e) {}

            if (compare) {
                return (result === compare.toUpperCase());
            }

            return result;
        };

        this.getLoadProgress = function () {

            try {
                return this.playerModel.getLoadProgress();
            } catch (e) {
                return 0;
            }
        };

        this._testItem = function (item) {

            for (var r = 0; r < this.itemRules.length; r++) {
                if (!this.itemRules[r](item)) {
                    return false;
                }
            }
            return true;
        };

        this.getItemAtIdx = function (atidx) {

            var ref = this,
                idx = atidx || 0,
                result = false;

            $.each(this.media.slice(idx), function () {

                if (!ref._testItem(this)) {
                    return true;
                }
                result = this;
                return false;
            });

            return result;
        };

        this.getNextItem = function () {

            var ref = this,
                idx = this.getItemIdx(),
                result = false;

            $.each(this.media.slice(idx + 1), function () {

                if (!ref._testItem(this)) {
                    return true;
                }
                result = this;
                return false;
            });

            if (this.getConfig('loop') && result === false) {

                $.each(this.media.slice(), function () {

                    if (!ref._testItem(this)) {
                        return true;
                    }
                    result = this;
                    return false;
                });
            }

            return result;
        };

        this.getPreviousItem = function () {

            var ref = this,
                idx = this.getItemIdx(),
                result = false;

            $.each(this.media.slice(0, idx).reverse(), function () {

                if (!ref._testItem(this)) {
                    return true;
                }
                result = this;
                return false;
            });

            if (this.getConfig('loop') && result === false) {

                $.each(this.media.slice().reverse(), function () {
                    if (!ref._testItem(this)) {
                        return true;
                    }
                    result = this;
                    return false;
                });
            }
            return result;
        };

        this.getItemCount = function () {
            // ignore NA dummy
            return (this.media.length === 1 && this.media[0].model === 'NA') ? 0 : this.media.length;
        };

        this.getItemId = function (idx) {

            try {
                return this.playerModel.getId();
            } catch (e) {
                return this.getItemAtIdx(idx).id;
            }
        };

        this.getItemIdx = function (itm) {

            var item = itm || {
                    id: false
                },
                id = item.id || this.getItemId();

            return this.media.indexOf(this.media.find(function (item) {
                return item.id === id;
            }));
        };

        this.getCurrentItem = function () {

            var ref = this;
            return $.grep(this.media, function (e) {
                return ref.getItemId() === e.id;
            })[0] || false;
        };

        this.getPlaylist = function () {

            return this.getItem('*');
        };

        this.getItem = function (idx) {

            // ignore NA dummy
            if (this.media.length === 1 && this.media[0].model === 'NA') {
                return false;
            }

            // some shortcuts
            switch (arguments[0] || 'current') {
                case 'next':
                    return this.getNextItem();

                case 'prev':
                    return this.getPreviousItem();

                case 'current':
                    return this.getCurrentItem();

                case '*':
                    return this.media;

                default:
                    return this.getItemAtIdx(idx);
            }
        };

        this.getVolume = function () {
            var volume = ('getIsReady' in this.playerModel && this.playerModel.getIsReady()) ? this.playerModel.getVolume() : this.env.volume,
                fixedVolume = this.getConfig('fixedVolume'),
                isMuted = this.getMuted();

            if (fixedVolume === true) {
                volume = this.getConfig('volume');
            }

            if(isMuted){
                volume = 0;
            }

            return volume;
        };

        this.getMuted = function () {
            return this.env.muted;
        };

        this.getTrackId = function () {

            if (this.getConfig('trackId')) {
                return this.config.trackId;
            }

            if (this._playlistServer != null) {
                return "pl" + this._currentItem;
            }

            return null;
        };

        this.getLoadPlaybackProgress = function () {

            try {
                return this.playerModel.getLoadPlaybackProgress();
            } catch (e) {
                return 0;
            }
        };

        this.getSource = function () {

            try {
                return this.playerModel.getSource()[0].src;
            } catch (e) {
                return false;
            }
        };

        this.getDuration = function () {

            try {
                return this.playerModel.getDuration();
            } catch (e) {
                return 0;
            }
        };

        this.getIsLiveOrDvr = function () {
            try {
                return this._isLive || this.playerModel._isDVR || this.playerModel._isLive;
            } catch (e) {
                return false;
            }
        };

        this.getPosition = function () {

            try {
                return this.playerModel.getPosition() || 0;
            } catch (e) {
                return 0;
            }
        };

        this.getMaxPosition = function () {

            try {
                return this.playerModel.getMaxPosition() || 0;
            } catch (e) {
                return 0;
            }
        };

        this.getFrame = function () {

            try {
                return this.playerModel.getFrame();
            } catch (e) {
                return 0;
            }
        };

        this.getTimeLeft = function () {

            try {
                return this.playerModel.getDuration() - this.playerModel.getPosition();
            } catch (e) {
                return this.getItem().duration;
            }
        };
        /**
         * Basing on fullscreen prioritized array config, currently used platform and device abilities
         * it detects fullscreen type/mode to use.
         *
         * @returns string - full | mediaonly | viewport | none
         */
        this.getFullscreenType = function () {
            var config = this.getConfig('fullscreen') || [],
                usedPlatform = this.getPlatform(),
                fullscreenTypesAvailableForUsedPlatform = this.config._platformsFullscreenConfig[usedPlatform] || [],
                availableFullscreenApiType = $p.fullscreenApi.type,
                fullscreenTypeAvailableForApi = [],
                available = [],
                result = 'none',
                i;

            switch (availableFullscreenApiType) {
                case 'full':
                    fullscreenTypeAvailableForApi = ['full', 'mediaonly'];
                    break;

                case 'mediaonly':
                    fullscreenTypeAvailableForApi = ['mediaonly'];
                    break;

                case 'none':
                    break;
            }

            // if device has support for inlinevideo then there is full viewport mode available
            if ($p.features.inlinevideo) {
                fullscreenTypeAvailableForApi.push('viewport');
            }

            available = $p.utils.intersect($p.utils.intersect(config, fullscreenTypesAvailableForUsedPlatform), fullscreenTypeAvailableForApi);

            // select one from the available fullscreen types with highest configured priority
            for (i = 0; i < config.length; i++) {
                if (available.indexOf(config[i]) > -1) {
                    result = config[i];
                    break;
                }
            }

            return result;
        };

        this.getFullscreenEnabled = function () {
            var fsType = this.getFullscreenType(),
                apiType = $p.fullscreenApi.type,
                result = false;

            switch (fsType) {
                case 'full':
                    result = this._getFullscreenEnabledApi();
                    break;

                case 'mediaonly':
                    /**
                     * there could be 4 cases in this situation:
                     * a) there is only 'mediaonly' fullscreen API available
                     * b) there is 'full' fullscreen API available, but the user prefer 'mediaonly' in config
                     * c) player is in the same-origin <iframe> and has 'mediaonly' fullscreen API available, 
                     *    but there is no <iframe> `allowfullscreen` attribute so we respect that.
                     * d) player is in the crossdomain <iframe> (so we can't check the attributes of the <iframe> element)
                     *    and has 'mediaonly' fullscreen API available, so we try to use it
                     */
                    if (this.getConfig('iframe') && !this.config._isCrossDomain) {
                        result = (this.getIframeAllowFullscreen() && this._getFullscreenEnabledApi(apiType));
                    } else {
                        result = this._getFullscreenEnabledApi(apiType);
                    }
                    break;

                case 'viewport':
                    /**
                     * In this case we just need to check if the player is inside the <iframe>
                     * and if the <iframe> attributes allowing fullscreen. We respect this even if it's
                     * possible to set fullviewport when the <iframe> is from the same domain.
                     * If the player isn't inside the <iframe> then we assume that it's possible to
                     * put the player into fullviewport mode when requested.
                     */
                    if (this.getConfig('iframe') && !this.config._isCrossDomain) {
                        result = this.getIframeAllowFullscreen();
                    } else {
                        result = true;
                    }
                    break;

                    /**
                     * The fullscreen functionality is disabled in configuration
                     */
                case 'none':
                    result = false;
                    break;
            }

            return result;
        };

        this._getFullscreenEnabledApi = function (apiType) {
            var apiType = apiType || $p.fullscreenApi.type,
                fsFullscreenEnabledPropName = $p.fullscreenApi[apiType]['fullscreenEnabled'] || false,
                fsSupportsFullscreenPropName = $p.fullscreenApi[apiType]['supportsFullscreen'] || false,
                result = false;

            switch (apiType) {
                case 'full':
                    // we need to check if the document fullscreenEnabled value is true or false
                    // cause even if the fullscreen API feature is available it could be blocked
                    // through browser configuration and/or <iframe> lack of allowfullscreen attribute
                    result = document[fsFullscreenEnabledPropName];
                    break;

                case 'mediaonly':
                    /**
                     * if the detected fullscreen API is 'mediaonly' then we need to check the status
                     * of current player model media element supportsFullscreen value. This value is
                     * reliable only after HTML <video> metadataloaded event was fired. If there is
                     * no player model media element available at the function execution time we return
                     * false.
                     */
                    if (!!this.playerModel.mediaElement) {
                        result = this.playerModel.mediaElement[0][fsSupportsFullscreenPropName];
                    }
                    break;
            }

            return result;
        };

        this.getIsFullscreen = function () {
            var fsType = this.getFullscreenType(),
                apiType = $p.fullscreenApi.type,
                result = false;

            switch (fsType) {
                case 'full':
                    result = this._getIsFullscreenApi();
                    break;

                case 'mediaonly':
                    /**
                     * there could be 2 cases in this situation:
                     * a) there is only 'mediaonly' fullscreen API available
                     * b) there is 'full' fullscreen API available, but the user prefer 'mediaonly' in config
                     */
                    result = this._getIsFullscreenApi(apiType);
                    break;

                case 'viewport':
                    result = this._isFullViewport;
                    break;

                    /**
                     * The fullscreen functionality is disabled in configuration
                     */
                case 'none':
                    result = false;
                    break;
            }

            return result;
        };

        this._getIsFullscreenApi = function (apiType) {
            var apiType = apiType || $p.fullscreenApi.type,
                fsElementPropName = $p.fullscreenApi[apiType]['fullscreenElement'] || false,
                fsIsFullscreenPropName = $p.fullscreenApi[apiType]['isFullscreen'] || false,
                fsDisplayingFullscreenPropName = $p.fullscreenApi[apiType]['isFullscreen'] || false,
                result = false;

            switch (apiType) {
                case 'full':
                    // NOTE: IE11 and IEMobile on Windows Phone 8.1 don't have isFullscreen property implemented,
                    // but we can use fullscreenElement property instead
                    result = document[fsIsFullscreenPropName] || !!document[fsElementPropName];
                    break;

                case 'mediaonly':
                    if (!!this.playerModel.mediaElement && fsDisplayingFullscreenPropName) {
                        result = this.playerModel.mediaElement[0][fsDisplayingFullscreenPropName];
                    } else {
                        result = this.getDC().hasClass('fullscreen');
                    }
                    break;
            }

            return result;
        };

        this.getMediaContainer = function () {

            // return "buffered" media container
            if (!this.env.mediaContainer) {
                this.env.mediaContainer = $('#' + this.getMediaId());
            }

            // if mediacontainer does not exist ...
            if (this.env.mediaContainer.length === 0 || !$.contains(document.body, this.env.mediaContainer[0])) {

                // and there is a "display", injects media container
                if (this.env.playerDom.find('.' + this.getNS() + 'display').length > 0) {
                    this.env.mediaContainer = $(document.createElement('div'))
                        .attr({
                            'id': this.getId() + "_media"
                        }) // IMPORTANT IDENTIFIER
                        .css({
                            // position: 'absolute',
                            overflow: 'hidden',
                            height: '100%',
                            width: '100%',
                            top: 0,
                            left: 0,
                            padding: 0,
                            margin: 0,
                            display: 'block'
                        })
                        .appendTo(this.env.playerDom.find('.' + this.getNS() + 'display'));
                }
                // else create a 1x1 pixel dummy somewhere
                else {
                    this.env.mediaContainer = $(document.createElement('div'))
                        .attr({
                            id: this.getMediaId()
                        })
                        .css({
                            width: '1px',
                            height: '1px'
                        })
                        .appendTo($(document.body));
                }
            }

            // go for it
            return this.env.mediaContainer;
        };

        this.getMediaId = function () {

            return this.getId() + "_media";
        };

        this.getMediaType = function () {

            // might be called before a model has been initialized
            if ('getSrc' in this.playerModel) {
                return this._getTypeFromFileExtension(this.playerModel.getSrc());
            } else {
                return 'none/none';
            }
        };

        this.getModel = function () {

            try {
                return this.getItem().model;
            } catch (e) {
                return "NA";
            }
        };

        this.getIframeParent = function () {

            try {
                var result = parent.location.host || false;
                return (result === false) ? false : $(parent.window);
            } catch (e) {
                return false;
            }
        };

        this.getIframe = function () {

            try {
                var result = [];

                if (this.config._iframe) {
                    result = window.$(frameElement) || [];
                }
                return (result.length === 0) ? false : result;
            } catch (e) {
                return false;
            }
        };

        this.getIframeAllowFullscreen = function () {

            var result = false;

            try {
                result = window.frameElement.attributes.allowFullscreen || window.frameElement.attributes.mozallowFullscreen || window.frameElement.attributes.webkitallowFullscreen || false;
            } catch (e) {
                result = false;
            }

            return result;
        };

        this.getPlaybackQuality = function () {

            var result = 'auto';

            try {
                result = this.playerModel.getPlaybackQuality();
            } catch (e) {}

            if (result === 'auto') {
                result = this.getConfig('playbackQuality');
            }

            if (result === 'auto' || $.inArray(result, this.getPlaybackQualities()) === -1) {
                result = this.getAppropriateQuality();
            }

            if ($.inArray(result, this.getPlaybackQualities()) === -1) {
                result = 'auto';
            }

            return result;
        };

        this.getPlaybackQualities = function () {

            try {
                return $.extend(true, [], this.getItem().qualities || []);
            } catch (e) {}

            return [];
        };

        this.getCanPlay = function (mimeType, platforms) {
            var ref = this,
                pt = (platforms === undefined) ? Array.from(this.getSupportedPlatforms().keys()) : platforms;

            return pt.some(function (pt) {
                return ref._canPlay(mimeType, pt);
            });
        };

        this.getCanPlayOnPlatforms = function (mimeType) {
            return this._canPlayOnPlatforms(mimeType);
        };

        this.getIsDrmSystemSupported = function (drmSystem) {
            return ($p.drm.supportedDrmSystems.indexOf(drmSystem) > -1);
        };

        this.getPlatform = function (item) {

            var item = item || this.getItem();

            return item.platform || 'browser';
        };

        this.getId = function () {

            return this._id;
        };

        this.getHasGUI = function () {

            try {
                return this.playerModel.getHasGUI();
            } catch (e) {
                return false;
            }
        };

        this.getCssPrefix = this.getNS = function () {

            return this.config._cssClassPrefix || this.config._ns || 'pp';
        };

        this.getPlayerDimensions = function () {

            return {
                width: this.getDC()
                    .width(),
                height: this.getDC()
                    .height()
            };
        };

        this.getMediaDimensions = function () {

            return this.playerModel.getMediaDimensions() || {
                width: 0,
                height: 0
            };
        };

        this.getAppropriateQuality = function (qualities) {

            var quals = qualities || this.getPlaybackQualities() || [];

            if (quals.length === 0) {
                return [];
            }

            var wid = this.env.playerDom.width(),
                hei = this.env.playerDom.height(),
                ratio = $p.utils.roundNumber(wid / hei, 2),
                temp = {};

            // find best available quality-config-set by "minHeight"
            $.each(this.getConfig('playbackQualities') || [], function () {

                // not available
                if ($.inArray(this.key, quals) < 0) {
                    return true;
                }

                // check player-dim against minHeight
                if ((this.minHeight || 0) > hei && temp.minHeight <= hei) {
                    return true;
                }

                // new set in case of higher resolution
                if ((temp.minHeight || 0) > this.minHeight) {
                    return true;
                }

                // check against minWidth - simple case:
                if (typeof this.minWidth === 'number') {
                    if (this.minWidth === 0 && this.minHeight > hei) {
                        return true;
                    }

                    if (this.minWidth > wid) {
                        return true;
                    }

                    temp = this;
                }
                // check against minWidth - aspect ratio
                else if (typeof this.minWidth === 'object') {
                    var ref = this;

                    $.each(this.minWidth, function () {
                        if ((this.ratio || 100) > ratio) {
                            return true;
                        }
                        if (this.minWidth > wid) {
                            return true;
                        }
                        temp = ref;

                        return true;
                    });
                }

                return true;
            });

            return ($.inArray('auto', this.getPlaybackQualities()) > -1) ? 'auto' : temp.key || 'auto';
        };

        /* asynchronously loads external XML and JSON data from server */
        this.getFromUrl = function (url, dest, callback, dataType, auxConfig) {

            var data = null;

            if (callback.substr(0, 1) !== '_') {
                window[callback] = function (data) {

                    try {
                        delete window[callback];
                    } catch (e) {}
                    dest[callback](data);
                };
            }

            if (dataType) {
                dataType = (dataType.indexOf('/') > -1) ? dataType.split('/')[1] : dataType;
            }

            var ajaxConf = {
                url: url,
                complete: function (xhr, status) {

                    if (dataType == undefined) {

                        try {

                            if (xhr.getResponseHeader("Content-Type").indexOf('xml') > -1) {
                                dataType = 'xml';
                            }

                            if (xhr.getResponseHeader("Content-Type").indexOf('json') > -1) {
                                dataType = 'json';
                            }

                            if (xhr.getResponseHeader("Content-Type").indexOf('html') > -1) {
                                dataType = 'html';
                            }
                        } catch (e) {}
                    }
                    data = $p.utils.cleanResponse(xhr.responseText, dataType);

                    if (status !== 'error') {

                        try {
                            dest[callback](data, xhr.responseText, auxConfig);
                        } catch (e) {}
                    }
                },
                error: function (data) {

                    // bypass jq 1.6.1 issues
                    if (dest[callback]) {
                        dest[callback](false);
                    }
                },
                cache: true,
                dataType: dataType
            };
            ajaxConf.xhrFields = {
                withCredentials: false
            };
            ajaxConf.beforeSend = function (xhr) {
                xhr.withCredentials = false;
            };
            $.support.cors = true;
            $.ajax(ajaxConf);

            return this;
        };

        /*******************************
         public (API) methods SETTERS
         *******************************/
        this.setActiveItem = function (mixedData, autoplay) {

            var lastItem = this.getItem(),
                newItem = null,
                ap = this.config._autoplay,
                M;

            if (typeof mixedData === 'string') {

                // prev/next shortcuts
                switch (mixedData) {
                    case 'previous':
                        newItem = this.getPreviousItem();
                        break;

                    case 'next':
                        newItem = this.getNextItem();
                        break;
                }
            } else if (typeof mixedData === 'number') {

                // index number given
                newItem = this.getItemAtIdx(mixedData);
                // wrong argument
            } else {
                return this;
            }

            if (newItem === false) {
                // end of playlist reached
                if (!this.getNextItem()) {
                    this._promote('done');
                }
                // nothing to do
                return this;
            }

            //

            // item change requested
            if (newItem.id !== lastItem.id) {

                // but and denied by config or state
                if (this.getConfig('disallowSkip') === true && ('COMPLETED|IDLE|ERROR'.indexOf(this.getState()) === -1)) {
                    return this;
                }
            }

            // do we have an continuous play situation?
            if (!this.getState('IDLE')) {
                if(newItem.config.hasOwnProperty('continuous')){
                    ap = newItem.config.continuous;
                }
                else {
                    ap = this.config._continuous;
                }
            }

            this._detachplayerModel();

            // reset player class
            var wasFullscreen = this.getIsFullscreen();
            this.getDC().attr('class', this.env.className);

            if (wasFullscreen) {
                this.getDC().addClass('fullscreen');
            }

            // create player instance
            var newModel = newItem.model;

            // model does not exist or is faulty:
            if (!$p.models.has(newModel)) {
                newModel = 'NA';
                newItem.model = newModel;
                newItem.errorCode = 8;
            }

            // start model
            this.playerModel = new playerModel();
            M = $p.models.get(newModel);
            $.extend(this.playerModel, new M());

            this.__promote('synchronizing', 'display');

            this.initPlayerModel({
                media: $.extend(true, {}, newItem),
                model: newModel,
                pp: this,
                environment: $.extend(true, {}, this.env),
                autoplay: (typeof autoplay === 'boolean') ? autoplay : ap,
                quality: this.getPlaybackQuality(),
                fullscreen: wasFullscreen
                // persistent: (ap || this.config._continuous) && (newModel==nextUp)
            });

            this.syncCuePoints();

            return this;
        };

        this.initPlayerModel = function (cfg) {

            this.playerModel._init(cfg);

            // apply item specific class(es) to player
            if (this.getConfig('className', null) != null) {
                this.getDC().addClass(this.getNS() + this.getConfig('className'));
            }
            this.getDC().addClass(this.getNS() + (this.getConfig('streamType') || 'http'));

            if (this.getConfig('streamType').indexOf('dvr') > -1 || this.getConfig('streamType').indexOf('live') > -1) {
                this.getDC().addClass(this.getNS() + 'live');
                this._isLive = true;
            }

            if (!$p.features.csstransitions) {
                this.getDC().addClass('notransitions');
            }

            if ($p.userAgent.isMobile) {
                this.getDC().addClass(this.getNS() + 'mobile');
            }

            if (!$p.features.volumecontrol){
                this.getDC().addClass(this.getNS() + 'novolumecontrol');
            }
        };

        /* queue ready */
        this.setPlay = function () {

            var ref = this;

            if (this.getConfig('thereCanBeOnlyOne')) {
                projekktor('*').each(function () {
                    if (this.getId() !== ref.getId()) {
                        this.setStop();
                    }
                });
            }
            this._enqueue('play', false);

            return this;
        };

        /* queue ready */
        this.setPause = function () {

            this._enqueue('pause', false);

            return this;
        };

        /* queue ready */
        this.setStop = function (toZero) {

            var ref = this;

            if (this.getState('IDLE')) {
                return this;
            }

            if (toZero) {
                this._enqueue(function () {
                    ref.setActiveItem(0);
                });
            } else {
                this._enqueue('stop', false);
            }

            return this;
        };

        /* queue ready */
        this.setPlayPause = function () {

            if (!this.getState('PLAYING')) {
                this.setPlay();
            } else {
                this.setPause();
            }

            return this;
        };

        /* queue ready */
        this.setVolume = function (vol, fadeDelay) {

            var initialVolume = this.getVolume();

            if (this.getConfig('fixedVolume') === true) {
                return this;
            }

            switch (typeof vol) {
                case 'string':
                    var dir = vol.substr(0, 1);
                    vol = parseFloat(vol.substr(1));
                    switch (dir) {
                        case '+':
                            vol = this.getVolume() + vol;
                            break;

                        case '-':
                            vol = this.getVolume() - vol;
                            break;

                        default:
                            vol = this.getVolume();
                    }
                    break;

                case 'number':
                    vol = parseFloat(vol);
                    vol = (vol > 1) ? 1 : vol;
                    vol = (vol < 0) ? 0 : vol;
                    break;

                default:
                    return this;
            }

            if (vol > initialVolume && fadeDelay) {

                if (vol - initialVolume > 0.03) {

                    for (var i = initialVolume; i <= vol; i = i + 0.03) {
                        this._enqueue('volume', i, fadeDelay);
                    }
                    this._enqueue('volume', vol, fadeDelay);
                    return this;
                }
            } else if (vol < initialVolume && fadeDelay) {

                if (initialVolume - vol > 0.03) {

                    for (var i = initialVolume; i >= vol; i = i - 0.03) {
                        this._enqueue('volume', i, fadeDelay);
                    }
                    this._enqueue('volume', vol, fadeDelay);
                    return this;
                }
            }
            this._enqueue('volume', vol);

            return this;
        };

        this.setMuted = function (value) {
            var value = value === undefined ? !this.env.muted : value,
                volume = this.getVolume(),
                isVolumeControllable = $p.features.volumecontrol;

            if(isVolumeControllable){
                if (value && volume > 0) {
                    this.env.lastVolume = volume;
                    this.setVolume(0);
                } else {
                    this.setVolume(typeof this.env.lastVolume === 'number' ? this.env.lastVolume : volume);
                    this.env.lastVolume = null;
                }
            }
            else {
                if(value){
                    this.setVolume(0);
                }
                else {
                    this.setVolume(1);
                }
            }

            return this;
        };

        /* queue ready */
        this.setPlayhead = this.setSeek = function (position) {

            if (this.getConfig('disallowSkip') === true) {
                return this;
            }

            if (typeof position === 'string') {

                var dir = position.substr(0, 1);

                position = parseFloat(position.substr(1));

                if (dir === '+') {
                    position = this.getPosition() + position;
                } else if (dir === '-') {
                    position = this.getPosition() - position;
                } else {
                    position = this.getPosition();
                }
            }

            if (typeof position === 'number') {
                this._enqueue('seek', Math.round(position * 100) / 100);
            }

            return this;
        };

        /* queue ready */
        this.setFrame = function (frame) {

            if (this.getConfig('fps') == null) {
                return this;
            }

            if (this.getConfig('disallowSkip') === true) {
                return this;
            }

            if (typeof frame === 'string') {
                var dir = frame.substr(0, 1);
                frame = parseFloat(frame.substr(1));

                if (dir === '+') {
                    frame = this.getFrame() + frame;
                } else if (dir === '-') {
                    frame = this.getFrame() - frame;
                } else {
                    frame = this.getFrame();
                }
            }

            if (typeof frame === 'number') {
                this._enqueue('frame', frame);
            }

            return this;
        };

        /* queue ready */
        this.setPlayerPoster = function (url) {

            var ref = this;

            this._enqueue(function () {
                ref.setConfig({
                        poster: url
                    },
                    0);
            });
            this._enqueue(function () {
                ref.playerModel.setPosterLive();
            });

            return this;
        };

        this.setConfig = function () {

            var ref = this,
                args = arguments;

            this._enqueue(function () {
                ref._setConfig(args[0] || null, args[1]);
            });

            return this;
        };

        this._setConfig = function () {
            if (!arguments.length) {
                return;
            }

            var confObj = arguments[0],
                dest = '*',
                value = false;

            if (typeof confObj !== 'object') {
                return this;
            }

            if (typeof arguments[1] === 'string' || typeof arguments[1] === 'number') {
                dest = arguments[1];
            } else {
                dest = this.getItemIdx();
            }

            for (var i in confObj) {

                // is constant:
                if (this.config['_' + i] != null) {
                    continue;
                }

                try {
                    value = eval(confObj[i]);
                } catch (e) {
                    value = confObj[i];
                }

                if (dest === '*') {

                    $.each(this.media, function () {
                        if (this.config == null) {
                            this.config = {};
                        }
                        this.config[i] = value;
                    });
                    continue;
                }

                if (this.media[dest] == undefined) {
                    return this;
                }

                if (this.media[dest]['config'] == null) {
                    this.media[dest]['config'] = {};
                }

                this.media[dest]['config'][i] = value;
            }

            return this;
        };

        this.setFullscreen = function (goFullscreen) {
            var goFullscreen = goFullscreen === void(0) ? !this.getIsFullscreen() : goFullscreen; // toggle or use argument value

            // inform player model about going fullscreen
            this.playerModel.applyCommand('fullscreen', goFullscreen);

            return this;
        };

        this._requestFullscreen = function () {
            var fsType = this.getFullscreenType(),
                apiType = $p.fullscreenApi.type,
                result = false;

            switch (fsType) {
                case 'full':
                    result = this._requestFullscreenApi(apiType, fsType);
                    break;

                case 'mediaonly':
                    /**
                     * there could be 2 cases in this situation:
                     * a) there is only 'mediaonly' fullscreen API available
                     * b) there is 'full' fullscreen API available, but the user prefer 'mediaonly' in config
                     */
                    result = this._requestFullscreenApi(apiType, fsType);
                    break;

                case 'viewport':
                    result = this._enterFullViewport();
                    break;

                    /**
                     * The fullscreen functionality is disabled in configuration
                     */
                case 'none':
                    result = false;
                    break;
            }

            return result;
        };

        this._requestFullscreenApi = function (apiType, fsType) {
            var apiType = apiType || $p.fullscreenApi.type,
                fsElement,
                fsRequestFunctionName = $p.fullscreenApi[apiType]['requestFullscreen'] ? $p.fullscreenApi[apiType]['requestFullscreen'] : false,
                fsEnterFunctionName = $p.fullscreenApi[apiType]['enterFullscreen'] ? $p.fullscreenApi[apiType]['enterFullscreen'] : false,
                fsChangeEventName = $p.fullscreenApi[apiType]['fullscreenchange'] ? $p.fullscreenApi[apiType]['fullscreenchange'].substr(2) : false,
                fsErrorEventName = $p.fullscreenApi[apiType]['fullscreenerror'] ? $p.fullscreenApi[apiType]['fullscreenerror'].substr(2) : false,
                fsEventsNS = '.' + this.getNS() + 'fullscreen',
                result = false,
                ref = this;

            switch (apiType) {
                case 'full':
                    if (fsType === 'full') {
                        fsElement = this.getDC();
                    } else if (fsType === 'mediaonly') {
                        if (!!this.playerModel.mediaElement) {
                            fsElement = this.playerModel.mediaElement;

                            // add native controls
                            fsElement.attr('controls', true);
                            result = true;
                        } else {
                            return false;
                        }
                    }

                    // remove all previous event listeners
                    $(document).off(fsEventsNS);

                    // add event listeners
                    if (fsChangeEventName) {

                        $(document).on(fsChangeEventName + fsEventsNS, function (event) {

                            if (!ref.getIsFullscreen()) {

                                if (fsType === 'mediaonly') {

                                    // remove native controls
                                    fsElement.attr('controls', false);
                                }
                                ref.setFullscreen(false);

                                // remove fullscreen event listeners
                                $(document).off(fsEventsNS);
                            }
                        });
                    } else {
                        $p.utils.log('No fullscreenchange event defined.');
                    }

                    if (fsErrorEventName) {

                        $(document).on(fsErrorEventName + fsEventsNS, function (event) {

                            $p.utils.log('fullscreenerror', event);
                            ref.setFullscreen(false);

                            // remove fullscreen event listeners
                            $(document).off(fsEventsNS);
                        });
                    } else {
                        $p.utils.log('No fullscreenerror event defined.');
                    }

                    // request fullscreen
                    fsElement[0][fsRequestFunctionName]();
                    result = true;
                    break;

                case 'mediaonly':
                    if (!!this.playerModel.mediaElement) {

                        fsElement = this.playerModel.mediaElement;
                        fsElement[0][fsEnterFunctionName]();
                        result = true;
                    } else {
                        result = false;
                    }
                    break;
            }

            return result;
        };

        this._exitFullscreen = function () {

            var fsType = this.getFullscreenType(),
                apiType = $p.fullscreenApi.type,
                result = false;

            switch (fsType) {
                case 'full':
                    result = this._exitFullscreenApi();
                    break;

                case 'mediaonly':
                    /**
                     * there could be 2 cases in this situation:
                     * a) there is only 'mediaonly' fullscreen API available
                     * b) there is 'full' fullscreen API available, but the user prefer 'mediaonly' in config
                     */
                    result = this._exitFullscreenApi(apiType);
                    break;

                case 'viewport':
                    result = this._exitFullViewport();
                    break;

                    /**
                     * The fullscreen functionality is disabled in configuration
                     */
                case 'none':
                    result = false;
                    break;
            }

            return result;
        };

        this._exitFullscreenApi = function () {

            var apiType = apiType || $p.fullscreenApi.type,
                fsElement,
                fsExitFunctionName = $p.fullscreenApi[apiType]['exitFullscreen'] ? $p.fullscreenApi[apiType]['exitFullscreen'] : false,
                result = false;

            switch (apiType) {
                case 'full':
                    fsElement = document;
                    this.getIsFullscreen() ? fsElement[fsExitFunctionName]() : null;
                    result = true;
                    break;

                case 'mediaonly':
                    if (!!this.playerModel.mediaElement) {
                        fsElement = this.playerModel.mediaElement[0];
                        fsElement[fsExitFunctionName]();
                        result = true;
                    } else {
                        result = false;
                    }
                    break;
            }

            return result;
        };

        this.setSize = function (data) {

            var target = this.getIframe() || this.getDC(),
                fsdata = target.data('fsdata') || null,
                w = (data && data.width != null) ? data.width :
                (this.getConfig('width') != null) ? this.getConfig('width') : false,
                h = (data && data.height != null) ? data.height :
                (this.getConfig('height') == null && this.getConfig('ratio')) ? Math.round((w || this.getDC()
                    .width()) / this.getConfig('ratio')) :
                (this.getConfig('height') != null) ? this.getConfig('height') : false;

            if (this.getIsFullscreen() && fsdata != null) {
                // remember new dims while in FS
                fsdata.targetWidth = w;
                fsdata.targetHeight = h;
                target.data('fsdata', fsdata);
            } else {
                // apply new dims
                if (w) {
                    target.css({
                        width: w + "px"
                    });
                }
                if (h) {
                    target.css({
                        height: h + "px"
                    });
                }
            }

            try {
                this.playerModel.applyCommand('resize', {
                    width: w,
                    height: h
                });
            } catch (e) {}
        };

        this.setLoop = function (value) {

            this.config._loop = value || !this.config._loop;

            return this;
        };

        this.setDebug = function (value) {

            $p.utils.logging = (value !== undefined) ? value : !$p.utils.logging;

            if ($p.utils.logging) {
                $p.utils.log('DEBUG MODE #' + this.getId() + " Level: " + this.getConfig('debugLevel'));
            }

            return this;
        };

        this.addListener = function (evt, callback) {

            var ref = this;

            this._enqueue(function () {
                ref._addListener(evt, callback);
            });

            return this;
        };

        this._addListener = function (event, callback) {

            var evt = (event.indexOf('.') > -1) ? event.split('.') : [event, 'default'];

            this.listeners.push({
                event: evt[0],
                ns: evt[1],
                callback: callback
            });

            return this;
        };

        /**
         * removes an JS object from the event queue
         *
         * @param {String} name of event to remove
         * @param {Function} [callback]
         * @returns {PPlayer} reference to the current instance of projekktor
         */
        this.removeListener = function (event, callback) {

            var len = this.listeners.length,
                evt = (event.indexOf('.') > -1) ? event.split('.') : [event, '*'],
                toKill = [];

            // gather listeners to remove
            for (var i = 0; i < len; i++) {

                if (this.listeners[i] === undefined) {
                    continue;
                }

                if (this.listeners[i].event != evt[0] && evt[0] !== '*') {
                    continue;
                }

                if ((this.listeners[i].ns != evt[1] && evt[1] !== '*') || (this.listeners[i].callback !== callback && callback != null)) {
                    continue;
                }
                toKill.push(i);
            }

            // than remove them
            for (var i = 0, l = toKill.length; i < l; i++) {
                this.listeners.splice(toKill[i] - i, 1);
            }

            return this;
        };
        /**
         * @deprecated since 1.4.00
         *
         * Adds, removes, replaces item
         *
         * @param {type} item
         * @param {number} [index]
         * @param {boolean} [replace=false]
         * @returns {PPlayer}
         */
        this.setItem = function (item, index, replace) {
            // remove item
            if (item === null) {
                this.removeItemAtIndex(index);
            }
            // add item
            else {
                this.addItems(item, index, replace);
            }
            return this;
        };

        this.setFile = function () {

            var fileNameOrObject = arguments[0] || '',
                dataType = arguments[1] || this._getTypeFromFileExtension(fileNameOrObject),
                parser = arguments[2] || null,
                result = [{
                    file: {
                        src: fileNameOrObject,
                        type: dataType,
                        parser: parser
                    }
                }];

            this._clearqueue();
            this._detachplayerModel();

            // incoming JSON Object / native Projekktor playlist
            if (typeof fileNameOrObject === 'object') {
                $p.utils.log('Applying incoming JS Object', fileNameOrObject);
                this.setPlaylist(fileNameOrObject);
                return this;
            }

            if (result[0].file.type.indexOf('/xml') > -1 || result[0].file.type.indexOf('/json') > -1) {
                // async. loaded playlist
                $p.utils.log('Loading playlist data from ' + result[0].file.src + ' supposed to be ' + result[0].file.type);
                this._promote('scheduleLoading', 1 + this.getItemCount());
                this._playlistServer = result[0].file.src;
                this.getFromUrl(result[0].file.src, this, '_collectParsers', result[0].file.type, parser);
            } else {
                // incoming single file:
                $p.utils.log('Applying single resource:' + result[0].file.src, result);
                this.setPlaylist(result);
            }

            return this;
        };

        this._collectParsers = function () {

            this._syncPlugins('parserscollected', arguments);
            this._promote('scheduleLoaded', arguments);
        };

        this.addParser = function (parserId, parser) {
            if (typeof parserId === 'string' && typeof parser === 'function') {
                this._parsers[parserId.toUpperCase()] = parser;
            } else {
                $p.utils.log('Failed to set improperly defined parser.');
            }
        };

        this.getParser = function (parserId) {
            if (typeof parserId === 'string') {
                return this._parsers[parserId.toUpperCase()];
            } else {
                return function (data) {
                    return (data);
                };
            }
        };

        this.setPlaylist = this.destroy = function (obj) {

            var data = obj || [{
                    file: {
                        src: '',
                        type: 'none/none'
                    }
                }],
                files = data.playlist || data;

            this.media = [];

            // gather and set alternate config from reel:
            try {

                for (var props in data.config) {

                    if (data.config.hasOwnProperty(props)) {

                        if (typeof data.config[props].indexOf('objectfunction') > -1) {
                            continue; // IE SUCKZ
                        }
                        this.config[props] = eval(data.config[props]);
                    }
                }

                if (data.config != null) {
                    $p.utils.log('Updated config var: ' + props + ' to ' + this.config[props]);
                    this._promote('configModified');
                    delete(data.config);
                }
            } catch (e) {}

            // add media items
            this.addItems(files, 0, true);

            this._syncPlugins('reelupdate');
        };

        this.setPlaybackQuality = function (quality) {

            var qual = quality || this.getAppropriateQuality();

            if ($.inArray(qual, this.getItem().qualities || []) > -1) {
                this.playerModel.applyCommand('quality', qual);
                this.setConfig({
                    playbackQuality: qual
                });
            }

            return this;
        };

        this.openUrl = function (cfg) {

            cfg = cfg || {
                url: '',
                target: '',
                pause: false
            };

            if (cfg.url === '') {
                return this;
            }

            if (cfg.pause === true) {
                this.setPause();
            }
            window.open(cfg.url, cfg.target).focus();

            return this;
        };

        /**
         * Removes THIS Projekktor and reconstructs original DOM
         *
         * ENQUEUED
         *
         * @public
         * @return {Object} this
         */
        this.selfDestruct = this.destroy = function () {

                var ref = this;

                this._enqueue(function () {
                    ref._destroy();
                });

                return this;
            },
            this._destroy = function () {

                var ref = this;

                $(this).off();
                this.removePlugins();
                this.playerModel.destroy();
                this._removeGUIListeners();

                $.each(projekktors, function (idx) {

                    try {

                        if (this.getId() === ref.getId() || this.getId() === ref.getId() || this.getParent() === ref.getId()) {
                            projekktors.splice(idx, 1);
                            return;
                        }
                    } catch (e) {}
                });

                this.env.playerDom.replaceWith(this.env.srcNode);
                this._promote('destroyed');
                this.removeListener('*');

                return this;
            };

        /**
         * @public
         * @return {Object} this
         */
        this.reset = function (autoplay) {

                var ref = this;

                try {
                    this.addListener('fullscreen.reset', function () {
                        ref.removeListener('fullscreen.reset');
                        ref._clearqueue();
                        ref._enqueue(function () {
                            ref._reset(autoplay);
                        });
                    });

                    this.setFullscreen(false);
                } catch (e) {
                    // this needs to be fixed
                    // fails with an "this.playerModel.applyCommand is not a function" from time to time
                    // ugly workaround to prevent player to hang up:
                    ref.removeListener('fullscreen.reset');
                    ref._clearqueue();
                    ref._enqueue(function () {
                        ref._reset(autoplay);
                    });
                }

                return this;
            },
            this._reset = function (autoplay) {

                var cleanConfig = {};

                // this._isReady = false;
                $(this).off();
                $((this.getIframe()) ? parent.window.document : document).off(".projekktor");
                $(window).off('.projekktor' + this.getId());

                this.playerModel.destroy();
                this.playerModel = {};
                this._parsers = {};

                this.removePlugins();
                this._removeGUIListeners();
                this.env.mediaContainer = null;

                for (var i in this.config) {
                    if (this.config.hasOwnProperty(i)) {
                        cleanConfig[(i.substr(0, 1) === '_') ? i.substr(1) : i] = this.config[i];
                    }
                }

                cleanConfig['autoplay'] = cleanConfig['loop'] || autoplay;

                return this;
            },
            /********************************************************************************************
             Queue Points
             *********************************************************************************************/
            this.setCuePoint = function (obj, opt, stopProp) {

                var item = (obj.item !== undefined) ? obj.item : this.getItemId(),
                    options = $.extend(true, {
                            offset: 0
                        },
                        opt),
                    stopPropagation = stopProp || false,
                    //should we propagate cuepointsAdd event after cuepoint was added

                    cuePoint = {
                        id: obj.id || $p.utils.randomId(8),
                        group: obj.group || 'default',
                        item: item,
                        on: ($p.utils.toSeconds(obj.on) || 0) + options.offset,
                        off: ($p.utils.toSeconds(obj.off) || $p.utils.toSeconds(obj.on) || 0) + options.offset,
                        value: obj.value || null,
                        callback: obj.callback || function () {},
                        precision: (obj.precision == null) ? 1 : obj.precision,
                        title: (obj.title == null) ? '' : obj.title,
                        once: obj.once || false,
                        blipEvents: obj.blipEvents || [],
                        _listeners: [],
                        _unlocked: false,
                        _active: false,
                        _lastTime: 0,
                        isAvailable: function () {
                            return this._unlocked;
                        },
                        _stateListener: function (state, player) {

                            if ('STOPPED|COMPLETED|DESTROYING'.indexOf(state) > -1) {

                                if (this._active) {

                                    try {
                                        this.callback(false, this, player);
                                    } catch (e) {}
                                }
                                this._active = false;
                                this._lastTime = -1;
                                this._unlocked = false;
                            }
                        },
                        _timeListener: function (time, player) {

                            if (player.getItemId() !== this.item && this.item !== '*') {
                                return;
                            }

                            if (player.getItemId() !== this.item && this.item !== '*') {
                                return;
                            }

                            var timeIdx = (this.precision === 0) ? Math.round(time) : $p.utils.roundNumber(time, this.precision),
                                ref = this;

                            // are we already unlocked?
                            // consider buffer state to unlock future cuepoints for user interactions
                            if (this._unlocked === false) {

                                var approxMaxTimeLoaded = player.getDuration() * player.getLoadProgress() / 100;

                                if (this.on <= approxMaxTimeLoaded || this.on <= timeIdx) {

                                    // trigger unlock-listeners
                                    $.each(this._listeners['unlock'] || [], function () {
                                        this(ref, player);
                                    });
                                    this._unlocked = true;
                                } else {
                                    return;
                                }
                            }

                            // something to do?
                            if (this._lastTime === timeIdx) {
                                return;
                            }

                            var nat = (timeIdx - this._lastTime <= 1 && timeIdx - this._lastTime > 0);

                            // trigger ON
                            if (((timeIdx >= this.on && timeIdx <= this.off) || (timeIdx >= this.on && this.on === this.off && timeIdx <= this.on + 1)) && this._active !== true) {
                                this._active = true;
                                $p.utils.log("Cue Point: [ON " + this.on + "] at " + timeIdx, this);
                                var cp = $.extend(this, {
                                    enabled: true,
                                    seeked: !nat,
                                    player: player
                                });
                                player._promote('cuepoint', cp);

                                try {
                                    this.callback(cp);
                                } catch (e) {}

                                // remove cue point if it should be triggered only once
                                if (this.once) {
                                    player.removeCuePointById(this.id, this.item);
                                }
                            }
                            // trigger OFF
                            else if ((timeIdx < this.on || timeIdx > this.off) && this.off !== this.on && this._active === true) {
                                this._active = false;
                                $p.utils.log("Cue Point: [OFF " + this.off + "] at " + timeIdx, this);

                                var cp = $.extend(this, {
                                    enabled: false,
                                    seeked: !nat,
                                    player: player
                                });
                                player._promote('cuepoint', cp);

                                try {
                                    this.callback(cp);
                                } catch (e) {}

                                // remove cue point if it should be triggered only once
                                if (this.once) {
                                    player.removeCuePointById(this.id, this.item);
                                }
                            }

                            if (this.off === this.on && this._active && Number(timeIdx - this.on).toPrecision(this.precision) >= 1) {
                                this._active = false;
                            }

                            this._lastTime = timeIdx;
                        },
                        addListener: function (event, func) {

                            if (this._listeners[event] == null) {
                                this._listeners[event] = [];
                            }
                            this._listeners[event].push(func || function () {});
                        }
                    };

                if (obj.unlockCallback != null) {
                    cuePoint.addListener('unlock', obj.unlockCallback);
                }

                // create itemidx key
                if (!this._cuePoints.hasOwnProperty(item)) {
                    this._cuePoints[item] = [];
                }
                this._cuePoints[item].push(cuePoint);

                if (!stopPropagation) {
                    this._promote('cuepointsAdd', [cuePoint]);
                }

                return this._cuePoints[item];
            },
            this.setCuePoints = function (cp, itmId, forceItmId, options) {

                var cuepoints = cp || [],
                    itemId = itmId || this.getItemId(),
                    forceItemId = forceItmId || false,
                    ref = this;

                $.each(cuepoints, function () {
                    this.item = forceItemId ? itemId : this.item || itemId; // use given itemId if there is no item id specified per cuepoint or forceItemId is true
                    ref.setCuePoint(this, options, true); // set cuepoint and suppress event propagation after every addition
                });

                if (cuepoints.length) {
                    this._promote('cuepointsAdd', cuepoints);
                }

                return this._cuePoints;
            },
            this.setGotoCuePoint = function (cuePointId, itmId) {
                var currentItemId = this.getItemId(),
                    itemId = itmId || currentItemId;

                if (itemId === currentItemId) {
                    this.setPlayhead(this.getCuePointById(cuePointId, itemId).on);
                } else {
                    //TODO: change playlist item and setPlayhead position
                }

                return this;
            },
            /**
             * Gets cuepoints for specified playlist item
             *
             * @param {String} itmId Playlist item id or wildcard '*' for universal cuepoint added to all of items on the playlist
             * @param {Boolean} withWildcarded Should it get wildcarded ('*') cuepoints too
             * @param {Array} groups Get cuepoints only from given cuepoint groups
             * @returns {Array} Returns array of cuepoints which satisfies the given criteria
             */
            this.getCuePoints = function (itmId, withWildcarded, groups) {
                var itemId = itmId || this.getItemId(),
                    cuePoints = withWildcarded && itemId !== '*' ? $.merge($.merge([], this._cuePoints[itemId] || []), this._cuePoints['*'] || []) : this._cuePoints[itemId] || [],
                    cuePointsGroup = [];

                if (groups && !$.isEmptyObject(cuePoints)) {

                    for (var cIdx = 0; cIdx < cuePoints.length; cIdx++) {
                        if ($.inArray(cuePoints[cIdx].group, groups) > -1) {
                            cuePointsGroup.push(cuePoints[cIdx]);
                        }
                    }
                    return cuePointsGroup;
                }

                return cuePoints;
            },
            /**
             * Gets cuepoint with given id from specified playlist item
             *
             * @param {String} cuePointId
             * @param {String} [itmId=currentItemId]
             * @returns {Object} Returns cuepoint object if the cuepoint exists otherwise false
             */
            this.getCuePointById = function (cuePointId, itmId) {
                var result = false,
                    itemId = itmId || this.getItemId(),
                    cuePoints = this.getCuePoints(itemId);

                for (var j = 0; j < cuePoints.length; j++) {
                    if (cuePoints[j].id === cuePointId) {
                        result = cuePoints[j];
                        break;
                    }
                }
                return result;
            },
            /**
             *
             * @param {String} [itmId=currentItemId]
             * @param {Boolean} [withWildcarded=false]
             * @param {Array} [cuePointGroups]
             * @returns {Array} Array of removed cuepoints
             */
            this.removeCuePoints = function (itmId, withWildcarded, cuePointGroups) {
                var itemId = itmId || this.getItemId(),
                    cuePoints = this._cuePoints,
                    itemKey = {},
                    cpForItem = [],
                    toKill = [],
                    removed = [];

                // remove cuepoints and relevant event listeners
                for (var itemKey in cuePoints) {
                    if (cuePoints.hasOwnProperty(itemKey) && (itemKey === itemId || (withWildcarded ? itemKey === '*' : false))) {
                        cpForItem = cuePoints[itemKey];

                        for (var cIdx = 0, cL = cpForItem.length; cIdx < cL; cIdx++) {

                            if (cuePointGroups === undefined || $.inArray(cpForItem[cIdx].group, cuePointGroups) > -1) {
                                this.removeListener('time', cpForItem[cIdx].timeEventHandler);
                                this.removeListener('state', cpForItem[cIdx].stateEventHandler);
                                toKill.push(cIdx);
                            }
                        }

                        for (var i = 0, l = toKill.length; i < l; i++) {
                            removed.push(cpForItem.splice(toKill[i] - i, 1)[0]);
                        }

                        if (!cpForItem.length) {
                            delete cuePoints[itemKey];
                        }
                        toKill = [];
                    }
                }

                if (removed.length) {
                    this._promote('cuepointsRemove', removed);
                }

                return removed;
            },
            /**
             * Remove cuepoint with given id from specified playlist item
             *
             * @param {String} cuePointId
             * @param {String} [itmId=currentItemId]
             * @returns {Array} Array with removed cuepoint if it was found or empty array otherwise
             */
            this.removeCuePointById = function (cuePointId, itmId) {

                if (typeof cuePointId !== 'string') {
                    return [];
                }

                var itemId = itmId || this.getItemId(),
                    cuePoints = this.getCuePoints(itemId),
                    removed = [];

                for (var cIdx = 0; cIdx < cuePoints.length; cIdx++) {

                    if (cuePoints[cIdx].id === cuePointId) {
                        this.removeListener('time', cuePoints[cIdx].timeEventHandler);
                        this.removeListener('state', cuePoints[cIdx].stateEventHandler);
                        removed = cuePoints.splice(cIdx, 1);
                        break;
                    }
                }

                if (removed.length) {
                    this._promote('cuepointsRemove', removed);
                }

                return removed;
            },
            this.syncCuePoints = function () {

                var ref = this;

                this._enqueue(function () {
                    try {
                        ref._applyCuePoints();
                    } catch (e) {}
                });

                return this;
            },
            this._cuepointsChangeEventHandler = function (cuepoints) {

                var ref = this;

                this._enqueue(function () {
                    try {
                        ref._applyCuePoints();
                    } catch (e) {}
                });
            },
            this._applyCuePoints = function () {

                var ref = this,
                    cuePoints = this.getCuePoints(this.getItemId(), true) || [];

                // remove all cuepoint listeners
                ref.removeListener('*.cuepoint');

                $.each(cuePoints, function (key, cuePointObj) {

                    // attach cuepoint event handlers
                    cuePointObj.timeEventHandler = function (time, player) {
                        try {
                            cuePointObj._timeListener(time, player);
                        } catch (e) {}
                    };

                    cuePointObj.stateEventHandler = function (state, player) {
                        try {
                            cuePointObj._stateListener(state, player);
                        } catch (e) {}
                    };

                    ref.addListener('time.cuepoint', cuePointObj.timeEventHandler);
                    ref.addListener('state.cuepoint', cuePointObj.stateEventHandler);
                });
                this._promote('cuepointsSync', cuePoints);
            },
            /********************************************************************************************
             Command Queue
             *********************************************************************************************/
            this._enqueue = function (command, params, delay) {

                if (command != null) {
                    this._queue.push({
                        command: command,
                        params: params,
                        delay: delay
                    });
                    this._processQueue();
                }
            };

        this._clearqueue = function (command, params) {

            if (this._isReady === true) {
                this._queue = [];
            }
        };

        this._processQueue = function () {

            var ref = this;

            if (this._processing === true) {
                return;
            }
            this._processing = true;

            (function pq() {
                try {

                    var msg = ref._queue.shift();
                    if (msg != null) {

                        if (typeof msg.command === 'string') {
                            if (msg.delay > 0) {
                                setTimeout(function () {
                                    ref.playerModel.applyCommand(msg.command, msg.params);
                                }, msg.delay);
                            } else {
                                ref.playerModel.applyCommand(msg.command, msg.params);
                            }
                        } else {
                            msg.command(ref);
                        }
                    }
                } catch (e) {
                    $p.utils.log("ERROR:", e);
                }

                if (ref._queue.length === 0) {
                    ref._processing = false;
                    return;
                }
                pq();
            })();
        };

        /********************************************************************************************
         GENERAL Tools
         *********************************************************************************************/
        /**
         *
         * @param {string} url or filename containing file extension for which mimeType we want to get
         * @returns {string} one of defined mimeTypes from available models iLove definitions
         * or 'none/none' if there is no such a type or url attribute was other than 'string'
         */
        this._getTypeFromFileExtension = function (url) {

            var regExp = $p.cache.fileExtensionsRegExp,
                extTypes = $p.cache.fileExtensionMimeTypeMap, // file extension -> mimeType map
                extMatch,
                fileExt = 'na'; // file extension string, 'na' -> none/none

            if (!regExp) {

                regExp = function () {

                    var extensions = [];

                    // build regexp matching all known extensions
                    extTypes.forEach(function (mimeType, ext) {
                        extensions.push('\\\.' + ext);
                    });

                    // match last occurrence of the extension 
                    return new RegExp('(' + extensions.join('|') + ')(?!' + extensions.join('|') + ')(?:[\?\/#&]{1}.*|$)', 'i');
                }();

                $p.cache.fileExtensionsRegExp = regExp;
            }

            if (typeof url === 'string') {

                extMatch = url.match(regExp);

                if (extMatch) {
                    fileExt = extMatch[1].replace('.', '');
                }
            }

            return Array.from(extTypes.get(fileExt))[0];
        };

        this._getSupportedPlatforms = function (global) {
            var supportedPlatformsGlobal = $p.cache.platformMimeTypeMap,
                supportedPlatformsLocal = new Map(),
                platformsConfig;

            return function () {
                if (global) {
                    return supportedPlatformsGlobal;
                }

                if (!supportedPlatformsLocal.size) {

                    platformsConfig = this.getConfig('platforms') || ['browser'];

                    // always add 'browser' platform if it's missing
                    if (platformsConfig.indexOf('browser') === -1) {
                        platformsConfig.unshift('browser');
                    }

                    platformsConfig.forEach(function (pt) {

                        if (supportedPlatformsGlobal.has(pt)) {
                            supportedPlatformsLocal.set(pt, supportedPlatformsGlobal.get(pt));
                        }
                    });
                }
                return supportedPlatformsLocal;
            };
        };

        this.getSupportedPlatforms = this._getSupportedPlatforms();

        this.getSupportedPlatformsGlobal = this._getSupportedPlatforms(true);

        this.getPriorityForPlatform = function () {
            var platforms;

            return function (platform) {
                if (!platforms) {
                    platforms = Array.from(this.getSupportedPlatforms());
                }
                return platforms.indexOf(platform);
            };
        }.call(this);

        this.getCanPlayWithDrm = function (drmSystem, mimeType, platforms) {
            var ref = this,
                supportedDrmSystems = $p.drm.supportedDrmSystems,
                modelsILoveSupported = $p.cache.modelsILoveSupported,
                supportedPlatforms = Array.from(ref.getSupportedPlatforms().keys()),
                pt = Array.isArray(platforms) ? $p.utils.intersect(supportedPlatforms, platforms) : supportedPlatforms;

            // check if DRM system is supported at this device
            if (supportedDrmSystems.indexOf(drmSystem) > -1) {
                // check if DRM system is supported for specified mimeType
                return modelsILoveSupported.some(function (iLove) {
                    return (iLove.drm &&
                        iLove.drm.indexOf(drmSystem) > -1 &&
                        iLove.type === mimeType &&
                        $p.utils.intersect(iLove.platform, pt).length
                    );
                });
            }
            return false;
        };

        this._readMediaTag = function (domNode) {
            var result = {},
                htmlTag = '',
                attr = [],
                ref = this;

            if ("VIDEOAUDIO".indexOf(domNode[0].tagName.toUpperCase()) === -1) {
                return false;
            }

            // gather general config attributes:
            // - Safari does not supply default-bools here:
            if (!this.getConfig('ignoreAttributes')) {
                result = {
                    autoplay: ((domNode.attr('autoplay') !== undefined || domNode.prop('autoplay') !== undefined) && domNode.prop('autoplay') !== false) ? true : false,
                    controls: ((domNode.attr('controls') !== undefined || domNode.prop('controls') !== undefined) && domNode.prop('controls') !== false) ? true : false,
                    muted: ((domNode.attr('muted') !== undefined || domNode.prop('muted') !== undefined) && domNode.prop('muted') !== false) ? true : false,
                    loop: ((domNode.attr('autoplay') !== undefined || domNode.prop('loop') !== undefined) && domNode.prop('loop') !== false) ? true : false,
                    title: (domNode.attr('title') !== undefined && domNode.attr('title') !== false) ? domNode.attr('title') : '',
                    poster: (domNode.attr('poster') !== undefined && domNode.attr('poster') !== false) ? domNode.attr('poster') : '',
                    width: (domNode.attr('width') !== undefined && domNode.attr('width') !== false) ? domNode.attr('width') : null,
                    height: (domNode.attr('height') !== undefined && domNode.attr('height') !== false) ? domNode.attr('height') : null
                };
            }

            // IE7+8 and some other idiots do not keep attributes w/o values:
            htmlTag = $($('<div></div>').html($(domNode).clone())).html();
            attr = ['autoplay', 'controls', 'loop', 'muted'];

            for (var i = 0; i < attr.length; i++) {

                if (htmlTag.indexOf(attr[i]) === -1) {
                    continue;
                }
                result[attr[i]] = true;
            }

            // get possible media sources:
            result.playlist = [];
            result.playlist[0] = [];
            result.playlist[0]['config'] = {
                tracks: []
            };

            // ... from "src" attribute:
            if (domNode.attr('src')) {
                result.playlist[0].push({
                    src: domNode.attr('src'),
                    type: domNode.attr('type') || this._getTypeFromFileExtension(domNode.attr('src'))
                });
            }

            // ... from media tag children
            // ... within a lame browser (IE <9) ...
            if (!$('<video/>').get(0).canPlayType) {

                var childNode = domNode;

                do {
                    childNode = childNode.next('source,track');

                    if (childNode.attr('src')) {
                        switch (childNode.get(0).tagName.toUpperCase()) {
                            case 'SOURCE':
                                result.playlist[0].push({
                                    src: childNode.attr('src'),
                                    type: childNode.attr('type') || this._getTypeFromFileExtension(childNode.attr('src')),
                                    quality: childNode.attr('data-quality') || ''
                                });
                                break;

                            case 'TRACK':

                                if ($(this).attr('src')) {
                                    result.playlist[0]['config']['tracks'].push({
                                        src: childNode.attr('src'),
                                        kind: childNode.attr('kind') || 'subtitle',
                                        lang: childNode.attr('srclang') || null,
                                        label: childNode.attr('label') || null
                                    });
                                }
                                break;
                        }
                    }
                } while (childNode.attr('src'));
            }

            // ... within a good browser ...
            if (result.playlist[0].length === 0) {
                domNode.children('source,track').each(function () {
                    if ($(this).attr('src')) {

                        switch ($(this).get(0).tagName.toUpperCase()) {
                            case 'SOURCE':
                                result.playlist[0].push({
                                    src: $(this).attr('src'),
                                    type: $(this).attr('type') || ref._getTypeFromFileExtension($(this)
                                        .attr('src')),
                                    quality: $(this).attr('data-quality') || ''
                                });
                                break;

                            case 'TRACK':
                                result.playlist[0]['config']['tracks'].push({
                                    src: $(this).attr('src'),
                                    kind: $(this).attr('kind') || 'subtitle',
                                    lang: $(this).attr('srclang') || null,
                                    label: $(this).attr('label') || null
                                });
                                break;
                        }
                    }
                });
            }

            return result;
        };

        this._init = function (customNode, customCfg) {

            var theNode = customNode || srcNode,
                theCfg = customCfg || cfg,
                cfgByTag = this._readMediaTag(theNode),
                ref = this,
                iframeParent = this.getIframeParent();

            // -----------------------------------------------------------------------------
            // - 1. GENERAL CONFIG ---------------------------------------------------------
            // -----------------------------------------------------------------------------

            // remember original node HTML for reset and reference purposes:
            this.env.srcNode = theNode.wrap('<div></div>').parent().html();
            theNode.unwrap();

            // remember initial classes
            this.env.className = theNode.attr('class') || '';

            // remember id
            this._id = theNode[0].id || $p.utils.randomId(8);

            if (cfgByTag !== false) {
                // swap videotag->playercontainer
                this.env.playerDom = $('<div/>')
                    .attr({
                        'class': theNode[0].className,
                        'style': theNode.attr('style')
                    });

                theNode.replaceWith(this.env.playerDom);

                // destroy theNode
                theNode.empty().removeAttr('type').removeAttr('src');

                try {
                    theNode.get(0).pause();
                    theNode.get(0).load();
                } catch (e) {}
                $('<div/>').append(theNode).get(0).innerHTML = '';
                theNode = null;
            } else {
                this.env.playerDom = theNode;
            }

            // merge configs we got so far:
            theCfg = $.extend(true, {}, cfgByTag, theCfg);

            for (var i in theCfg) {

                if (this.config['_' + i] != null) {
                    this.config['_' + i] = theCfg[i];
                } else {

                    if (i.indexOf('plugin_') > -1) {
                        this.config[i] = $.extend(this.config[i], theCfg[i]);
                    } else {
                        this.config[i] = theCfg[i];
                    }
                }
            }

            // turn debug mode on/off
            this.setDebug(this.getConfig('debug'));

            // check platforms config is valid
            // should be array with at least 1 platform 'browser' defined
            if (!$.isArray(this.config['_platforms'])) {
                $p.utils.log('ERROR: platforms config must be an array. Reset platforms config to the defaults.');
                this.config['_platforms'] = Object.getPrototypeOf(this.config)['_platforms'] || [];
            }
            // add BROWSER platform if it's not defined in config
            if ($.inArray('browser', this.config['_platforms']) === -1) {
                $p.utils.log('ERROR: "browser" platform not present in platforms config. Adding it.');
                this.config._platforms.unshift('browser');
            }

            // initial DOM scaling
            this.setSize();

            // set initial volume and muted values
            if (this.getConfig('forceMuted')) {
                this.env.muted = true;
            } else {
                this.env.muted = this.storage.restore('muted') !== null ? this.storage.restore('muted') : this.env.muted;
            }

            if (this.env.muted) {
                this.env.volume = 0;
            } else {
                this.env.volume = this.storage.restore('volume') !== null ? this.storage.restore('volume') : this.getConfig('volume');
            }

            // -----------------------------------------------------------------------------
            // - TRIM DEST --------------------------------------------------------------
            // -----------------------------------------------------------------------------

            // make sure we can deal with a domID here:
            this.env.playerDom.attr('id', this._id);

            // load and initialize plugins
            this._registerPlugins();

            // set up iframe environment
            if (this.config._iframe === true) {
                if (iframeParent) {
                    iframeParent.ready(function () {
                        ref._expandView($(window), ref.getDC());
                    });
                } else {
                    ref._expandView($(window), ref.getDC());
                }
            }

            // cross domain
            if (iframeParent === false) {
                this.config._isCrossDomain = true;
            }

            // playlist?
            for (var i in this.config._playlist[0]) {

                // we prefer playlists - search one:
                if (this.config._playlist[0][i].type) {

                    if (this.config._playlist[0][i].type.indexOf('/json') > -1 || this.config._playlist[0][i].type.indexOf('/xml') > -1) {
                        this.setFile(this.config._playlist[0][i].src, this.config._playlist[0][i].type, this.config._playlist[0][i].parser);
                        return this;
                    }
                }
            }

            this.setFile(this.config._playlist);

            return this;
        };

        var ref = this;
        // if there are some initPromises, wait with _init() 
        // until all of them will be fulfilled. Otherwise _init() immediately
        if ($p.initPromises.length > 0) {
            Promise.all($p.initPromises).then(function (result) {
                // clear promises queue
                $p.initPromises.length = 0;
                return ref._init();
            },
                function (reason) {
                    $p.utils.log('initPromises failed: ' + reason);

                });
        }
        else {
            ref._init();
        }
    }

    function Projekktor() {

        var arg = arguments[0],
            instances = [];

        // test media support
        $p.testMediaSupport();

        if (!arguments.length) {
            return projekktors[0] || null;
        }

        // get instances
        // projekktor(idx:number);
        if (typeof arg === 'number') {
            return projekktors[arg];
        }

        // by string selection unique "id" or "*"
        if (typeof arg === 'string') {

            // get all instances
            if (arg === '*') {
                return new Iterator(projekktors);
            }

            // get instance by Jquery OBJ, 'containerId' or selector
            for (var i = 0; i < projekktors.length; i++) {
                try {
                    if (projekktors[i].getId() == arg.id) {
                        instances.push(projekktors[i]);
                        continue;
                    }
                } catch (e) {}
                try {
                    for (var j = 0; j < $(arg).length; j++) {
                        if (projekktors[i].env.playerDom.get(0) == $(arg).get(j)) {
                            instances.push(projekktors[i]);
                            continue;
                        }
                    }
                } catch (e) {}
                try {
                    if (projekktors[i].getParent() == arg) {
                        instances.push(projekktors[i]);
                        continue;
                    }
                } catch (e) {}
                try {
                    if (projekktors[i].getId() == arg) {
                        instances.push(projekktors[i]);
                        continue;
                    }
                } catch (e) {}
            }

            if (instances.length > 0) {
                return (instances.length == 1) ? instances[0] : new Iterator(instances);
            }
        }

        // build instances
        if (instances.length === 0) {
            var cfg = arguments[1] || {},
                callback = arguments[2] || {},
                count = 0,
                playerA;

            if (typeof arg === 'string') {
                $.each($(arg), function () {
                    playerA = new PPlayer($(this), cfg, callback);
                    projekktors.push(playerA);
                    count++;
                });
                return (count > 1) ? new Iterator(projekktors) : playerA;
                // arg is a DOM element
            } else if (arg) {
                projekktors.push(new PPlayer(arg, cfg, callback));
                return new Iterator(projekktors);
            }
        }
    }

    Object.defineProperties(Projekktor, {
        initPromises: {
            value: []
        },
        cache: {
            value: {
                modelsILove: [],
                modelsILoveSupported: undefined,
                platformMimeTypeMap: undefined,
                fileExtensionMimeTypeMap: undefined
            }
        },
        models: {
            value: new Map()
        },
        newModel: {
            value: function (newModelDef, parentModelId) {
                var models = this.models,
                    mILove = this.cache.modelsILove,
                    modelId = newModelDef.modelId,
                    parentModel = models.has(parentModelId) ? models.get(parentModelId).prototype : {},
                    newModel;

                // skip if already exists
                if (models.has(modelId)) {
                    return false;
                }

                // register new model and extend its parent
                newModel = function () {};
                newModel.prototype = $.extend({}, parentModel, newModelDef);

                // add new model to the models register
                models.set(modelId, newModel);

                // add model iLove definitions to the cache
                newModelDef.iLove.forEach(function (iLoveObj) {
                    iLoveObj.model = modelId;
                    mILove.push(iLoveObj);
                });

                return true;
            }
        },
        plugins: {
            value: {}
        },
        /**
         * generates:
         * - platform -> mimeType map 
         * - file extension -> mimeType map 
         * - supported iLoves array
         */
        testMediaSupport: {
            value: function () {

                var fileExtensionMimeTypeMap,
                    platformMimeTypeMap,
                    modelsILoveSupported,
                    mILove;

                // process only once
                if (!$p.cache.platformMimeTypeMap && !$p.cache.fileExtensionMimeTypeMap) {

                    fileExtensionMimeTypeMap = new Map();
                    platformMimeTypeMap = new Map();
                    modelsILoveSupported = [];
                    mILove = $p.cache.modelsILove || [];

                    mILove.forEach(function (iLove) {

                        var platforms = iLove.platform || [],
                            modelId = iLove.model,
                            mimeType = iLove.type,
                            fileExt = iLove.ext;

                        // create file extension -> mimeType map for later use
                        if (!fileExtensionMimeTypeMap.has(fileExt)) {
                            fileExtensionMimeTypeMap.set(fileExt, new Set());
                        }
                        // add mimeType to the set of supported for this platform
                        fileExtensionMimeTypeMap.get(fileExt).add(mimeType);

                        // test mimeType support for every platform specified in iLove
                        platforms.forEach(function (platform) {

                            // check if the platform is known to the player
                            if ($p.platforms.hasOwnProperty(platform)) {

                                // requested platform version is minPlatformVersion from platformsConfig or model prototype
                                var reqPlatformVersion = String($p.models.get(modelId).prototype[platform + 'Version']);

                                // perform version and config check:
                                if ($p.utils.versionCompare($p.platforms[platform](mimeType), reqPlatformVersion)) {

                                    if (!platformMimeTypeMap.has(platform)) {
                                        platformMimeTypeMap.set(platform, new Set());
                                    }
                                    // add mimeType to the set of supported for this platform
                                    platformMimeTypeMap.get(platform).add(mimeType);

                                    modelsILoveSupported.push(iLove);
                                }
                            }
                        });
                    });

                    // cache values
                    $p.cache.fileExtensionMimeTypeMap = fileExtensionMimeTypeMap;
                    $p.cache.platformMimeTypeMap = platformMimeTypeMap;
                    $p.cache.modelsILoveSupported = modelsILoveSupported;
                }
            }
        }
    });

    return Projekktor;

}(window, document, jQuery));
var projekktorConfig = (function (window, document, $, $p){

    "use strict";

function projekktorConfig() {
    this._version = "1.8.2";
}

return projekktorConfig;

}(window, document, jQuery, projekktor));/*
* this file is part of:
* projekktor zwei
* http://www.projekktor.com
*
* Copyright 2010-2012, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
* under GNU General Public License
* http://www.filenew.org/projekktor/license/
*/
(function (window, document, $, $p, projekktorConfig){
    
    "use strict";
    
projekktorConfig.prototype = {
    /**************************************************************
        Config options to be customized prior initialization only:
    ***************************************************************/

    _playerName:                    'Projekktor',

    _playerHome:                    'http://www.projekktor.com?via=context',

    /* Plugins to load on instance initialization, plugins are automatically extending the projekktorPluginInterface class.
    The order how the plugins are set here is important because they are added from z-index 0 to n one by one to the player DOM.
    As such it is useful to add the "Display" plugin always first.
    */
    _plugins:                       ['display', 'controlbar', 'contextmenu', 'settings'],

    /* Add one plugin or more plugins to the player. Alternative to "plugins" above. Will be merged with it. */
    _addplugins:                    [],

    /* custom reel parser (data:JSObject), default function(data){return data;} */
    _reelParser:                    null,

    /* Prefix prepended to all css-Classnames and data-attributes used by the player in order to avoid conflicts with existing layouts and scripts */
    _ns:                            'pp',

    /* a prioritized array of available platforms */
    _platforms:                     ['browser', 'android', 'ios', 'mse', 'native', 'videojs'],

    /* additional platforms config */
    _platformsConfig: {
        mse: {
            hlsjs: {
                src: '',
                initVars: {}
            },
            dashjs: {
                src: '',
                initVars: {}
            }
        },
        videojs: {
            src: ''
        }
    },

    _platformsFullscreenConfig: {
        browser: ['full', 'viewport'],
        native: ['full', 'mediaonly', 'viewport'],
        android: ['full', 'mediaonly', 'viewport'],
        ios: ['full', 'mediaonly', 'viewport'],
        mse: ['full', 'viewport'],
        videojs: ['full', 'viewport']
    },

    /* if set to true, projekktor assumes to live within an iframe and will act accordingly (used for embedding) */
    _iframe:                        false,

    /* if set to true projekktor will discard native media tag attributes (loop,controls,autoplay,preload etc.pp) */
    _ignoreAttributes:              false,

    /* looping scheduled media elements -  will be overwritten by loop-attribute of a replaced <video> tag. */
    _loop:                          false,

    /* automatically start playback once page has loaded -  will be overwritten by autoplay-attribute of a replaced <video> tag. */
    _autoplay:                      false,

    /* if more than one item is scheduled, true will automatically start playback of the next item in line once current one completed */
    _continuous:                    true,

    /* "true" will stop all other player instances but the one the user clicked play on. */
    _thereCanBeOnlyOne:             true,

    /* An array of items to be played. Check http://www.projekktor.com/docs/playlists to learn more */
    _playlist:                      [],

    /* debug on / off */
    _debug:                         false,
    debugLevel:                     'plugins,events,',

    /* the width of the player - >0= overwrite destNodes width, 0= keep dest node width, false=maintain ratio */
    _width:                         null,

    /* guess what.... the hight of the player - >0= overwrite destNodes height, 0 = keep height , false=maintain ratio */
    _height:                        null,

    _ratio:                         false,

    /* An array of objects featuring keycode=>function sets for keyboard-controls-customizing */
    _keys: [],

    /* cross domain */
    _isCrossDomain:                 false,

    /* on "true" try to leave fullscreen on player "complete" */
    _leaveFullscreen:               true,

    /* A prioritized list of available fullscreen modes:
     * - full - use HTML5 fullscreen API if available - will push all the player controls and video into fullscreen mode
     * - mediaonly - will use native video player in fullscreen mode (no custom overlays or controls will be displayed)
     * - viewport - this is 'pseudo fullscreen', it'll stretch the player with it's controls to the browser viewport size
     *
     * If the array is empty or value is null then the fullscreen functionality will be disabled. If you prefer to use
     * fullviewport mode even if the native fullscreen for <video> elements is available (e.g. iPad), just push 'viewport' before
     * 'mediaonly' into array like: ['full', 'viewport', 'mediaonly']
     */
    _fullscreen:                    ['full', 'mediaonly', 'viewport'],

    /**************************************************************
        Config options available per playlist item:
    ***************************************************************/

    /* unique itemID for the item currently played - dynamically generated if not provided via config */
    id:                             null,

    /* a title is a title is a title */
    title:                          null,

    cat:                            'clip',

    /* How to select best media format to play. There are two modes available:
        - 'platformsOrder'
        - 'sourcesOrder'
    */
    prioritizeBy: 'platformsOrder', 

    /* URL to poster image -  will be overwritten by poster-attribute of the replaced media tag. */
    poster:                         null,

    /* enable/disable controls -  will be overwritten by controls-attribute of the replaced <video> tag. */
    controls:                       true,

    /* start offset in seconds for randomly seekable media. (EXPERIMENTAL) */
    start:                          false,

    /* stop endpoint in seconds for randomly seekable media. (EXPERIMENTAL) */
    stop:                           false,

    /* initial volume on player-startup, 0=muted, 1=max */
    volume:                         0.8,

    /* a cover which will fill the display on audio-only playback */
    cover:                          '',

    /* enable/disable the possibility to PAUSE the video once playback started. */
    disablePause:                   false,

    /* enable/disable the possibility to skip the video by hitting NEXT or using the SCRUBBER */
    disallowSkip:                   false,

    /* if set to TRUE users can not change the volume of the player - neither via API nor through controls */
    fixedVolume:                    false,

    /* if set to true the initial value of muted will be always taken from configuration instead of user last remember settings */
    forceMuted: false,

    /* scaling used for images (playlist items and posters) "fill", "aspectratio" or "none" */
    imageScaling:                   'aspectratio',

    /* scaling used for videos (flash and native, not youtube) "fill", "aspectratio" or "none" */
    videoScaling:                   'aspectratio',

    /* defines the streamtype of the current item.
        'http':  http  streaming
    */
    streamType:                     'http',

    /* Youtube offers two different player APIs: fLaSh and "iFrame" for HTML5 . Make your choice here:
      For mobile devices this is forced to TRUE
    */
    useYTIframeAPI:                 true,

    /* enable/disable fetching of keyboard events - works in "fullscreen" only */
    enableKeyboard:                 true,

    /*
    small: Player height is 240px, and player dimensions are at least 320px by 240px for 4:3 aspect ratio.
    medium: Player height is 360px, and player dimensions are 640px by 360px (for 16:9 aspect ratio) or 480px by 360px (for 4:3 aspect ratio).
    large: Player height is 480px, and player dimensions are 853px by 480px (for 16:9 aspect ratio) or 640px by 480px (for 4:3 aspect ratio).
    hd720: Player height is 720px, and player dimensions are 1280px by 720px (for 16:9 aspect ratio) or 960px by 720px (for 4:3 aspect ratio).
    hd1080: Player height is 1080px, and player dimensions are 1920px by 1080px (for 16:9 aspect ratio) or 1440px by 1080px (for 4:3 aspect ratio).
    highres: Player height is greater than 1080px, which means that the player's aspect ratio is greater than 1920px by 1080px.
    */
    playbackQuality:                'auto',

    _playbackQualities:
    [
        {key: 'small', minHeight: 240, minWidth: 240},
        {key: 'medium', minHeight: 360, minWidth: [{ratio: 1.77, minWidth: 640}, {ratio: 1.33, minWidth: 480}]},
        {key: 'large', minHeight: 480, minWidth: [{ratio: 1.77, minWidth: 853}, {ratio: 1.33, minWidth: 640}]},
        {key: 'hd1080', minHeight: 1080, minWidth: [{ratio: 1.77, minWidth: 1920}, {ratio: 1.33, minWidth: 1440}]},
        {key: 'hd720', minHeight: 720, minWidth: [{ratio: 1.77, minWidth: 1280}, {ratio: 1.33, minWidth: 960}]},
        {key: 'highres', minHeight: 1081, minWidth: 0}
    ],

    /**
     * Format of dynamic stream (HDS, HLS, MSS, etc.) audio/video quality keys in which they will be displayed in the settings menu
     *
     * The available template values you can use:
     * %{width} - width in px
     * %{height} - height in px
     *
     * %{bitrate} - bitrate in kbps or Mbps
     * %{bitrateunit} - kbps or Mbps
     * %{bitratekbps} - bitrate in kbps
     * %{bitratembps} - bitrate in Mbps
     */
    dynamicStreamQualityKeyFormatAudioVideo: '%{height}p | %{bitrate}%{bitrateunit}',

    /**
     * Format of dynamic stream (HDS, HLS, MSS, etc.) audio-only quality keys in which they will be displayed in the settings menu
     *
     * The available template values you can use:
     * %{bitrate} - bitrate in kbps or Mbps
     * %{bitrateunit} - kbps or Mbps
     * %{bitratekbps} - bitrate in kbps
     * %{bitratembps} - bitrate in Mbps
     *
     * Note: the audio-only qualities will appear on the list only when the 'dynamicStreamShowAudioOnlyQualities' config option is set to true.
     */
    dynamicStreamQualityKeyFormatAudioOnly: 'audio | %{bitrate}%{bitrateunit}',

    /**
     * If the value is set to >0 than there will be decimal point and so many decimal places shown within
     * the bitrate parte of the key. E.g.:
     *
     * dynamicStreamQualityKeyBitrateRoundingDecimalPlacesCount: 2,
     * dynamicStreamQualityKeyFormatAudioVideo: '%{bitrate}%{bitrateunit}'
     * // stream bitrate = 1656kbps
     * // key will be rendered as: 1.66Mbps
     *
     */
    dynamicStreamQualityKeyBitrateRoundingDecimalPlacesCount: 0,

    // if true, the player will add audio only streams to the list of available qualities
    dynamicStreamShowAudioOnlyQualities: false,

    /* if testcard is disabled, the player will force a file download when no playback platform
    is available. Otherwise (enableTestcard=true) a testcard with an error message is shown in case of issues */
    enableTestcard:                 true,

    /* if the scheduled playlist holds more than one item an "skipTestcard" is set to TRUE in case of an error
    the player will proceed to the next item without showing a testcard */
    skipTestcard:                   false,

    /* (pre-) sets the media-duration / will be overwritten once META data is available */
    duration:                       0,

    /* add this CSS classes on startup */
    className:                      ''
};

}(window, document, jQuery, projekktor, projekktorConfig));(function (window, document, $, $p) {

    "use strict";
    
    $p.utils = {
        imageDummy: function () {
            return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAABBJREFUeNpi/v//PwNAgAEACQsDAUdpTjcAAAAASUVORK5CYII=';
        },
        videoDummy: function (type) {
            switch (type) {
                case 'mp4':
                default:
                    // black 256x144 (16:9) h264/AAC - 1s
                    return 'data:video/mp4;base64,AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAABfttZGF0AAACoAYF//+c3EXpvebZSLeWLNgg2SPu73gyNjQgLSBjb3JlIDE0OCAtIEguMjY0L01QRUctNCBBVkMgY29kZWMgLSBDb3B5bGVmdCAyMDAzLTIwMTYgLSBodHRwOi8vd3d3LnZpZGVvbGFuLm9yZy94MjY0Lmh0bWwgLSBvcHRpb25zOiBjYWJhYz0xIHJlZj0zIGRlYmxvY2s9MTowOjAgYW5hbHlzZT0weDM6MHgxMTMgbWU9aGV4IHN1Ym1lPTcgcHN5PTEgcHN5X3JkPTEuMDA6MC4wMCBtaXhlZF9yZWY9MSBtZV9yYW5nZT0xNiBjaHJvbWFfbWU9MSB0cmVsbGlzPTEgOHg4ZGN0PTEgY3FtPTAgZGVhZHpvbmU9MjEsMTEgZmFzdF9wc2tpcD0xIGNocm9tYV9xcF9vZmZzZXQ9LTIgdGhyZWFkcz00IGxvb2thaGVhZF90aHJlYWRzPTEgc2xpY2VkX3RocmVhZHM9MCBucj0wIGRlY2ltYXRlPTEgaW50ZXJsYWNlZD0wIGJsdXJheV9jb21wYXQ9MCBjb25zdHJhaW5lZF9pbnRyYT0wIGJmcmFtZXM9MyBiX3B5cmFtaWQ9MiBiX2FkYXB0PTEgYl9iaWFzPTAgZGlyZWN0PTEgd2VpZ2h0Yj0xIG9wZW5fZ29wPTAgd2VpZ2h0cD0yIGtleWludD0yNTAga2V5aW50X21pbj0yNSBzY2VuZWN1dD00MCBpbnRyYV9yZWZyZXNoPTAgcmNfbG9va2FoZWFkPTQwIHJjPWNyZiBtYnRyZWU9MSBjcmY9MjMuMCBxY29tcD0wLjYwIHFwbWluPTAgcXBtYXg9NjkgcXBzdGVwPTQgaXBfcmF0aW89MS40MCBhcT0xOjEuMDAAgAAAADRliIQAN//+9vD+BTZWBFCXEc3onTMfvxW4ujQ3vdAiDuN5tmMABMa1jgAAAwNyBesyMBavAAAADEGaJGxDf/6nhAAwIAAAAAlBnkJ4hX8AJuHeAgBMYXZjNTcuNjQuMTAxAEIgCMEYOCEQBGCMHAAAAAkBnmF0Qn8AMqAhEARgjBwhEARgjBwAAAAJAZ5jakJ/ADKhIRAEYIwcAAAAEkGaaEmoQWiZTAhv//6nhAAwISEQBGCMHCEQBGCMHAAAAAtBnoZFESwr/wAm4SEQBGCMHAAAAAkBnqV0Qn8AMqEhEARgjBwhEARgjBwAAAAJAZ6nakJ/ADKgIRAEYIwcAAAAEkGarEmoQWyZTAhv//6nhAAwICEQBGCMHCEQBGCMHAAAAAtBnspFFSwr/wAm4SEQBGCMHCEQBGCMHAAAAAkBnul0Qn8AMqAhEARgjBwAAAAJAZ7rakJ/ADKgIRAEYIwcIRAEYIwcAAAAEkGa8EmoQWyZTAhv//6nhAAwISEQBGCMHAAAAAtBnw5FFSwr/wAm4SEQBGCMHCEQBGCMHAAAAAkBny10Qn8AMqEhEARgjBwAAAAJAZ8vakJ/ADKgIRAEYIwcIRAEYIwcAAAAEkGbNEmoQWyZTAhv//6nhAAwICEQBGCMHCEQBGCMHAAAAAtBn1JFFSwr/wAm4SEQBGCMHAAAAAkBn3F0Qn8AMqAhEARgjBwhEARgjBwAAAAJAZ9zakJ/ADKgIRAEYIwcAAAAEkGbeEmoQWyZTAhn//6eEAC7gSEQBGCMHCEQBGCMHAAAAAtBn5ZFFSwr/wAm4CEQBGCMHAAAAAkBn7V0Qn8AMqEhEARgjBwhEARgjBwAAAAJAZ+3akJ/ADKhIRAEYIwcAAAAEkGbvEmoQWyZTAhf//6MsAC8gCEQBGCMHCEQBGCMHAAAAAtBn9pFFSwr/wAm4SEQBGCMHCEQBGCMHAAAAAkBn/l0Qn8AMqAhEARgjBwAAAAJAZ/7akJ/ADKhIRAEYIwcIRAEYIwcAAAAEkGb/kmoQWyZTBRMJ//98QAG9SEQBGCMHAAAAAkBnh1qQn8AMqAhEARgjBwhEARgjBwhEARgjBwhEARgjBwhEARgjBwhEARgjBwhEARgjBwAAAlUbW9vdgAAAGxtdmhkAAAAAAAAAAAAAAAAAAAD6AAABEAAAQAAAQAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAABDt0cmFrAAAAXHRraGQAAAADAAAAAAAAAAAAAAABAAAAAAAABAsAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAQAAAACQAAAAAAAkZWR0cwAAABxlbHN0AAAAAAAAAAEAAAQLAAAH0gABAAAAAAOzbWRpYQAAACBtZGhkAAAAAAAAAAAAAAAAAAB1MAAAeTdVxAAAAAAALWhkbHIAAAAAAAAAAHZpZGUAAAAAAAAAAAAAAABWaWRlb0hhbmRsZXIAAAADXm1pbmYAAAAUdm1oZAAAAAEAAAAAAAAAAAAAACRkaW5mAAAAHGRyZWYAAAAAAAAAAQAAAAx1cmwgAAAAAQAAAx5zdGJsAAAApnN0c2QAAAAAAAAAAQAAAJZhdmMxAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAQAAkABIAAAASAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGP//AAAAMGF2Y0MBZAAM/+EAF2dkAAys2UEBOwEQAAA+kAAOpgDxQplgAQAGaOvjyyLAAAAAEHBhc3AAAAABAAAAAQAAABhzdHRzAAAAAAAAAAEAAAAfAAAD6QAAABRzdHNzAAAAAAAAAAEAAAABAAABCGN0dHMAAAAAAAAAHwAAAAEAAAfSAAAAAQAAE40AAAABAAAH0gAAAAEAAAAAAAAAAQAAA+kAAAABAAATjQAAAAEAAAfSAAAAAQAAAAAAAAABAAAD6QAAAAEAABONAAAAAQAAB9IAAAABAAAAAAAAAAEAAAPpAAAAAQAAE40AAAABAAAH0gAAAAEAAAAAAAAAAQAAA+kAAAABAAATjQAAAAEAAAfSAAAAAQAAAAAAAAABAAAD6QAAAAEAABONAAAAAQAAB9IAAAABAAAAAAAAAAEAAAPpAAAAAQAAE40AAAABAAAH0gAAAAEAAAAAAAAAAQAAA+kAAAABAAALuwAAAAEAAAPpAAAAKHN0c2MAAAAAAAAAAgAAAAEAAAADAAAAAQAAAAIAAAABAAAAAQAAAJBzdHN6AAAAAAAAAAAAAAAfAAAC3AAAABAAAAANAAAADQAAAA0AAAAWAAAADwAAAA0AAAANAAAAFgAAAA8AAAANAAAADQAAABYAAAAPAAAADQAAAA0AAAAWAAAADwAAAA0AAAANAAAAFgAAAA8AAAANAAAADQAAABYAAAAPAAAADQAAAA0AAAAWAAAADQAAAIRzdGNvAAAAAAAAAB0AAAAwAAADRgAAA18AAANyAAADlAAAA6kAAAPCAAAD1QAAA/cAAAQSAAAEJQAABD4AAARaAAAEdQAABIgAAAShAAAEwwAABNgAAATxAAAFBAAABSYAAAU7AAAFVAAABWcAAAWJAAAFpAAABbcAAAXQAAAF7AAABEN0cmFrAAAAXHRraGQAAAADAAAAAAAAAAAAAAACAAAAAAAABEAAAAAAAAAAAAAAAAEBAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAkZWR0cwAAABxlbHN0AAAAAAAAAAEAAARAAAAAAAABAAAAAAO7bWRpYQAAACBtZGhkAAAAAAAAAAAAAAAAAAC7gAAAzABVxAAAAAAALWhkbHIAAAAAAAAAAHNvdW4AAAAAAAAAAAAAAABTb3VuZEhhbmRsZXIAAAADZm1pbmYAAAAQc21oZAAAAAAAAAAAAAAAJGRpbmYAAAAcZHJlZgAAAAAAAAABAAAADHVybCAAAAABAAADKnN0YmwAAABqc3RzZAAAAAAAAAABAAAAWm1wNGEAAAAAAAAAAQAAAAAAAAAAAAIAEAAAAAC7gAAAAAAANmVzZHMAAAAAA4CAgCUAAgAEgICAF0AVAAAAAAH0AAAACUcFgICABRGQVuUABoCAgAECAAAAGHN0dHMAAAAAAAAAAQAAADMAAAQAAAABPHN0c2MAAAAAAAAAGQAAAAEAAAACAAAAAQAAAAMAAAABAAAAAQAAAAQAAAACAAAAAQAAAAUAAAABAAAAAQAAAAYAAAACAAAAAQAAAAcAAAABAAAAAQAAAAgAAAACAAAAAQAAAAoAAAABAAAAAQAAAAsAAAACAAAAAQAAAAwAAAABAAAAAQAAAA0AAAACAAAAAQAAAA4AAAABAAAAAQAAAA8AAAACAAAAAQAAABEAAAABAAAAAQAAABIAAAACAAAAAQAAABMAAAABAAAAAQAAABQAAAACAAAAAQAAABUAAAABAAAAAQAAABYAAAACAAAAAQAAABcAAAABAAAAAQAAABgAAAACAAAAAQAAABoAAAABAAAAAQAAABsAAAACAAAAAQAAABwAAAABAAAAAQAAAB0AAAAHAAAAAQAAAOBzdHN6AAAAAAAAAAAAAAAzAAAAFwAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAABgAAAAYAAAAGAAAAhHN0Y28AAAAAAAAAHQAAAykAAANTAAADbAAAA4gAAAOjAAADtgAAA88AAAPrAAAEBgAABB8AAAQyAAAEVAAABGkAAASCAAAElQAABLcAAATSAAAE5QAABP4AAAUaAAAFNQAABUgAAAVhAAAFfQAABZgAAAWxAAAFxAAABeYAAAX5AAAAYnVkdGEAAABabWV0YQAAAAAAAAAhaGRscgAAAAAAAAAAbWRpcmFwcGwAAAAAAAAAAAAAAAAtaWxzdAAAACWpdG9vAAAAHWRhdGEAAAABAAAAAExhdmY1Ny41Ni4xMDE=';
            }
        },
        /**
         * blocks text selection attempts by the user for the given obj
         * @private
         * @param (Object) Object
         */
        blockSelection: function (dest) {
            if (dest) {

                dest.css({
                    "-webkit-touch-callout": "none",
                    /* iOS Safari */
                    "-webkit-user-select": "none",
                    /* Safari */
                    "-khtml-user-select": "none",
                    /* Konqueror HTML */
                    "-moz-user-select": "none",
                    /* Firefox */
                    "-ms-user-select": "none",
                    /* IE 11 / Edge */
                    "user-select": "none" /* Non-prefixed version */
                });
            }
            return dest;
        },
        unique: function (arr) {
            return Array.from(new Set(arr));
        },
        intersect: function (array1, array2) {
            var aA = Array.from(new Set(array1)),
                setB = new Set(array2),
                intersection = new Set(aA.filter(function (val) {
                    return setB.has(val);
                }));

            return Array.from(intersection);
        },
        roundNumber: function (value, decimals) {
            return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
        },
        /* generates a random string of <length> */
        randomId: function (length) {
            var chars = "abcdefghiklmnopqrstuvwxyz",
                charsLen = chars.length,
                len = length || 8, // default to 8 char id
                result = '',
                r,
                i;

            for (i = 0; i < len; i++) {
                r = Math.floor(Math.random() * charsLen);
                result += chars.substr(r, 1);
            }
            return result;
        },
        toAbsoluteURL: function (s) {
            var l = location,
                h, p, f, i;

            if (s == null || s == '') {
                return '';
            }

            if (/^\w+:/.test(s)) {
                return s;
            }

            h = l.protocol + '//' + l.host;
            if (s.indexOf('/') === 0) {
                return h + s;
            }

            p = l.pathname.replace(/\/[^\/]*$/, '');
            f = s.match(/\.\.\//g);
            if (f) {
                s = s.substring(f.length * 3);
                for (i = f.length; i--;) {
                    p = p.substring(0, p.lastIndexOf('/'));
                }
            }

            return h + p + '/' + s;
        },
        /**
         * strips / trims
         * @public
         * @param (String) Da string to get processed
         * @return (String) Da trimmed string
         */
        strip: function (s) {
            return s.replace(/^\s+|\s+$/g, "");
        },
        /**
         * strips / trims
         * @public
         * @param (String) Da human readable time to parse
         * @return (Integer) Absolute seconds
         */
        toSeconds: function (t) {
            var s = 0.0;
            if (typeof t != 'string') {
                return t;
            }
            if (t) {
                var p = t.split(':');
                if (p.length > 3) {
                    p = p.slice(0, 3);
                }

                for (var i = 0; i < p.length; i++) {
                    s = s * 60 + parseFloat(p[i].replace(',', '.'));
                }
            }

            return parseFloat(s);
        },
        toTimeObject: function (secs) {
            var hours = Math.floor(secs / (60 * 60)),
                divisor_for_minutes = secs % (60 * 60),
                minutes = Math.floor(divisor_for_minutes / 60),
                divisor_for_seconds = divisor_for_minutes % 60,
                seconds = Math.floor(divisor_for_seconds);

            return {
                h: hours,
                m: minutes,
                s: seconds
            };
        },
        toTimeString: function (secs, noSecs) {
            var time = this.toTimeObject(secs),
                hours = time.h,
                minutes = time.m,
                seconds = time.s;

            if (hours < 10) {
                hours = "0" + hours;
            }
            if (minutes < 10) {
                minutes = "0" + minutes;
            }
            if (seconds < 10) {
                seconds = "0" + seconds;
            }
            return (noSecs === true) ? hours + ':' + minutes : hours + ':' + minutes + ':' + seconds;
        },
        /**
         * script that allows fetching a cached/uncached script
         * set options to {cache: true} if you want to cache requests
         */
        getScript: function (url, options) {
            options = $.extend(options || {}, {
                dataType: "script",
                url: url
            });

            return jQuery.ajax(options);
        },
        getCss: function (url, onload) {
            var css = $("<link>", {
                "rel": "stylesheet",
                "type": "text/css",
                "href": url
            });

            if (typeof callback === 'function') {
                css.on('load', onload);
            }

            if (url) {
                css.appendTo('head');
            }
        },
        /**
         * replaces {}-tags with parameter equivalents
         * @public
         * @param (String) Da string to get processed
         * @param (Object) Object holding data to fill in
         * @return (String) Da parsed string
         * OBSOLETE
         parseTemplate: function (template, data, encode) {

         if (data === undefined || data.length == 0 || typeof data != 'object') return template;

         for (var i in data) {
         template = template.replace(new RegExp('%{' + i + '}', 'gi'), ((encode === true) ? window.encodeURIComponent(data[i]) : data[i]))
         }
         template = template.replace(/%{(.*?)}/gi, '');
         return template;
         },
         */

        /**
         * stretches target to fit into specified dimensions keeping aspect ratio
         * @public
         * @param (String) "fill" or "aspectratio" (default)
         * @param (Object) the Dom-Obj to scale
         * @param (Float) The maximum available width in px
         * @param (Float) The maximum available height in px
         * @param (Float) A forced assumed with of the target object (optional)
         * @param (Float) A forced assumed height of the target object (optional)
         * @return (Boolean) Returns TRUE if <target> was resized in any way, otherwise FALSE
         */
        stretch: function (stretchStyle, target, owid, ohei, twf, thf) {
            var unit = "%",
                wid = owid,
                hei = ohei;

            if (!target) {
                return false;
            }

            if ((target instanceof $) === false) {
                target = $(target);
            }

            if (!target.attr("data-od-width")) {
                target.attr("data-od-width", target.width());
            }
            if (!target.attr("data-od-height")) {
                target.attr("data-od-height", target.height());
            }

            var tw = (twf !== undefined) ? twf : target.attr("data-od-width"),
                th = (thf !== undefined) ? thf : target.attr("data-od-height"),
                xsc = (wid / tw),
                ysc = (hei / th),
                rw = wid,
                rh = hei;

            // fill area
            switch (stretchStyle) {
                case 'none':
                    wid = tw;
                    hei = th;
                    unit = "px";

                    break;

                case 'fill':
                    if (xsc > ysc) {
                        rw = tw * xsc;
                        rh = th * xsc;
                    } else if (xsc < ysc) {
                        rw = tw * ysc;
                        rh = th * ysc;
                    }
                    wid = $p.utils.roundNumber((rw / wid) * 100, 0);
                    hei = $p.utils.roundNumber((rh / hei) * 100, 0);
                    unit = "%";
                    break;

                case 'aspectratio':
                default:
                    // scale, keep aspect ratio
                    if (xsc > ysc) {
                        rw = tw * ysc;
                        rh = th * ysc;
                    } else if (xsc < ysc) {
                        rw = tw * xsc;
                        rh = th * xsc;
                    }
                    wid = $p.utils.roundNumber((rw / wid) * 100, 0);
                    hei = $p.utils.roundNumber((rh / hei) * 100, 0);
                    unit = "%";
                    break;
            }

            if (wid === 0 || hei === 0) {
                return false;
            }

            target.css({
                'margin': 0,
                'padding': 0,
                'width': wid + unit,
                'height': hei + unit,
                'left': (((unit === "%") ? 100 : owid) - wid) / 2 + unit,
                'top': (((unit === "%") ? 100 : ohei) - hei) / 2 + unit
            });

            if (target.attr("data-od-width") != target.width() || target.attr("data-od-height") != target.height()) {
                return true;
            }

            return false;
        },
        // parseUri 1.2.2
        // (c) Steven Levithan <stevenlevithan.com>
        // MIT License
        parseUri: function (str) {
            var o = {
                    strictMode: false,
                    key: ["source", "protocol", "authority", "userInfo", "user", "password", "host", "port", "relative", "path", "directory", "file", "query", "anchor"],
                    q: {
                        name: "queryKey",
                        parser: /(?:^|&)([^&=]*)=?([^&]*)/g
                    },
                    parser: {
                        strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
                        loose: /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
                    }
                },
                m = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
                uri = {},
                i = 14;

            while (i--) {
                uri[o.key[i]] = m[i] || "";
            }

            uri[o.q.name] = {};
            uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
                if ($1) {
                    uri[o.q.name][$1] = $2;
                }
            });

            return uri;
        },
        // usage: log('inside coolFunc',this,arguments);
        // http://paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
        log: function () {

            if (this.logging === false) {
                return;
            }

            this.history = this.history || []; // store logs to an array for reference
            this.history.push(arguments);
            if (window.console) {
                console.log(Array.prototype.slice.call(arguments));
            }
        },
        copyToClipboard: function (value) {
            var element = document.createElement('textarea'),
                result = false;

            element.value = value;
            document.body.appendChild(element);
            element.focus();
            element.setSelectionRange(0, element.value.length);

            try {
                result = document.execCommand('copy');
            }
            catch(e){}
            // cleanup
            document.body.removeChild(element);

            return result;
        },
        cleanResponse: function (responseText, type) {
            var data = false;

            switch (type) {
                case 'html':
                case 'xml':
                    // Create the xml document from the responseText string.
                    data = new DOMParser();
                    data = data.parseFromString(responseText, "text/xml");
                    break;

                case 'json':
                    data = responseText;
                    if (typeof data == 'string') {
                        data = JSON.parse(data);
                    }
                    break;
                default:
                    data = responseText;
                    break;

            }
            return data;
        },
        versionCompare: function (installed, required) {
            var installedArr = String(installed).split('.').map(Number),
                requiredArr = String(required).split('.').map(Number),
                insVal, reqVal;

            if(installedArr.some(isNaN) || requiredArr.some(isNaN)){
                return false;
            }

            for (var i = 0; i < 3; i++) {
                reqVal = requiredArr[i];
                insVal = installedArr[i] === undefined ? 0 : installedArr[i];

                if(insVal > reqVal){
                    return true;
                }
                if(reqVal > insVal){
                    return false;
                }
            }

            return true;        
        },
        /**
         * replaces {}-tags with parameter equivalents
         * @public
         * @param (String) Da string to get processed
         * @param (Object) Object holding data to fill in
         * @return (String) Da parsed string
         */
        parseTemplate: function (template, data, encode) {
            var tpl = template,
            i;

            if (data === undefined || data.length == 0 || typeof data !== 'object') {
                return tpl;
            }

            for (i in data) {
                if(data.hasOwnProperty(i)){
                    tpl = tpl.replace(new RegExp('%{' + this.regExpEsc(i) + '}', 'gi'), ((encode === true) ? window.encodeURIComponent(data[i]) : data[i]));
                }
            }
            
            tpl = tpl.replace(/%{(.*?)}/gi, '');
            return tpl;
        },
        i18n: function (str, customData) {
            var regexp = /%{([^}]+)}/g,
                messages = $.extend({}, projekktorMessages, customData),
                text,
                msg = '';

            while (text = regexp.exec(str)) {
                msg = messages.hasOwnProperty(text[1]) ? messages[text[1]] : text[1];
                str = str.replace(new RegExp('%{' + $p.utils.regExpEsc(text[1]) + '}', 'gi'), msg);
            }

            return str;
        },
        errorMessage: function (errorCode, pp) {
            var customData = {
                title: pp.getConfig('title'),
                version: pp.getVersion()
            };

            return this.i18n("%{error" + errorCode + "}", customData);
        },
        regExpEsc: function (s) {
            return s.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        },
        parseMimeType: function (mimeType) {
            var type,
                subtype,
                params,
                parameters,
                tokenRegexp = /^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$/,
                contentTypeRegex = /^(.*?)\/(.*?)([\t ]*;.*)?$/,
                parameterPattern = /; *([!#$%&'*+.^_`|~0-9A-Za-z-]+) *= *("(?:[\u000b\u0020\u0021\u0023-\u005b\u005d-\u007e\u0080-\u00ff]|\\[\u000b\u0020-\u00ff])*"|[!#$%&'*+.^_`|~0-9A-Za-z-]+) */g,
                quotedStringRegexp = /"(?:[\t \x21\x23-\x5B\x5D-\x7E\x80-\xFF]|(?:\\[\t \x21-\x7E\x80-\xFF]))*"/,
                qescRegExp = /\\([\u000b\u0020-\u00ff])/g,
                contentTypeMatch,
                paramMatch,
                key,
                value;

            if (!mimeType) {
                return null;
            }

            contentTypeMatch = contentTypeRegex.exec(mimeType);

            if (contentTypeMatch) {

                type = contentTypeMatch[1];
                subtype = contentTypeMatch[2];
                params = contentTypeMatch[3];

                if (tokenRegexp.test(type) && tokenRegexp.test(subtype)) {

                    parameters = {};

                    while ((paramMatch = parameterPattern.exec(params))) {
                        key = paramMatch[1];
                        value = paramMatch[2];

                        if (quotedStringRegexp.test(value)) {
                            value = value
                                .substr(1, value.length - 2)
                                .replace(qescRegExp, "$1");
                        }

                        if (key) {
                            parameters[key.toLowerCase()] = value;
                        }
                    }
                    return {
                        type: type,
                        subtype: subtype,
                        parameters: parameters
                    };

                }
                return null;
            }
            return null;
        },
        /**
         * serializes a simple object to a JSON formatted string.
         * Note: stringify() is different from jQuery.serialize() which URLEncodes form elements
         * CREDITS: http://blogs.sitepointstatic.com/examples/tech/json-serialization/json-serialization.js
         */
        stringify: function (obj) {
            if ("JSON" in window) {
                return JSON.stringify(obj);
            }

            var t = typeof (obj);
            if (t != "object" || obj === null) {
                // simple data type
                if (t == "string") {
                    obj = '"' + obj + '"';
                }

                return String(obj);
            } else {
                // recourse array or object
                var n, v, json = [],
                    arr = (obj && obj.constructor == Array);

                for (n in obj) {
                    if (obj.hasOwnProperty(n)) {
                        v = obj[n];
                        t = typeof (v);
                        if (obj.hasOwnProperty(n)) {
                            if (t == "string") {
                                v = '"' + v + '"';
                            } else if (t == "object" && v !== null) {
                                v = $p.utils.stringify(v);
                            }

                            json.push((arr ? "" : '"' + n + '":') + String(v));
                        }
                    }
                }

                return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
            }
        },
        /*
         * Check if object has any of given properties/methods
         * and returns the name of first existing one
         * otherwise returns false.
         * If the prefix is set then method will make a second pass
         * to check all of the prefixed versions of given properties/methods
         */
        hasProp: function (obj, prop, prefix, hasOwn) {
            // add prefixed prop version(s)
            if (this.is(prefix, 'string')) {
                prop = this.addPrefix(prop, prefix, false, true);
            }

            if (this.is(prop, 'string')) {
                if (!!(prop in obj) && (!!hasOwn ? obj.hasOwnProperty(prop) : true)) {
                    return prop;
                }
            } else if ($.isArray(prop)) {
                for (var i = 0; i < prop.length; i++) {
                    if (!!(prop[i] in obj) && (!!hasOwn ? obj.hasOwnProperty(prop[i]) : true)) {
                        return prop[i];
                    }
                }
            }
            return false;
        },
        /*
         *
         * @param {string or array} obj - string or array of strings to prefix
         * @param {string} prefix
         * @param (boolean) replace - if the obj is array should the prefixed strings be replaced or added to existing ones
         * @param {boolean} capitalize - should be the first letter of prefixed string capitalized (to preserve camelCase)
         * @returns {string or array} - returns prefixed string or array of strings
         */
        addPrefix: function (obj, prefix, replace, capitalize) {
            if (this.is(obj, 'string') && this.is(prefix, 'string')) {
                if (!!replace) {
                    return prefix + (!!capitalize ? this.ucfirst(obj) : obj);
                } else {
                    return [obj, prefix + (!!capitalize ? this.ucfirst(obj) : obj)];
                }
            } else if ($.isArray(obj) && this.is(prefix, 'string')) {
                var initLength = obj.length;
                for (var i = 0; i < initLength; i++) {
                    if (!!replace) {
                        obj[i] = prefix + (!!capitalize ? this.ucfirst(obj[i]) : obj[i]);
                    } else {
                        obj.push(prefix + (!!capitalize ? this.ucfirst(obj[i]) : obj[i]));
                    }
                }
            }
            return obj;
        },
        /**
         * is returns a boolean for if typeof obj is exactly type.
         * CREDITS: Modernizr
         */
        is: function (obj, type) {
            return typeof obj === type;
        },
        /**
         * contains returns a boolean for if substr is found within str
         * CREDITS: Modernizr
         */
        contains: function (str, substr) {
            return !!~('' + str).indexOf(substr);
        },
        /*
         * Returns a string with the first character of string capitalized
         * @param {string} str
         * @returns {string or boolean}
         */
        ucfirst: function (str) {
            if (this.is(str, 'string')) {
                return str[0].toUpperCase() + str.substr(1);
            }
            return false;
        },
        logging: false
    };

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2015 Radosław Włodkowski, radoslaw@wlodkowski.net
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 *
 */

(function(window, document, $, $p){

    "use strict";
    
$p.userAgent = (function () {

   /*
    * Modified version of:
    * UAParser.js v0.7.9
    * Lightweight JavaScript-based User-Agent string parser
    * https://github.com/faisalman/ua-parser-js
    *
    * Copyright © 2012-2015 Faisal Salman <fyzlman@gmail.com>
    * Dual licensed under GPLv2 & MIT
    */
    var UAParser = new (function (window, undefined) {

        'use strict';

        //////////////
        // Constants
        /////////////


        var LIBVERSION  = '0.7.9',
            EMPTY       = '',
            UNKNOWN     = '?',
            FUNC_TYPE   = 'function',
            UNDEF_TYPE  = 'undefined',
            OBJ_TYPE    = 'object',
            STR_TYPE    = 'string',
            MAJOR       = 'major', // deprecated
            MODEL       = 'model',
            NAME        = 'name',
            TYPE        = 'type',
            VENDOR      = 'vendor',
            VERSION     = 'version',
            ARCHITECTURE= 'architecture',
            CONSOLE     = 'console',
            MOBILE      = 'mobile',
            TABLET      = 'tablet',
            SMARTTV     = 'smarttv',
            WEARABLE    = 'wearable',
            EMBEDDED    = 'embedded';


        ///////////
        // Helper
        //////////


        var util = {
            extend : function (regexes, extensions) {
                for (var i in extensions) {
                    if ("browser cpu device engine os".indexOf(i) !== -1 && extensions[i].length % 2 === 0) {
                        regexes[i] = extensions[i].concat(regexes[i]);
                    }
                }
                return regexes;
            },
            has : function (str1, str2) {
              if (typeof str1 === "string") {
                return str2.toLowerCase().indexOf(str1.toLowerCase()) !== -1;
              } else {
                return false;
              }
            },
            lowerize : function (str) {
                return str.toLowerCase();
            },
            major : function (version) {
                return typeof(version) === STR_TYPE ? version.split(".")[0] : undefined;
            }
        };


        ///////////////
        // Map helper
        //////////////


        var mapper = {

            rgx : function () {

                var result, i = 0, j, k, p, q, matches, match, args = arguments;

                // loop through all regexes maps
                while (i < args.length && !matches) {

                    var regex = args[i],       // even sequence (0,2,4,..)
                        props = args[i + 1];   // odd sequence (1,3,5,..)

                    // construct object barebones
                    if (typeof result === UNDEF_TYPE) {
                        result = {};
                        for (p in props) {
                            q = props[p];
                            if (typeof q === OBJ_TYPE) {
                                result[q[0]] = undefined;
                            } else {
                                result[q] = undefined;
                            }
                        }
                    }

                    // try matching uastring with regexes
                    j = k = 0;
                    while (j < regex.length && !matches) {
                        matches = regex[j++].exec(this.getUA());
                        if (!!matches) {
                            for (p = 0; p < props.length; p++) {
                                match = matches[++k];
                                q = props[p];
                                // check if given property is actually array
                                if (typeof q === OBJ_TYPE && q.length > 0) {
                                    if (q.length == 2) {
                                        if (typeof q[1] == FUNC_TYPE) {
                                            // assign modified match
                                            result[q[0]] = q[1].call(this, match);
                                        } else {
                                            // assign given value, ignore regex match
                                            result[q[0]] = q[1];
                                        }
                                    } else if (q.length == 3) {
                                        // check whether function or regex
                                        if (typeof q[1] === FUNC_TYPE && !(q[1].exec && q[1].test)) {
                                            // call function (usually string mapper)
                                            result[q[0]] = match ? q[1].call(this, match, q[2]) : undefined;
                                        } else {
                                            // sanitize match using given regex
                                            result[q[0]] = match ? match.replace(q[1], q[2]) : undefined;
                                        }
                                    } else if (q.length == 4) {
                                            result[q[0]] = match ? q[3].call(this, match.replace(q[1], q[2])) : undefined;
                                    }
                                } else {
                                    result[q] = match ? match : undefined;
                                }
                            }
                        }
                    }
                    i += 2;
                }
                return result;
            },

            str : function (str, map) {

                for (var i in map) {
                    // check if array
                    if (typeof map[i] === OBJ_TYPE && map[i].length > 0) {
                        for (var j = 0; j < map[i].length; j++) {
                            if (util.has(map[i][j], str)) {
                                return (i === UNKNOWN) ? undefined : i;
                            }
                        }
                    } else if (util.has(map[i], str)) {
                        return (i === UNKNOWN) ? undefined : i;
                    }
                }
                return str;
            }
        };


        ///////////////
        // String map
        //////////////


        var maps = {

            browser : {
                oldsafari : {
                    version : {
                        '1.0'   : '/8',
                        '1.2'   : '/1',
                        '1.3'   : '/3',
                        '2.0'   : '/412',
                        '2.0.2' : '/416',
                        '2.0.3' : '/417',
                        '2.0.4' : '/419',
                        '?'     : '/'
                    }
                }
            },

            device : {
                amazon : {
                    model : {
                        'Fire Phone' : ['SD', 'KF']
                    }
                },
                sprint : {
                    model : {
                        'Evo Shift 4G' : '7373KT'
                    },
                    vendor : {
                        'HTC'       : 'APA',
                        'Sprint'    : 'Sprint'
                    }
                }
            },

            os : {
                windows : {
                    version : {
                        'ME'        : '4.90',
                        'NT 3.11'   : 'NT3.51',
                        'NT 4.0'    : 'NT4.0',
                        '2000'      : 'NT 5.0',
                        'XP'        : ['NT 5.1', 'NT 5.2'],
                        'Vista'     : 'NT 6.0',
                        '7'         : 'NT 6.1',
                        '8'         : 'NT 6.2',
                        '8.1'       : 'NT 6.3',
                        '10'        : ['NT 6.4', 'NT 10.0'],
                        'RT'        : 'ARM'
                    }
                }
            }
        };


        //////////////
        // Regex map
        /////////////


        var regexes = {

            browser : [[

                // Presto based
                /(opera\smini)\/([\w\.-]+)/i,                                       // Opera Mini
                /(opera\s[mobiletab]+).+version\/([\w\.-]+)/i,                      // Opera Mobi/Tablet
                /(opera).+version\/([\w\.]+)/i,                                     // Opera > 9.80
                /(opera)[\/\s]+([\w\.]+)/i                                          // Opera < 9.80

                ], [NAME, VERSION], [

                /\s(opr)\/([\w\.]+)/i                                               // Opera Webkit
                ], [[NAME, 'Opera'], VERSION], [

                // Mixed
                /(kindle)\/([\w\.]+)/i,                                             // Kindle
                /(lunascape|maxthon|netfront|jasmine|blazer)[\/\s]?([\w\.]+)*/i,
                                                                                    // Lunascape/Maxthon/Netfront/Jasmine/Blazer

                // Trident based
                /(avant\s|iemobile|slim|baidu)(?:browser)?[\/\s]?([\w\.]*)/i,
                                                                                    // Avant/IEMobile/SlimBrowser/Baidu
                /(?:ms|\()(ie)\s([\w\.]+)/i,                                        // Internet Explorer

                // Webkit/KHTML based
                /(rekonq)\/([\w\.]+)*/i,                                            // Rekonq
                /(chromium|flock|rockmelt|midori|epiphany|silk|skyfire|ovibrowser|bolt|iron|vivaldi|iridium)\/([\w\.-]+)/i
                                                                                    // Chromium/Flock/RockMelt/Midori/Epiphany/Silk/Skyfire/Bolt/Iron/Iridium
                ], [NAME, VERSION], [

                /(trident).+rv[:\s]([\w\.]+).+like\sgecko/i                         // IE11
                ], [[NAME, 'IE'], VERSION], [

                /(edge)\/((\d+)?[\w\.]+)/i                                          // Microsoft Edge
                ], [NAME, VERSION], [

                /(yabrowser)\/([\w\.]+)/i                                           // Yandex
                ], [[NAME, 'Yandex'], VERSION], [

                /(comodo_dragon)\/([\w\.]+)/i                                       // Comodo Dragon
                ], [[NAME, /_/g, ' '], VERSION], [

                /(chrome|omniweb|arora|[tizenoka]{5}\s?browser)\/v?([\w\.]+)/i,
                                                                                    // Chrome/OmniWeb/Arora/Tizen/Nokia
                /(qqbrowser)[\/\s]?([\w\.]+)/i
                                                                                    // QQBrowser
                ], [NAME, VERSION], [

                /(uc\s?browser)[\/\s]?([\w\.]+)/i,
                /ucweb.+(ucbrowser)[\/\s]?([\w\.]+)/i,
                /JUC.+(ucweb)[\/\s]?([\w\.]+)/i
                                                                                    // UCBrowser
                ], [[NAME, 'UCBrowser'], VERSION], [

                /(dolfin)\/([\w\.]+)/i                                              // Dolphin
                ], [[NAME, 'Dolphin'], VERSION], [

                /((?:android.+)crmo|crios)\/([\w\.]+)/i                             // Chrome for Android/iOS
                ], [[NAME, 'Chrome'], VERSION], [

                /XiaoMi\/MiuiBrowser\/([\w\.]+)/i                                   // MIUI Browser
                ], [VERSION, [NAME, 'MIUI Browser']], [

                /android.+version\/([\w\.]+)\s+(?:mobile\s?safari|safari)/i         // Android Browser
                ], [VERSION, [NAME, 'Android Browser']], [

                /FBAV\/([\w\.]+);/i                                                 // Facebook App for iOS
                ], [VERSION, [NAME, 'Facebook']], [

                /version\/([\w\.]+).+?mobile\/\w+\s(safari)/i                       // Mobile Safari
                ], [VERSION, [NAME, 'Mobile Safari']], [

                /version\/([\w\.]+).+?(mobile\s?safari|safari)/i                    // Safari & Safari Mobile
                ], [VERSION, NAME], [

                /webkit.+?(mobile\s?safari|safari)(\/[\w\.]+)/i                     // Safari < 3.0
                ], [NAME, [VERSION, mapper.str, maps.browser.oldsafari.version]], [

                /(konqueror)\/([\w\.]+)/i,                                          // Konqueror
                /(webkit|khtml)\/([\w\.]+)/i
                ], [NAME, VERSION], [

                // Gecko based
                /(navigator|netscape)\/([\w\.-]+)/i                                 // Netscape
                ], [[NAME, 'Netscape'], VERSION], [
                /fxios\/([\w\.-]+)/i                                                // Firefox for iOS
                ], [VERSION, [NAME, 'Firefox']], [
                /(swiftfox)/i,                                                      // Swiftfox
                /(icedragon|iceweasel|camino|chimera|fennec|maemo\sbrowser|minimo|conkeror)[\/\s]?([\w\.\+]+)/i,
                                                                                    // IceDragon/Iceweasel/Camino/Chimera/Fennec/Maemo/Minimo/Conkeror
                /(firefox|seamonkey|k-meleon|icecat|iceape|firebird|phoenix)\/([\w\.-]+)/i,
                                                                                    // Firefox/SeaMonkey/K-Meleon/IceCat/IceApe/Firebird/Phoenix
                /(mozilla)\/([\w\.]+).+rv\:.+gecko\/\d+/i,                          // Mozilla

                // Other
                /(polaris|lynx|dillo|icab|doris|amaya|w3m|netsurf)[\/\s]?([\w\.]+)/i,
                                                                                    // Polaris/Lynx/Dillo/iCab/Doris/Amaya/w3m/NetSurf
                /(links)\s\(([\w\.]+)/i,                                            // Links
                /(gobrowser)\/?([\w\.]+)*/i,                                        // GoBrowser
                /(ice\s?browser)\/v?([\w\._]+)/i,                                   // ICE Browser
                /(mosaic)[\/\s]([\w\.]+)/i                                          // Mosaic
                ], [NAME, VERSION]

                /* /////////////////////
                // Media players BEGIN
                ////////////////////////
                , [
                /(apple(?:coremedia|))\/((\d+)[\w\._]+)/i,                          // Generic Apple CoreMedia
                /(coremedia) v((\d+)[\w\._]+)/i
                ], [NAME, VERSION], [
                /(aqualung|lyssna|bsplayer)\/((\d+)?[\w\.-]+)/i                     // Aqualung/Lyssna/BSPlayer
                ], [NAME, VERSION], [
                /(ares|ossproxy)\s((\d+)[\w\.-]+)/i                                 // Ares/OSSProxy
                ], [NAME, VERSION], [
                /(audacious|audimusicstream|amarok|bass|core|dalvik|gnomemplayer|music on console|nsplayer|psp-internetradioplayer|videos)\/((\d+)[\w\.-]+)/i,
                                                                                    // Audacious/AudiMusicStream/Amarok/BASS/OpenCORE/Dalvik/GnomeMplayer/MoC
                                                                                    // NSPlayer/PSP-InternetRadioPlayer/Videos
                /(clementine|music player daemon)\s((\d+)[\w\.-]+)/i,               // Clementine/MPD
                /(lg player|nexplayer)\s((\d+)[\d\.]+)/i,
                /player\/(nexplayer|lg player)\s((\d+)[\w\.-]+)/i                   // NexPlayer/LG Player
                ], [NAME, VERSION], [
                /(nexplayer)\s((\d+)[\w\.-]+)/i                                     // Nexplayer
                ], [NAME, VERSION], [
                /(flrp)\/((\d+)[\w\.-]+)/i                                          // Flip Player
                ], [[NAME, 'Flip Player'], VERSION], [
                /(fstream|nativehost|queryseekspider|ia-archiver|facebookexternalhit)/i
                                                                                    // FStream/NativeHost/QuerySeekSpider/IA Archiver/facebookexternalhit
                ], [NAME], [
                /(gstreamer) souphttpsrc (?:\([^\)]+\)){0,1} libsoup\/((\d+)[\w\.-]+)/i
                                                                                    // Gstreamer
                ], [NAME, VERSION], [
                /(htc streaming player)\s[\w_]+\s\/\s((\d+)[\d\.]+)/i,              // HTC Streaming Player
                /(java|python-urllib|python-requests|wget|libcurl)\/((\d+)[\w\.-_]+)/i,
                                                                                    // Java/urllib/requests/wget/cURL
                /(lavf)((\d+)[\d\.]+)/i                                             // Lavf (FFMPEG)
                ], [NAME, VERSION], [
                /(htc_one_s)\/((\d+)[\d\.]+)/i                                      // HTC One S
                ], [[NAME, /_/g, ' '], VERSION], [
                /(mplayer)(?:\s|\/)(?:(?:sherpya-){0,1}svn)(?:-|\s)(r\d+(?:-\d+[\w\.-]+){0,1})/i
                                                                                    // MPlayer SVN
                ], [NAME, VERSION], [
                /(mplayer)(?:\s|\/|[unkow-]+)((\d+)[\w\.-]+)/i                      // MPlayer
                ], [NAME, VERSION], [
                /(mplayer)/i,                                                       // MPlayer (no other info)
                /(yourmuze)/i,                                                      // YourMuze
                /(media player classic|nero showtime)/i                             // Media Player Classic/Nero ShowTime
                ], [NAME], [
                /(nero (?:home|scout))\/((\d+)[\w\.-]+)/i                           // Nero Home/Nero Scout
                ], [NAME, VERSION], [
                /(nokia\d+)\/((\d+)[\w\.-]+)/i                                      // Nokia
                ], [NAME, VERSION], [
                /\s(songbird)\/((\d+)[\w\.-]+)/i                                    // Songbird/Philips-Songbird
                ], [NAME, VERSION], [
                /(winamp)3 version ((\d+)[\w\.-]+)/i,                               // Winamp
                /(winamp)\s((\d+)[\w\.-]+)/i,
                /(winamp)mpeg\/((\d+)[\w\.-]+)/i
                ], [NAME, VERSION], [
                /(ocms-bot|tapinradio|tunein radio|unknown|winamp|inlight radio)/i  // OCMS-bot/tap in radio/tunein/unknown/winamp (no other info)
                                                                                    // inlight radio
                ], [NAME], [
                /(quicktime|rma|radioapp|radioclientapplication|soundtap|totem|stagefright|streamium)\/((\d+)[\w\.-]+)/i
                                                                                    // QuickTime/RealMedia/RadioApp/RadioClientApplication/
                                                                                    // SoundTap/Totem/Stagefright/Streamium
                ], [NAME, VERSION], [
                /(smp)((\d+)[\d\.]+)/i                                              // SMP
                ], [NAME, VERSION], [
                /(vlc) media player - version ((\d+)[\w\.]+)/i,                     // VLC Videolan
                /(vlc)\/((\d+)[\w\.-]+)/i,
                /(xbmc|gvfs|xine|xmms|irapp)\/((\d+)[\w\.-]+)/i,                    // XBMC/gvfs/Xine/XMMS/irapp
                /(foobar2000)\/((\d+)[\d\.]+)/i,                                    // Foobar2000
                /(itunes)\/((\d+)[\d\.]+)/i                                         // iTunes
                ], [NAME, VERSION], [
                /(wmplayer)\/((\d+)[\w\.-]+)/i,                                     // Windows Media Player
                /(windows-media-player)\/((\d+)[\w\.-]+)/i
                ], [[NAME, /-/g, ' '], VERSION], [
                /windows\/((\d+)[\w\.-]+) upnp\/[\d\.]+ dlnadoc\/[\d\.]+ (home media server)/i
                                                                                    // Windows Media Server
                ], [VERSION, [NAME, 'Windows']], [
                /(com\.riseupradioalarm)\/((\d+)[\d\.]*)/i                          // RiseUP Radio Alarm
                ], [NAME, VERSION], [
                /(rad.io)\s((\d+)[\d\.]+)/i,                                        // Rad.io
                /(radio.(?:de|at|fr))\s((\d+)[\d\.]+)/i
                ], [[NAME, 'rad.io'], VERSION]
                //////////////////////
                // Media players END
                ////////////////////*/

            ],

            cpu : [[

                /(?:(amd|x(?:(?:86|64)[_-])?|wow|win)64)[;\)]/i                     // AMD64
                ], [[ARCHITECTURE, 'amd64']], [

                /(ia32(?=;))/i                                                      // IA32 (quicktime)
                ], [[ARCHITECTURE, util.lowerize]], [

                /((?:i[346]|x)86)[;\)]/i                                            // IA32
                ], [[ARCHITECTURE, 'ia32']], [

                // PocketPC mistakenly identified as PowerPC
                /windows\s(ce|mobile);\sppc;/i
                ], [[ARCHITECTURE, 'arm']], [

                /((?:ppc|powerpc)(?:64)?)(?:\smac|;|\))/i                           // PowerPC
                ], [[ARCHITECTURE, /ower/, '', util.lowerize]], [

                /(sun4\w)[;\)]/i                                                    // SPARC
                ], [[ARCHITECTURE, 'sparc']], [

                /((?:avr32|ia64(?=;))|68k(?=\))|arm(?:64|(?=v\d+;))|(?=atmel\s)avr|(?:irix|mips|sparc)(?:64)?(?=;)|pa-risc)/i
                                                                                    // IA64, 68K, ARM/64, AVR/32, IRIX/64, MIPS/64, SPARC/64, PA-RISC
                ], [[ARCHITECTURE, util.lowerize]]
            ],

            device : [[

                /\((ipad|playbook);[\w\s\);-]+(rim|apple)/i                         // iPad/PlayBook
                ], [MODEL, VENDOR, [TYPE, TABLET]], [

                /applecoremedia\/[\w\.]+ \((ipad)/                                  // iPad
                ], [MODEL, [VENDOR, 'Apple'], [TYPE, TABLET]], [

                /(apple\s{0,1}tv)/i                                                 // Apple TV
                ], [[MODEL, 'Apple TV'], [VENDOR, 'Apple']], [

                /(archos)\s(gamepad2?)/i,                                           // Archos
                /(hp).+(touchpad)/i,                                                // HP TouchPad
                /(kindle)\/([\w\.]+)/i,                                             // Kindle
                /\s(nook)[\w\s]+build\/(\w+)/i,                                     // Nook
                /(dell)\s(strea[kpr\s\d]*[\dko])/i                                  // Dell Streak
                ], [VENDOR, MODEL, [TYPE, TABLET]], [

                /(kf[A-z]+)\sbuild\/[\w\.]+.*silk\//i                               // Kindle Fire HD
                ], [MODEL, [VENDOR, 'Amazon'], [TYPE, TABLET]], [
                /(sd|kf)[0349hijorstuw]+\sbuild\/[\w\.]+.*silk\//i                  // Fire Phone
                ], [[MODEL, mapper.str, maps.device.amazon.model], [VENDOR, 'Amazon'], [TYPE, MOBILE]], [

                /\((ip[honed|\s\w*]+);.+(apple)/i                                   // iPod/iPhone
                ], [MODEL, VENDOR, [TYPE, MOBILE]], [
                /\((ip[honed|\s\w*]+);/i                                            // iPod/iPhone
                ], [MODEL, [VENDOR, 'Apple'], [TYPE, MOBILE]], [

                /(blackberry)[\s-]?(\w+)/i,                                         // BlackBerry
                /(blackberry|benq|palm(?=\-)|sonyericsson|acer|asus|dell|huawei|meizu|motorola|polytron)[\s_-]?([\w-]+)*/i,
                                                                                    // BenQ/Palm/Sony-Ericsson/Acer/Asus/Dell/Huawei/Meizu/Motorola/Polytron
                /(hp)\s([\w\s]+\w)/i,                                               // HP iPAQ
                /(asus)-?(\w+)/i                                                    // Asus
                ], [VENDOR, MODEL, [TYPE, MOBILE]], [
                /\(bb10;\s(\w+)/i                                                   // BlackBerry 10
                ], [MODEL, [VENDOR, 'BlackBerry'], [TYPE, MOBILE]], [
                                                                                    // Asus Tablets
                /android.+(transfo[prime\s]{4,10}\s\w+|eeepc|slider\s\w+|nexus 7)/i
                ], [MODEL, [VENDOR, 'Asus'], [TYPE, TABLET]], [

                /(sony)\s(tablet\s[ps])\sbuild\//i,                                  // Sony
                /(sony)?(?:sgp.+)\sbuild\//i
                ], [[VENDOR, 'Sony'], [MODEL, 'Xperia Tablet'], [TYPE, TABLET]], [
                /(?:sony)?(?:(?:(?:c|d)\d{4})|(?:so[-l].+))\sbuild\//i
                ], [[VENDOR, 'Sony'], [MODEL, 'Xperia Phone'], [TYPE, MOBILE]], [

                /\s(ouya)\s/i,                                                      // Ouya
                /(nintendo)\s([wids3u]+)/i                                          // Nintendo
                ], [VENDOR, MODEL, [TYPE, CONSOLE]], [

                /android.+;\s(shield)\sbuild/i                                      // Nvidia
                ], [MODEL, [VENDOR, 'Nvidia'], [TYPE, CONSOLE]], [

                /(playstation\s[3portablevi]+)/i                                    // Playstation
                ], [MODEL, [VENDOR, 'Sony'], [TYPE, CONSOLE]], [

                /(sprint\s(\w+))/i                                                  // Sprint Phones
                ], [[VENDOR, mapper.str, maps.device.sprint.vendor], [MODEL, mapper.str, maps.device.sprint.model], [TYPE, MOBILE]], [

                /(lenovo)\s?(S(?:5000|6000)+(?:[-][\w+]))/i                         // Lenovo tablets
                ], [VENDOR, MODEL, [TYPE, TABLET]], [

                /(htc)[;_\s-]+([\w\s]+(?=\))|\w+)*/i,                               // HTC
                /(zte)-(\w+)*/i,                                                    // ZTE
                /(alcatel|geeksphone|huawei|lenovo|nexian|panasonic|(?=;\s)sony)[_\s-]?([\w-]+)*/i
                                                                                    // Alcatel/GeeksPhone/Huawei/Lenovo/Nexian/Panasonic/Sony
                ], [VENDOR, [MODEL, /_/g, ' '], [TYPE, MOBILE]], [

                /(nexus\s9)/i                                                       // HTC Nexus 9
                ], [MODEL, [VENDOR, 'HTC'], [TYPE, TABLET]], [

                /[\s\(;](xbox(?:\sone)?)[\s\);]/i                                   // Microsoft Xbox
                ], [MODEL, [VENDOR, 'Microsoft'], [TYPE, CONSOLE]], [
                /(kin\.[onetw]{3})/i                                                // Microsoft Kin
                ], [[MODEL, /\./g, ' '], [VENDOR, 'Microsoft'], [TYPE, MOBILE]], [

                                                                                    // Motorola
                /\s(milestone|droid(?:[2-4x]|\s(?:bionic|x2|pro|razr))?(:?\s4g)?)[\w\s]+build\//i,
                /mot[\s-]?(\w+)*/i,
                /(XT\d{3,4}) build\//i
                ], [MODEL, [VENDOR, 'Motorola'], [TYPE, MOBILE]], [
                /android.+\s(mz60\d|xoom[\s2]{0,2})\sbuild\//i
                ], [MODEL, [VENDOR, 'Motorola'], [TYPE, TABLET]], [

                /android.+((sch-i[89]0\d|shw-m380s|gt-p\d{4}|gt-n8000|sgh-t8[56]9|nexus 10))/i,
                /((SM-T\w+))/i
                ], [[VENDOR, 'Samsung'], MODEL, [TYPE, TABLET]], [                  // Samsung
                /((s[cgp]h-\w+|gt-\w+|galaxy\snexus|sm-n900))/i,
                /(sam[sung]*)[\s-]*(\w+-?[\w-]*)*/i,
                /sec-((sgh\w+))/i
                ], [[VENDOR, 'Samsung'], MODEL, [TYPE, MOBILE]], [
                /(samsung);smarttv/i
                ], [VENDOR, MODEL, [TYPE, SMARTTV]], [

                /\(dtv[\);].+(aquos)/i                                              // Sharp
                ], [MODEL, [VENDOR, 'Sharp'], [TYPE, SMARTTV]], [
                /sie-(\w+)*/i                                                       // Siemens
                ], [MODEL, [VENDOR, 'Siemens'], [TYPE, MOBILE]], [

                /(maemo|nokia).*(n900|lumia\s\d+)/i,                                // Nokia
                /(nokia)[\s_-]?([\w-]+)*/i
                ], [[VENDOR, 'Nokia'], MODEL, [TYPE, MOBILE]], [

                /android\s3\.[\s\w;-]{10}(a\d{3})/i                                 // Acer
                ], [MODEL, [VENDOR, 'Acer'], [TYPE, TABLET]], [

                /android\s3\.[\s\w;-]{10}(lg?)-([06cv9]{3,4})/i                     // LG Tablet
                ], [[VENDOR, 'LG'], MODEL, [TYPE, TABLET]], [
                /(lg) netcast\.tv/i                                                 // LG SmartTV
                ], [VENDOR, MODEL, [TYPE, SMARTTV]], [
                /(nexus\s[45])/i,                                                   // LG
                /lg[e;\s\/-]+(\w+)*/i
                ], [MODEL, [VENDOR, 'LG'], [TYPE, MOBILE]], [

                /android.+(ideatab[a-z0-9\-\s]+)/i                                  // Lenovo
                ], [MODEL, [VENDOR, 'Lenovo'], [TYPE, TABLET]], [

                /linux;.+((jolla));/i                                               // Jolla
                ], [VENDOR, MODEL, [TYPE, MOBILE]], [

                /((pebble))app\/[\d\.]+\s/i                                         // Pebble
                ], [VENDOR, MODEL, [TYPE, WEARABLE]], [

                /android.+;\s(glass)\s\d/i                                          // Google Glass
                ], [MODEL, [VENDOR, 'Google'], [TYPE, WEARABLE]], [

                /android.+(\w+)\s+build\/hm\1/i,                                        // Xiaomi Hongmi 'numeric' models
                /android.+(hm[\s\-_]*note?[\s_]*(?:\d\w)?)\s+build/i,                   // Xiaomi Hongmi
                /android.+(mi[\s\-_]*(?:one|one[\s_]plus)?[\s_]*(?:\d\w)?)\s+build/i    // Xiaomi Mi
                ], [[MODEL, /_/g, ' '], [VENDOR, 'Xiaomi'], [TYPE, MOBILE]], [

                /(mobile|tablet);.+rv\:.+gecko\//i                                  // Unidentifiable
                ], [[TYPE, util.lowerize], VENDOR, MODEL]

                /*//////////////////////////
                // TODO: move to string map
                ////////////////////////////
                /(C6603)/i                                                          // Sony Xperia Z C6603
                ], [[MODEL, 'Xperia Z C6603'], [VENDOR, 'Sony'], [TYPE, MOBILE]], [
                /(C6903)/i                                                          // Sony Xperia Z 1
                ], [[MODEL, 'Xperia Z 1'], [VENDOR, 'Sony'], [TYPE, MOBILE]], [
                /(SM-G900[F|H])/i                                                   // Samsung Galaxy S5
                ], [[MODEL, 'Galaxy S5'], [VENDOR, 'Samsung'], [TYPE, MOBILE]], [
                /(SM-G7102)/i                                                       // Samsung Galaxy Grand 2
                ], [[MODEL, 'Galaxy Grand 2'], [VENDOR, 'Samsung'], [TYPE, MOBILE]], [
                /(SM-G530H)/i                                                       // Samsung Galaxy Grand Prime
                ], [[MODEL, 'Galaxy Grand Prime'], [VENDOR, 'Samsung'], [TYPE, MOBILE]], [
                /(SM-G313HZ)/i                                                      // Samsung Galaxy V
                ], [[MODEL, 'Galaxy V'], [VENDOR, 'Samsung'], [TYPE, MOBILE]], [
                /(SM-T805)/i                                                        // Samsung Galaxy Tab S 10.5
                ], [[MODEL, 'Galaxy Tab S 10.5'], [VENDOR, 'Samsung'], [TYPE, TABLET]], [
                /(SM-G800F)/i                                                       // Samsung Galaxy S5 Mini
                ], [[MODEL, 'Galaxy S5 Mini'], [VENDOR, 'Samsung'], [TYPE, MOBILE]], [
                /(SM-T311)/i                                                        // Samsung Galaxy Tab 3 8.0
                ], [[MODEL, 'Galaxy Tab 3 8.0'], [VENDOR, 'Samsung'], [TYPE, TABLET]], [
                /(R1001)/i                                                          // Oppo R1001
                ], [MODEL, [VENDOR, 'OPPO'], [TYPE, MOBILE]], [
                /(X9006)/i                                                          // Oppo Find 7a
                ], [[MODEL, 'Find 7a'], [VENDOR, 'Oppo'], [TYPE, MOBILE]], [
                /(R2001)/i                                                          // Oppo YOYO R2001
                ], [[MODEL, 'Yoyo R2001'], [VENDOR, 'Oppo'], [TYPE, MOBILE]], [
                /(R815)/i                                                           // Oppo Clover R815
                ], [[MODEL, 'Clover R815'], [VENDOR, 'Oppo'], [TYPE, MOBILE]], [
                 /(U707)/i                                                          // Oppo Find Way S
                ], [[MODEL, 'Find Way S'], [VENDOR, 'Oppo'], [TYPE, MOBILE]], [
                /(T3C)/i                                                            // Advan Vandroid T3C
                ], [MODEL, [VENDOR, 'Advan'], [TYPE, TABLET]], [
                /(ADVAN T1J\+)/i                                                    // Advan Vandroid T1J+
                ], [[MODEL, 'Vandroid T1J+'], [VENDOR, 'Advan'], [TYPE, TABLET]], [
                /(ADVAN S4A)/i                                                      // Advan Vandroid S4A
                ], [[MODEL, 'Vandroid S4A'], [VENDOR, 'Advan'], [TYPE, MOBILE]], [
                /(V972M)/i                                                          // ZTE V972M
                ], [MODEL, [VENDOR, 'ZTE'], [TYPE, MOBILE]], [
                /(i-mobile)\s(IQ\s[\d\.]+)/i                                        // i-mobile IQ
                ], [VENDOR, MODEL, [TYPE, MOBILE]], [
                /(IQ6.3)/i                                                          // i-mobile IQ IQ 6.3
                ], [[MODEL, 'IQ 6.3'], [VENDOR, 'i-mobile'], [TYPE, MOBILE]], [
                /(i-mobile)\s(i-style\s[\d\.]+)/i                                   // i-mobile i-STYLE
                ], [VENDOR, MODEL, [TYPE, MOBILE]], [
                /(i-STYLE2.1)/i                                                     // i-mobile i-STYLE 2.1
                ], [[MODEL, 'i-STYLE 2.1'], [VENDOR, 'i-mobile'], [TYPE, MOBILE]], [

                /(mobiistar touch LAI 512)/i                                        // mobiistar touch LAI 512
                ], [[MODEL, 'Touch LAI 512'], [VENDOR, 'mobiistar'], [TYPE, MOBILE]], [
                /////////////
                // END TODO
                ///////////*/

            ],

            engine : [[

                /windows.+\sedge\/([\w\.]+)/i                                       // EdgeHTML
                ], [VERSION, [NAME, 'EdgeHTML']], [

                /(presto)\/([\w\.]+)/i,                                             // Presto
                /(webkit|trident|netfront|netsurf|amaya|lynx|w3m)\/([\w\.]+)/i,     // WebKit/Trident/NetFront/NetSurf/Amaya/Lynx/w3m
                /(khtml|tasman|links)[\/\s]\(?([\w\.]+)/i,                          // KHTML/Tasman/Links
                /(icab)[\/\s]([23]\.[\d\.]+)/i                                      // iCab
                ], [NAME, VERSION], [

                /rv\:([\w\.]+).*(gecko)/i                                           // Gecko
                ], [VERSION, NAME]
            ],

            os : [[

                // Windows based
                /microsoft\s(windows)\s(vista|xp)/i                                 // Windows (iTunes)
                ], [NAME, VERSION], [
                /(windows)\snt\s6\.2;\s(arm)/i,                                     // Windows RT
                /(windows\sphone(?:\sos)*|windows\smobile|windows)[\s\/]?([ntce\d\.\s]+\w)/i
                ], [NAME, [VERSION, mapper.str, maps.os.windows.version]], [
                /(win(?=3|9|n)|win\s9x\s)([nt\d\.]+)/i
                ], [[NAME, 'Windows'], [VERSION, mapper.str, maps.os.windows.version]], [

                // Mobile/Embedded OS
                /\((bb)(10);/i                                                      // BlackBerry 10
                ], [[NAME, 'BlackBerry'], VERSION], [
                /(blackberry)\w*\/?([\w\.]+)*/i,                                    // Blackberry
                /(tizen)[\/\s]([\w\.]+)/i,                                          // Tizen
                /(android|webos|palm\sos|qnx|bada|rim\stablet\sos|meego|contiki)[\/\s-]?([\w\.]+)*/i,
                                                                                    // Android/WebOS/Palm/QNX/Bada/RIM/MeeGo/Contiki
                /linux;.+(sailfish);/i                                              // Sailfish OS
                ], [NAME, VERSION], [
                /(symbian\s?os|symbos|s60(?=;))[\/\s-]?([\w\.]+)*/i                 // Symbian
                ], [[NAME, 'Symbian'], VERSION], [
                /\((series40);/i                                                    // Series 40
                ], [NAME], [
                /mozilla.+\(mobile;.+gecko.+firefox/i                               // Firefox OS
                ], [[NAME, 'Firefox OS'], VERSION], [

                // Console
                /(nintendo|playstation)\s([wids3portablevu]+)/i,                    // Nintendo/Playstation

                // GNU/Linux based
                /(mint)[\/\s\(]?(\w+)*/i,                                           // Mint
                /(mageia|vectorlinux)[;\s]/i,                                       // Mageia/VectorLinux
                /(joli|[kxln]?ubuntu|debian|[open]*suse|gentoo|arch|slackware|fedora|mandriva|centos|pclinuxos|redhat|zenwalk|linpus)[\/\s-]?([\w\.-]+)*/i,
                                                                                    // Joli/Ubuntu/Debian/SUSE/Gentoo/Arch/Slackware
                                                                                    // Fedora/Mandriva/CentOS/PCLinuxOS/RedHat/Zenwalk/Linpus
                /(hurd|linux)\s?([\w\.]+)*/i,                                       // Hurd/Linux
                /(gnu)\s?([\w\.]+)*/i                                               // GNU
                ], [NAME, VERSION], [

                /(cros)\s[\w]+\s([\w\.]+\w)/i                                       // Chromium OS
                ], [[NAME, 'Chromium OS'], VERSION],[

                // Solaris
                /(sunos)\s?([\w\.]+\d)*/i                                           // Solaris
                ], [[NAME, 'Solaris'], VERSION], [

                // BSD based
                /\s([frentopc-]{0,4}bsd|dragonfly)\s?([\w\.]+)*/i                   // FreeBSD/NetBSD/OpenBSD/PC-BSD/DragonFly
                ], [NAME, VERSION],[

                /(ip[honead]+)(?:.*os\s*([\w]+)*\slike\smac|;\sopera)/i             // iOS
                ], [[NAME, 'iOS'], [VERSION, /_/g, '.']], [

                /(mac\sos\sx)\s?([\w\s\.]+\w)*/i,
                /(macintosh|mac(?=_powerpc)\s)/i                                    // Mac OS
                ], [[NAME, 'Mac OS'], [VERSION, /_/g, '.']], [

                // Other
                /((?:open)?solaris)[\/\s-]?([\w\.]+)*/i,                            // Solaris
                /(haiku)\s(\w+)/i,                                                  // Haiku
                /(aix)\s((\d)(?=\.|\)|\s)[\w\.]*)*/i,                               // AIX
                /(plan\s9|minix|beos|os\/2|amigaos|morphos|risc\sos|openvms)/i,
                                                                                    // Plan9/Minix/BeOS/OS2/AmigaOS/MorphOS/RISCOS/OpenVMS
                /(unix)\s?([\w\.]+)*/i                                              // UNIX
                ], [NAME, VERSION]
            ]
        };


        /////////////////
        // Constructor
        ////////////////


        var UAParser = function (uastring, extensions) {

            if (!(this instanceof UAParser)) {
                return new UAParser(uastring, extensions).getResult();
            }

            var ua = uastring || ((window && window.navigator && window.navigator.userAgent) ? window.navigator.userAgent : EMPTY);
            var rgxmap = extensions ? util.extend(regexes, extensions) : regexes;

            this.getBrowser = function () {
                var browser = mapper.rgx.apply(this, rgxmap.browser);
                browser.major = util.major(browser.version);
                return browser;
            };
            this.getCPU = function () {
                return mapper.rgx.apply(this, rgxmap.cpu);
            };
            this.getDevice = function () {
                return mapper.rgx.apply(this, rgxmap.device);
            };
            this.getEngine = function () {
                return mapper.rgx.apply(this, rgxmap.engine);
            };
            this.getOS = function () {
                return mapper.rgx.apply(this, rgxmap.os);
            };
            this.getResult = function() {
                return {
                    ua      : this.getUA(),
                    browser : this.getBrowser(),
                    engine  : this.getEngine(),
                    os      : this.getOS(),
                    device  : this.getDevice(),
                    cpu     : this.getCPU()
                };
            };
            this.getUA = function () {
                return ua;
            };
            this.setUA = function (uastring) {
                ua = uastring;
                return this;
            };
            this.setUA(ua);
            return this;
        };

        UAParser.VERSION = LIBVERSION;
        UAParser.BROWSER = {
            NAME    : NAME,
            MAJOR   : MAJOR, // deprecated
            VERSION : VERSION
        };
        UAParser.CPU = {
            ARCHITECTURE : ARCHITECTURE
        };
        UAParser.DEVICE = {
            MODEL   : MODEL,
            VENDOR  : VENDOR,
            TYPE    : TYPE,
            CONSOLE : CONSOLE,
            MOBILE  : MOBILE,
            SMARTTV : SMARTTV,
            TABLET  : TABLET,
            WEARABLE: WEARABLE,
            EMBEDDED: EMBEDDED
        };
        UAParser.ENGINE = {
            NAME    : NAME,
            VERSION : VERSION
        };
        UAParser.OS = {
            NAME    : NAME,
            VERSION : VERSION
        };

        return UAParser;

    })(window)();

    function isMobile(){
        if(navigator.userAgent.search(/Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|NetFront|Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|Dolfin|Dolphin|Skyfire|Zune/i) > -1){
            return true;
        }
        else {
            return false;
        }
    }

    /**
    * Detect Vendor Prefix with JavaScript
    * CREDITS: http://davidwalsh.name/vendor-prefix
    */
    function vendorPrefix(){
        var styles = window.getComputedStyle(document.documentElement, ''),
                pre = (Array.prototype.slice
                        .call(styles)
                        .join('')
                        .match(/-(moz|webkit|ms)-/) || (styles.OLink === '' && ['', 'o'])
                        )[1],
                dom = ('WebKit|Moz|MS|O').match(new RegExp('(' + pre + ')', 'i'))[1];
        return {
            dom: dom,
            lowercase: pre,
            css: '-' + pre + '-',
            js: $p.utils.ucfirst(pre)
        };
    }

    return {
        browser: UAParser.browser,
        cpu: UAParser.cpu,
        device: UAParser.device,
        engine: UAParser.engine,
        os: UAParser.os,
        string: navigator.userAgent,
        prefix: vendorPrefix(),
        isMobile: isMobile()
    };
})();

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2015 Radosław Włodkowski, radoslaw@wlodkowski.net
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 *
 * Code borrowed from:
 * Modernizr 2.8.3 (Custom Build) | MIT & BSD
 *
 */
(function(window, document, $, $p){

    "use strict";
    
$p.features = (function () {

    var Modernizr = {},
        features = {},
        docElement = document.documentElement,
        mod = 'modernizr',
        modElem = document.createElement(mod),
        mStyle = modElem.style,
        inputElem,
        toString = {}.toString,
        prefixes = ' -webkit- -moz- -o- -ms- '.split(' '),
        omPrefixes = 'Webkit Moz O ms',
        cssomPrefixes = omPrefixes.split(' '),
        domPrefixes = omPrefixes.toLowerCase().split(' '),
        ns = {
            'svg': 'http://www.w3.org/2000/svg'
        },
        tests = {},
        inputs = {},
        attrs = {},
        classes = [],
        slice = classes.slice,
        featureName,
        injectElementWithStyles = function (rule, callback, nodes, testnames) {

            var style, ret, node, docOverflow,
                div = document.createElement('div'),
                body = document.body,
                fakeBody = body || document.createElement('body');

            if (parseInt(nodes, 10)) {
                while (nodes--) {
                    node = document.createElement('div');
                    node.id = testnames ? testnames[nodes] : mod + (nodes + 1);
                    div.appendChild(node);
                }
            }

            style = ['&#173;', '<style id="s', mod, '">', rule, '</style>'].join('');
            div.id = mod;
            (body ? div : fakeBody).innerHTML += style;
            fakeBody.appendChild(div);
            if (!body) {
                fakeBody.style.background = '';
                fakeBody.style.overflow = 'hidden';
                docOverflow = docElement.style.overflow;
                docElement.style.overflow = 'hidden';
                docElement.appendChild(fakeBody);
            }

            ret = callback(div, rule);
            if (!body) {
                fakeBody.parentNode.removeChild(fakeBody);
                docElement.style.overflow = docOverflow;
            } else {
                div.parentNode.removeChild(div);
            }

            return !!ret;

        },
        isEventSupported = (function () {

            var TAGNAMES = {
                'select': 'input',
                'change': 'input',
                'submit': 'form',
                'reset': 'form',
                'error': 'img',
                'load': 'img',
                'abort': 'img'
            };

            function isEventSupported (eventName, element) {

                element = element || document.createElement(TAGNAMES[eventName] || 'div');
                eventName = 'on' + eventName;

                var isSupported = eventName in element;

                if (!isSupported) {
                    if (!element.setAttribute) {
                        element = document.createElement('div');
                    }
                    if (element.setAttribute && element.removeAttribute) {
                        element.setAttribute(eventName, '');
                        isSupported = is(element[eventName], 'function');

                        if (!is(element[eventName], 'undefined')) {
                            element[eventName] = undefined;
                        }
                        element.removeAttribute(eventName);
                    }
                }

                element = null;
                return isSupported;
            }
            return isEventSupported;
        })(),
        _hasOwnProperty = ({}).hasOwnProperty, hasOwnProp;

    Modernizr._prefixes = prefixes;
    Modernizr._domPrefixes = domPrefixes;
    Modernizr._cssomPrefixes = cssomPrefixes;
    Modernizr.hasEvent = isEventSupported;
    Modernizr.testProp = function (prop) {
        return testProps([prop]);
    };
    Modernizr.testAllProps = testPropsAll;
    Modernizr.testStyles = injectElementWithStyles;
    Modernizr.prefixed = function (prop, obj, elem) {
        if (!obj) {
            return testPropsAll(prop, 'pfx');
        } else {
            return testPropsAll(prop, obj, elem);
        }
    };

    if (!is(_hasOwnProperty, 'undefined') && !is(_hasOwnProperty.call, 'undefined')) {
        hasOwnProp = function (object, property) {
            return _hasOwnProperty.call(object, property);
        };
    }
    else {
        hasOwnProp = function (object, property) {
            return ((property in object) && is(object.constructor.prototype[property], 'undefined'));
        };
    }

    if (!Function.prototype.bind) {
        Function.prototype.bind = function bind (that) {

            var target = this;

            if (typeof target != "function") {
                throw new TypeError();
            }

            var args = slice.call(arguments, 1),
                bound = function () {

                    if (this instanceof bound) {

                        var F = function () {
                        };
                        F.prototype = target.prototype;
                        var self = new F();

                        var result = target.apply(
                            self,
                            args.concat(slice.call(arguments))
                            );
                        if (Object(result) === result) {
                            return result;
                        }
                        return self;

                    } else {

                        return target.apply(
                            that,
                            args.concat(slice.call(arguments))
                            );

                    }

                };

            return bound;
        };
    }

    function setCss (str) {
        mStyle.cssText = str;
    }

    function setCssAll (str1, str2) {
        return setCss(prefixes.join(str1 + ';') + (str2 || ''));
    }

    function is (obj, type) {
        return typeof obj === type;
    }

    function contains (str, substr) {
        return !!~('' + str).indexOf(substr);
    }

    function testProps (props, prefixed) {
        /* eslint-disable guard-for-in */
        for (var i in props) {
            var prop = props[i];
            if (!contains(prop, "-") && mStyle[prop] !== undefined) {
                return prefixed == 'pfx' ? prop : true;
            }
        }
        /* eslint-enable */
        return false;
    }

    function testDOMProps (props, obj, elem) {
        /* eslint-disable guard-for-in */
        for (var i in props) {
            var item = obj[props[i]];
            if (item !== undefined) {

                if (elem === false) {
                    return props[i];
                }

                if (is(item, 'function')) {
                    return item.bind(elem || obj);
                }

                return item;
            }
        }
        /* eslint-enable */
        return false;
    }

    function testPropsAll (prop, prefixed, elem) {

        var ucProp = prop.charAt(0).toUpperCase() + prop.slice(1),
            props = (prop + ' ' + cssomPrefixes.join(ucProp + ' ') + ucProp).split(' ');

        if (is(prefixed, "string") || is(prefixed, "undefined")) {
            return testProps(props, prefixed);

        } else {
            props = (prop + ' ' + (domPrefixes).join(ucProp + ' ') + ucProp).split(' ');
            return testDOMProps(props, prefixed, elem);
        }
    }

    tests['canvas'] = function () {
        var elem = document.createElement('canvas');
        return !!(elem.getContext && elem.getContext('2d'));
    };

    tests['canvastext'] = function () {
        return !!(Modernizr['canvas'] && is(document.createElement('canvas')
            .getContext('2d').fillText, 'function'));
    };

    tests['csstransitions'] = function() {
        return testPropsAll('transition');
    };

    tests['touch'] = function () {
        var bool;

        if (('ontouchstart' in window) || window.DocumentTouch && document instanceof DocumentTouch) {
            bool = true;
        } else {
            injectElementWithStyles(['@media (', prefixes.join('touch-enabled),('), mod, ')',
                '{#modernizr{top:9px;position:absolute}}'].join(''), function (node) {
                bool = node.offsetTop === 9;
            });
        }

        return bool;
    };
    tests['svg'] = function () {
        return !!document.createElementNS && !!document.createElementNS(ns.svg, 'svg').createSVGRect;
    };

    tests['inlinesvg'] = function () {
        var div = document.createElement('div');
        div.innerHTML = '<svg/>';
        return (div.firstChild && div.firstChild.namespaceURI) == ns.svg;
    };

    tests['inlinevideo'] = function() {
        var isIPhone = $p.userAgent.device.model === 'iPhone',
            isWindowsPhone = $p.userAgent.os.name === 'Windows Phone',
            isAndroid = $p.userAgent.os.name === 'Android',
            ieMobileVer = ($p.userAgent.browser.name === 'IEMobile') ? parseInt($p.userAgent.browser.major) : 0,
            osVer = parseFloat($p.userAgent.os.version);

        return (!isIPhone || (isIPhone && osVer >= 10)) && (!isWindowsPhone || (isWindowsPhone && osVer >= 8.1 && ieMobileVer >= 11)) && (!isAndroid || isAndroid && osVer >= 3);
    };

    tests['localstorage'] = function () {
        var mod = 'modernizr';
        try {
            localStorage.setItem(mod, mod);
            localStorage.removeItem(mod);
            return true;
        } catch (e) {
            return false;
        }
    };

    tests['mse'] = function(){
        return !!(window.MediaSource || window.WebKitMediaSource);
    };
    
    tests['eme'] = function () {
        var result = false,
            testVideoEl = document.createElement('video');
        
        // EME
        if (window.navigator.requestMediaKeySystemAccess) {
            if (typeof window.navigator.requestMediaKeySystemAccess === 'function') {
                result = true;
            }
        }
        // MS-EME
        else if (window.MSMediaKeys) {
            if (typeof window.MSMediaKeys === 'function') {
                result = true;
            }
        }
        // WEBKIT-EME    
        else if (testVideoEl.webkitGenerateKeyRequest) {
            if (typeof testVideoEl.webkitGenerateKeyRequest === 'function') {
                result = true;
            }
        }

        return result;
    };

    tests['hlsjs'] = function(){
        window.MediaSource = window.MediaSource || window.WebKitMediaSource;
        return (window.MediaSource &&
            typeof window.MediaSource.isTypeSupported === 'function' &&
            window.MediaSource.isTypeSupported('video/mp4; codecs="avc1.42E01E,mp4a.40.2"'));
    };

    tests['volumecontrol'] = function(){
        var result = false,
            testVideoEl = document.createElement('video'),
            testVol = 0.4;

            testVideoEl.volume = testVol;
            
            return (testVideoEl.volume === testVol);
    };

    for (var feature in tests) {
        if (hasOwnProp(tests, feature)) {
            featureName = feature.toLowerCase();
            features[featureName] = tests[feature]();
            classes.push((features[featureName] ? '' : 'no-') + featureName);
        }
    }

    setCss('');
    modElem = inputElem = null;

    return features;

})();

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2015 Radosław Włodkowski, radoslaw@wlodkowski.net
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 *
 */
(function(window, document, $, $p){

    "use strict";
    
$p.fullscreenApi = (function () {

    var videoElement = document.createElement('video'),
    fsApiVersionsMap = {
        /*
         * mediaonly API applies to HTMLVideoElement, mainly on iOS and Android devices (WebKit)
         */
        mediaonly: {
            /*
             * Methods
             */
            enterFullscreen: ['enterFullscreen', 'enterFullScreen'],
            exitFullscreen: ['exitFullscreen', 'exitFullScreen', 'cancelFullScreen', 'cancelFullscreen'],
            /*
             * Properties
             */
            supportsFullscreen: ['supportsFullscreen', 'supportsFullScreen'],
            displayingFullscreen: ['displayingFullscreen', 'fullScreen', 'isFullScreen', 'isFullscreen'],
            /*
             * Events
             */
            beginfullscreen: 'onwebkitbeginfullscreen', // webkit specific, NOTE: this event is unexposed
            // in the newest versions of WebKit based browsers, but it's still dispatched
            endfullscreen: 'onwebkitendfullscreen' // ditto
        },
        /*
         * HTML5 fully blown fullscreen API in different flavours. There are differences in function names
         * and naming conventions between implementations of fullscreen API so we list all of known versions
         * and map them to those specified in WHATWG Fullscreen API Living Standard — Last Updated 29 September 2015.
         * Eventually we are trying to determine which combination does current browser use (if any).
         */
        full: {
            /*
             * Methods
             */
            // HTMLElement
            requestFullscreen: ['requestFullscreen', 'requestFullScreen', 'enterFullscreen', 'enterFullScreen'],
            // DOMDocument
            exitFullscreen: ['exitFullscreen', 'exitFullScreen', 'cancelFullScreen', 'cancelFullscreen'],
            /*
             * Properties
             */
            // DOMDocument property informing if you can use the API
            fullscreenEnabled: ['fullscreenEnabled', 'fullScreenEnabled', 'supportsFullscreen', 'supportsFullScreen'],
            // DOMDocument property returning element which is currently in the fullscreen stage
            fullscreenElement: ['fullscreenElement', 'fullScreenElement', 'currentFullScreenElement'],
            // DOMDocument property informing if the browser is currently in the fullscreen stage. There is no W3C proposal for this property.
            isFullscreen: ['fullScreen', 'isFullScreen', 'isFullscreen', 'displayingFullscreen', 'displayingFullScreen'],
            /*
             * Events
             */
            // fired on DOMDocument
            // NOTE: Internet Explorer 11 and IEMobile on Windows Phone 8.1 are using cammelcase, prefixed, event names
            // for addEventListener (e.g. MSFullscreenChange) but have lowercase event names in document object (e.g. onmsfullscreenchange)
            // so in this case detection is useless cause when we detect lowercase event name we can't use it with addEventListener
            // - there is need for exception
            fullscreenchange: ['onfullscreenchange', 'onwebkitfullscreenchange', 'onmozfullscreenchange'],
            fullscreenerror: ['onfullscreenerror', 'onwebkitfullscreenerror', 'onmozfullscreenerror']
        }
    },
    /**
     * this object contains proper names for current UA native fullscreen API functions,
     * properties and events
     */
    fullscreenApi = {
        type: 'none',
        mediaonly: {
            enterFullscreen: '',
            exitFullscreen: '',
            supportsFullscreen: '',
            displayingFullscreen: '',
            beginfullscreen: fsApiVersionsMap.mediaonly['beginfullscreen'], // because in the newest versions of WebKit based browsers this event is unexposed,
            // but it is still dispatched the string value is fixed (not detected)
            endfullscreen: fsApiVersionsMap.mediaonly['endfullscreen'] // ditto
        },
        /*
         * HTML5 fully blown fullscreen API in different flavours. There are differences in function names
         * and naming conventions between implementations of fullscreen API so we list all of known versions
         * and map them to those specified in WHATWG Fullscreen API Living Standard — Last Updated 29 September 2015.
         * Eventually we are trying to determine which combination does current browser use (if any).
         */
        full: {
            requestFullscreen: '',
            exitFullscreen: '',
            fullscreenEnabled: '',
            fullscreenElement: '',
            isFullscreen: '',
            fullscreenchange: '',
            fullscreenerror: '',
        }
    },
    prefix = $p.userAgent.prefix.lowercase;

    // find if there are two distinctive values
    fullscreenApi.mediaonly.enterFullscreen = $p.utils.hasProp(videoElement, fsApiVersionsMap.mediaonly.enterFullscreen.slice(), prefix);
    fullscreenApi.full.exitFullscreen = $p.utils.hasProp(document, fsApiVersionsMap.full.exitFullscreen.slice(), prefix);

    // if there is full fullscreen API support then of course the mediaonly is also supported
    if (!!fullscreenApi.full.exitFullscreen) {
        fullscreenApi.type = 'full';
    }
    else if (!!fullscreenApi.mediaonly.enterFullscreen) {
        fullscreenApi.type = 'mediaonly';
    }

    // detect versions of all other functions/properties/events
    switch(fullscreenApi.type){
        case 'mediaonly':
            fullscreenApi.mediaonly.exitFullscreen       = $p.utils.hasProp(videoElement, fsApiVersionsMap.mediaonly.exitFullscreen.slice(), prefix);
            fullscreenApi.mediaonly.supportsFullscreen   = $p.utils.hasProp(videoElement, fsApiVersionsMap.mediaonly.supportsFullscreen.slice(), prefix);
            fullscreenApi.mediaonly.displayingFullscreen = $p.utils.hasProp(videoElement, fsApiVersionsMap.mediaonly.displayingFullscreen.slice(), prefix);
        break;

        case 'full':
            fullscreenApi.full.requestFullscreen = $p.utils.hasProp(videoElement, fsApiVersionsMap.full.requestFullscreen.slice(), prefix);
            fullscreenApi.full.fullscreenEnabled = $p.utils.hasProp(document, fsApiVersionsMap.full.fullscreenEnabled.slice(), prefix);
            fullscreenApi.full.fullscreenElement = $p.utils.hasProp(document, fsApiVersionsMap.full.fullscreenElement.slice(), prefix);
            fullscreenApi.full.isFullscreen      = $p.utils.hasProp(document, fsApiVersionsMap.full.isFullscreen.slice(), prefix);

            // Internet Explorer 11 and IEMobile on Windows Phone 8.1
            if(prefix === 'ms'){
                fullscreenApi.full.fullscreenchange = 'onMSFullscreenChange';
                fullscreenApi.full.fullscreenerror = 'onMSFullscreenError';
            }
            else {
                fullscreenApi.full.fullscreenchange  = $p.utils.hasProp(document, fsApiVersionsMap.full.fullscreenchange.slice());
                fullscreenApi.full.fullscreenerror   = $p.utils.hasProp(document, fsApiVersionsMap.full.fullscreenerror.slice());
            }
        break;
    }

    return fullscreenApi;
})();

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2015 Radosław Włodkowski, radoslaw@wlodkowski.net
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 *
 */
var projekktorPersistentStorage = (function (window, document, $, $p){

    "use strict";
    
function projekktorPersistentStorage(pp){
    this.pp = pp;
}

projekktorPersistentStorage.prototype = (function () {
    var persistentStorage = {

        save: function (key, value) {
            var ns = this.pp.getNS(),
                nskey = ns + '_' + key;

            if (window.$p.features.localstorage) {
                try {
                    window.localStorage.setItem(nskey, JSON.stringify(value));
                    return true;
                } catch (e) {
                    return false;
                }
            }
        },

        restore: function (key) {
            var ns = this.pp.getNS(),
                nskey = ns + '_' + key;

            if (window.$p.features.localstorage){
                try {
                    return JSON.parse(window.localStorage.getItem(nskey));
                } catch (e) {}
            }
        },

        remove: function(key) {
            var ns = this.pp.getNS(),
                nskey = ns + '_' + key;

            if (window.$p.features.localstorage){
                try {
                    window.localStorage.removeItem(nskey);
                } catch (e) {}
            }
        },

        list: function() {
            var ns = this.pp.getNS() + '_',
                regexp = new RegExp('^' + ns),
                result = {},
                key;

            if (window.$p.features.localstorage){
                try {
                    for (key in window.localStorage){
                        if(regexp.test(key)){
                            result[key] = window.localStorage.getItem(key);
                        }
                    }
                } catch (e) {}
            }

            return result;
        },

        clear: function() {
            var ns = this.pp.getNS() + '_',
                regexp = new RegExp('^' + ns),
                key;

            if (window.$p.features.localstorage){
                try {
                    for (key in window.localStorage){
                        if(regexp.test(key)){
                            window.localStorage.removeItem(key);
                        }
                    }
                } catch (e) {}
            }
        }
    };

    return persistentStorage;
})();

return projekktorPersistentStorage;

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2010, 2011, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * Copyright 2014-2017 - Radosław Włodkowski, www.wlodkowski.net, radoslaw@wlodkowski.net
 *
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 */

(function(window, document, $, $p){

    "use strict";
    
    var testVideoEl = document.createElement('video');

    $p.platforms = {
        videojs: function() {
            return "1";
        },

        /**
         * returns 1 if MSE is available 0 otherwise
         */
        mse: function() {
            return $p.features.mse ? "1" : "0";
        },

        android: function () {
            if($p.userAgent.os.name === "Android"){
                return $p.userAgent.os.version || "0";
            }
            return "0";
        },

        ios: function () {
            if($p.userAgent.os.name === "iOS"){
                return $p.userAgent.os.version || "0";
            }
            return "0";
        },

        native: function (type) {
            switch (testVideoEl.canPlayType(type)) {
                    case null:
                    case "no":
                    case "":
                        return "0";
                    case "maybe":
                    case "probably":
                    default:
                        return "1";
            }
        },
        
        browser: function () {
            return "1";
        }
    };
    
}(window, document, jQuery, projekktor));
(function (window, document, $, $p) {

    "use strict";

        var drmSystems = {
                widevine: ['com.widevine.alpha'],
                playready: ['com.microsoft.playready', 'com.youtube.playready'],
                clearkey: ['webkit-org.w3.clearkey', 'org.w3.clearkey'],
                primetime: ['com.adobe.primetime', 'com.adobe.access'],
                fairplay: ['com.apple.fairplay']
            },
            supportedDrmSystems = [],
            emeType = getEmeType(),
            testConfig = [{
                initDataTypes: ['cenc', 'webm'],
                sessionTypes: ['temporary'],
                audioCapabilities: [{
                        contentType: 'audio/mp4; codecs="mp4a.40.5"',
                        robustness: 'SW_SECURE_CRYPTO'
                    },
                    {
                        contentType: 'audio/mp4; codecs="mp4a.40.2"',
                        robustness: 'SW_SECURE_CRYPTO'
                    },
                    {
                        contentType: 'audio/webm; codecs="vorbis"',
                        robustness: 'SW_SECURE_CRYPTO'
                    },
                ],
                videoCapabilities: [{
                        contentType: 'video/webm; codecs="vp9"',
                        robustness: 'HW_SECURE_ALL'
                    },
                    {
                        contentType: 'video/webm; codecs="vp9"',
                        robustness: 'SW_SECURE_DECODE'
                    },
                    {
                        contentType: 'video/mp4; codecs="avc1.640028"',
                        robustness: 'HW_SECURE_ALL'
                    },
                    {
                        contentType: 'video/mp4; codecs="avc1.640028"',
                        robustness: 'SW_SECURE_DECODE'
                    },
                    {
                        contentType: 'video/mp4; codecs="avc1.4d401e"',
                        robustness: 'HW_SECURE_ALL'
                    },
                    {
                        contentType: 'video/mp4; codecs="avc1.4d401e"',
                        robustness: 'SW_SECURE_DECODE'
                    },
                ],
            }];

        function getEmeType() {

            if (navigator.requestMediaKeySystemAccess &&
                MediaKeySystemAccess.prototype.getConfiguration) {
                return 'eme'; // current EME as of 16 March 2017
            } else if (HTMLMediaElement.prototype.webkitGenerateKeyRequest) {
                return 'webkit'; // webkit-prefixed EME v0.1b
            } else if (HTMLMediaElement.prototype.generateKeyRequest) {
                return 'oldunprefixed'; // nonprefixed EME v0.1b
            } else if (window.MSMediaKeys) {
                return 'ms'; // ms-prefixed EME v20140218
            } else {
                return 'none'; // EME unavailable
            }
        }

        function msIsTypeSupportedPromissified(keySystem) {
            return new Promise(function (resolve, reject) {
                var e;
                if (window.MSMediaKeys.isTypeSupported && window.MSMediaKeys.isTypeSupported(keySystem)) {
                    resolve({
                        keySystem: keySystem
                    });
                } else {
                    e = new Error('Unsupported keySystem');
                    e.name = 'NotSupportedError';
                    e.code = DOMException.NOT_SUPPORTED_ERR;
                    reject(e);
                    throw e;
                }
            });
        }

        function getSupportedDrmSystems() {
            var ref = this,
                isKeySupported,
                promises = [];

            if (emeType === 'eme') {
                isKeySupported = window.navigator.requestMediaKeySystemAccess.bind(window.navigator);
            } 
            else if (emeType === 'ms') {
                isKeySupported = msIsTypeSupportedPromissified;
            }
            else {
                // if there is no EME then resolve promise immediately
                return Promise.resolve();
            }

            Object.keys(drmSystems).forEach(function(keySystemName) {
                var keySystemNS = drmSystems[keySystemName];

                keySystemNS.forEach(function (ks) {
                    promises.push(isKeySupported(ks, testConfig).then(
                        function (val) {
                            supportedDrmSystems.push(keySystemName);
                        },
                        function (error) {
                            // skip
                        }
                    ));
                }, ref);
            });

            return Promise.all(promises);
        };

        $p.initPromises.push(
            getSupportedDrmSystems().then(function (val) {
                $p.drm = {
                    supportedDrmSystems: supportedDrmSystems,
                    drmSystems: drmSystems,
                    emeType: emeType
                };
                return Promise.resolve();
            })
        );
}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2010-2013 Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 */
var projekktorPluginInterface = (function (window, document, $, $p){

    "use strict";
    
    function projekktorPluginInterface() {}

    projekktorPluginInterface.prototype = {

        pluginReady: false,
        reqVer: null,
        name: '',
        pp: {},
        config: {},
        playerDom: null,

        _appliedDOMObj: [],
        _pageDOMContainer: {},
        _childDOMContainer: {},

        _init: function (pluginConfig) {
            this.config = $.extend(true, this.config, pluginConfig);
            if (this.reqVer != null) {
                if (!$p.utils.versionCompare(this.pp.getVersion(), this.reqVer)) {
                    alert("Plugin '" + this.name + "' requires Projekktor v" + this.reqVer + " or later! Please visit http://www.projekktor.com and get the most recent version.");
                    this.pluginReady = true;
                    return;
                }
            }
            this.initialize();
        },

        getConfig: function (idx, defaultValue) {
            var result = null,
                def = defaultValue || null;

            if (this.pp.getConfig('plugin_' + this.name) != null) {
                result = this.pp.getConfig('plugin_' + this.name)[idx];
            }

            if (result == null) {
                result = this.pp.getConfig(idx);
            }

            if (result == null) {
                result = this.config[idx];
            }

            if ($.isPlainObject(result)) {
                result = $.extend(true, {}, result, this.config[idx]);
            } else if ($.isArray(result)) {
                result = $.extend(true, [], this.config[idx] || [], result || []);
            }

            if (idx == undefined) {
                return this.pp.getConfig();
            }
            return (result == null) ? def : result;
        },

        getDA: function (name) {
            return 'data-' + this.pp.getNS() + '-' + this.name + '-' + name;
        },

        getCN: function (name) {
            return this.pp.getNS() + name;
        },

        sendEvent: function (eventName, data) {
            this.pp._promote({
                _plugin: this.name,
                _event: eventName
            }, data);
        },

        deconstruct: function () {
            this.pluginReady = false;
            $.each(this._appliedDOMObj, function () {
                $(this).off();
            });
        },

        /**
         * applies a new dom element to the player in case it is not yet present
         * also transparently applies the cssclass prefix as configured
         *
         * @private
         * @element (Object) the element
         * @fu (String) function, default 'container'
         * @visible (Boolean) display on init, default is 'false'
         * @return (Object) the element
         */
        applyToPlayer: function (element, fu, visible) {
            if (!element) {
                return null;
            }

            var func = fu || 'container',
                tmpClass = '',
                ref = this;

            try {
                tmpClass = element.attr("class") || this.name;
            } catch (e) {
                tmpClass = this.name;
            }

            this._pageDOMContainer[func] = $("[" + this.getDA('host') + "='" + this.pp.getId() + "'][" + this.getDA('func') + "='" + func + "']");
            this._childDOMContainer[func] = this.playerDom.find("[" + this.getDA('func') + "='" + func + "'],." + this.getCN(tmpClass) + ":not([" + this.getDA('func') + "=''])");

            // check if this element already exists somewhere on page
            if (this._pageDOMContainer[func].length > 0) {
                this._pageDOMContainer[func].removeClass('active').addClass('inactive');

                $.each(this._pageDOMContainer[func], function () {
                    ref._appliedDOMObj.push($(this));
                });

                return this._pageDOMContainer[func];
            }

            // add new DOM container to the player
            if (this._childDOMContainer[func].length == 0) {
                element
                    .removeClass(tmpClass)
                    .addClass(this.pp.getNS() + tmpClass)
                    .removeClass('active')
                    .addClass('inactive')
                    .attr(this.getDA('func'), func)
                    .appendTo(this.playerDom);

                this._childDOMContainer[func] = element;
                this._appliedDOMObj.push(element);
                if (visible === true) {
                    element.addClass('active').removeClass('inactive');
                }

                return element;
            } else {
                $.each(this._childDOMContainer[func], function () {
                    $(this).attr(ref.getDA('func'), func);
                    ref._appliedDOMObj.push($(this));
                });
            }

            if (visible === true) {
                this._childDOMContainer[func].addClass('active').removeClass('inactive');
            }

            return $(this._childDOMContainer[func][0]);
        },

        getElement: function (name) {
            return this.pp.env.playerDom.find('.' + this.pp.getNS() + name);
        },

        setInactive: function () {
            $(this._pageDOMContainer['container']).removeClass('active').addClass('inactive');
            $(this._childDOMContainer['container']).removeClass('active').addClass('inactive');
            this.sendEvent('inactive', $.extend(true, {}, this._pageDOMContainer['container'], this._childDOMContainer['container']));
        },

        setActive: function (elm, on) {
            var dest = (typeof elm == 'object') ? elm : this.getElement(elm);

            if (elm == null) {
                this._pageDOMContainer['container'].removeClass('inactive').addClass('active');
                this._childDOMContainer['container'].removeClass('inactive').addClass('active');
                this.sendEvent('active', $.extend(true, {}, this._pageDOMContainer['container'], this._childDOMContainer['container']));
                return dest;
            }

            if (on != false) {
                dest.addClass('active').removeClass('inactive');
            } else {
                dest.addClass('inactive').removeClass('active');
            }

            dest.css('display', '');

            return dest;
        },

        getActive: function (elm) {
            return $(elm).hasClass('active');
        },

        // triggered on plugin-instantiation
        initialize: function () {},

        isReady: function () {
            return this.pluginReady;
        },

        clickHandler: function (what) {
            try {
                this.pp[this.getConfig(what + 'Click').callback](this.getConfig(what + 'Click').value);
            } catch (e) {
                try {
                    this.getConfig(what + 'Click')(this.getConfig(what + 'Click').value);
                } catch (e) {}
            }
            return false;
        },
        
        // important
        eventHandler: function () {}
    };

    return projekktorPluginInterface;

}(window, document, jQuery, projekktor));var projekktorMessages = (function(window, document, $, $p){

    "use strict";
    
return {

    // controlbar
    "play": "start playback",
    "pause": "pause playback",

    // settings
    "help": "help:",
    "keyboard controls": "keyboard",
    "debug": "debug",
    "player info": "player info",
    "auto": "automatic",
    "quality": "quality",
    "high": "high",
    "medium": "medium",
    "low": "low",

    // platforms
    "platform": "platform",

    // Native <video>
    "platform_native": "HTML5",
    "platform_native_info": "Get one of the modern web browsers: <ul><li>Chrome</li><li>Edge</li><li>Firefox</li><li>Opera</li></ul>",

    // MSE
    "platform_mse": "MSE",
    "platform_mse_info": "",

    // settings
    'ok': 'OK',
    'report': 'Report a bug',
    'cancel': 'cancel',
    'continue': 'continue',
    'sendto': 'Please send this information to the webmaster of this site.',
    'please': 'Please describe your problem as detailed as possible....',
    'thanks': 'Thank you very much.',
    'error': 'An error occurred',
    'help1': '<em>space</em> play / pause',
    'help2': '<em>up</em><em>down</em> volume <em>left</em><em>right</em> scrub',
    'help3': '<em>ENTER</em> toggle fullscreen',
    'help4': 'Mouse must hover the player.',

    // flash & native:
    "error0": '#0 An (unknown) error occurred.',
    "error1": '#1 You aborted the media playback. ',
    "error2": '#2 A network error caused the media download to fail part-way. ',
    "error3": '#3 The media playback was aborted due to a corruption problem. ',
    "error4": '#4 The media (%{title}) could not be loaded because the server or network failed.',
    "error5": '#5 Sorry, your browser does not support the media format of the requested file.',
    "error6": '#6 Your client is in lack of the Flash Plugin V%{flashver} or higher.',
    "error7": '#7 No media scheduled.',
    "error8": '#8 ! Invalid media model configured !',
    "error9": '#9 File (%{file}) not found.',
    "error10": '#10 Invalid or missing quality settings for %{title}.',
    "error11": '#11 Invalid streamType and/or streamServer settings for %{title}.',
    "error12": '#12 Invalid or inconsistent quality setup for %{title}.',
    "error13": '#13 Invalid playlist or missing/broken playlist parser. No media scheduled.',
    "error20": '#20 Invalid or malicious parser applied',
    "error80": '#80 The requested file does not exist or is delivered with an invalid content-type.',
    "error97": 'No media scheduled.',
    "error98": 'Invalid or malformed playlist data!',
    "error99": 'Click display to proceed. ',
    "error100": 'Keyboard Shortcuts',

    "error200": 'Loading timeout',

    // DRM errors
    "error300": "#300 No support for any of the DRM systems used to encrypt this media.",
    "error301": "#301 DRM system required but no valid license server config defined.",
    "error302": "#302 DRM license invalid or license server unavailable.",

    // youtube errors:
    "error500": 'This Youtube video has been removed or set to private',
    "error501": 'The Youtube user owning this video disabled embedding.',
    "error502": 'Invalid Youtube Video-Id specified.'

};

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2010, 2011, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 */
var playerModel = (function(window, document, $, $p){

    "use strict";

    function playerModel() {}

    playerModel.prototype = {
        modelId: 'player',
        browserVersion: '1.0',
        iLove: [],
        platform: ['browser'],
        // all the player states
        _currentState: null,
        _currentBufferState: 'EMPTY', // EMPTY / FULL
        _currentSeekState: null,
        _ap: false, // autoplay
        _volume: 1, // async
        _fixedVolume: false,
        _muted: false,
        _quality: 'auto',
        _displayReady: false,
        _isPlaying: false,
        _isReady: false,
        _isDVR: false,
        _isLive: false,
        _id: null,
        // experimental
        _KbPerSec: 0,
        _bandWidthTimer: null,
        // flags
        _isPoster: false,
        _isFullscreen: false,
        hasGUI: false,
        allowRandomSeek: false,
        mediaElement: null,
        pp: {},
        media: {
            duration: 0,
            position: 0,
            maxpos: 0,
            file: false,
            poster: '',
            ended: false,
            loadProgress: 0,
            errorCode: 0
        },
        /*******************************
         *        CORE
         *******************************/
        _init: function (params) {
            this.pp = params.pp || null;
            this.media = $.extend(true, {}, this.media, params.media);
            this.mediaId = params.media.id;
            this._ap = params.autoplay;
            this._isFullscreen = params.fullscreen;
            this._id = $p.utils.randomId(8);
            this._quality = params.quality || this._quality;
            this._volume = params.environment.volume;
            this._muted = params.environment.muted;
            this.init();
        },
        init: function (params) {
            this.ready();
        },
        ready: function () {
            this.sendUpdate('modelReady');
            this._isReady = true;
            if (!this._ap) {
                this.displayItem(false);
            }
            else {
                this.displayReady();
            }
        },
        /* apply poster while sleeping or get ready for true multi media action */
        displayItem: function (showMedia) {
            // reset
            this._displayReady = false;
            this._isPoster = false;

            this.pp.removeListener('fullscreen.poster');
            this.pp.removeListener('resize.poster');

            // poster
            if (showMedia !== true || this.getState('STOPPED')) {
                this._setState('idle');
                this.applyImage(this.getPoster(), this.pp.getMediaContainer().html(''));
                this._isPoster = true;
                this.displayReady();
                return;
            }

            // media
            $('#' + this.pp.getMediaId() + "_image").remove();
            // apply media
            this.applyMedia(this.pp.getMediaContainer());
        },
        applyMedia: function () {
        },
        sendUpdate: function (type, value) {
            // type = type.toLowerCase();
            this.pp._modelUpdateListener(type, value);
            if (type == 'error') {
                this.removeListeners();
                this.detachMedia();
                this._setState('error');
            }
        },
        /* wait for the playback element to initialize */
        displayReady: function () {
            this._displayReady = true;
            this.pp._modelUpdateListener('displayReady');
        },
        start: function () {

            if (this.mediaElement == null && this.modelId !== 'PLAYLIST') {
                return;
            }

            if (this.getState('STARTING')) {
                return;
            }

            // check if there is start position configured
            // and try to seek to it before play
            // TODO: this is definitely sub-optimal solution
            // and probably not working on some platform
            // We need to use per-platform/model approach
            // using Temporal Dimension of Media Fragments URI etc.
            if($.isNumeric(this.media.config.start)){
                this.setSeek(this.media.config.start);
            }

            this._setState('STARTING');

            if (!this.getState('STOPPED')) {
                this.addListeners();
            }

            this.applyCommand('volume', this.pp.getVolume());

            this.setPlay();
        },
        addListeners: function () {
        },
        removeListeners: function () {
            try {
                this.mediaElement.off('.projekktor' + this.pp.getId());
            } catch (e) {
            }
        },
        detachMedia: function () {
        },
        destroy: function () {

            this.removeListeners();

            if (!this.getState('IDLE')) {
                this._setState('destroying');
            }

            this.detachMedia();

            try {
                $('#' + this.mediaElement.id).empty();
            } catch (e) {
            }

            this.mediaElement = null;

            this.media.loadProgress = 0;
            this.media.playProgress = 0;
            this.media.frame = 0;
            this.media.position = 0;
            this.media.duration = 0;
        },
        applyCommand: function (command, value) {
            switch (command) {
                case 'quality':
                    this.setQuality(value);
                    break;
                case 'error':
                    this._setState('error');
                    this.pp._modelUpdateListener('error', value);
                    break;
                case 'play':
                    if (this.getState('ERROR')) {
                        break;
                    }
                    if (this.getState('IDLE')) {
                        this._setState('awakening');
                        break;
                    }
                    this.setPlay();
                    break;
                case 'pause':
                    if (this.getState('ERROR')) {
                        break;
                    }
                    this.setPause();
                    break;
                case 'volume':
                    if (this.getState('ERROR')) {
                        break;
                    }
                    this.setVolume(value);
                    break;
                case 'stop':
                    this.setStop();
                    break;
                case 'frame':
                    this.setFrame(value);
                    break;
                case 'seek':
                    if (this.getState('ERROR')) {
                        break;
                    }

                    if (this.getSeekState('SEEKING')) {
                        break;
                    }

                    if (this.getState('IDLE')) {
                        break;
                    }

                    if (this.media.loadProgress == -1) {
                        break;
                    }

                    this._setSeekState('seeking', value);
                    this.setSeek(value);
                    break;
                case 'fullscreen':
                    /*
                     * It is vital to first tell the controller what happened in order to have an already altered DOM
                     * before processing further scaling processes.
                     * This is a break in the logic but seems to work.
                     */
                    if (value !== this._isFullscreen) {
                        this._isFullscreen = value;
                        this.setFullscreen();
                    }
                    break;
                case 'resize':
                    this.setResize();
                    this.sendUpdate('resize', value);
                    break;
            }
        },
        /*******************************
         *   PUBLIC ELEMENT SETTERS
         *******************************/
        setFrame: function (frame) {
            var newPos = (frame / this.pp.getConfig('fps')) + 0.00001;
            this.setSeek(newPos);
        },
        setSeek: function (newpos) {
        },
        setPlay: function () {
        },
        setPause: function () {
        },
        setStop: function () {
            this.detachMedia();
            this._setState('stopped');
            // this._ap=false;
            this.displayItem(false);

        },
        setVolume: function (volume) {
            this.volumeListener(volume);
        },
        setMuted: function(muted) {

        },
        setFullscreen: function (inFullscreen) {
            this.sendUpdate('fullscreen', this._isFullscreen);
            this.setResize();
        },
        setResize: function () {
            if (this.element === 'audio' || this.getState('ERROR')) {
                return;
            }
            this._scaleVideo();
        },
        setPosterLive: function () {
        },
        setSrc: function(src) {
            try {
                this.media.file[0].src = src;
            } catch (e) {}
        },
        setQuality: function (quality) {
            if (this._quality === quality) {
                return;
            }

            this._quality = quality;

            try {
                this.applySrc();
            }
            catch (e) {
            }

            this.qualityChangeListener();
        },
        /*******************************
         ELEMENT GETTERS
         *******************************/
        getId: function () {
            return this.mediaId;
        },
        getQuality: function () {
            return this._quality;
        },
        getVolume: function () {
            return this._volume;
        },
        getMuted: function () {
            return this._muted;
        },
        getLoadProgress: function () {
            return this.media.loadProgress || 0;
        },
        getLoadPlaybackProgress: function () {
            return this.media.playProgress || 0;
        },
        getPosition: function () {
            return this.media.position || 0;
        },
        getFrame: function () {
            return this.media.frame || 0;
        },
        getDuration: function () {
            return this.media.duration || this.pp.getConfig('duration') || 0;
        },
        getMaxPosition: function () {
            return this.media.maxpos || 0;
        },
        getPlaybackQuality: function () {
            return ($.inArray(this._quality, this.media.qualities) > -1) ? this._quality : 'auto';
        },
        getIsFullscreen: function () {
            return this.pp.getIsFullscreen();
        },
        getKbPerSec: function () {
            return this._KbPerSec;
        },
        getState: function (isThis) {
            var result = (this._currentState == null) ? 'IDLE' : this._currentState;
            if (isThis != null) {
                return (result == isThis.toUpperCase());
            }
            return result;
        },
        getBufferState: function (isThis) {
            var result = this._currentBufferState;
            if (isThis != null) {
                return (result === isThis.toUpperCase());
            }
            return result;
        },
        getSeekState: function (isThis) {
            var result = (this._currentSeekState == null) ? 'NONE' : this._currentSeekState;
            if (isThis != null) {
                return (result == isThis.toUpperCase());
            }
            return result;
        },
        getSrc: function () {
            try {
                return this.mediaElement.get(0).currentSrc;
            }
            catch (e) {
            }

            try {
                return this.media.file[0].src;
            }
            catch (e) {
            }

            try {
                return this.getPoster();
            }
            catch (e) {
            }
            return null;
        },
        getModelName: function () {
            return this.modelId || null;
        },
        getMediaElementId: function() {
            try {
                return this.pp.getMediaId() + "_" + this.getModelName().toLowerCase();
            }
            catch(e){
                return "";
            }
        },
        getHasGUI: function () {
            return (this.hasGUI && !this._isPoster);
        },
        getIsReady: function () {
            return this._isReady;
        },
        getPoster: function (type) {
            var type = type || 'poster',
                result = null,
                cfg = this.pp.getConfig(type),
                qual = 'default',
                quals = [];

            if (typeof cfg !== 'object') {
                return cfg;
            }

            for (var i in cfg) {
                if (cfg[i].quality) {
                    quals.push(cfg[i].quality);
                }
            }

            qual = this.pp.getAppropriateQuality(quals);

            for (var j in cfg) {
                if (cfg[j].src != undefined && (cfg[j].quality == qual || result == "" || qual == "default")) {
                    result = cfg[j].src;
                }
            }
            return result;
        },
        getMediaElement: function () {
            return this.mediaElement || $('<video/>');
        },
        getMediaDimensions: function () {
            return {
                width: this.media.videoWidth || 0,
                height: this.media.videoHeight || 0
            };
        },
        getSource: function () {

            var resultSrc = [],
                ref = this;

            $.each(this.media.file || [], function () {
                // set proper quality source
                if (ref._quality !== this.quality && ref._quality !== null) {
                    return true;
                }

                resultSrc.push(this);
                return true;
            });

            if (resultSrc.length === 0) {
                return this.media.file;
            }
            else {
                return resultSrc;
            }
        },
        /*******************************
         *      ELEMENT LISTENERS
         *******************************/
        timeListener: function (obj) {
            if (typeof obj !== 'object' || obj === null) {
                return;
            }

            var position = parseFloat((obj.position || obj.currentTime || this.media.position || 0).toFixed(2)),
                duration = null;

            /*
             * When the duration is POSITIVE_INFINITY then we're dealing with a native live stream (e.g. HLS)
             */
            if (obj.duration === Number.POSITIVE_INFINITY && obj.seekable && obj.seekable.length) {

                /*
                 * When the seekable.end(0) === POSITIVE_INFINITY we don't have any option to determine DVR window,
                 * so we set _isLive to true and propagate streamTypeChange event with 'live' value
                 */
                if(obj.seekable.end(0) === Number.POSITIVE_INFINITY){
                    // set live and DVR flag to true and propagate streamTypeChange event with 'dvr' value (mainly to the controlbar plugin)
                    if (!this._isLive) {
                        this._isLive = true;
                        this._isDVR = false;
                        this.sendUpdate('streamTypeChange', 'live');
                    }
                }
                /*
                 * Otherwise we've got DVR stream
                 */
                else {
                    // set live and DVR flag to true and propagate streamTypeChange event with 'dvr' value (mainly to the controlbar plugin)
                    if (!this._isDVR && !this._isLive) {
                        this._isLive = true;
                        this._isDVR = true;
                        this.sendUpdate('streamTypeChange', 'dvr');
                    }
                    /*
                     * When seekable.start(0) is >0 the seekable.start is probably set properly (e.g. Safari 7.0.5 on OS X 10.9.4)
                     * so we could use it to determine DVR window duration
                     */
                    if (obj.seekable.start(0) > 0) {
                        duration = parseFloat((obj.seekable.end(0) - obj.seekable.start(0)).toFixed(2));
                    }
                    /*
                     * When seekable.start(0) == 0 then the only way to determine DVR window is to get the first known seekable.end(0)
                     * value and store it for the whole live session (e.g. Safari 7.0 on iOS 7.1.2).
                     * It's not 100% reliable method, but it's the best estimation we could possibly get.
                     */
                    else {
                        if (obj.seekable.end(0) > 0 && this.media.duration === 0) {
                            duration = parseFloat(obj.seekable.end(0).toFixed(2));
                        }
                        else {
                            duration = this.media.duration;
                        }
                    }
                    position = (duration - (obj.seekable.end(0) - obj.currentTime));
                    position = position < 0 ? 0 : parseFloat(position.toFixed(2));
                }
            }
            /*
             * If duration is a number
             */
            else if (!isNaN(obj.duration)) {
                duration = obj.duration > position ? parseFloat((obj.duration || 0).toFixed(2)) : 0; // Android native browsers tend to report bad duration (1-100s)
            }

            // duration has changed:
            if (duration !== null && (duration !== this.media.duration)) {
                this.media.duration = duration;
                this.sendUpdate('durationChange', duration);
            }

            this.media.position = position;

            this.media.maxpos = Math.max(this.media.maxpos || 0, this.media.position || 0);
            this.media.playProgress = parseFloat((this.media.position > 0 && this.media.duration > 0) ? this.media.position * 100 / this.media.duration : 0);
            this.media.frame = this.media.position * this.pp.getConfig('fps');

            this.sendUpdate('time', this.media.position);

            this.loadProgressUpdate();
        },
        loadProgressUpdate: function () {

            var me = this.mediaElement.get(0),
                progress = 0;

            if (this.media.duration === 0) {
                return;
            }
            if (typeof me.buffered !== 'object') {
                return;
            }
            if (me.buffered.length === 0 && me.seekable.length === 0) {
                return;
            }
            if (this.media.loadProgress === 100) {
                return;
            }

            if (me.seekable && me.seekable.length > 0) {
                progress = Math.round(me.seekable.end(0) * 100 / this.media.duration);
            } else {
                progress = Math.round(me.buffered.end(me.buffered.length - 1) * 100) / this.media.duration;
            }

            if (this.media.loadProgress > progress) {
                return;
            }

            this.media.loadProgress = (this.allowRandomSeek === true) ? 100 : -1;
            this.media.loadProgress = (this.media.loadProgress < 100 || this.media.loadProgress === undefined) ? progress : 100;

            this.sendUpdate('progress', this.media.loadProgress);

        },
        progressListener: function (obj, evt) {

            // we prefer time ranges but keep catching "progress" events by default
            // for historical and compatibility reasons:
            if (this.mediaElement instanceof jQuery) { // fix this - make sure all instances are jquery objects
                if (typeof this.mediaElement.get(0).buffered === 'object') {
                    if (this.mediaElement.get(0).buffered.length > 0) {
                        this.mediaElement.off('progress');
                        return;
                    }
                }
            }

            if (this._bandWidthTimer == null) {
                this._bandWidthTimer = (new Date()).getTime();
            }

            var current = 0,
                total = 0;

            try {
                if (!isNaN(evt.loaded / evt.total)) {
                    current = evt.loaded;
                    total = evt.total;
                } else if (evt.originalEvent && !isNaN(evt.originalEvent.loaded / evt.originalEvent.total)) {
                    current = evt.originalEvent.loaded;
                    total = evt.originalEvent.total;
                }
            } catch (e) {
                if (obj && !isNaN(obj.loaded / obj.total)) {
                    current = obj.loaded;
                    total = obj.total;
                }
            }

            var loadedPercent = (current > 0 && total > 0) ? current * 100 / total : 0;

            if (Math.round(loadedPercent) > Math.round(this.media.loadProgress)) {
                this._KbPerSec = ((current / 1024) / (((new Date()).getTime() - this._bandWidthTimer) / 1000));
            }

            loadedPercent = (this.media.loadProgress !== 100) ? loadedPercent : 100;
            loadedPercent = (this.allowRandomSeek === true) ? 100 : 5 * Math.round(loadedPercent / 5);

            if (this.media.loadProgress != loadedPercent) {
                this.media.loadProgress = loadedPercent;
                this.sendUpdate('progress', loadedPercent);
            }

            // Mac flash fix:
            if (this.media.loadProgress >= 100 && this.allowRandomSeek === false) {
                this._setBufferState('FULL');
            }
        },
        qualityChangeListener: function () {
            this.sendUpdate('qualityChange', this._quality);
        },
        endedListener: function (obj) {
            if (this.mediaElement === null) {
                return;
            }
            if (this.media.maxpos <= 0) {
                return;
            }
            if (this.getState() === 'STARTING') {
                return;
            } 
            this._setState('completed');
        },
        waitingListener: function (event) {
            this._setBufferState('EMPTY');
        },
        canplayListener: function (obj) {
            this._setBufferState('FULL');
        },
        canplaythroughListener: function (obj) {
            this._setBufferState('FULL');
        },
        playingListener: function (obj) {
            this._setState('playing');
        },
        pauseListener: function (obj) {
            this._setState('paused');
        },
        fullscreenchangeListener: function(value){
            this.applyCommand('fullscreen', value);
        },
        resizeListener: function(obj) {
            try {
                if(this.media.videoWidth !== obj.videoWidth || this.media.videoHeight !== obj.videoHeight){
                    this.media.videoWidth = obj.videoWidth;
                    this.media.videoHeight = obj.videoHeight;
                    this._scaleVideo();
                }
            }
            catch(e){
                $p.log('resizeListener error', e);
            }
        },
        seekedListener: function (value) {
            this._setSeekState('SEEKED', value || this.media.position);
        },
        volumeListener: function (obj) {
            var newVolume = obj.volume !== void(0) ? parseFloat(obj.volume) : parseFloat(obj);
            if(newVolume !== this._volume) {
                this._volume = newVolume;
                
                // mute / unmute 
                this.setMuted(this._volume === 0);
                this.sendUpdate('volume', newVolume);
            }
        },
        errorListener: function (event, obj) {
        },
        nullListener: function (obj) {
        },
        applySrc: function () {
        },
        applyImage: function (url, destObj) {

            var imageObj = $('<img/>').hide(),
                currentImageObj = $("." + this.pp.getMediaId() + "_image"),
                // select by class to workaround timing issues causing multiple <img> of the same ID being present in the DOM
                ref = this;

            $p.utils.blockSelection(imageObj);

            // empty URL... apply placeholder
            if (url == null || url === false) {
                currentImageObj.remove();
                return $('<img/>').attr({
                    "id": this.pp.getMediaId() + "_image",
                    "src": $p.utils.imageDummy()
                }).appendTo(destObj);
            }

            // no changes
            if ($(currentImageObj[0]).attr('src') == url) {
                if ($p.utils.stretch(ref.pp.getConfig('imageScaling'), $(currentImageObj[0]), destObj.width(), destObj.height())) {
                    try {
                        ref.sendUpdate('scaled', {
                            originalWidth: currentImageObj._originalDimensions.width,
                            originalHeight: currentImageObj._originalDimensions.height,
                            scaledWidth: ref.mediaElement.width(),
                            scaledHeight: ref.mediaElement.height(),
                            displayWidth: destObj.width(),
                            displayHeight: destObj.height()
                        });
                    } catch (e) {
                    }
                }
                return $(currentImageObj[0]);
            }

            imageObj.on("load", function (event) {
                var target = $(event.currentTarget),
                    imgObj;

                if (!imageObj.attr("data-od-width")){
                    imageObj.attr("data-od-width", target[0].naturalWidth);
                }
                if (!imageObj.attr("data-od-height")){
                    imageObj.attr("data-od-height", target[0].naturalHeight);
                }

                currentImageObj.remove();

                imageObj.attr('id', ref.pp.getMediaId() + "_image");
                imageObj.show();

                if ($p.utils.stretch(ref.pp.getConfig('imageScaling'), target, destObj.width(), destObj.height())) {
                    try {
                        ref.sendUpdate('scaled', {
                            originalWidth: imgObj._originalDimensions.width,
                            originalHeight: imgObj._originalDimensions.height,
                            scaledWidth: ref.mediaElement.width(),
                            scaledHeight: ref.mediaElement.height(),
                            displayWidth: destObj.width(),
                            displayHeight: destObj.height()
                        });
                    } catch (e) {
                    }
                }
            });

            imageObj.removeData('od');

            this.pp.removeListener('fullscreen.poster');
            this.pp.removeListener('resize.poster');

            this.pp.addListener('fullscreen.poster', function () {
                ref.applyImage(ref.getPoster(), destObj);
            });

            this.pp.addListener('resize.poster', function () {
                ref.applyImage(ref.getPoster(), destObj);
            });

            imageObj.appendTo(destObj).attr({
                "alt": this.pp.getConfig('title') || ''
            }).css({
                position: 'absolute'
            }).addClass(this.pp.getMediaId() + "_image");

            // IE<9 trap:
            imageObj.attr('src', url);

            imageObj.on("error", function (event) {
                $(this).remove();
                currentImageObj.show();
            });

            return imageObj;
        },
        _setState: function (state) {
            var ref = this,
                state = state.toUpperCase(),
                old = this._currentState;

            this._currentState = state.toUpperCase();

            if (old !== state && old !== 'ERROR') {
                if (old === 'PAUSED' && state === 'PLAYING') {
                    this.sendUpdate('resume', this.media);
                    this._isPlaying = true;
                }

                if ((old === 'IDLE' || old === 'STARTING') && state === 'PLAYING') {
                    this.sendUpdate('start', this.media);
                    this._isPlaying = true;
                }

                if (state === 'PAUSED') {
                    this._isPlaying = false;
                    this._setBufferState('FULL');
                }

                if (state === 'ERROR') {
                    this.setPlay = this.setPause = function () {
                        ref.sendUpdate('start');
                    };
                }

                this.sendUpdate('state', this._currentState);
            }
        },
        _setBufferState: function (state) {
            if (this._currentBufferState !== state.toUpperCase()) {
                this._currentBufferState = state.toUpperCase();
                this.sendUpdate('buffer', this._currentBufferState);
            }
        },
        _setSeekState: function (state, value) {
            if (this._currentSeekState !== state.toUpperCase()) {
                this._currentSeekState = state.toUpperCase();
                this.sendUpdate('seek', this._currentSeekState, value);
            }
        },
        _scaleVideo: function () {
            var mediaDisplay = this.pp.getMediaContainer(),
                displayWidth, displayHeight,
                videoWidth, videoHeight;

            try {
                displayWidth = mediaDisplay.width();
                displayHeight = mediaDisplay.height();
                videoWidth = this.media.videoWidth;
                videoHeight = this.media.videoHeight;

                if (this.mediaElement.attr("data-od-width") != videoWidth) {
                    this.mediaElement.attr("data-od-width", videoWidth);
                }
                if (this.mediaElement.attr("data-od-height") != videoHeight) {
                    this.mediaElement.attr("data-od-height", videoHeight);
                }

                if ($p.utils.stretch(this.pp.getConfig('videoScaling'), this.mediaElement, displayWidth, displayHeight)) {
                    this.sendUpdate('scaled', {
                        originalWidth: videoWidth,
                        originalHeight: videoHeight,
                        scaledWidth: this.mediaElement.width(),
                        scaledHeight: this.mediaElement.height(),
                        displayWidth: displayWidth,
                        displayHeight: displayHeight
                    });
                }
            } catch (e) {
                $p.utils.log('_scaleVideo error', e);
            }
        }
    };

    return playerModel;
    
}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2010, 2011, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
*/
(function(window, document, $, $p){

    "use strict";
    
$p.newModel({
    modelId: 'NA',
    browserVersion: '1.0',
    iLove: [
        {ext:'na', type:'none/none', platform: ['browser']}
    ],
    hasGUI: true,

    applyMedia: function(destContainer) {

        destContainer.html('');
        this.displayReady();

        this.sendUpdate( 'error', this.media.errorCode);

        if (!this.pp.getConfig('enableTestcard')) {
            if(this.media.file.length && this.media.file[0].src) {
                window.location.href = this.media.file[0].src;
            }
        }
    }
});

}(window, document, jQuery, projekktor));
/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2010, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
*/
(function(window, document, $, $p){
    
    "use strict";

$p.newModel({

    modelId: 'VIDEO',
    androidVersion: "4.0",
    iosVersion: "5.0",
    nativeVersion: "1.0",
    iLove: [
        {ext:'mp4', type:'video/mp4', platform:['ios', 'android', 'native']},
        {ext:'m4v', type:'video/mp4', platform:['ios', 'android', 'native']},
        {ext:'ogv', type:'video/ogg', platform:['native']},
        {ext:'webm',type:'video/webm', platform:['native']},
        {ext:'ogg', type:'video/ogg', platform:['native']},
        {ext:'anx', type:'video/ogg', platform:['native']}
    ],

    _eventMap: {
        pause:          "pauseListener",
        play:           "playingListener",
        volumechange:   "volumeListener",
        progress:       "progressListener",
        timeupdate:     "_timeupdate",
        ended:          "_ended",
        waiting:        "waitingListener",
        canplaythrough: "canplayListener",
        canplay:        "canplayListener",
        // suspend:        "suspendListener",
        // abort:          "abortListener",
        error:          "errorListener",
        emptied:        "emptiedListener",
        stalled:        "stalledListener",
        seeked:         "seekedListener",
        loadedmetadata: "resizeListener",
        loadeddata:     "resizeListener",
        resize:         "resizeListener",
        // loadstart:      null,
        webkitbeginfullscreen: "webkitfullscreenListener",
        webkitendfullscreen: "webkitfullscreenListener"
    },
    _eventsBinded: [],
    allowRandomSeek: false,
    videoWidth: 0,
    videoHeight: 0,
    wasPersistent: true,
    endedTimeout: 0,
    displayingFullscreen: false,
    _lastPosition: null,

    init: function() {
        this._lastPosition = null;
        this._eventsBinded = [];
        this.ready();
    },

    applyMedia: function(destContainer) {

        if ($('#'+this.pp.getMediaId()+"_html").length === 0) {

            this.wasPersistent = false;

            destContainer.html('').append(
                $('<video/>')
                .attr({
                    "id": this.pp.getMediaId()+"_html",
                    "loop": false,
                    "autoplay": false,
                    "preload": "none",
                    "x-webkit-airplay": "allow",
                    "playsinline": ""
                }).prop({
                    controls: false,
                    volume: this.getVolume(),
                    muted: this.getMuted()
                }).css({
                    'width': '100%',
                    'height': '100%',
                    'position': 'absolute',
                    'top': 0,
                    'left': 0
                })
            );
        }

        this.mediaElement = $('#'+this.pp.getMediaId()+"_html");
        this.addListeners();
        this.applySrc();
    },

    applySrc: function() {
        var ref = this,
            media = this.getSource(),
            wasAwakening = ref.getState('AWAKENING');

        /*
         * Using 'src' attribute directly in <video> element is safer than using it inside <source> elements.
         * Some of the mobile browsers (e.g. Samsung Galaxy S2, S3 Android native browsers <= 4.2.2)
         * will not initialize video playback with <source> elements at all, displaying only gray screen instead.
         * HLS stream on iOS and Android will not work if its URL is defined through <source> 'src' attribute
         * instead of <video> 'src' attribute.
         */
        this.mediaElement.attr('src', media[0].src);
        this.mediaElement.attr('type', media[0].type );

        /*
         * Some of the mobile browsers (e.g. Android native browsers <= 4.2.x, Opera Mobile)
         * have by default play/pause actions bound directly to click/mousedown events of <video>.
         * That causes conflict with display plugin play/pause actions, which makes it impossible
         * to pause the currently playing video. Precisely _setState is called twice:
         * first by pauseListener triggered by <video> default click/mousedown action,
         * secondly by display plugin actions bound to mousedown events. The result is that
         * the video is paused by native <video> events and then immediately started by display
         * plugin that uses the setPlayPause function. setPlayPause function toggles between
         * "PAUSED" and "PLAYING" states, so when a video is being played, the function causes its pausing.
         */
        this.mediaElement.on('mousedown.projekktorqs'+this.pp.getId(), this.disableDefaultVideoElementActions);
        this.mediaElement.on('click.projekktorqs'+this.pp.getId(), this.disableDefaultVideoElementActions);

        var func = function(e){
            ref.mediaElement.off('loadstart.projekktorqs'+ref.pp.getId());
            ref.mediaElement.off('loadeddata.projekktorqs'+ref.pp.getId());
            ref.mediaElement.off('canplay.projekktorqs'+ref.pp.getId());

            ref.mediaElement = $('#'+ref.pp.getMediaId()+"_html");

            if (wasAwakening) {
                ref.displayReady();
                return;
            }

            if (ref.getSeekState('SEEKING')) {
                if (ref._isPlaying){
                    ref.setPlay();
                }

                ref.seekedListener();
                return;
            }

            ref.setSeek(ref.media.position || 0);

            if (ref._isPlaying){
                ref.setPlay();
            }

        };

        this.mediaElement.on('loadstart.projekktorqs'+this.pp.getId(), func);
        this.mediaElement.on('loadeddata.projekktorqs'+this.pp.getId(), func);
        this.mediaElement.on('canplay.projekktorqs'+this.pp.getId(), func);

        this.mediaElement[0].load(); // important especially for iOS devices
    },

    detachMedia: function() {
        try {
            this.mediaElement.off('.projekktorqs'+this.pp.getId());
            this.mediaElement[0].pause();
        } catch(e){}
    },

    /*****************************************
     * Handle Events
     ****************************************/
    addListeners: function(evtId, subId) {
        if (this.mediaElement==null) {
            return;
        }
        var id = (subId!=null) ? '.projekktor'+subId+this.pp.getId() : '.projekktor'+this.pp.getId(),
            ref = this,
            evt = (evtId==null) ? '*' : evtId;

        $.each(this._eventMap, function(key, value){
            if ((key==evt || evt=='*') && value!=null && ref._eventsBinded.indexOf(key) === -1) {
                ref.mediaElement.on(key + id, function(evt) { ref[value](this, evt); });
                ref._eventsBinded.push(key);
            }
        });
    },

    removeListeners: function(evt, subId) {
        if (this.mediaElement==null) {
            return;
        }
        evt = (evt === void 0) ? '*' : evt;

        var id = (subId!=null) ? '.projekktor'+subId+this.pp.getId() : '.projekktor'+this.pp.getId(),
            ref = this;

        $.each(this._eventMap, function(key, value){
            if (key === evt || evt === '*') {
                ref.mediaElement.off(key + id);
                var idx = ref._eventsBinded.indexOf(key);
                if(idx>-1){
                    ref._eventsBinded.splice(idx,1);
                }
            }
        });
    },

    // Workaround for problems with firing ended event in Chromium based browsers
    // e.g. Samsung Galaxy S4 on Android 4.4.2 KitKat native Internet Browser 1.5.28 1528 based on Chrome 28.0.1500.94
    // More info about the issues with ended event here: https://code.google.com/p/chromium/issues/detail?id=349543
    _timeupdate: function(video, event) {
        var ref = this;
        if(video.duration - video.currentTime < 1) {
            this.endedTimeout = setTimeout(function(){
                clearTimeout(ref.endedTimeout);
                if(!video.paused && Math.round(video.duration - video.currentTime) === 0){
                    $p.utils.log('VIDEO model: ended event forced');
                    ref._ended();
                }
            }, 1000);
        }
        // check for video size change (e.g. HLS on Safari OSX or iOS)
        this.resizeListener(video);

        // IE & Edge firing timeupdate event even if the currentTime didn't change,
        // this has place when the video is buffering and cause IE & Edge
        // don't fire waiting & stalled events we can use that bug to set
        // buffering state to 'EMPTY'. It's a hack but it's working.
        if(video.currentTime !== this._lastPosition){
            // we assume that the buffer is full when the video time was updated
            if(this._lastPosition !== null){
                this._setBufferState('FULL');
            }
            this._lastPosition = video.currentTime;
            this.timeListener.apply(this, arguments);
        }
        else {
            this._setBufferState('EMPTY');
        }
    },

    _ended: function() {
        clearTimeout(this.endedTimeout);

        var dur = this.mediaElement[0].duration, // strange android behavior workaround
            complete = (Math.round(this.media.position) === Math.round(dur)),
            fixedEnd = ( (dur-this.media.maxpos) < 2 ) && (this.media.position===0) || false;

        if (complete || fixedEnd) {
            this.endedListener(this);
        } else {
            this.pauseListener(this);
        }
    },

    playingListener: function(obj) {
        var ref = this;
        (function pl() {
            try{
                if (ref.getDuration()===0) {
                    if(ref.mediaElement.get(0).currentSrc!=='' && ref.mediaElement.get(0).networkState==ref.mediaElement.get(0).NETWORK_NO_SOURCE) {
                        ref.sendUpdate('error', 80);
                        return;
                    }
                    setTimeout(pl, 500);
                    return;
                }
            } catch(e) {}
        })();

        this._setState('playing');
    },

    errorListener: function(obj, evt) {
        try {
            switch (evt.target.error.code) {
                case evt.target.error.MEDIA_ERR_ABORTED:
                    this.sendUpdate('error', 1);
                    break;
                case evt.target.error.MEDIA_ERR_NETWORK:
                    this.sendUpdate('error', 2);
                    break;
                case evt.target.error.MEDIA_ERR_DECODE:
                    this.sendUpdate('error', 3);
                    break;
                case evt.target.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
                    this.sendUpdate('error', 4);
                    break;
                default:
                    this.sendUpdate('error', 5);
                    break;
            }
        } catch(e) {}
    },

    emptiedListener: function (obj) {
        this._setBufferState('EMPTY');
    },

    stalledListener: function (obj) {
        this._setBufferState('EMPTY');
    },

    canplayListener: function(obj) {
        this._setBufferState('FULL');
    },

    webkitfullscreenListener: function(evt){
        this.displayingFullscreen = this.mediaElement[0][$p.fullscreenApi.mediaonly.displayingFullscreen];
        this.fullscreenchangeListener(this.displayingFullscreen);
    },

    disableDefaultVideoElementActions: function(evt){
            evt.preventDefault();
    },

    getMediaStatus: function(name){
        if($p.utils.logging){
            var m = this.mediaElement[0],
                networkState = m.networkState,
                readyState = m.readyState,
                error = m.error,
                pos = m.currentTime,
                dur = m.duration,
                buffered = m.buffered,
                seekable = m.seekable;

            $p.utils.log('| ' + name + ' |');
            $p.utils.log(
                        '| networkState: ', this._getNetworkStateName(networkState),
                        'readyState: ', this._getReadyStateName(readyState),
                        'error: ', this._getErrorName(error)
                        );
            $p.utils.log('| duration: ', dur, 'currentTime: ', pos);
            $p.utils.log('| buffered: ', this._loopThroughTimeRanges(buffered));
            $p.utils.log('| seekable: ', this._loopThroughTimeRanges(seekable));
        }
    },

    _getNetworkStateName: function(networkStateCode){
        var result = networkStateCode + " - ";
        switch(networkStateCode){
            case 0:
                result += "NETWORK_EMPTY";
                break;
            case 1:
                result += "NETWORK_IDLE";
                break;
            case 2:
                result += "NETWORK_LOADING";
                break;
            case 3:
                result += "NETWORK_NO_SOURCE";
                break;
        }
        return result;
    },

    _getReadyStateName: function(readyStateCode){
        var result = readyStateCode + " - ";
        switch(readyStateCode){
            case 0:
                result += "HAVE_NOTHING";
                break;
            case 1:
                result += "HAVE_METADATA";
                break;
            case 2:
                result += "HAVE_CURRENT_DATA";
                break;
            case 3:
                result += "HAVE_FUTURE_DATA";
                break;
            case 4:
                result += "HAVE_ENOUGH_DATA";
                break;
        }
        return result;
    },

    _getErrorName: function(errorCode){
        var result = errorCode + " - ";
        switch(errorCode){
            case 1:
                result += "MEDIA_ERR_ABORTED";
                break;
            case 2:
                result += "MEDIA_ERR_NETWORK";
                break;
            case 3:
                result += "MEDIA_ERR_DECODE";
                break;
            case 4:
                result += "MEDIA_ERR_SRC_NOT_SUPPORTED";
                break;
        }
        return result;
    },

    _loopThroughTimeRanges: function(timeRanges) {
        var i = 0,
            l = timeRanges.length,
            result = "length: " + l + "; ";

        for(; i<l; i++){
            result += "#" + i + " - ";
            result += "start: " + timeRanges.start(i) + ", ";
            result += "end: " + timeRanges.end(i);
            result += "; ";
        }

        return result;
    },

    /*****************************************
     * Setters
     ****************************************/
    setPlay: function() {
        var ref = this, 
            promise;

        try {
            promise = this.mediaElement[0].play();

            if (promise !== undefined) {
                promise.catch(function(error) {
                    // Auto-play was prevented reset and disable autoplay
                    ref.pp.setActiveItem(0, false);
                });
            }
            
        } catch(e){}
    },

    setPause: function() {
        try {this.mediaElement[0].pause();} catch(e){}
    },

    setVolume: function(volume) {
        if (this.mediaElement === null || !$p.features.volumecontrol) {
            this.volumeListener(volume);
        }
        else {
            this.mediaElement.prop('volume', volume);
        }
    },

    setMuted: function(muted) {
        if (this.mediaElement === null) {
            this.volumeListener(0);
        }
        else {
            this.mediaElement.prop('muted', muted);
        }
    },

    setSeek: function(newpos) {
        var ref = this,
            np = newpos,
            relPos = true;

        // IE9 sometimes raises INDEX_SIZE_ERR
        (function ss(){
            try {
                // if it's a DVR stream
                if(ref._isDVR){
                    /*
                     * iOS 7.1.2 Safari 7.0 behavior is weird cause it takes absolute values
                     * when the OSX 10.9.4 Safari 7.0.5 takes relative values for seeking through timeline.
                     * E.g. when we want to seek to the beginning of the DVR window which duration is 60s
                     * and the stream already plays for 120s on iOS Safari we must seek to 0 position, when
                     * on OSX Safari we must seek to 60 position. Same for seeking to the live point:
                     * on iOS Safari we must seek to the 60 position (duration of DVR window) but on
                     * OSX Safari we must seek to the seeking.end(0) position, which is in our case 120.
                     */
                    relPos = (ref.mediaElement[0].seekable.start(0) > 0);
                    if(newpos<0) { // snap to live position
                        if(relPos){
                            np = ref.mediaElement[0].seekable.end(0)-2;
                        }
                        else {
                            np = ref.media.duration;
                        }
                    }
                    else {
                        if(relPos){
                            np = ref.mediaElement[0].seekable.end(0) - (ref.media.duration - newpos);
                        }
                        else {
                            np = newpos;
                        }
                    }
                }

                ref.mediaElement[0].currentTime = np;
                ref.timeListener({position: np});
            }
            catch(e){
                if (ref.mediaElement !== null) {
                    setTimeout(ss, 100);
                }
            }

        })();
    },
    /************************************************
     * getters
     ************************************************/

    getVolume: function () {
        if (this.mediaElement === null) {
            return this._volume;
        }

        return this.mediaElement.prop('volume');
    },

    getMuted: function () {
        if (this.mediaElement === null) {
            return this._volume === 0;
        }

        return this.mediaElement.prop('muted');
    }
});

$p.newModel({

    modelId: 'AUDIO',

    iLove: [
        {ext:'ogg', type:'audio/ogg', platform:['native']},
        {ext:'oga', type:'audio/ogg', platform:['native']},
        {ext:'mp3', type:'audio/mp3', platform:['ios', 'android', 'native']},
        {ext:'mp3', type:'audio/mpeg', platform:['ios', 'android', 'native']}
    ],

    imageElement: {},

    applyMedia: function(destContainer) {

        $p.utils.blockSelection(destContainer);

        if ($('#'+this.pp.getMediaId()+"_html").length===0) {
            this.wasPersistent = false;
            destContainer.append(
                $('<audio/>')
                .attr({
                    "id": this.pp.getMediaId()+"_html",
                    "poster": $p.utils.imageDummy(),
                    "loop": false,
                    "autoplay": false,
                    "preload": "none",
                    "x-webkit-airplay": "allow",
                    "playsinline": ""
                }).prop({
                    controls: false,
                    volume: this.getVolume()
                }).css({
                    'width': '1px',
                    'height': '1px',
                    'position': 'absolute',
                    'top': 0,
                    'left': 0
                })
            );
        }
        // create cover image
        this.imageElement = this.applyImage(this.getPoster('cover') || this.getPoster('poster'), destContainer);
        this.imageElement.css({border: '0px'});

        this.mediaElement = $('#'+this.pp.getMediaId()+"_html");
        this.applySrc();
    },

    setPosterLive: function() {
        if (this.imageElement.parent) {
            var dest = this.imageElement.parent(),
            ref = this;

            if (this.imageElement.attr('src') == this.getPoster('cover') || this.getPoster('poster')) {
                return;
            }

            this.imageElement.fadeOut('fast', function() {
                $(this).remove();
                ref.imageElement = ref.applyImage(ref.getPoster('cover') || ref.getPoster('poster'), dest );
            });
        }
    }

}, 'VIDEO');

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://www.projekktor.com
 *
 * Copyright 2014, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
*/
(function(window, document, $, $p){
    
    "use strict";
    
$p.newModel({
    modelId: 'VIDEOHLS',
    androidVersion: '4.1',
    iosVersion: '5.0',
    iLove: [
        {ext:'m3u8', type:'application/vnd.apple.mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u', type:'application/vnd.apple.mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u8', type:'application/x-mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u', type:'application/x-mpegurl', platform: ['ios', 'android', 'native']}
    ]
}, 'VIDEO');

$p.newModel({
    modelId: 'AUDIOHLS',
    androidVersion: '4.1',
    iosVersion: '5.0',
    iLove: [
        {ext:'m3u8', type:'application/vnd.apple.mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u', type:'application/vnd.apple.mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u8', type:'application/x-mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u', type:'application/x-mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u8', type:'audio/mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u', type:'audio/mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u8', type:'audio/x-mpegurl', platform: ['ios', 'android', 'native']},
        {ext:'m3u', type:'audio/x-mpegurl', platform: ['ios', 'android', 'native']}
    ]
}, 'AUDIO');

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor zwei
 * http://filenew.org/projekktor/
 *
 * Copyright 2010, 2011, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
*/
(function(window, document, $, $p){
    
    "use strict";

$p.newModel({

    modelId: 'PLAYLIST',
    browserVersion: '1.0',
    iLove: [
        {ext:'json', type:'text/json', platform: ['browser']},
        {ext:'xml', type:'text/xml', platform: ['browser']},
        {ext:'json', type:'application/json', platform: ['browser']},
        {ext:'xml', type:'application/xml', platform: ['browser']}
    ],

    applyMedia: function(destContainer) {
        this.displayReady();
    },

    setPlay: function() {
        this.sendUpdate('playlist', this.media);
    }
});

}(window, document, jQuery, projekktor));
/*
 * this file is part of:
 * projekktor zwei
 * http://filenew.org/projekktor/
 *
 * Copyright 2010, 2011, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
*/

(function(window, document, $, $p){

    "use strict";

$p.newModel({

    modelId: 'IMAGE',
    browserVersion: "1.0",
    iLove: [
        {ext:'jpg', type:'image/jpeg', platform: ['browser']},
        {ext:'gif', type:'image/gif', platform: ['browser']},
        {ext:'png', type:'image/png', platform: ['browser']}
    ],

    allowRandomSeek: true,

    _position: 0,
    _duration: 0,
    _fixedVolume: true,

    applyMedia: function(destContainer) {
        this.mediaElement = this.applyImage(this.media.file[0].src, destContainer.html(''));
        this._duration = this.pp.getConfig('duration') || 1;
        this._position = -1;
        this.displayReady();
        this._position = -0.5;
    },

    /* start timer */
    setPlay: function() {

        var ref = this;

        this._setBufferState('FULL');
        this.progressListener(100);
        this.playingListener();

        if (this._duration==0) {
            ref._setState('completed');
            return;
        }

        (function sp() {
            if (ref._position>=ref._duration) {
                ref._setState('completed');
                return;
            }

            if (!ref.getState('PLAYING')) {
                return;
            }

            ref.timeListener({duration: ref._duration, position:ref._position});
            setTimeout(sp, 200);
            ref._position += 0.2;
        })();

    },

    detachMedia: function() {
        this.mediaElement.remove();
    },

    setPause: function() {
        this.pauseListener();
    },

    setSeek: function(newpos) {
        if (newpos<this._duration) {
            this._position = newpos;
            this.seekedListener()
        }
    }

});

$p.newModel({

    modelId: 'HTML',
    browserVersion: "1.0",
    iLove: [
        {ext:'html', type:'text/html', platform: ['browser']}
    ],

   applyMedia: function(destContainer) {
        var ref = this;

        this.mediaElement = $(document.createElement('iframe')).attr({
            "id": this.pp.getMediaId()+"_iframe",
            "name": this.pp.getMediaId()+"_iframe",
            "src": this.media.file[0].src,
            "scrolling": 'no',
            "frameborder": "0",
            'width': '100%',
            'height': '100%'
        }).css({
            'overflow': 'hidden',
            'border': '0px',
            "width": '100%',
            "height": '100%'
        }).appendTo(destContainer.html(''));

        this.mediaElement.load(function(event){ref.success();});
        this.mediaElement.error(function(event){ref.remove();});

        this._duration = this.pp.getConfig('duration');

    },

    success: function() {
        this.displayReady();
    },

    remove: function() {
        this.mediaElement.remove();
    }
}, 'IMAGE');

}(window, document, jQuery, projekktor));/*
 * this file is part of:
 * projekktor player
 * http://www.projekktor.com
 *
 * Copyright 2016-2017 - Radosław Włodkowski, www.wlodkowski.net, radoslaw@wlodkowski.net
 * 
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 *
 * This model is interfacing hls.js library
 *
 * hls.js
 * Website: https://github.com/video-dev/hls.js
 * License: Apache 2.0 License
 *
 */

(function(window, document, $, $p){

    "use strict";

    $p.newModel({

        modelId: 'MSEVIDEOHLS',
        mseVersion: '1.0',

        iLove: [{
            ext: 'm3u8',
            type: 'application/x-mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u8',
            type: 'application/vnd.apple.mpegurl',
            platform: ['mse']
        }],

        _hlsjs: null,
        _hlsjsPlatformConfig: {},

        availableQualities: {},

        _qualitySwitching: false,
        _isDynamicStream: false,
        _requestedDynamicStreamIndex: -1, // inited with "auto switch" value to indicate that no index was manually requested
        _bufferTime: 0,
        _liveOffset: 2,

        applyMedia: function (destContainer) {

            var ref = this,
                hlsJsLoadSuccess = function () {
                    if ($('#' + ref.pp.getMediaId() + "_html").length === 0) {

                        ref.wasPersistent = false;

                        destContainer.html('').append(
                            $('<video/>')
                            .attr({
                                "id": ref.pp.getMediaId() + "_html",
                                "poster": $p.utils.imageDummy(),
                                "loop": false,
                                "autoplay": false,
                                "preload": "auto",
                                "x-webkit-airplay": "allow",
                                "playsinline": ""
                            }).prop({
                                controls: false,
                                volume: ref.getVolume()
                            }).css({
                                'width': '100%',
                                'height': '100%',
                                'position': 'absolute',
                                'top': 0,
                                'left': 0
                            })
                        );
                    }

                    ref.mediaElement = $('#' + ref.pp.getMediaId() + "_html");
                    ref.addListeners();
                    ref.applySrc();
                },
                hlsJsLoadFailed = function (jqxhr, settings, exception) {
                    ref.sendUpdate('error', 2);
                },
                msePlatformConfig = this.pp.getConfig('platformsConfig').mse || {};
            
            // guarantee hls.js config values
            $.extend(true, ref._hlsjsPlatformConfig, {src:'/MISSING_PATH_TO_HLSJS_LIB/', initVars:{}}, msePlatformConfig.hlsjs);
            
            // check if hls.js is already loaded
            if (window.Hls && typeof window.Hls.isSupported === 'function') {
                // just continue
                hlsJsLoadSuccess();
            } else {
                // load hls.js
                $p.utils.getScript(ref._hlsjsPlatformConfig.src, {
                        cache: true
                    })
                    .done(hlsJsLoadSuccess)
                    .fail(hlsJsLoadFailed);
            }
        },

        applySrc: function () {
            var ref = this,
                media = ref.getSource(),
                wasAwakening = ref.getState('AWAKENING');

            ref._hlsjs = new Hls(ref._hlsjsPlatformConfig.initVars);

            ref._hlsjs.loadSource(media[0].src);
            ref._hlsjs.attachMedia(ref.mediaElement[0]);
            // add hlsjs event listeners
            ref._hlsjs.on(Hls.Events.MANIFEST_PARSED, function (event, data) {
                ref.updateAvailableDynamicStreamsQualities(data);
                if (wasAwakening) {
                    ref.displayReady();
                    return;
                }

                if (ref.getSeekState('SEEKING')) {
                    if (ref._isPlaying) {
                        ref.setPlay();
                    }

                    ref.seekedListener();
                    return;
                }

                if (ref._isPlaying) {
                    ref.setPlay();
                }
            });
            ref._hlsjs.on(Hls.Events.LEVEL_SWITCH, function (event, data) {
                ref.qualityChangeListener();
            });

            /*
             * Some of the mobile browsers (e.g. Android native browsers <= 4.2.x, Opera Mobile)
             * have by default play/pause actions bound directly to click/mousedown events of <video>.
             * That causes conflict with display plugin play/pause actions, which makes it impossible
             * to pause the currently playing video. Precisely _setState is called twice:
             * first by pauseListener triggered by <video> default click/mousedown action,
             * secondly by display plugin actions bound to mousedown events. The result is that
             * the video is paused by native <video> events and then immediately started by display
             * plugin that uses the setPlayPause function. setPlayPause function toggles between
             * "PAUSED" and "PLAYING" states, so when a video is being played, the function causes its pausing.
             */
            this.mediaElement.on('mousedown.projekktorqs' + this.pp.getId(), this.disableDefaultVideoElementActions);
            this.mediaElement.on('click.projekktorqs' + this.pp.getId(), this.disableDefaultVideoElementActions);
        },

        detachMedia: function () {
            try {
                this._hlsjs.detachMedia();
                this._hlsjs.destroy();
                this.mediaElement.off('.projekktorqs' + this.pp.getId());
            } catch (e) {}
        },

        /**
         * Update projekktor internal quality keys for currently active playlist item
         * with hls.js dynamic stream item values
         *
         * To use different quality keys format than default:
         * audio/video key: '%{height}p | %{bitrate}kbps'
         * audio-only key: 'audio | %{bitrate}kbps'
         *
         * set 'dynamicStreamQualityKeyFormatAudioVideo', 'dynamicStreamQualityKeyFormatAudioOnly' config options respectively.
         *
         * To show audio-only qualities set 'dynamicStreamShowAudioOnlyQualities' config option to true (default: false)
         *
         * Note: Quality keys must have unique names, otherwise they will be overwritten.
         *
         * @returns {Array} - returns available dynamic streams quality keys in the projekktor's format
         */
        updateAvailableDynamicStreamsQualities: function (data) {

            var dynamicStreams = data.levels,
                numStreams = dynamicStreams.length,
                keyName = '',
                isAudioOnly = false,
                showAudioOnly = this.pp.getConfig('dynamicStreamShowAudioOnlyQualities'),
                avKeyFormat = this.pp.getConfig('dynamicStreamQualityKeyFormatAudioVideo'),
                aoKeyFormat = this.pp.getConfig('dynamicStreamQualityKeyFormatAudioOnly'),
                dpc = this.pp.getConfig('dynamicStreamQualityKeyBitrateRoundingDecimalPlacesCount'),
                bitrate = 0,
                bitrateKbps = 0,
                bitrateMbps = 0,
                bitrateUnit = 'kbps',
                qualityKeys = [];

            this.availableQualities = {};

            for (var i = 0; i < numStreams; i++) {
                if (dynamicStreams[i].bitrate !== undefined) {

                    bitrateKbps = Math.floor(dynamicStreams[i].bitrate / 1000);
                    bitrateMbps = $p.utils.roundNumber(bitrateKbps / 1000, dpc);
                    bitrate = bitrateKbps < 1000 ? bitrateKbps : bitrateMbps;
                    bitrateUnit = bitrateKbps < 1000 ? 'kbps' : 'Mbps';

                    // audio/video stream quality
                    if (dynamicStreams[i].height > 0) {
                        isAudioOnly = false;
                        keyName = $p.utils.parseTemplate(avKeyFormat, {
                            height: dynamicStreams[i].height,
                            width: dynamicStreams[i].width,
                            bitrate: bitrate,
                            bitrateunit: bitrateUnit,
                            bitratekbps: bitrateKbps,
                            bitratembps: bitrateMbps
                        });
                    }
                    // audio-only stream quality
                    else {
                        isAudioOnly = true;
                        if (showAudioOnly) {
                            keyName = $p.utils.parseTemplate(aoKeyFormat, {
                                bitrate: bitrate,
                                bitrateunit: bitrateUnit,
                                bitratekbps: bitrateKbps,
                                bitratembps: bitrateMbps
                            });
                        }
                    }

                    if (keyName.length && (isAudioOnly === showAudioOnly)) {
                        this.availableQualities[keyName] = i;
                        qualityKeys.push(keyName);
                    }
                }
            }

            // always add auto
            qualityKeys.push('auto');

            this._isDynamicStream = true; // important: set this before sending the update

            this.sendUpdate('availableQualitiesChange', qualityKeys);
            return qualityKeys;
        },

        /**
         * Switch to a specific dynamic stream index.
         *
         * @param {int} index - if < 0 then the automatic stream switch will be enabled,
         * otherwise if the index value is a valid stream index the manual switch will be performed
         *
         * @returns {mixed} - if the requested index is invalid, is the same as current index or is out of valid range function returns false
         * otherwise it returns requested index value.
         * Note: Always use strict comparison when using return value cause the lowest valid index could be 0.
         *
         * Note:  If the media is paused, switching will not take place until after play resumes.
         */
        switchDynamicStreamIndex: function (index) {
            // return if the index is NaN or is the current index or is out of range
            if ((isNaN(index) ||
                    (index < 0 && this.getAutoDynamicStreamSwitch()) ||
                    (index === this.getCurrentDynamicStreamIndex() && !this.getAutoDynamicStreamSwitch()) ||
                    index > this.getMaxAllowedDynamicStreamIndex())) {
                return false;
            }

            this._requestedDynamicStreamIndex = index;

            this.getDynamicStreamingStatus('before switch');

            // auto quality switching if requested index is < 0
            if (index < 0) {
                this.setAutoDynamicStreamSwitch(true);
            }
            // manual quality switching
            else {
                // auto dynamic stream switch must be set to false before any attempt of manual index switching
                this.setAutoDynamicStreamSwitch(false);

                // if there is attempt to manual switch but after disabling auto switching
                // current index is already the requested one (without that check the player tend to hang)
                if (index !== this.getCurrentDynamicStreamIndex()) {
                    this._hlsjs.currentLevel = index;
                }
            }

            this.getDynamicStreamingStatus('after switchDynamicStreamIndexTo');

            return index;
        },

        getStreamItems: function () {
            return this._hlsjs.levels;
        },

        getNumDynamicStreams: function () {
            return this._hlsjs.levels.length;
        },

        /**
         * The maximum allowed index. This can be set at run-time to
         * provide a ceiling for the switching profile, for example,
         * to keep from switching up to a higher quality stream when
         * the current video is too small to handle a higher quality stream.
         *
         * The default is the highest stream index.
         */
        getMaxAllowedDynamicStreamIndex: function () {
            if (this.getAutoDynamicStreamSwitch() && this._hlsjs.autoLevelCapping >= 0) {
                return this._hlsjs.autoLevelCapping;
            } else {
                return this.getNumDynamicStreams() - 1;
            }
        },

        setMaxAllowedDynamicStreamIndex: function (val) {
            if (!isNaN(val) && val !== this.getMaxAllowedDynamicStreamIndex() && val >= 0 && val < this.getNumDynamicStreams()) {
                this._hlsjs.autoLevelCapping = val;
            } else if (val < 0) {
                this._hlsjs.autoLevelCapping = -1;
            }
        },

        /**
         * The index of the current dynamic stream. Uses a zero-based index.
         */
        getCurrentDynamicStreamIndex: function () {
            return this._hlsjs.currentLevel;
        },

        /**
         * Defines whether or not the model should be in manual
         * or auto-switch mode. If in manual mode the switchDynamicStreamIndex
         * method can be used to manually switch to a specific stream index.
         */
        getAutoDynamicStreamSwitch: function () {
            return this._hlsjs.autoLevelEnabled;
        },

        setAutoDynamicStreamSwitch: function (val) {
            if (val === true) { // enable auto stream switching
                this._hlsjs.currentLevel = -1;
                this._hlsjs.nextLevel = -1;
                this._hlsjs.loadLevel = -1;
            }
        },

        getDynamicStreamingStatus: function (name) {
            if ($p.utils.logging) {
                $p.utils.log('| ' + name + ' | getDynamicStreamingStatus ===');
                $p.utils.log(
                    '| reqIdx: ', this._requestedDynamicStreamIndex,
                    ', current index: ', this.getCurrentDynamicStreamIndex(),
                    ', max allowed index: ', this.getMaxAllowedDynamicStreamIndex(),
                    ', num streams: ', this.getNumDynamicStreams(),
                    ', auto:', this.getAutoDynamicStreamSwitch()
                );
                var streams = this.getStreamItems();
                for (var index in streams) {
                    if (streams.hasOwnProperty(index) && streams[index].bitrate !== undefined) {
                        name = index + ' dimensions: ' + streams[index].width + "x" + streams[index].height + " | bitrate: " + streams[index].bitrate + ' | streamName: ' + streams[index].streamName;
                        $p.utils.log('| ' + name);
                    }
                }
                $p.utils.log('| ======================================');
            }
        },

        setQuality: function (quality) {
            if (this._quality == quality) {
                return;
            }
            this._quality = quality;

            // dynamic streams
            if (this._isDynamicStream === true) {
                this.switchDynamicStreamIndex((quality == 'auto') ? -1 : this.availableQualities[quality]);
            }
        },

    }, 'VIDEO');

    $p.newModel({

        modelId: 'MSEAUDIOHLS',

        mseVersion: '1.0',
        platform: 'mse',

        iLove: [{
            ext: 'm3u8',
            type: 'application/vnd.apple.mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u',
            type: 'application/vnd.apple.mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u8',
            type: 'application/x-mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u',
            type: 'application/x-mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u8',
            type: 'audio/mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u',
            type: 'audio/mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u8',
            type: 'audio/x-mpegurl',
            platform: ['mse']
        }, {
            ext: 'm3u',
            type: 'audio/x-mpegurl',
            platform: ['mse']
        }],
        applyMedia: function (destContainer) {
            var ref = this,
                hlsJsLoadSuccess = function () {

                    $p.utils.blockSelection(destContainer);

                    if ($('#' + ref.pp.getMediaId() + "_html").length === 0) {
                        ref.wasPersistent = false;

                        destContainer.html('').append(
                            $('<audio/>')
                            .attr({
                                "id": ref.pp.getMediaId() + "_html",
                                "poster": $p.utils.imageDummy(),
                                "loop": false,
                                "autoplay": false,
                                "preload": "auto",
                                "x-webkit-airplay": "allow",
                                "playsinline": ""
                            }).prop({
                                controls: false,
                                volume: ref.getVolume()
                            }).css({
                                'width': '1px',
                                'height': '1px',
                                'position': 'absolute',
                                'top': 0,
                                'left': 0
                            })
                        );
                    }
                    // create cover image
                    ref.imageElement = ref.applyImage(ref.getPoster('cover') || ref.getPoster('poster'), destContainer);
                    ref.imageElement.css({
                        border: '0px'
                    });
                    ref.mediaElement = $('#' + ref.pp.getMediaId() + "_html");
                    ref.addListeners();
                    ref.applySrc();
                },
                hlsJsLoadFailed = function (jqxhr, settings, exception) {
                    ref.sendUpdate('error', 2);
                };

            // check if hls.js is already loaded
            if (window.Hls && typeof window.Hls.isSupported === 'function') {
                // just continue
                hlsJsLoadSuccess();
            } else {
                // load hls.js
                $p.utils.getScript(ref.pp.getConfig('platformsConfig').mse.src, {
                        cache: true
                    })
                    .done(hlsJsLoadSuccess)
                    .fail(hlsJsLoadFailed);
            }
        }
    }, 'MSEVIDEOHLS');
    
}(window, document, jQuery, projekktor));(function (window, document, $, $p) {

    "use strict";

    $p.newModel({
        modelId: 'MSEVIDEODASH',
        mseVersion: '1.0',

        iLove: [{
                ext: 'ism',
                type: 'application/dash+xml',
                platform: ['mse'],
                drm: ['widevine', 'playready']
            },
            {
                ext: 'mpd',
                type: 'application/dash+xml',
                platform: ['mse'],
                drm: ['widevine', 'playready']
            }
        ],

        _dashjs: null,
        _dashjsPlatformConfig: {},
        _video: null,
        _quality: null,
        _qualityMap: null,
        _showAudioOnly: null,

        mediaElement: null,

        applyMedia: function (destContainer) {
            var ref = this;

            this._showAudioOnly = this.pp.getConfig('dynamicStreamShowAudioOnlyQualities');

            this._fetchDashJs(function (dashjsLib) {
                $p.utils.log('dashjs lib successfully loaded');

                ref._initMedia(destContainer);
            });
        },

        /**
         *  `_initMedia` setting up DashJS.
         * 
         * @param {object} destContainer
         *        container element for <video>
         */
        _initMedia: function (destContainer) {
            var ref = this,
                dashjsConfig = ref._dashjsPlatformConfig.initVars,
                wasAwakening = ref.getState('AWAKENING');

            ///// Stage 1:
            // Create dash.js MediaPlayer instance.
            this._dashjs = window.dashjs.MediaPlayer().create();

            ///// Stage 2:
            // If there is <video> element in the display container then use it,
            // otherwise create new one. 
            var videoID = this.pp.getMediaId() + "_html";
            this._video = document.getElementById(videoID);

            if (!this._video) {
                this._video = $('<video/>').attr({
                    "id": videoID,
                    "poster": $p.utils.imageDummy(),
                    "loop": false,
                    "autoplay": false,
                    "preload": "none",
                    "x-webkit-airplay": "allow",
                    "playsinline": ""
                }).prop({
                    controls: false,
                    volume: this.getVolume()
                }).css({
                    'width': '100%',
                    'height': '100%',
                    'position': 'absolute',
                    'top': 0,
                    'left': 0
                })[0];

                destContainer.html('').append(this._video);
            }

            this.mediaElement = $(this._video);

            ///// Stage 3:
            // Attach event listeners `this._dashjs`.
            var events = window.dashjs.MediaPlayer.events;

            this._dashjs.on(events["STREAM_INITIALIZED"], function (data) {

                // after "STREAM_INITIALIZED" it should be safe to set config values
                ref._setDashJsConfig(dashjsConfig);

                if (wasAwakening) {
                    ref.displayReady();
                    return;
                }

                if (ref.getSeekState('SEEKING')) {
                    if (ref._isPlaying) {
                        ref.setPlay();
                    }

                    ref.seekedListener();
                    return;
                }

                if (ref._isPlaying) {
                    ref.setPlay();
                }
            });

            this._dashjs.on(events["PLAYBACK_METADATA_LOADED"], function () {
                var qualityList = ref._getQualityList();

                if (ref._qualityMap === null) {
                    ref._qualityMap = {};
                }

                for (var i = 0; i < qualityList.length; i++) {
                    ref._qualityMap[qualityList[i]] = i;
                }

                ref.sendUpdate('availableQualitiesChange', qualityList);
            });

            this._dashjs.on(events["QUALITY_CHANGE_REQUESTED"], function () {
                ref.qualityChangeListener();
            });

            this._dashjs.on(events["ERROR"], function (error) {
                ref.sendUpdate('error', 4, error);
            });

            this._dashjs.on(events["PLAYBACK_ERROR"], function (error) {
                ref.sendUpdate('error', 5, error);
            });

            this._dashjs.on("public_keyError", function (error) {
                ref.sendUpdate('error', 302, error);
            });

            this._dashjs.on("public_keySessionClosed", function (event) {
                if (event.error !== undefined) {
                    ref.sendUpdate('error', 302, event.error);
                }
            });
            this._dashjs.on("public_licenseRequestComplete", function (event) {
                if (event.error !== undefined) {
                    ref.sendUpdate('error', 302, event.error);
                }
            });

            // set config set only 'debug' value here
            this._setDashJsConfig({
                debug: dashjsConfig.debug ? true : false
            });

            this.applySrc();
        },

        _setDashJsConfig: function(dashjsConfig){

            var ref = this;

            Object.keys(dashjsConfig).forEach(function (configKey) {

                var configVal = dashjsConfig[configKey];

                // not all of the methods are available in every phase of dashjs instance
                // life cycle so we need to catch that 
                try {
                    switch (configKey) {
                        case 'debug':
                            ref._dashjs.getDebug().setLogToBrowserConsole(configVal);
                            break;
                        case 'fastSwitchEnabled':
                            ref._dashjs.setFastSwitchEnabled(configVal);
                            break;
                        case 'limitBitrateByPortal':
                            ref._dashjs.setLimitBitrateByPortal(configVal);
                            break;
                        case 'usePixelRatioInLimitBitrateByPortal':
                            ref._dashjs.setUsePixelRatioInLimitBitrateByPortal(configVal);
                            break;
                    }
                } catch (error) {
                    $p.utils.log("DASHJS config setting failed on: ", configKey, configVal, error);
                }
            });
        },

        detachMedia: function () {

            if (this.mediaElement) {
                this.mediaElement = null;
            }

            if (this._dashjs) {
                if (this._dashjs.isReady()) {
                    this._dashjs.reset();
                }
                this._dashjs = null;
            }

            this._video = null;

            this._qualityMap = null;
            this._quality = null;
        },

        applySrc: function () {

            var file = this.getSource()[0],
                fileDrmConfig = Array.isArray(file.drm) ? file.drm : [],
                drmConfig = this.pp.getConfig('drm') || {}, // item or global
                availableDrmConfig = $p.utils.intersect(fileDrmConfig, Object.keys(drmConfig)),
                dashjsProtectionDataConf;

            if (fileDrmConfig.length > 0) {
                if (availableDrmConfig.length > 0) {
                    // DRM config required and available
                    dashjsProtectionDataConf = {};
                } else {
                    // DRM system required but no valid license server config defined
                    this.sendUpdate('error', 301);
                    return;
                }
            }

            availableDrmConfig.forEach(function (drm) {
                var dpc = dashjsProtectionDataConf;

                switch (drm) {
                    case 'widevine':
                        dpc["com.widevine.alpha"] = {
                            serverURL: drmConfig[drm]
                        };
                        break;
                    case 'playready':
                        dpc["com.microsoft.playready"] = {
                            serverURL: drmConfig[drm]
                        };
                        break;
                }
            });

            if (dashjsProtectionDataConf !== undefined) {
                this._dashjs.setProtectionData(dashjsProtectionDataConf);
            }

            // Initialize dash.js MediaPlayer
            this._dashjs.initialize(this._video, file.src, false);
        },

        /**
         * `_fetchDashJs` return `window.dashjs` if it's available.
         * Otherwise load DashJS lib from URL.
         * 
         * @param {function|null} cb
         *        {function} Callback function called after successful load of DashJS lib
         *                   Usage: `cb(dashjs)`
         *                  `dashjs` - reference to the DashJS lib
         *        {null} Callback function not specified.
         */
        _fetchDashJs: function (cb) {
            var ref = this,
                msePlatformConfig = this.pp.getConfig('platformsConfig').mse || {};

            // guarantee hls.js config values
            $.extend(true, ref._dashjsPlatformConfig, {src:'/MISSING_PATH_TO_DASHJS_LIB/', initVars:{}}, msePlatformConfig.dashjs);

            if (typeof window.dashjs === "object") {
                cb(window.dashjs);
            } else {
                $p.utils.getScript(ref._dashjsPlatformConfig.src, {
                    cache: true
                }).done(function () {
                    if (typeof window.dashjs === "object") {
                        cb(window.dashjs);
                    } else {
                        ref.sendUpdate('error', 2);
                    }
                }).fail(function () {
                    ref.sendUpdate('error', 2);
                });
            }
        },

        _getQualityList: function () {

            var avKeyFormat = this.pp.getConfig('dynamicStreamQualityKeyFormatAudioVideo'),
                aoKeyFormat = this.pp.getConfig('dynamicStreamQualityKeyFormatAudioOnly'),
                dpc = this.pp.getConfig('dynamicStreamQualityKeyBitrateRoundingDecimalPlacesCount'),
                bitrateKbps = 0,
                bitrateMbps = 0,
                bitrateUnit = 'kbps',
                bitrate = 0,
                audioList = null,
                videoList = null,
                buffer = [],
                keyName = null;


            if (!!this._showAudioOnly) {
                // Audio:
                audioList = this._dashjs.getBitrateInfoListFor('audio');

                for (var i = 0; i < audioList.length; i++) {
                    var item = audioList[i];

                    bitrateKbps = Math.floor(item['bitrate'] / 1000);
                    bitrateMbps = $p.utils.roundNumber(bitrateKbps / 1000, dpc);
                    bitrate = bitrateKbps < 1000 ? bitrateKbps : bitrateMbps;
                    bitrateUnit = bitrateKbps < 1000 ? 'kbps' : 'Mbps';

                    keyName = $p.utils.parseTemplate(aoKeyFormat, {
                        bitrate: bitrate,
                        bitrateunit: bitrateUnit,
                        bitratekbps: bitrateKbps,
                        bitratembps: bitrateMbps
                    });

                    buffer.push("" + keyName);
                }
            } else {
                // Video:
                videoList = this._dashjs.getBitrateInfoListFor('video');

                for (var i = 0; i < videoList.length; i++) {
                    var item = videoList[i];

                    bitrateKbps = Math.floor(item['bitrate'] / 1000);
                    bitrateMbps = $p.utils.roundNumber(bitrateKbps / 1000, dpc);
                    bitrate = bitrateKbps < 1000 ? bitrateKbps : bitrateMbps;
                    bitrateUnit = bitrateKbps < 1000 ? 'kbps' : 'Mbps';

                    keyName = $p.utils.parseTemplate(avKeyFormat, {
                        height: item['height'],
                        width: item['width'],
                        bitrate: bitrate,
                        bitrateunit: bitrateUnit,
                        bitratekbps: bitrateKbps,
                        bitratembps: bitrateMbps
                    });

                    buffer.push("" + keyName);
                }
            }

            buffer.push('auto');
            return buffer;
        },

        /*****************************************
         * Setters
         ****************************************/

        setQuality: function (quality) {

            if (this._quality === quality) {
                return;
            }

            if (!!this._showAudioOnly) {
                if (quality === "auto") {
                    this._dashjs.setAutoSwitchQualityFor('audio', true);
                } else {
                    this._dashjs.setAutoSwitchQualityFor('audio', false);
                    this._dashjs.setQualityFor('audio', this._qualityMap[quality]);
                }
            } else {
                if (quality === "auto") {
                    this._dashjs.setAutoSwitchQualityFor('video', true);
                } else {
                    this._dashjs.setAutoSwitchQualityFor('video', false);
                    this._dashjs.setQualityFor('video', this._qualityMap[quality]);
                }
            }

            this._quality = quality;
        },

        /************************************************
         * Getters
         ************************************************/

        getQuality: function () {
            return this._quality;
        }

    }, 'VIDEO');

}(window, document, jQuery, projekktor));/*
 * Copyright 2016-2017 - Radosław Włodkowski, www.wlodkowski.net, radoslaw@wlodkowski.net
 *
 * under GNU General Public License
 * http://www.filenew.org/projekktor/license/
 *
 * This model is interfacing video.js library
 *
 * video.js
 * Website: http://videojs.com/
 * License: Apache 2.0 License
 *
 */

(function(window, document, $, $p){
    
    "use strict";

    $p.newModel({
        modelId: 'VIDEOJS',
        videojsVersion: '1.0',

        iLove: [{
            ext: 'mp4',
            type: 'video/mp4',
            platform: ['videojs']
        }],

        _videojs: null,

        _eventMap: {
            pause: "vjsPauseListener",
            play: "vjsPlayingListener",
            volumechange: "vjsVolumeListener",
            progress: "vjsProgressListener",
            timeupdate: "vjsTimeListener",
            ended: "vjsEndedListener",
            waiting: "vjsWaitingListener",
            canplaythrough: "vjsCanplayListener",
            canplay: "vjsCanplayListener",
            error: "vjsErrorListener",
            emptied: "vjsEmptiedListener",
            stalled: "vjsStalledListener",
            seeked: "vjsSeekedListener",
            loadedmetadata: "vjsResizeListener",
            loadeddata: "vjsResizeListener",
            resize: "vjsResizeListener"
        },

        applyMedia: function (destContainer) {
            var ref = this,
                videoJsLoadSuccess = function () {
                    if ($('#' + ref.getMediaElementId()).length === 0) {

                        ref.wasPersistent = false;

                        destContainer.html('').append(
                            $('<video/>')
                            .attr({
                                "id": ref.getMediaElementId(),
                                "poster": $p.utils.imageDummy(),
                                "src": ref.getSource()[0].src,
                                "loop": false,
                                "autoplay": false,
                                "preload": "none",
                                "x-webkit-airplay": "allow",
                                "playsinline": ""
                            }).prop({
                                controls: false,
                                volume: ref.getVolume()
                            }).css({
                                'width': '100%',
                                'height': '100%',
                                'position': 'absolute',
                                'top': 0,
                                'left': 0
                            })
                        );
                    }

                    ref.mediaElement = $('#' + ref.getMediaElementId());
                    ref.initVideoJs();
                },
                videoJsLoadFailed = function (jqxhr, settings, exception) {
                    ref.sendUpdate('error', 2);
                };

            // check if videojs.js is already loaded
            if (window.videojs && typeof window.videojs === 'function') {
                // just continue
                videoJsLoadSuccess();
            } else {
                // load video.js CSS
                $p.utils.getCss(ref.pp.getConfig('platformsConfig').videojs.css);
                // load video.js JS
                $p.utils.getScript(ref.pp.getConfig('platformsConfig').videojs.src, {
                        cache: true
                    })
                    .done(videoJsLoadSuccess)
                    .fail(videoJsLoadFailed);
            }
        },

        initVideoJs: function () {
            var ref = this,
                wasAwakening = ref.getState('AWAKENING'),
                vjsConfig = ref.pp.getConfig('platformsConfig').videojs.initVars;

            ref._videojs = window.videojs(ref.mediaElement[0], vjsConfig, function (event, data) {
                // on video.js ready
                ref.mediaElement = $(this.contentEl());

                ref.addVideoJsEventListeners();
                if (wasAwakening) {
                    ref.displayReady();
                    return;
                }

                if (ref.getSeekState('SEEKING')) {
                    if (ref._isPlaying) {
                        ref.setPlay();
                    }

                    ref.seekedListener();
                    return;
                }

                if (ref._isPlaying) {
                    ref.setPlay();
                }
            });
        },

        detachMedia: function () {
            try {
                this._videojs.dispose();
            } catch (e) {}
        },

        /*****************************************
         * Handle Events
         ****************************************/
        addVideoJsEventListeners: function () {
            var ref = this;
            // add model reference to current videojs instance for later usage within event handlers
            // NOTE: all event listeners in video.js are binded to the video.js instance (this === _videojs)
            ref._videojs._ppModel = ref;

            // add event listeners
            $.each(this._eventMap, function (key, value) {
                var listener = ref[value];
                ref._videojs.on(key, listener);
            });
        },

        removeVideoJsEventListeners: function () {
            var ref = this;

            // remove event listeners
            $.each(this._eventMap, function (key, value) {
                var listener = ref[value];
                ref._videojs.off(key, listener);
            });
        },

        vjsPlayingListener: function (evt) {
            var ref = this._ppModel;
            ref.playingListener();
        },

        vjsPauseListener: function (evt) {
            var ref = this._ppModel;
            ref.pauseListener();
        },
        vjsVolumeListener: function (evt) {
            var ref = this._ppModel;
            ref.volumeListener(this.volume());
        },

        vjsProgressListener: function (evt) {
            var ref = this._ppModel;
            ref.progressListener(evt);
        },
        vjsSeekedListener: function (evt) {
            var ref = this._ppModel;
            ref.seekedListener(this.currentTime());
        },

        vjsTimeListener: function (evt) {
            var ref = this._ppModel,
                time = {
                    position: this.currentTime(),
                    duration: this.duration()
                };
            ref.timeListener(time);
        },

        vjsEndedListener: function (evt) {
            var ref = this._ppModel || this;
            ref.removeVideoJsEventListeners();
            ref.endedListener(evt);
        },

        vjsResizeListener: function (evt) {
            var ref = this._ppModel,
                size = {
                    videoWidth: this.videoWidth(),
                    videoHeight: this.videoHeight()
                };

            ref.resizeListener(size);
        },

        vjsWaitingListener: function (evt) {
            var ref = this._ppModel;
            ref.waitingListener(evt);
        },

        vjsCanplayListener: function (evt) {
            var ref = this._ppModel;
            ref.canplayListener(evt);
        },

        vjsEmptiedListener: function (evt) {
            var ref = this._ppModel;
            ref._setBufferState('EMPTY');
        },

        vjsStalledListener: function (evt) {
            var ref = this._ppModel;
            ref._setBufferState('EMPTY');
        },

        vjsErrorListener: function (evt, vjsRef) {
            var ref = this._ppModel || this,
                vjsPlayer = vjsRef || this,
                error = vjsPlayer.error() || evt.error;
            try {
                switch (error.code) {
                    case error.MEDIA_ERR_ABORTED:
                        ref.sendUpdate('error', 1);
                        break;
                    case error.MEDIA_ERR_NETWORK:
                        ref.sendUpdate('error', 2);
                        break;
                    case error.MEDIA_ERR_DECODE:
                        ref.sendUpdate('error', 3);
                        break;
                    case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
                        ref.sendUpdate('error', 4);
                        break;
                    default:
                        ref.sendUpdate('error', 5);
                        break;
                }
            } catch (e) {
                $p.utils.log(error, e);
            }
        },

        /*****************************************
         * Setters
         ****************************************/
        setPlay: function () {
            try {
                this._videojs.play();
            } catch (e) {}
        },

        setPause: function () {
            try {
                this._videojs.pause();
            } catch (e) {}
        },

        setVolume: function (volume) {
            if (this.mediaElement === null) {
                this.volumeListener(volume);
            } else {
                this._videojs.volume(volume);
            }
        },

        setSeek: function (newpos) {
            var ref = this,
                np = newpos;

            (function sk() {
                try {
                    ref._videojs.currentTime(np);
                    ref.timeListener({
                        position: np
                    });
                } catch (e) {
                    if (ref.mediaElement !== null) {
                        setTimeout(sk, 100);
                    }
                }
            })();
        },
        /************************************************
         * getters
         ************************************************/

        getVolume: function () {
            if (this.mediaElement === null) {
                return this._volume;
            }

            return this._videojs.volume();
        }
    });
    
}(window, document, jQuery, projekktor));/*
 * Projekktor II Plugin: Display
 *
 * DESC: Provides a standard display for cover-art, video or html content
 * features startbutton, logo-overlay and buffering indicator
 * Copyright 2010-2013, Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 *
 * under GNU General Public License
 * http://www.projekktor.com/license/
 */
(function (window, document, $, $p) {
    'use strict';

    if($p === undefined || !$p.hasOwnProperty('plugins')){
        throw new Error('Projekktor player not found. Please initialize Projekktor before adding any plugins.');
    }

    function projekktorDisplay() {}

    projekktorDisplay.prototype = {

        version: '1.1.2',
        reqVer: '1.8.0',

        logo: null,
        logoIsFading: false,

        display: null,

        displayClicks: 0,

        buffIcn: null,
        buffIcnSprite: null,
        buffIcnHangWatcher: null,
        bufferDelayTimer: null,


        _controlsDims: null,

        config: {
            displayClick: {
                callback: 'setPlayPause',
                value: null
            },
            displayPlayingClick: {
                callback: 'setPlayPause',
                value: null
            },
            displayDblClick: {
                callback: null,
                value: null
            },

            staticControls: false,

            /* time to delay buffering-icon-overlay once "waiting" event has been triggered */
            bufferIconDelay: 1000,

            bufferIconHangWatcherInterval: 5000,

            /* if set the indicator animation is tinkered from a cssprite - must be horizontal */
            spriteUrl: '',
            spriteWidth: 50,
            spriteHeight: 50,
            spriteTiles: 25,
            spriteOffset: 1,
            spriteCountUp: false
        },


        /* triggered on plugin-instantiation */
        initialize: function () {
            // create the display container itself
            this.display = this.applyToPlayer($('<div/>'));

            // create the startbutton
            this.startButton = this.applyToPlayer($('<div/>').addClass('start'), 'startbtn');

            // create buffericon
            this.buffIcn = this.applyToPlayer($('<div/>').addClass('buffering'), 'buffericn');

            this.setActive();

            // add spritelayer to buffericon (if required)
            if (this.config.spriteUrl !== '') {
                this.buffIcnSprite = $('<div/>')
                    .appendTo(this.buffIcn)
                    .css({
                        width: this.config.spriteWidth,
                        height: this.config.spriteHeight,
                        marginLeft: ((this.buffIcn.width() - this.config.spriteWidth) / 2) + "px",
                        marginTop: ((this.buffIcn.height() - this.config.spriteHeight) / 2) + "px",
                        backgroundColor: 'transparent',
                        backgroundImage: 'url(' + this.config.spriteUrl + ')',
                        backgroundRepeat: 'no-repeat',
                        backgroundPosition: '0 0'
                    })
                    .addClass('inactive');
            }

            // create a dedicated media container (if none exists)
            this.pp.getMediaContainer();

            this.pluginReady = true;
        },



        /*****************************************
            EVENT HANDLERS
        *****************************************/
        displayReadyHandler: function () {

            if (this.pp.playerModel.getBufferState('FULL')) {
                this.hideBufferIcon();
            }
        },

        synchronizingHandler: function () {
            var ref = this;
            this.hideStartButton();
            this.showBufferIcon();
            // the startbutton
            this.startButton.off().click(function () {
                ref.pp.setPlay();
            });
        },

        synchronizedHandler: function () {
            this.readyHandler();
        },

        readyHandler: function () {
            this.hideBufferIcon();
            if (this.pp.getState('IDLE')) {
                this.showStartButton();
            }
        },

        bufferHandler: function (state) {
            if (this.pp.playerModel.getBufferState('EMPTY') && !this.pp.getState('PAUSED')) {
                this.showBufferIcon();
            } else {
                this.hideBufferIcon();
            }
        },

        stateHandler: function (state) {
            var bufferState = this.pp.playerModel.getBufferState();

            switch (state) {

                case 'IDLE':
                    clearTimeout(this._cursorTimer);
                    this.display.css('cursor', 'pointer');
                    break;

                case 'PLAYING':
                    this.bufferHandler(bufferState);
                    this.hideStartButton();
                    break;

                case 'IDLE':
                    this.showStartButton();
                    this.hideBufferIcon();
                    break;

                case 'STARTING':
                case 'AWAKENING':
                    this.showBufferIcon();
                    this.hideStartButton();
                    break;

                case 'COMPLETED':
                    this.hideBufferIcon();
                    break;

                default:
                    this.hideStartButton();
            }
        },

        errorHandler: function (errorCode) {
            this.hideBufferIcon();
            this.hideStartButton();
            if (!this.getConfig('skipTestcard')) {
                this.testCard(errorCode);
            }

        },

        startHandler: function () {
            this.mousemoveHandler();
        },

        stoppedHandler: function () {
            this.hideBufferIcon();
        },

        scheduleLoadingHandler: function () {
            this.hideStartButton();
            this.showBufferIcon();
        },

        scheduledHandler: function () {
            if (!this.getConfig('autoplay')) {
                this.showStartButton();
            }
            this.hideBufferIcon();
        },

        plugineventHandler: function (data) {
            if (data.PLUGIN == 'controlbar' && data.EVENT == 'show' && this.getConfig('staticControls')) {
                var pctCtrl = data.height * 100 / this.pp.getDC().height();
                this.display.height((100 - pctCtrl) + "%").data('sc', true);
            }
        },

        qualityChangeHandler: function () {
            var bufferState = this.pp.playerModel.getBufferState();
            this.bufferHandler(bufferState);
        },

        /*****************************************,
            DISPLAY: Mouse Handling
        *****************************************/
        mousemoveHandler: function (evt) {
            var dest = this.display;
            if (this.pp.getState('IDLE')) {
                dest.css('cursor', 'pointer');
                return;
            }
            dest.css('cursor', 'auto');
            clearTimeout(this._cursorTimer);
            if ("AWAKENING|ERROR|PAUSED".indexOf(this.pp.getState()) == -1) {
                this._cursorTimer = setTimeout(function () {
                    dest.css('cursor', 'none');
                }, 3000);
            }
        },

        mousedownHandler: function (evt) {
            var ref = this;

            if (($(evt.target).attr('id') || '').indexOf('_media') == -1 && !$(evt.target).hasClass(this.pp.getNS() + 'testcard')){
                return;
            }

            clearTimeout(this._cursorTimer);
            this.display.css('cursor', 'auto');

            if (evt.which != 1){
                return;
            }

            switch (this.pp.getState()) {
                case 'ERROR':
                    this.pp.setConfig({
                        disallowSkip: false
                    });
                    this.pp.setActiveItem('next');
                    this.display.html('').removeClass(this.pp.getNS() + 'testcard');
                    return;
                case 'IDLE':
                    this.pp.setPlay();
                    return;
            }

            if (this.pp.getHasGUI() === true){
                return;
            }

            this.displayClicks++;

            this.pp._promote('displayClick');

            if (this.displayClicks > 0) {
                setTimeout(
                    function () {
                        if (ref.displayClicks == 1) {
                            if (ref.pp.getState() == 'PLAYING'){
                                ref.clickHandler('displayPlaying');
                            }
                            else {
                                ref.clickHandler('display');
                            }
                        } 
                        else if (ref.displayClicks == 2) {
                            ref.clickHandler('displayDbl');
                        }
                        ref.displayClicks = 0;
                    }, 150
                );
            }
            return;
        },


        /*****************************************
            STARTBUTTON
        *****************************************/
        showStartButton: function () {
            this.startButton.addClass('active').removeClass('inactive');
        },

        hideStartButton: function () {
            this.startButton.addClass('inactive').removeClass('active');
        },


        /*****************************************
            BUFFERICON: fader and animator
        *****************************************/
        hideBufferIcon: function () {
            clearTimeout(this.bufferDelayTimer);
            clearInterval(this.buffIcnHangWatcher);
            this.buffIcn.addClass('inactive').removeClass('active');
        },

        showBufferIcon: function (instant) {
            var ref = this;

            clearTimeout(this.bufferDelayTimer);

            /* setup buffer icon hang watcher */
            clearInterval(this.buffIcnHangWatcher);
            if (this.getConfig('bufferIconHangWatcherInterval')) {
                this.buffIcnHangWatcher = setInterval(function () {
                    if (ref.pp.playerModel.getBufferState('FULL')) {
                        ref.hideBufferIcon();
                    }
                }, this.getConfig('bufferIconHangWatcherInterval'));
            }

            if (this.pp.getHasGUI() || this.pp.getState('IDLE')) {
                return;
            }

            if ((this.pp.getModel() === 'YTAUDIO' || this.pp.getModel() === 'YTVIDEO') && !this.pp.getState('IDLE')){
                instant = true;
            }

            if (instant !== true && this.getConfig('bufferIconDelay') > 0) {
                this.bufferDelayTimer = setTimeout(function () {
                    ref.showBufferIcon(true);
                }, this.getConfig('bufferIconDelay'));
                return;
            }

            if (this.buffIcn.hasClass('active')) {
                return;
            }
            this.buffIcn.addClass('active').removeClass('inactive');

            if (ref.buffIcnSprite === null) {
                return;
            }

            var startOffset = (ref.config.spriteCountUp === true) ? 0 : (ref.config.spriteHeight + ref.config.spriteOffset) * (ref.config.spriteTiles - 1),
                spriteOffset = startOffset;
            ref.buffIcnSprite.addClass('active').removeClass('inactive');
            (function bi() {

                if (!ref.buffIcn.is(':visible')) {
                    return;
                }
                ref.buffIcnSprite.css('backgroundPosition', '0px -' + spriteOffset + "px");

                if (ref.config.spriteCountUp === true){
                    spriteOffset += ref.config.spriteHeight + ref.config.spriteOffset;
                }
                else {
                    spriteOffset -= ref.config.spriteHeight + ref.config.spriteOffset;
                }

                if (spriteOffset > (startOffset + ref.config.spriteHeight) * ref.config.spriteTiles || spriteOffset < ref.config.spriteOffset) {
                    spriteOffset = startOffset;
                }

                setTimeout(bi, 60);
            })();
        },

        testCard: function (errorCode) {
            var msgTxt = $p.utils.errorMessage(errorCode, this.pp);

            if (this.pp.getItemCount() > 1) {
                // "press next to continue"
                msgTxt += ' ' + $p.utils.errorMessage(99, this.pp);
            }

            if (msgTxt.length < 3) {
                msgTxt = 'ERROR #' + errorCode;
            }

            this.display
                .html('')
                .addClass(this.pp.getNS() + 'testcard')
                .html('<p>' + msgTxt + '</p>');
        }


    };

    $p.plugins.projekktorDisplay = projekktorDisplay;
}(window, document, jQuery, projekktor));/*
 * Projekktor II Plugin: Controlbar
 *
 * DESC: Adds a fully features cb element to the player
 * Copyright 2010-2014 Sascha Kluger, Spinning Airwhale Media, http://www.spinningairwhale.com
 * Copyright 2015-2018 - Radosław Włodkowski, www.wlodkowski.net, radoslaw@wlodkowski.net
 *
 * under GNU General Public License
 * http://www.projekktor.com/license/
 */
(function (window, document, $, $p) {
    'use strict';

    if($p === undefined || !$p.hasOwnProperty('plugins')){
        throw new Error('Projekktor player not found. Please initialize Projekktor before adding any plugins.');
    }

    function projekktorControlbar() {}

    projekktorControlbar.prototype = {

        version: '1.2.2',
        reqVer: '1.8.0',
        
        _cTimer: null,
        _lastPos: -1,
        _isDVR: false,
        _noHide: false,
        _sSliderAct: false,
        _vSliderAct: false,

        cb: null,

        controlElements: {},
        controlElementsConfig: {
            'timeleft': null,
            'sec_dur': null,
            'min_dur': null,
            'sec_abs_dur': null,
            'min_abs_dur': null,
            'hr_dur': null,
            'sec_elp': null,
            'min_elp': null,
            'sec_abs_elp': null,
            'min_abs_elp': null,
            'hr_elp': null,
            'sec_rem': null,
            'min_rem': null,
            'sec_abs_rem': null,
            'min_abs_rem': null,
            'hr_rem': null,
            'sec_tip': null,
            'min_tip': null,
            'sec_abs_tip': null,
            'min_abs_tip': null,
            'hr_tip': null,

            'cb': null,

            'playhead': {
                on: null,
                call: null
            },
            'loaded': null, // { on:['touchstart', 'click'], call:'scrubberClk'},
            'golive': [{
                on: ['touchstart', 'click'],
                call: 'goliveClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'scrubber': null, // { on:['touchstart', 'click'], call:'scrubberClk'},
            'scrubbertip': null,
            'scrubberknob': null,
            'scrubberdrag': [{
                on: ['mouseenter', 'touchstart'],
                call: 'scrubberShowTooltip'
            }, {
                on: ['mouseout', 'touchend'],
                call: 'scrubberHideTooltip'
            }, {
                on: ['mousemove', 'touchmove'],
                call: 'scrubberdragTooltip'
            }, {
                on: ['mousedown', 'touchstart'],
                call: 'scrubberdragStartDragListener'
            }],
            'play': [{
                on: ['touchend', 'click'],
                call: 'playClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'pause': [{
                on: ['touchstart', 'click'],
                call: 'pauseClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'stop': [{
                on: ['touchstart', 'click'],
                call: 'stopClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'prev': [{
                on: ['touchstart', 'click'],
                call: 'prevClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'next': [{
                on: ['touchstart', 'click'],
                call: 'nextClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'rewind': [{
                on: ['touchstart', 'click'],
                call: 'rewindClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'forward': [{
                on: ['touchstart', 'click'],
                call: 'forwardClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],

            'fsexit': [{
                on: ['touchstart', 'click'],
                call: 'exitFullscreenClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'fsenter': [{
                on: ['touchend', 'click'],
                call: 'enterFullscreenClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],

            'loquality': [{
                on: ['touchstart', 'click'],
                call: 'setQualityClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'hiquality': [{
                on: ['touchstart', 'click'],
                call: 'setQualityClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],

            'vslider': [{
                on: ['touchstart', 'click'],
                call: 'vsliderClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'vmarker': [{
                on: ['touchstart', 'click'],
                call: 'vsliderClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'vknob': {
                on: ['mousedown'],
                call: 'vknobStartDragListener'
            },

            'volumePanel': [{
                on: ['mousemove'],
                call: 'volumeBtnHover'
            }, {
                on: ['mouseout'],
                call: 'volumeBtnOut'
            }],
            'volume': null,

            'mute': [{
                on: ['touchstart', 'click'],
                call: 'muteClk'
            }, {
                on: ['mouseout'],
                call: 'volumeBtnOut'
            }, {
                on: ['mousemove'],
                call: 'volumeBtnHover'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'unmute': [{
                on: ['touchstart', 'click'],
                call: 'unmuteClk'
            }, {
                on: ['mouseout'],
                call: 'volumeBtnOut'
            }, {
                on: ['mousemove'],
                call: 'volumeBtnHover'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'vmax': [{
                on: ['touchstart', 'click'],
                call: 'vmaxClk'
            }, {
                on: ['mouseout'],
                call: 'volumeBtnOut'
            }, {
                on: ['mousemove'],
                call: 'volumeBtnHover'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],

            'open': [{
                on: ['touchstart', 'click'],
                call: 'openCloseClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'close': [{
                on: ['touchstart', 'click'],
                call: 'openCloseClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],
            'loop': [{
                on: ['touchstart', 'click'],
                call: 'loopClk'
            }, {
                on: ['touchend'],
                call: 'touchEnd'
            }],

            'controls': null,
            'title': null,
            'logo': {
                on: ['touchstart', 'click'],
                call: 'logoClk'
            }
        },

        config: {
            /* Plugin: cb - enable/disable fade away of overlayed controls */
            toggleMute: true,
            fadeDelay: 2500,
            showOnStart: false,
            showOnIdle: false,
            hideWhenPaused: false,

            /* cuepoints */
            showCuePoints: true,
            showCuePointsImmediately: true, // should the cuepoint be displayed immediately after current playlist item duration is known or only if the relevant part of the playlist item is buffered and ready to be played
            showCuePointGroups: [],
            minCuePointSize: '2px', // minimal cuepoint size
            cuePointEvents: [
                /* { // Sample global blip events config. You can set individual events for every blip within cuepoint blipEvents object.
                  'events': ['click', 'mouseover'],
                  'handler': function(e){ // the event parameter passed to the event handler has data property which contains:
                                          // pp - reference to the current projekktor instance
                                          // cuepoint - reference to the cuepoint represented by current blip
                                          // any other custom data which was passed inside 'data' property described below
                     e.data.pp.setGotoCuePoint(e.data.cuepoint.id);
                     console.log(e.data.test);
                  },
                  'data': {test:'data test'} // you can add any custom data you want
                 } */
            ],
            /**
             * displays logo on the controlbar
             * You can set the logo config globally for all playlist items in the controlbar plugin config or locally for every playlist item.
             * Playlist item config overwrites the global config.
             */
            logo: {
                /* // Sample global config (per item config follows the same schema).
                src: 'media/logo.png', // URL to your logo image (works fine with SVG too)
                title: 'visit our website', // Title added to the <img> element title and alt attributes.
                link: { // URL to go to after click on the logo [optional].
                    url: 'http://www.projekktor.com',
                    target: '_blank'
                },
                callback: function(player, e){ // Function called after click on the logo [optional]. It works only if the link config isn't present.
                                               // There are two parameters passed to the callback function:
                                               // player - reference to the current projekktor instance
                                               // e - event object
                    alert("projekktor v." + player.getVersion());
                }*/
            },


            /* Default layout */
            controlsTemplate: '<ul class="left"><li><div %{play}></div><div %{pause}></div></li></ul><ul class="right"><li><div %{logo}></div></li><li><div %{fsexit}></div><div %{fsenter}></div></li><li><div %{settingsbtn}></div></li><li><div %{tracksbtn}></div></li><li><div %{vmax}></div></li><li><div %{vslider}><div %{vmarker}></div><div %{vknob}></div></div></li><li><div %{mute}></div><div %{unmute}></div></li><li><div %{timeleft}>%{hr_elp}:%{min_elp}:%{sec_elp} | %{hr_dur}:%{min_dur}:%{sec_dur}</div></li><li><div %{next}></div></li><li><div %{prev}></div></li></ul><ul class="bottom"><li><div %{scrubber}><div %{loaded}></div><div %{playhead}></div><div %{scrubberknob}></div><div %{scrubberdrag}></div></div></li></ul><div %{scrubbertip}>%{hr_tip}:%{min_tip}:%{sec_tip}</div>'
        },

        initialize: function () {

            var ref = this,
                playerHtml = this.playerDom.html(),
                useTemplate = true,
                classPrefix = this.pp.getNS();

            // check if ANY control element already exists
            Object.keys(this.controlElementsConfig).some(function (controlElementName) {
                if (playerHtml.match(new RegExp(classPrefix + controlElementName, 'gi'))) {
                    useTemplate = false;
                    return true;
                }
            });

            if (useTemplate) {
                this.cb = this.applyToPlayer($(('<div/>')).addClass('controls'));
                this.applyTemplate(this.cb, this.getConfig('controlsTemplate'));
            } else {
                this.cb = this.playerDom.find("." + classPrefix + 'controls');
            }

            // find (inter)active elements
            Object.keys(this.controlElementsConfig).forEach(function (controlElementName) {
                ref.controlElements[controlElementName] = $(ref.playerDom).find('.' + classPrefix + controlElementName);
                $p.utils.blockSelection($(ref.controlElements[controlElementName]));
            });

            this.addGuiListeners();
            this.showcb();
            this.pluginReady = true;
        },

        /* parse and apply controls dom-template */
        applyTemplate: function (dest, templateString) {
            var classPrefix = this.pp.getNS();

            // apply template string if required:
            if (templateString) {
                // replace tags by class directive
                var tagsUsed = templateString.match(/\%{[a-zA-Z_]*\}/gi);
                if (tagsUsed != null) {
                    $.each(tagsUsed, function (key, value) {
                        var cn = value.replace(/\%{|}/gi, '');
                        if (value.match(/\_/gi)) {
                            // replace with span markup
                            templateString = templateString.replace(value, '<span class="' + classPrefix + cn + '"></span>');
                        } else {
                            templateString = templateString.replace(value, 'class="' + classPrefix + cn + '"' + $p.utils.i18n(' aria-label="%{' + cn + '}" title="%{' + cn + '}" '));
                        }
                    });
                }

                dest.html(templateString);
            }
        },

        updateDisplay: function () {
            var state = this.pp.getState();

            // nothing to do
            if (this.getConfig('controls') === false) {
                this.hidecb();
                return;
            }

            // prev / next button
            if (this.getConfig('disallowSkip')) {
                this._active('prev', false);
                this._active('next', false);
            } else {
                this._active('prev', this.pp.getPreviousItem() !== false);
                this._active('next', this.pp.getNextItem() !== false);
            }

            // play / pause button
            if (this.getConfig('disablePause')) {
                this._active('play', false);
                this._active('pause', false);
            } else {
                if (state === 'PLAYING') {
                    this.drawPauseButton();
                }
                if (state === 'PAUSED') {
                    this.drawPlayButton();
                }
                if (state === 'IDLE') {
                    this.drawPlayButton();
                }    
            }

            // stop button
            this._active('stop', state !== 'IDLE');



            // rewind & forward
            this._active('forward', state !== 'IDLE');
            this._active('rewind', state !== 'IDLE');


            // fullscreen button
            if (this.pp.getIsFullscreen() === true) {
                this.drawExitFullscreenButton();
            } else {
                this.drawEnterFullscreenButton();
            }

            if (!this.pp.getFullscreenEnabled()) {
                this._active('fsexit', false);
                this._active('fsenter', false);
            }


            // loop button
            this._active('loop', true);
            this.controlElements.loop
                .addClass(this.pp.getConfig('loop') ? 'on' : 'off')
                .removeClass(!this.pp.getConfig('loop') ? 'on' : 'off');

            // hd / sd toggl
            this.displayQualityToggle();

            // init time display
            this.displayTime();

            // update progress
            this.displayProgress();

            // init volume display
            this.displayVolume(this.pp.getVolume());
        },

        deconstruct: function () {
            this.pluginReady = false;
            $.each(this.controlElements, function () {
                $(this).off();
            });
            $.each(this._appliedDOMObj, function () {
                $(this).off();
            });
        },


        /* assign listener methods to controlbar elements */
        addGuiListeners: function () {
            var ref = this;

            // if (!this.getConfig('controls')) return;

            $.each(this.controlElementsConfig, function (key, elmCfg) {
                if (elmCfg == null) {
                    return true;
                }

                if (!(elmCfg instanceof Array)) {
                    elmCfg = [elmCfg];
                }

                for (var subset = 0; subset < elmCfg.length; subset++) {

                    if (elmCfg[subset].on == null) {
                        continue;
                    }

                    $.each(elmCfg[subset].on, function (evtKey, eventName) {

                        // thanx to FF3.6 this approach became a little complicated:
                        var isSupported = ("on" + eventName in window.document),
                            callback = elmCfg[subset].call;

                        if (!isSupported) {
                            var el = document.createElement('div');
                            el.setAttribute("on" + eventName, 'return;');
                            isSupported = (typeof el["on" + eventName] == 'function');
                        }

                        if (isSupported) {
                            ref.controlElements[key].on(eventName, function (event) {
                                ref.clickCatcher(event, callback, ref.controlElements[key]);
                            });

                        }

                    });
                }
                return true;
            });
            this.cb.mousemove(function (event) {
                ref.controlsFocus(event);
            });
            this.cb.mouseout(function (event) {
                ref.controlsBlur(event);
            });
        },

        /* generic click handler for all controlbar buttons */
        clickCatcher: function (evt, callback, element) {
            //evt.stopPropagation();
            evt.preventDefault();

            this[callback](evt, element);

            return false;
        },


        touchEnd: function () {
            var ref = this;
            this._cTimer = setTimeout(function () {
                ref.hidecb();
            }, this.getConfig('fadeDelay'));
            this._noHide = false;
        },


        /*******************************
        DOM Manipulations
        *******************************/
        drawTitle: function () {
            this.controlElements['title'].html(this.getConfig('title', ''));
        },

        displayLogo: function () {
            var logoConfig = this.pp.getConfig('logo') || this.getConfig('logo'),
                logoElement = this.controlElements['logo'],
                img;

            if (logoElement && logoConfig && logoConfig.src) {
                img = $('<img>')
                    .attr({
                        src: logoConfig.src,
                        alt: logoConfig.title,
                        title: logoConfig.title
                    });

                if ((logoConfig.link && logoConfig.link.url) || typeof logoConfig.callback == 'function') {
                    img.css({
                        cursor: 'pointer'
                    });
                }

                logoElement.empty().append(img);
                this._active('logo', true);
            } else {
                this._active('logo', false);
            }
        },

        canHide: function () {
            var state = this.pp.getState(),
                result = this.cb === null ||
                this._noHide ||
                (state === 'IDLE' && this.getConfig('showOnIdle')) ||
                (state === 'PAUSED' && !this.getConfig('hideWhenPaused'));

            return !result;
        },

        canShow: function () {
            var state = this.pp.getState(),
                result = this.cb === null ||
                !this.getConfig('controls') ||
                this.pp.getHasGUI() ||
                ('ERROR|COMPLETED|DESTROYING'.indexOf(state) > -1) ||
                ('AWAKENING|STARTING'.indexOf(state) > -1 && !this.getConfig('showOnStart')) ||
                (state === 'IDLE' && !this.getConfig('showOnIdle')) ||
                false;

            return !result;
        },

        hidecb: function () {
            var wasVisible = this.cb.hasClass('active');

            clearTimeout(this._cTimer);

            // don't hide
            if (!this.canHide()) {
                return;
            }

            this.cb.removeClass('active').addClass('inactive');

            if (wasVisible) {
                this.sendEvent('hide', this.cb);
            }
        },

        showcb: function () {
            var ref = this,
                isVisible = this.cb.hasClass('active');

            // always clear timeout, stop animations
            clearTimeout(this._cTimer);
            this._cTimer = setTimeout(
                function () {
                    ref.hidecb();
                }, this.getConfig('fadeDelay')
            );

            if (!this.canShow()) {
                return;
            }

            // show up:
            if (!isVisible) {
                this.cb.removeClass('inactive').addClass('active');
                this.sendEvent('show', this.cb);
            }

            this.updateDisplay();
        },

        displayTime: function (pct, dur, pos) {
            if (this.pp.getHasGUI()) {
                return;
            }

            var percent = ((pct || this.pp.getLoadPlaybackProgress() || 0) * 10) / 10,
                duration = dur || this.pp.getDuration() || 0,
                position = pos || this.pp.getPosition() || 0,
                times;

            // limit updates to one per second
            if (Math.abs(this._lastPos - position) >= 1) {

                // check if there is anything to display
                if (duration === 0) { // hide time display elements e.g. live streams on Android
                    this._active('scrubber', false);
                    this._active('timeleft', false);
                } else { // show time display elements
                    this._active('scrubber', true);
                    this._active('timeleft', true);
                }

                times = $.extend({}, this._clockDigits(duration, 'dur'), this._clockDigits(position, 'elp'), this._clockDigits(duration - position, 'rem'));

                // update scrubber:
                this.controlElements['playhead'].css({
                    width: percent + "%"
                });
                this.controlElements['scrubberknob'].css({
                    left: percent + "%"
                });

                // update last position value
                this._lastPos = position;

                // update numeric displays
                for (var key in this.controlElements) {
                    if(this.controlElements.hasOwnProperty(key)){
                        if (key == 'cb') {
                            break;
                        }

                        if (times[key]) {
                            $.each(this.controlElements[key], function () {
                                $(this).html(times[key]);
                            });
                        }
                    }
                }
            }

        },

        displayProgress: function () {
            var percent = Math.round(this.pp.getLoadProgress() * 10) / 10,
                lastUpdatedPercent = this.controlElements['loaded'].data('pct') || undefined;

            // limit updates to 1 per 5%
            if (lastUpdatedPercent === undefined || lastUpdatedPercent !== percent) {
                this.controlElements['loaded'].data('pct', percent).css("width", percent + "%");
            };
        },

        displayVolume: function (volume) {

            if (this._vSliderAct == true) {
                return;
            }
            if (volume == null) {
                return;
            }    

            var fixed = this.getConfig('fixedVolume') || (this.pp.playerModel && this.pp.playerModel._fixedVolume),
                toggleMute = (this.controlElements['mute'].hasClass('toggle') || this.controlElements['unmute'].hasClass('toggle') || this.getConfig('toggleMute')),
                // check if the volume is in the proper range and correct its value if it's not
                volume = volume > 1 ? 1 : volume,
                volume = volume < 0 ? 0 : volume;

            // hide volume mess in case volume is fixed
            this._active('mute', !fixed);
            this._active('unmute', !fixed);
            this._active('vmax', !fixed);
            this._active('vknob', !fixed);
            this._active('vmarker', !fixed);
            this._active('vslider', !fixed);

            if (fixed) {
                return;
            }

            // make controls visible in order to allow dom manipulations
            // this.cb.stop(true, true).show();
            var vslider = this.controlElements['vslider'],
                vmarker = this.controlElements['vmarker'],
                vknob = this.controlElements['vknob'],
                orientation = vslider.width() > vslider.height() ? "horizontal" : "vertical";

            switch (orientation) {
                case "horizontal":

                    vmarker.css('width', volume * 100 + "%");
                    vknob.css('left', Math.round((vslider.width() * volume) - (vknob.width() * volume)) + "px");

                    break;

                case "vertical":

                    vmarker.css('height', volume * 100 + "%");
                    vknob.css('bottom', Math.round((vslider.height() * volume) - (vknob.height() * volume)) + "px");

                    break;
            }

            // "li" hack
            var lis = this.controlElements['volume'].find('li'),
                set = lis.length - Math.ceil((volume * 100) / lis.length);

            for (var i = 0; i <= lis.length; i++) {
                if (i >= set) {
                    $(lis[i]).addClass('active');
                }
                else {
                    $(lis[i]).removeClass('active');
                }
            }


            if (toggleMute) {
                switch (parseFloat(volume)) {
                    case 0:
                        this._active('mute', false);
                        this._active('unmute', true);
                        break;

                    default:
                        this._active('mute', true);
                        this._active('unmute', false);
                        break;
                }
            }
        },

        displayCuePoints: function (immediately) {

            if (!this.getConfig('showCuePoints')){
                return;
            }

            var ref = this,
                prefix = this.pp.getNS(),
                duration = this.pp.getDuration();

            ref.controlElements['scrubber'].children().remove('.' + prefix + 'cuepoint');

            $.each(this.pp.getCuePoints(this.pp.getItemId(), true) || [], function () {

                // display cuepoins only from given groups or all cuepoints if there are no specyfic groups defined (showCuePointGroups array is empty)
                if (ref.getConfig('showCuePointGroups').length && ref.getConfig('showCuePointGroups').indexOf(this.group) == -1) {
                    return;
                }

                var blipWidth = this.on != this.off ? (((this.off - this.on) / duration) * 100) + '%' : ref.getConfig('minCuePointSize'),
                    blipPos = (this.on / duration) * 100,
                    blip = $(document.createElement('div'))
                    .addClass(prefix + 'cuepoint')
                    .addClass(prefix + 'cuepoint_group_' + this.group)
                    .addClass(prefix + 'cuepoint_' + this.id)
                    .addClass(immediately ? 'active' : 'inactive')
                    .css('left', blipPos + "%")
                    .css('width', blipWidth),
                    blipEvents = ref.config.cuePointEvents.concat(this.blipEvents);

                if (this.title != '') {
                    blip.attr('title', this.title);
                }

                if (!immediately) {
                    this.addListener('unlock', function () {
                        $(blip).removeClass('inactive').addClass('active');
                        ref._bindCuePointBlipEvents(blip, blipEvents, {
                            pp: ref.pp,
                            cuepoint: this
                        });
                    });
                } else {
                    ref._bindCuePointBlipEvents(blip, blipEvents, {
                        pp: ref.pp,
                        cuepoint: this
                    });
                }

                ref.controlElements['scrubber'].append(blip);

            });

        },

        drawPauseButton: function (event) {
            this._active('pause', true);
            this._active('play', false);
        },

        drawPlayButton: function (event) {
            this._active('pause', false);
            this._active('play', true);
        },


        drawEnterFullscreenButton: function (event) {
            this._active('fsexit', false);
            this._active('fsenter', true);
        },

        drawExitFullscreenButton: function (event) {
            this._active('fsexit', true);
            this._active('fsenter', false);
        },

        displayQualityToggle: function (qual) {

            var qualsCfg = this.getConfig('playbackQualities'),
                qualsItm = this.pp.getPlaybackQualities(),
                classPrefix = this.pp.getNS(),
                best = [];

            // off
            if (qualsItm.length < 2 || qualsCfg.length < 2) {
                this.controlElements['loquality'].removeClass().addClass('inactive').addClass(classPrefix + 'loquality').data('qual', '');
                this.controlElements['hiquality'].removeClass().addClass('inactive').addClass(classPrefix + 'hiquality').data('qual', '');
                return;
            }

            // get two best variants
            qualsCfg.sort(function (a, b) {
                return a.minHeight - b.minHeight;
            });
            for (var i = qualsCfg.length; i--; i > 0) {
                if ($.inArray(qualsCfg[i].key, qualsItm) > -1){
                    best.push(qualsCfg[i].key);
                }
                if (best.length > 1) {
                    break;
                }
            }

            this.cb.addClass('qualities');
            if (best[0] == this.pp.getPlaybackQuality()) {
                this._active('loquality', true).addClass('qual' + best[1]).data('qual', best[1]);
                this._active('hiquality', false).addClass('qual' + best[0]).data('qual', best[0]);
            } else {
                this._active('loquality', false).addClass('qual' + best[1]).data('qual', best[1]);
                this._active('hiquality', true).addClass('qual' + best[0]).data('qual', best[0]);
            }
        },


        /*******************************
        Player Event Handlers
        *******************************/
        itemHandler: function (data) {

            $(this.cb).find('.' + this.pp.getNS() + 'cuepoint').remove();
            this._lastPos = -1;
            this.updateDisplay();
            this.drawTitle();
            this.displayLogo();
            this.pluginReady = true;
        },

        startHandler: function () {
            if (this.getConfig('showOnStart') === true) {
                this.showcb();
            } else {
                this.hidecb();
            }
        },

        readyHandler: function (data) {
            this.showcb();
            this.pluginReady = true;
        },

        stateHandler: function (state) {
            this.updateDisplay();

            if ('STOPPED|AWAKENING|IDLE|COMPLETED'.indexOf(state) > -1) {
                this.displayTime(0, 0, 0);
                this.displayProgress(0);
            }

            if ('PLAYING|STOPPED|COMPLETED|DESTROYING'.indexOf(state) > -1) {
                return;
            }

            if ('ERROR'.indexOf(state) > -1) {
                this._noHide = false;
            }

            this.showcb();

            this.displayProgress();
        },

        scheduleModifiedHandler: function () {
            if (this.pp.getState() === 'IDLE') {
                return;
            }
            this.updateDisplay();
            this.displayTime();
            this.displayProgress();
        },

        volumeHandler: function (value) {
            this.displayVolume(value);
        },

        progressHandler: function (obj) {
            this.displayProgress();
        },

        timeHandler: function (obj) {
            this.displayTime();
            this.displayProgress();
        },

        qualityChangeHandler: function (qual) {
            this.displayQualityToggle(qual);
        },

        streamTypeChangeHandler: function (streamType) {
            if (streamType === 'dvr' || streamType === 'live') {
                this._isDVR = true;
                this.setActive(this.controlElements['golive'], true);
            } else {
                this._isDVR = false;
                this.setActive(this.controlElements['golive'], false);
            }
        },

        isLiveHandler: function (islive) {
            if (islive) {
                this.controlElements['golive'].addClass('on').removeClass('off');
            } else {
                this.controlElements['golive'].addClass('off').removeClass('on');
            }
        },

        fullscreenHandler: function (inFullscreen) {

            this._noHide = false;
            this._vSliderAct = false;

            if (!this.getConfig('controls')) {
                return;
            }
            if (!this.pp.getFullscreenEnabled()) {
                return;
            }

            if (inFullscreen) {
                this.cb.addClass('fullscreen');
                this.drawExitFullscreenButton();
            } else {
                this.cb.removeClass('fullscreen');
                this.drawEnterFullscreenButton();
            }
        },

        durationChangeHandler: function () {
            if (this.pp.getDuration() != 0) {
                this.displayCuePoints(this.getConfig('showCuePointsImmediately'));
            }
        },

        cuepointsSyncHandler: function (cuepoints) {
            if (this.pp.getDuration() != 0) {
                this.displayCuePoints(this.getConfig('showCuePointsImmediately'));
            }
        },

        errorHandler: function (value) {
            this._noHide = false;
            this.hidecb();
        },

        leftclickHandler: function () {
            this.mouseleaveHandler();
        },

        focusHandler: function (evt) {
            this.showcb();
        },

        mouseenterHandler: function (evt) {
            this.showcb();
        },

        mousemoveHandler: function (evt) {
            if (this.pp.getState('STARTING')) {
                return;
            }
            this.showcb();
        },

        mouseleaveHandler: function () {},

        mousedownHandler: function (evt) {
            this.showcb();
        },

        /*******************************
        ControlUI Event LISTENERS
        *******************************/
        controlsFocus: function (evt) {

            this._noHide = true;
        },

        controlsBlur: function (evt) {
            this._noHide = false;
        },

        setQualityClk: function (evt) {
            this.pp.setPlaybackQuality($(evt.currentTarget).data('qual'));
        },

        goliveClk: function (evt) {
            this.pp.setSeek(-1);
        },

        playClk: function (evt) {
            this.pp.setPlay();
        },

        pauseClk: function (evt) {
            this.pp.setPause();
        },

        stopClk: function (evt) {
            this.pp.setStop();
        },

        startClk: function (evt) {
            this.pp.setPlay();
        },

        controlsClk: function (evt) {},

        prevClk: function (evt) {
            this.pp.setActiveItem('previous');
        },

        nextClk: function (evt) {
            this.pp.setActiveItem('next');
        },

        forwardClk: function (evt) {
            this.pp.setPlayhead('+10');
        },

        rewindClk: function (evt) {
            this.pp.setPlayhead('-10');
        },

        muteClk: function (evt) {
            this.pp.setMuted(true);
        },

        unmuteClk: function (evt) {
            this.pp.setMuted(false);
        },

        vmaxClk: function (evt) {
            this.pp.setVolume(1);
        },

        enterFullscreenClk: function (evt) {
            this.pp.setFullscreen(true);
        },

        exitFullscreenClk: function (evt) {
            this.pp.setFullscreen(false);
        },

        loopClk: function (evt) {
            this.pp.setLoop($(evt.currentTarget).hasClass('inactive') || false);
            this.updateDisplay();
        },

        vmarkerClk: function (evt) {
            this.vsliderClk(evt);
        },

        openCloseClk: function (evt) {
            var ref = this;
            $($(evt.currentTarget).attr('class').split(/\s+/)).each(function (key, value) {
                if (value.indexOf('toggle') === -1) {
                    return;
                }
                ref.playerDom.find('.' + value.substring(6)).slideToggle('slow', function () {
                    ref.pp.setSize();
                });
                ref.controlElements['open'].toggle();
                ref.controlElements['close'].toggle();
            });
        },

        logoClk: function (evt) {
            var logoConfig = this.pp.getConfig('logo') || this.getConfig('logo');
            if (logoConfig) {
                if (logoConfig.link && logoConfig.link.url) {
                    window.open(logoConfig.link.url, logoConfig.link.target);
                } else if (typeof logoConfig.callback === 'function') {
                    logoConfig.callback(this.pp, evt);
                }
            }
        },

        volumeBtnHover: function (evt) {
            clearTimeout(this._outDelay);
            this.setActive(this.controlElements['volumePanel'], true);
        },

        volumeBtnOut: function (evt, elm) {
            var ref = this;
            if (evt.currentTarget != elm.get(0)) {
                return;
            }    
            if (evt.relatedTarget == elm.get(0)) {
                return;
            }
            this._outDelay = setTimeout(function () {
                ref.setActive(ref.controlElements['volumePanel'], false);
            }, 100);
        },

        vsliderClk: function (evt) {
            if (this._vSliderAct == true) {
                return;
            }


            var slider = $(this.controlElements['vslider']),
                orientation = slider.width() > slider.height() ? 'hor' : 'vert',
                totalDim = (orientation == 'hor') ? slider.width() : slider.height(),
                pageX = (evt.originalEvent.touches) ? evt.originalEvent.touches[0].pageX : evt.pageX,
                pageY = (evt.originalEvent.touches) ? evt.originalEvent.touches[0].pageY : evt.pageY,
                requested = (orientation == 'hor') ? pageX - slider.offset().left : pageY - slider.offset().top,
                result = 0;

            if (requested < 0 || isNaN(requested) || requested == undefined) {
                result = 0;
            } else {
                result = (orientation == 'hor') ? (requested / totalDim) : 1 - (requested / totalDim);
            }

            this.pp.setVolume(result);
        },

        scrubberShowTooltip: function (event) {
            var pointerPosition = this._getPointerPosition(event);

            if (this.pp.getDuration() === 0) {
                return;
            }
            clearTimeout(this._cTimer);

            this.updateScrubberTooltip(pointerPosition);
        },

        scrubberHideTooltip: function (event) {
            this.setActive(this.controlElements['scrubbertip'], false);
        },

        scrubberdragTooltip: function (event) {
            
            var pointerPosition = this._getPointerPosition(event);

            // IE amd Chrome issues (mouseenter,mouseleave)
            if (this.pp.getDuration() === 0) {
                return;
            }

            this.updateScrubberTooltip(pointerPosition);
        },

        updateScrubberTooltip: function (pointerPosition) {
            var ref = this,
                slider = $(this.controlElements['scrubberdrag'][0]),
                tip = $(this.controlElements['scrubbertip']),
                newPos = pointerPosition.clientX - slider.offset().left - (tip.outerWidth() / 2),
                timeIdx = this.pp.getDuration() / 100 * ((pointerPosition.clientX - slider.offset().left) * 100 / slider.width()),
                times = this._clockDigits(timeIdx, 'tip', 0, this.pp.getDuration());

            this.setActive(this.controlElements['scrubbertip'], true);

            Object.keys(times).forEach(function (key) {
                if (ref.controlElements.hasOwnProperty(key)) {
                    $(ref.controlElements[key]).html(times[key]);
                }
            });

            newPos = (newPos < 0) ? 0 : newPos;
            newPos = (newPos > slider.width() - tip.outerWidth()) ? slider.width() - tip.outerWidth() : newPos;

            tip.css({
                left: newPos + "px"
            });
        },

        scrubberdragStartDragListener: function (event) {

            if (this.getConfig('disallowSkip') === true) {
                return;
            }

            this._sSliderAct = true;

            var ref = this,
                jqEventNS = '.' + this.pp.getNS() + 'scrubberdrag',
                slider = ref.controlElements['scrubberdrag'],
                loaded = ref.controlElements['loaded'],
                lastPointerPosition = this._getPointerPosition(event),
                seekDelayTimer,

                applyValue = function (pointerPosition) {

                    var newPos = Math.abs(slider.offset().left - pointerPosition.clientX);

                    newPos = (newPos > slider.width()) ? slider.width() : newPos;
                    newPos = (newPos > loaded.width()) ? loaded.width() : newPos;
                    newPos = (newPos < 0) ? 0 : newPos;
                    newPos = Math.abs(newPos / slider.width()) * ref.pp.getDuration();

                    if (newPos > 0) {
                        // delay the seek call
                        clearInterval(seekDelayTimer);
                        seekDelayTimer = setTimeout(function() {
                            ref.pp.setPlayhead(newPos);
                        }, 100);
                    }

                },

                pointerUp = function (evt) {
                    $(window).off(jqEventNS);

                    applyValue(lastPointerPosition);

                    ref._sSliderAct = false;
                    return false;
                },

                pointerMove = function (evt) {
                    lastPointerPosition = ref._getPointerPosition(evt);
                    
                    clearTimeout(ref._cTimer);
                    applyValue(lastPointerPosition);
                    return false;
                };
                
                if($p.features.touch){
                    $(window).on('touchmove' + jqEventNS, pointerMove);
                    $(window).on('touchend' + jqEventNS, pointerUp);
                }
                else {
                    $(window).on('mousemove' + jqEventNS, pointerMove);
                    $(window).on('mouseup' + jqEventNS, pointerUp);
                }

            applyValue(lastPointerPosition);
        },

        vknobStartDragListener: function (event, domObj) {
            this._vSliderAct = true;

            var ref = this,

                jqEventNS = '.' + this.pp.getNS() + 'vknob', 
                vslider = ref.controlElements['vslider'],
                vmarker = ref.controlElements['vmarker'],
                vknob = ref.controlElements['vknob'],

                orientation = vslider.width() > vslider.height() ? "horizontal" : "vertical",

                volume = 0,

                mouseUp = function (mouseUpEvent) {
                    $(window).off(jqEventNS);

                    ref._vSliderAct = false;

                    return false;
                },

                mouseMove = function (dragEvent) {
                    clearTimeout(ref._cTimer);

                    var newXPos = (dragEvent.clientX - vslider.offset().left),
                        newXPos = (newXPos > vslider.width()) ? vslider.width() : newXPos,
                        newXPos = (newXPos < 0) ? 0 : newXPos,

                        newYPos = (dragEvent.clientY - vslider.offset().top),
                        newYPos = (newYPos > vslider.height()) ? vslider.height() : newYPos,
                        newYPos = (newYPos < 0) ? 0 : newYPos;



                    switch (orientation) {
                        case "horizontal":
                            volume = Math.abs(newXPos / vslider.width());

                            vmarker.css('width', volume * 100 + "%");
                            vknob.css('left', Math.round((vslider.width() * volume) - (vknob.width() * volume)) + "px");

                            break;

                        case "vertical":
                            volume = 1 - Math.abs(newYPos / vslider.height());

                            vmarker.css('height', volume * 100 + "%");
                            vknob.css('bottom', Math.round((vslider.height() * volume) - (vknob.height() * volume)) + "px");

                            break;
                    }

                    ref.pp.setVolume(volume);
                    return false;
                };

                $(window).on('mousemove' + jqEventNS, mouseMove);
                $(window).on('mouseup' + jqEventNS, mouseUp);
        },

        /*******************************
            GENERAL HELPERS
        *******************************/
        _active: function (elmName, on) {
            var dest = this.controlElements[elmName];
            if (on == true) {
                dest.addClass('active').removeClass('inactive');
            } else {
                dest.addClass('inactive').removeClass('active');
            }
            return dest;
        },

        /* convert a num of seconds to a digital-clock like display string */
        _clockDigits: function (secs, postfix, minValSecs, maxValSecs) {

            if (isNaN(secs) || secs === undefined) {
                secs = 0;
            }

            if(minValSecs !== undefined){
                secs = secs < minValSecs ? minValSecs : secs;
            }

            if(maxValSecs !== undefined){
                secs = secs > maxValSecs ? maxValSecs : secs;
            }

            var hr = Math.floor(secs / (60 * 60)),
                divisor_for_minutes = secs % (60 * 60),
                min = Math.floor(divisor_for_minutes / 60),
                min_abs = hr * 60 + min,
                divisor_for_seconds = divisor_for_minutes % 60,
                sec = Math.floor(divisor_for_seconds),
                sec_abs = secs,
                result = {};

            result['min_' + postfix] = (min < 10) ? "0" + min : min;
            result['min_abs_' + postfix] = (min_abs < 10) ? "0" + min_abs : min_abs;
            result['sec_' + postfix] = (sec < 10) ? "0" + sec : sec;
            result['sec_abs_' + postfix] = (sec_abs < 10) ? "0" + sec_abs : sec_abs;
            result['hr_' + postfix] = (hr < 10) ? "0" + hr : hr;

            return result;
        },
        _bindCuePointBlipEvents: function (blip, events, data) {
            if (events.length) { // bind events if there are some
                for (var i = 0; i < events.length; i++) {
                    var e = events[i]['events'].join(' '),
                        d = $.extend({}, events[i]['data'], data) || {},
                        h = (typeof events[i]['handler'] == 'function' ? events[i]['handler'] : function (e) {});
                    blip.on(e, d, h);
                }
            } else { // otherwise make the blip 'invisible' for mouse events (works everywhere but IE up to 10)
                blip.css('pointer-events', 'none');
            }
        },
        _getPointerPosition: function(event){

            var positionSource = {};

            if(event) {

                if(('touches' in event.originalEvent) && event.originalEvent.touches.length > 0) {
                    positionSource = event.originalEvent.touches[0];
                }
                else {
                    positionSource = event;
                }

                return {
                    clientX: positionSource.clientX,
                    clientY: positionSource.clientY,
                    pageX: positionSource.pageX,
                    pageY: positionSource.pageY
                };
            }
        }
    };

    $p.plugins.projekktorControlbar = projekktorControlbar;
}(window, document, jQuery, projekktor));/*
 * Projekktor II Plugin: Contextmenu
 *
 * under GNU General Public License
 * http://www.projekktor.com/license/
 */
(function (window, document, $, $p) {
    'use strict';

    if($p === undefined || !$p.hasOwnProperty('plugins')){
        throw new Error('Projekktor player not found. Please initialize Projekktor before adding any plugins.');
    }

    function projekktorContextmenu() {}

    projekktorContextmenu.prototype = {

        version: '1.1.4',
        reqVer: '1.8.0',

        _dest: null,
        config: {
            items: {
                /*
                playerInfo: {
                    getContextTitle: function (pp) {
                        return pp.getConfig('playerName') + ' V' + pp.getVersion();
                    },
                    open: function(pp) {
                        
                    }
                }
                */
            }
        },

        initialize: function () {

            this._dest = $p.utils.blockSelection(this.applyToPlayer($('<ul/>')));

            this.pluginReady = true;
        },

        mousedownHandler: function (evt) {
            var parentOffset,
                xPos, yPos;

            switch (evt.which) {
                case 3:
                        parentOffset = this.pp.getDC().offset(),
                        yPos = (evt.pageY - parentOffset.top),
                        xPos = (evt.pageX - parentOffset.left);

                    if (xPos + this._dest.width() > this.pp.getDC().width()){
                        xPos = this.pp.getDC().width() - this._dest.width() - 2;
                    }

                    if (yPos + this._dest.height() > this.pp.getDC().height()){
                        yPos = this.pp.getDC().height() - this._dest.height() - 2;
                    }

                    this.setActive();
                    this._dest.css({
                        top: yPos + "px",
                        left: xPos + "px"
                    });
                    break;
                case 1:
                    try {
                        $(evt.target).data('plugin').open(this.pp);
                    } catch (e) {}
                default:
                    this.setInactive();
            }
        },

        mouseleaveHandler: function () {
            this.setInactive();
        },

        eventHandler: function (evt, obj) {
            var items = this.getConfig('items');

            if (evt.indexOf('Contextmenu') > -1) {
                if (items.hasOwnProperty(obj.name)) {
                    items[obj.name] = obj;
                }
            }
        },

        displayReadyHandler: function () {
            var ref = this,
                span = null,
                items = this.getConfig('items');

            this.setInactive();
            this._dest.html('');

            Object.keys(items).forEach(function(itemName){
                var item = items[itemName];

                span = $('<span/>')
                    .data('plugin', item)
                    .html(item.getContextTitle(ref.pp) || item);

                try {
                    item.setContextEntry(span);
                } catch (ignore) { }

                $('<li/>')
                    .append(span)
                    .data('plugin', item)
                    .appendTo(ref._dest);
                });
        },

        popup: function (url, width, height) {
            var centeredY = window.screenY + (((window.outerHeight / 2) - (height / 2))),
            centeredX = window.screenX + (((window.outerWidth / 2) - (width / 2)));
            window.open(url, 'projekktor', 'height=' + height + ',width=' + width + ',toolbar=0,scrollbars=0,status=0,resizable=1,location=0,menuBar=0' + ',left=' + centeredX + ',top=' + centeredY).focus();
        }
    };

    $p.plugins.projekktorContextmenu = projekktorContextmenu;
}(window, document, jQuery, projekktor));/*
 * Projekktor II Plugin: Settings Service Menu
 *
 * under GNU General Public License
 * http://www.projekktor.com/license/
 */
(function (window, document, $, $p) {
    'use strict';

    if($p === undefined || !$p.hasOwnProperty('plugins')){
        throw new Error('Projekktor player not found. Please initialize Projekktor before adding any plugins.');
    }

    function projekktorSettings() {}

    projekktorSettings.prototype = {

        version: '1.0.2',
        reqVer: '1.8.0',

        _qualities: [],

        config: {
            contextTitle: 'Settings',
            feedbackUrl: false,
            settingsMenu: '<ul id="tool" class="ppsettingslist active">' +
                '<li class="first label">%{help}</li>' +
                '<li data-pp-settings-func="tool_help" class="inactive">%{keyboard controls}</li>' +
                '<li data-pp-settings-func="tool_debug" class="inactive">%{debug}</li>' +
                '<li data-pp-settings-func="tool_version" class="inactive">%{player info}</li>' +
                '<li></li>' +
                '</ul>' +
                '<ul id="quality" class="ppsettingslist active">' +
                '<li class="first label">%{quality}</li>' +
                '</ul>' +
                '<div class="ppclear"></div>',

            versionTpl: '<div data-pp-settings-func="toolwindow_version">' +
                '<p>Projekktor V%{version}</p>' +
                '<p><a class="btn cancel" href="#">%{ok}</a></p>' +
                '</div>',


            debugTpl: '<div data-pp-settings-func="toolwindow_debug">' +
                '<div class="wizzard inactive" id="debug_1">' +
                '<p><b>%{report}</b></p>' +
                '<p><textarea id="message">%{please}</textarea></p>' +
                '<p>' +
                '<a class="btn cancel" href="#">%{cancel}</a>' +
                '<a class="btn next" data-step="2" href="#">%{continue}</a>' +
                '</p>' +
                '</div>' +
                '<div class="wizzard inactive" id="debug_2">' +
                '<p><b>%{sendto}</b></p>' +
                '<p><textarea id="result">%{please}</textarea></p>' +
                '<p><a class="btn next" href="#" data-step="3">%{ok}</a></p>' +
                '</div>' +
                '<div class="wizzard inactive" id="debug_3">' +
                '<p>%{thanks}</p>' +
                '<p><a class="btn cancel" href="#">%{ok}</a></p>' +
                '</div>' +
                '</div>' +
                '<div data-pp-settings-func="toolwindow_error">' +
                '<div class="wizzard inactive" id="error_1">' +
                '<p><b>%{error}<br/> %{sendto}</b></p>' +
                '<p><textarea id="errortxt"></textarea></p>' +
                '<p><a class="btn next" href="#" data-step="3">%{ok}</a></p>' +
                '</div>' +
                '<div class="wizzard inactive" id="error_2">' +
                '<p>%{thanks}</p>' +
                '<p><a class="btn cancel" href="#">%{ok}</a></p>' +
                '</div>' +
                '</div>',

            helpTpl: '<div data-pp-settings-func="toolwindow_help">' +
                '<p><b>%{keyboard assignments}</b></p>' +
                '<p class="key">%{help1}</p>' +
                '<p class="key">%{help2}</p>' +
                '<p class="key">%{help3}</p>' +
                '<p>%{help4}</p>' +
                '<p><a class="btn cancel" href="#">%{ok}</a></p>' +
                '</div>'

        },

        initialize: function () {

            var ref = this,
                _outDelay = 0;

            // button, main container and options
            this.dest = this.applyToPlayer($('<div/>').addClass('settingsmenu').html($p.utils.i18n(this.getConfig('settingsMenu'))));
            this.btn = this.applyToPlayer($('<div/>').addClass('settingsbtn'), 'btn');
            this.tool = this.applyToPlayer($('<div/>').addClass('tool'), 'toolwindow');

            this.setActive(this.btn, true);

            // hide menu
            this.setInactive();
            $p.utils.blockSelection(this.dest);

            // fade in / out
            this.dest.on('mouseleave', function () {
                clearTimeout(_outDelay);
                _outDelay = setTimeout(function () {
                    ref.setInactive();
                }, 200);
            });

            this.dest.on('mouseenter', function () {
                clearTimeout(_outDelay);
            });

            // enable "settings" button
            this.btn.click(function (evt) {
                if (ref.dest.hasClass('active')) {
                    ref.setInactive();
                } else {
                    ref.setActive();
                }
                evt.stopPropagation();
                evt.preventDefault();
                return false;
            });

            this.btn.on('mouseleave', function () {
                $(this).blur();
                clearTimeout(_outDelay);
                _outDelay = setTimeout(function () {
                    ref.setInactive();
                }, 200);
            });

            this.btn.on('mouseenter', function () {
                clearTimeout(_outDelay);
            });

            this.pluginReady = true;
        },

        optionSelect: function (dest, func, value) {
            // visual feedback
            if (this[func + 'Set'](value) === true) {
                dest.parent().find('li').each(function () {
                    if (!$(this).hasClass('first')) {
                        $(this).addClass('off').removeClass('on');
                    }
                });
                dest.addClass('on').removeClass('off');
            }
        },

        /*****************************************************
         * Player Event Handlers
         * **************************************************/

        itemHandler: function () {
            this._qualities = [];
            this.setupSettingsMenu();
        },

        plugin_controlbarHideHandler: function (controlBar) {
            this.setInactive();
            this.btn.addClass('off').removeClass('on');
        },

        availableQualitiesChangeHandler: function (qualities) {
            this._qualities = qualities.slice().reverse();
            this.setupSettingsMenu();
        },

        qualityChangeHandler: function (val) {
            this.qualitySet(val);
            this.setupSettingsMenu();
        },

        errorHandler: function (code) {
            var msg = $p.utils.i18n("%{error" + code + "}");
            this.toolSet('error', 1, msg);
        },

        /*****************************************************
         * availability checks
         * **************************************************/
        toolCheck: function (value) {
            return true;
        },

        qualityCheck: function (value) {
            if ($.inArray(value, this.pp.getPlaybackQualities()) == -1) {
                return false;
            }
            return true;
        },

        /*****************************************************
         * Config SETTERS
         * **************************************************/
        toolSet: function (func, stp, data) {

            var tpl = this.applyToPlayer($('<div/>'), 'toolwindow_' + func),
                step = stp || 1,
                ref = this,
                isPlaying = this.pp.getState('PLAYING');

            if (func == 'debug' && this.getConfig('feedbackUrl')) {
                window.location.href = this.getConfig('feedbackUrl');
                return;
            }

            tpl.html($p.utils.i18n(this.getConfig(func + 'Tpl')));

            this.tool.html($p.utils.parseTemplate(tpl.html(), this.pp.config));
            this.tool.find('.wizzard').addClass('inactive').removeClass('active');
            this.tool.find('#' + func + '_' + step).addClass('active').removeClass('inactive');
            this.setActive(this.tool);


            if (data == null) {
                this.tool.find('#message').focus(function () {
                    $(this).html('').off('focus').css({
                        color: '#000'
                    });
                });
                this.tool.find('#message').css({
                    color: '#aaa'
                });
            } else {
                var topHref = this.pp.getIframe() && window.top.location.href;

                var debugData = {
                    version: this.pp.getVersion(),
                    message: data,
                    timestamp: new Date().getTime(),
                    userAgent: $p.userAgent,
                    features: $p.features,
                    iframeHref: window.location.href,
                    topHref: topHref,
                    referrer: window.document.referrer,
                    modelstate: this.pp.getState(),
                    duration: this.pp.getDuration(),
                    position: this.pp.getPosition(),
                    maxposition: this.pp.getMaxPosition(),
                    platform: this.pp.getPlatform(),
                    platformscfg: this.pp.config._platforms,
                    plugins: this.pp.config._plugins,
                    media: this.pp.media,
                    compTable: this.pp.getSupportedPlatforms(),
                    rnd: $p.utils.randomId(22)
                };

                $.each(this.pp.config._platforms, function (key, value) {
                    debugData[value + 'ver'] = $p.platforms[value]();
                });

                this.tool.find((func == 'debug') ? '#result' : '#errortxt')
                    .attr({
                        readonly: 'readonly'
                    })
                    .val(
                        $p.utils.stringify(debugData)
                    )
                    .off()
                    .on('focus', function () {
                        $(this).select();
                    });
            }

            $(this.pp.getDC().find('.next')).click(function () {
                $(this).off();
                ref.toolSet('debug', parseInt($(this).attr('data-step'), 10), ref.tool.find('#message').val());
                return false;
            });

            $(this.pp.getDC().find('.cancel')).click(function () {
                $(this).off();
                ref.setActive(ref.tool, false);
                if (isPlaying) {
                    ref.pp.setPlay();
                }
                return false;
            });

            this.tool.css({
                margin: '-' + (this.tool.outerHeight() / 2) + 'px 0 0 -' + (this.tool.outerWidth() / 2) + 'px'
            });

            if (this.pp.getConfig('streamType').toUpperCase().indexOf('LIVE') == -1 && func != null) {
                this.pp.setPause();
            }

            this.setInactive();
            return false;
        },


        qualitySet: function (val) {

            var value = val || this.pp.storage.restore('quality') || null;

            if (value === 'auto' || !this.qualityCheck(value)) {
                this.pp.storage.remove('quality');
                value = this.pp.getAppropriateQuality();
            }

            if (value !== null) {
                this.pp.storage.save('quality', value);
            }

            if (this.pp.getPlaybackQuality() !== value) {
                this.pp.setPlaybackQuality(value);
            }

            return true;
        },

        _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",

        // public method for encoding
        encode: function (input) {
            var output = "";
            var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
            var i = 0;

            input = this._utf8_encode(input);

            while (i < input.length) {

                chr1 = input.charCodeAt(i++);
                chr2 = input.charCodeAt(i++);
                chr3 = input.charCodeAt(i++);

                enc1 = chr1 >> 2;
                enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
                enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
                enc4 = chr3 & 63;

                if (isNaN(chr2)) {
                    enc3 = enc4 = 64;
                } else if (isNaN(chr3)) {
                    enc4 = 64;
                }

                output = output +
                    this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
                    this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);

            }

            return output;
        },

        // private method for UTF-8 encoding
        _utf8_encode: function (string) {
            string = string.replace(/\r\n/g, "\n");
            var utftext = "";

            for (var n = 0; n < string.length; n++) {

                var c = string.charCodeAt(n);

                if (c < 128) {
                    utftext += String.fromCharCode(c);
                } else if ((c > 127) && (c < 2048)) {
                    utftext += String.fromCharCode((c >> 6) | 192);
                    utftext += String.fromCharCode((c & 63) | 128);
                } else {
                    utftext += String.fromCharCode((c >> 12) | 224);
                    utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                    utftext += String.fromCharCode((c & 63) | 128);
                }

            }

            return utftext;
        },

        setupSettingsMenu: function () {
            var ref = this,
                pCount = 0,
                menuOptions = [];

            // setup quality menu for current playlist item
            this.setupQualityMenu();

            $.each(this.dest.find("[" + this.getDA('func') + "]"), function () {
                var currentElement = $(this),
                func = currentElement.attr(ref.getDA('func')).split('_'),
                menuName = func[0],
                optionName = func[1],
                storedValue = ref.pp.storage.restore(menuName);
                
                if (!menuOptions.hasOwnProperty(menuName)) {
                    menuOptions[menuName] = [];
                }

                // check
                if (!ref[menuName + 'Check'](optionName) && optionName !== 'auto') {
                    currentElement.addClass('inactive').removeClass('active');
                    return true;
                } else {
                    currentElement.addClass('active').removeClass('inactive');
                }

                menuOptions[menuName].push(optionName);

                if ((storedValue === optionName) || (storedValue === null && optionName === 'auto')) {
                    currentElement.addClass('on').removeClass('off');
                } else {
                    currentElement.addClass('off').removeClass('on');
                }

                currentElement.click(function (evt) {
                    ref.optionSelect(currentElement, menuName, optionName);
                    evt.stopPropagation();
                    evt.preventDefault();
                    return false;
                });

                return true;
            });

            // restore presets:
            for (var i in menuOptions) {
                if (menuOptions[i].length < 3) {
                    this.dest.find('#' + i).addClass('inactive').removeClass('active');
                } else {
                    this.dest.find('#' + i).addClass('active').removeClass('inactive');
                    this[i + 'Set']();
                    pCount++;
                }
            }

            // apply "columns" class
            var classes = this.dest.attr("class").split(" ").filter(function (item) {
                return item.lastIndexOf("column", 0) !== 0;
            });

            if (pCount) {
                this.setActive(this.btn, true);
            } else {
                this.setActive(this.btn, false);
            }

            this.dest.attr("class", classes.join(" "));
            this.dest.addClass('column' + pCount);
        },

        setupQualityMenu: function () {
            var qualities = this._qualities.length ? this._qualities : this.pp.getPlaybackQualities(),
                qualityList = this.createQualityList(qualities);
            // remove all the current quality menu items
            this.removeMenuItems('quality');

            // add new items
            this.addMenuItems('quality', qualityList);
        },

        createQualityList: function (qualities) {
            var qualityValues = qualities || this.pp.getPlaybackQualities(),
                qualityList = '',
                val = '';

            for (var i = 0; i < qualityValues.length; i++) {
                val = qualityValues[i];

                if (val != 'auto' && val != 'default') {
                    qualityList += '<li data-' + this.pp.getNS() + '-settings-func="quality_' + val + '"  class="inactive">%{' + val + '}</li>';
                }
            }

            qualityList += '<li data-' + this.pp.getNS() + '-settings-func="quality_auto"  class="auto inactive">%{auto}</li>';

            return $p.utils.i18n(qualityList);
        },

        addMenuItems: function (menuId, content, prepend) {
            var id = menuId || false,
                cont = content || false,
                prep = prepend || false;

            if (!(id && cont)) {
                return false;
            }

            var menu = this.dest.find('#' + id);

            if (prep) {
                menu.children('.label').after(content);
            } else {
                menu.append(content);
            }

            return this.dest.find('#' + id);
        },

        /**
         * Removes all the menu items from the selected menu
         *
         * @param {String} menuId - id of the menu
         * @returns {jQuery} - jQuery object containing removed elements
         */
        removeMenuItems: function (menuId) {
            var id = menuId || false;

            if (!id) {
                return false;
            }

            return this.dest.find('#' + id).children().not('.label').remove();
        }
    };

    $p.plugins.projekktorSettings = projekktorSettings;
}(window, document, jQuery, projekktor));