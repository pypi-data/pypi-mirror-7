var purely = {
    throwAssertionError: function(msg) {
        // throws TypeError as there isn't a built-in assertion error type
        throw TypeError('AssertionError: ' + msg);

        /*
            // Safer alternative?
            throw {
                name: 'TypeError',
                message: 'AssertionError: ' + msg
            };
        */
    },

    contains: function(item, arr) {
        var found = false;

        for (var i = 0; i < arr.length; i++) {
            if (arr[i] == item) {
                found = true;
                break;
            }
        }

        return found;
    },


    assertEqual: function(x, y) {
        // jshint -W018
        if (!(x === y)) {
            purely.throwAssertionError((x && x.toString()) + ' === ' + (y && y.toString()));
        }
    },

    assertNotEqual: function(x, y) {
        // jshint -W018
        if (!(x !== y)) {
            purely.throwAssertionError((x && x.toString()) + ' !== ' + (y && y.toString()));
        }
    },


    assertGreater: function(x, y) {
        // jshint -W018
        if (!(x > y)) {
            purely.throwAssertionError((x && x.toString()) + ' > ' + (y && y.toString()));
        }
    },

    assertGreaterEqual: function(x, y) {
        // jshint -W018
        if (!(x >= y)) {
            purely.throwAssertionError((x && x.toString()) + ' >= ' + (y && y.toString()));
        }
    },

    assertLess: function(x, y) {
        // jshint -W018
        if (!(x < y)) {
            purely.throwAssertionError((x && x.toString()) + ' < ' + (y && y.toString()));
        }
    },

    assertLessEqual: function(x, y) {
        // jshint -W018
        if (!(x <= y)) {
            purely.throwAssertionError((x && x.toString()) + ' <= ' + (y && y.toString()));
        }
    },


    assertIn: function(item, arr) {
        var found = purely.contains(item, arr);

        if (!found) {
            purely.throwAssertionError((item && item.toString()) + ' not in ' + (arr && arr.toString()));
        }
    },

    assertNotIn: function(item, arr) {
        var found = purely.contains(item, arr);

        if (found) {
            purely.throwAssertionError((item && item.toString()) + ' in ' + (arr && arr.toString()));
        }
    },


    assertRaises: function(exceptionName, func) {
        var thrown = false;

        try {
            func();
        } catch (e) {
            if (e.name === exceptionName) {
                thrown = true;
            }
        }

        if (!thrown) {
            purely.throwAssertionError(exceptionName + ' not thrown');
        }
    },

    assertRaisesAssertion: function(func) {
        var thrown = false;

        try {
            func();
        } catch (e) {
            if ((e.name == 'TypeError') && (/^AssertionError: /.test(e.message))) {
                thrown = true;
            }
        }

        if (!thrown) {
            purely.throwAssertionError('AssertionError not thrown');
        }
    }
};
