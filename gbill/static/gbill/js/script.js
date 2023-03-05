function doOper(op, a, b) {
    switch (op) {
        case '+':
            return (parseFloat(a) + parseFloat(b)).toFixed(4);
        case '-':
            return (parseFloat(a) - parseFloat(b)).toFixed(4);
        case '*':
            return (parseFloat(a) * parseFloat(b)).toFixed(4);
        case '/':
            return (parseFloat(a) / parseFloat(b)).toFixed(4);
        default:
            return null;
    }
}
function doEval(s) {
    // Evaluate equations with operators: +, -, *, /
    // Any other operator will cause incorrect calculation or an error

    var numbers = s.split(new RegExp('[\\+\\-\\/\\*]'));
    var operators = s.split(new RegExp('[.0-9]')).filter(function (op) {
        return op !== '';
    });
    
    while (operators.length > 0) {
        let index = operators.findIndex(function (op) {
            return op === '*' || op ==='/';
        });
        if (index == -1) {
            index = operators.findIndex(function (op) {
                return op === '+' || op === '-';
            });
        }
        if (index == -1) {
            break;
        }
        let result = doOper(operators[index], numbers[index], numbers[index+1]);
        numbers[index] = result;
        numbers.splice(index+1, 1);
        operators.splice(index, 1);
    }
    return parseFloat(numbers.join('')).toFixed(3);
}



exports._test = {
    doEval: doEval
}