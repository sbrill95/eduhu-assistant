H5P.TextUtilities = (function () {
  var self = {};
  self.computeLevenshteinDistance = function (a, b, caseSensitive) {
    if (!caseSensitive) { a = a.toLowerCase(); b = b.toLowerCase(); }
    var m = a.length, n = b.length;
    var d = [];
    for (var i = 0; i <= m; i++) { d[i] = [i]; }
    for (var j = 0; j <= n; j++) { d[0][j] = j; }
    for (var j2 = 1; j2 <= n; j2++) {
      for (var i2 = 1; i2 <= m; i2++) {
        if (a[i2-1] === b[j2-1]) { d[i2][j2] = d[i2-1][j2-1]; }
        else { d[i2][j2] = Math.min(d[i2-1][j2]+1, d[i2][j2-1]+1, d[i2-1][j2-1]+1); }
      }
    }
    return d[m][n];
  };
  return self;
})();
