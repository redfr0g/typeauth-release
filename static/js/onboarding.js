/**
onboarding.js - handles onboarding keystroke registration and DOM changes during form switching.
@redfr0g 2021 
**/

// wait for DOM to load
$(function () {
    fixStepIndicator(0)
    // global timer array
    var tmr = [];
    var backspc = 0;
    var shift = 0;
    var capslock = false;
    var step = 1;

    // configure ajax
    $.postJSON = function (url, data, callback) {
        return jQuery.ajax({
            'async': false, // to submit keystroke dynamics before form submission
            'type': 'POST',
            'url': url,
            'contentType': 'application/json; charset=utf-8',
            'data': JSON.stringify(data),
            'dataType': 'json',
            'success': callback
        });
    };

    // get keypress event from text input
    $('#floatingInput').keypress(function (evt) {
        // check if the user just started typing
        if (tmr.length > 0 && tmr[tmr.length - 1].evt == "keypress") {
            return;
        }

        if (evt.keyCode == 13) { // ignore enter
            return;
        }

        else {
            tmr.push({
                "tmr": evt.timeStamp,
                "key_code": evt.keyCode,
                "evt": "keypress"
            });
        }
        //console.log("Key code: " + evt.which + " On time: " + evt.timeStamp);
    });

    // get keyup event from text input  
    $('#floatingInput').keyup(function (evt) {
        // check if the user just started typing and ignore special keys
        if (tmr.length > 0 && tmr[tmr.length - 1].evt == "keyup" && evt.keyCode != 8 && evt.keyCode != 20 && evt.keyCode != 16) {
            return;
        }

        if (evt.keyCode == 13) { // ignore enter
            return;
        }

        if (evt.keyCode == 20) { // check if caps lock was pressed
            capslock = true;
        }

        if (evt.keyCode == 8) { // increment backspace presses
            backspc += 1;
        }

        if (evt.keyCode == 16) { // increment shift presses
            shift += 1;
        }

        tmr.push({
            "tmr": evt.timeStamp,
            "key_code": evt.keyCode,
            "evt": "keyup"
        });
        //console.log("Key code: " + evt.which + " On time: " + evt.timeStamp);
    });

    $('#submit').click(
        function computeDynamic() { // compute dynamic
            // result from this function you can send as any other input 
            // to server for dynamics evaluation
            var ret = "";

            for (var i = 0; i < tmr.length - 1; ++i) {
                ret += ((i > 0) ? ";" : "") + (tmr[i].tmr);
            }

            //console.log("Keystroke dynamics: " + ret);

            //set value of keystroke dynamics parameters and feature keys presses
            $("#keystrokeDynamics_" + step).val(ret);
            $("#backspaceCount").val(backspc);
            $("#shiftCount").val(shift);

            //set value to true if caps lock was pressed at least once
            if (capslock) {
                $("#isCapsLock").val("True");
            }
            else {
                $("#isCapsLock").val("False");
            }

        });
    // fires when onboarding "Next" button is pressed
    $('#submit-onboard').click(
        function () {
            var ret = "";

            for (var i = 0; i < tmr.length - 1; ++i) {
                ret += ((i > 0) ? ";" : "") + (tmr[i].tmr);
            }
            $("#keystrokeDynamics_" + step).val(ret) // append dynamics to the hidden input that corresponds to the current onboarding step 
            tmr = []; // clear tmr for the next step

            // console.log(step)
            // console.log($("#keystrokeDynamics_1").val())
            // console.log($("#keystrokeDynamics_2").val())
            // console.log($("#keystrokeDynamics_3").val())
            // console.log($("#keystrokeDynamics_4").val())

            fixStepIndicator(step + 1) // update step indicators
            step++; // increment step

        });

    // this fires when the first step of onboarding is passed
    $('#submit-register').click(
        function () {
            fixStepIndicator(1) // update step indicators for the first step
        });
});

// step indicator update function
function fixStepIndicator(n) {
    var i, x = document.getElementsByClassName("step");
    for (i = 0; i < x.length; i++) {
        x[i].className = x[i].className.replace(" active", "");
        if (n > 0) {
            x[n - 1].className += " finish" // if already been in the step, mark it as finished
        }
    }
    // make current step indicator active
    x[n].className += " active";
}
