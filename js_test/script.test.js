var script = require('../gbill/static/gbill/js/script');
var assert = require('assert').strict;

describe('Function doEval()', function() {
    it('should compute "1+2*3-4/2" and return "5"', function() {
        assert.equal(
            script._test.doEval("1+2*3-4/2"), 
            parseFloat("5").toFixed(3)
        );
    })
    it('should add two values (with decimals) and return the sum', function() {
        let a = Math.floor(Math.random() * 10000000)/1000;
        let b = Math.floor(Math.random() * 10000000)/1000;
        let c = a + b;
        assert.strictEqual(
            script._test.doEval(`${a}+${b}`), 
            parseFloat(c).toFixed(3),
            `${a} + ${b} ?= ${c}`
        );
    })
    it('should subtract two values (with decimals) and return the result', function() {
        let a = Math.floor(Math.random() * 10000000)/1000;
        let b = Math.floor(Math.random() * 10000000)/1000;
        let c = a - b;
        assert.strictEqual(
            script._test.doEval(`${a}-${b}`), 
            parseFloat(c).toFixed(3),
            `${a} - ${b} ?= ${c}`
        );
    })
    it('should multiply two values (with decimals) and return the result', function() {
        let a = Math.floor(Math.random() * 10000000)/1000;
        let b = Math.floor(Math.random() * 10000000)/1000;
        let c = a * b;
        assert.strictEqual(
            script._test.doEval(`${a}*${b}`), 
            parseFloat(c).toFixed(3),
            `${a} * ${b} ?= ${c}`
        );
    })
    it('should divide two values (with decimals) and return the result', function() {
        let a = Math.floor(Math.random() * 10000000)/1000;
        let b = Math.floor(Math.random() * 10000000)/1000;
        let c = a / b;
        assert.strictEqual(
            script._test.doEval(`${a}/${b}`), 
            parseFloat(c).toFixed(3),
            `${a} / ${b} ?= ${c}`
        );
    })
})