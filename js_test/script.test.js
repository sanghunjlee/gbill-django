var script = require('../gbill/static/gbill/js/script.js');
var assert = require('assert').strict;

describe('Function doEval()', function() {
    it('should add two values and return the sum', function() {
        let a = Math.floor(Math.random() * 100);
        let b = Math.floor(Math.random() * 100);
        let c = a + b;
        let eq = `${a}+${b}`
        let sol = `${c}`
        assert.strictEqual(doEval(eq), sol)
    })
})