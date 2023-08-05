var sys    = require('sys'),
    React  = require('react-tools'),
    source = '';

var options = {
  // harmony: true
};

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function(chunk) {
    source += chunk;
});

process.stdin.on('end', function() {
    var compiled = React.transform(source, options);
    process.stdout.write(compiled);
});
