import querystring from "querystring";
// package bookmark from canvas to be embedded as a query parameter to the same
// path as the current request, and with all the same query parameters as the
// current request (except replacing any existing bookmark)
//
// OPE: Overrides upstream app/api/packageBookmark.js so "load more" links point back
// through the canvas domain (RCE_API_HOST, e.g. canvas.<domain>/rce) instead of the
// internal RCE host. Upstream converted to ESM in 1.27.7 - keep the named export.
function packageBookmark(request, bookmark) {
  if (bookmark) {
    const path = request.baseUrl + request.path;
    const query = Object.assign({}, request.query, { bookmark });
    const qs = querystring.stringify(query);
    //    return `${request.protocol}://${request.get("Host")}${path}?${qs}`;
    const myUrl = process.env.RCE_API_HOST || request.get("Host");
    return `${request.protocol}://${myUrl}${path}?${qs}`;
  } else {
    return null;
  }
}

export { packageBookmark };
