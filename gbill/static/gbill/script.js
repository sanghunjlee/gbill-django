function doEval(s) {
    const re_op = /[+-*/%]/;
    const re_num = /[0-9.,]/;
    const re_par = /[()]/;
    const input = s.split("");

    var result = "";
    var bucket = new Array("", "");

    for (let i = 0; i < input.length; i++) {
        let c = input[i];
        if (re_num.test(c)) bucket[1] += c;
        else if (re_op.test(c)) bucket[0] = c;
        else if (re_par.text(c)) bucket[1] = parseNest(input);

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