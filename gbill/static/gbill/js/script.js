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

    var numbers = s.split(new RegExp('[+-\/\*]'));
    var operators = s.split(new RegExp('[0-9]'));
    
    while (true) {
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
        let result = doOper(operators[index], numbers[index-1], numbers[index]);
        
    }

}

function evalInput(ele) {
    var inp_val = ele.value.replace(" ", "")
    var inp = inp_val.split("");
    var result = 0.0;
    var bucket = new Array("", "");
    for (let i = 0; i < inp.length; i++) {
        const c = inp[i];
        if (re_num.test(c)) {
            bucket[0] += c;
        } else if (re_op.test(c)) {
            if (bucket[1].length == 0 && bucket[0].length > 0) {
                result = parseFloat(bucket[0]);
                bucket[0] = "";
            } else if (bucket[1].length > 0) {
                switch (bucket[1]) {
                    case "%":
                        bucket[0] = (parseFloat(bucket[0]) / 100);
                        break;
                    case "+":
                        result += parseFloat(bucket[0]);
                    case "-":
                        result -= parseFloat(bucket[0]);
                    case "*":
                        result *= parseFloat(bucket[0]);
                        break;
                    case "/":
                        result /= parseFloat(bucket[0]);
                    default:
                        bucket[0] = "";
                        bucket[1] = "";
                }
            }
            bucket[1] = c;
        } else if (re_par.text(c)) {

        }
        console.log(bucket);
        console.log(result);
    }
}

exports = {
    doEval: doEval
}