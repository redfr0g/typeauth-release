/**
typeauth.js - handles recording keystroke dynamics from sentence form during login process.
@redfr0g 2021 
**/

// wait for DOM to load
$(function () {
    // global timer array
    var tmr = [];
    var backspc = 0;
    var shift = 0;
    var capslock = false;

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
        // //console.log(tmr)
    });

    // get keyup event from text input  
    $('#floatingInput').keyup(function (evt) {

        if (tmr.length > 0 && tmr[tmr.length - 1].evt == "keyup" && evt.keyCode != 8 && evt.keyCode != 20 && evt.keyCode != 16) {
            return;
        }

        if (evt.keyCode == 13) { // ignore enter
            return;
        }

        if (evt.keyCode == 20) { // check if caps lock was pressed
            capslock = true;
        }

        if (evt.keyCode == 8) { // increment backspace count
            backspc += 1;
        }

        if (evt.keyCode == 16) {
            shift += 1; // increment shift count
        }

        tmr.push({
            "tmr": evt.timeStamp,
            "key_code": evt.keyCode,
            "evt": "keyup"
        });
        //console.log("Key code: " + evt.which + " On time: " + evt.timeStamp);
        ////console.log(tmr)
    });

    $('#submit').click(
        function computeDynamic() { // compute keystroke dynamic
            // result from this function you can send as any other input 
            // to server for dynamics evaluation
            var ret = "";

            for (var i = 0; i < tmr.length - 1; ++i) {
                ret += ((i > 0) ? ";" : "") + (tmr[i].tmr);
            }

            //console.log("Keystroke dynamics: " + ret);

            //set value of keystroke dynamics parameters and feature keys presses
            $("#keystrokeDynamics").val(ret);
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
});
