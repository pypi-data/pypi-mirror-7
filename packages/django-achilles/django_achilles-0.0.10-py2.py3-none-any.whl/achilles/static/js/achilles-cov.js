
// instrument by jscoverage, do not modifly this file
(function (file, lines, conds, source) {
  var BASE;
  if (typeof global === 'object') {
    BASE = global;
  } else if (typeof window === 'object') {
    BASE = window;
  } else {
    throw new Error('[jscoverage] unknow ENV!');
  }
  if (BASE._$jscoverage) {
    BASE._$jscmd(file, 'init', lines, conds, source);
    return;
  }
  var cov = {};
  /**
   * jsc(file, 'init', lines, condtions)
   * jsc(file, 'line', lineNum)
   * jsc(file, 'cond', lineNum, expr, start, offset)
   */
  function jscmd(file, type, line, express, start, offset) {
    var storage;
    switch (type) {
      case 'init':
        storage = [];
        for (var i = 0; i < line.length; i ++) {
          storage[line[i]] = 0;
        }
        var condition = express;
        var source = start;
        storage.condition = condition;
        storage.source = source;
        cov[file] = storage;
        break;
      case 'line':
        storage = cov[file];
        storage[line] ++;
        break;
      case 'cond':
        storage = cov[file];
        storage.condition[line] ++;
        return express;
    }
  }
  
  BASE._$jscoverage = cov;
  BASE._$jscmd = jscmd;
  jscmd(file, 'init', lines, conds, source);
})('achilles/static/js/achilles.js', [8,11,16,20,61,71,121,157,162,187,194,218,247,252,264,275,280,293,298,308,313,336,340,17,24,31,28,42,55,56,50,51,67,68,77,78,87,93,94,101,113,103,105,108,109,125,134,135,151,137,142,143,147,158,164,165,166,169,183,176,178,179,196,203,204,198,209,210,211,212,219,243,224,225,229,234,235,239,248,253,254,255,256,257,258,266,271,287,302,318,319,321,322,329,330], {"49_22_1":0,"49_27_16":0,"50_58_1":0,"75_18_3":0,"75_33_5":0,"102_12_15":0,"102_31_21":0,"102_31_15":0,"104_28_1":0,"104_32_14":0,"107_20_36":0,"107_60_12":0,"107_40_11":0,"107_61_4":0,"108_70_11":0,"210_54_13":0,"221_41_21":0,"221_58_4":0,"225_36_31":0,"227_24_7":0,"227_36_8":0,"235_38_33":0,"237_24_9":0,"237_38_10":0,"256_35_32":0,"257_37_34":0,"321_29_45":0,"321_29_31":0,"321_63_11":0,"321_29_24":0,"321_45_8":0}, ["/*"," * Achilles - Django AJAX framework"," *"," * This file provides the javascript framework to communicate with"," * Django Achilles backend"," *"," */","(function(window) {","","    // Make sure jquery is in the correct namespace","    var $ = window.jQuery;","","    /* CORE */","","    // Main constructor","    var Achilles = function(endpoint) {","        return new Achilles.fn.init(endpoint);","    };","","    Achilles.fn = Achilles.prototype = {","","        // Init achilles instance, set the server endpoint URL","        init: function(endpoint) {","            this.transport = new JSONTransport(this, endpoint);","","            // Init controllers for this instance","            for (c in this.controllers) {","                controller = this.controllers[c];","                if (controller.init) controller.init(this);","            }","            return this;","        },","","","        // Response controllers","        controllers: {},","","        // Register a response controller","        //     key - key from the response data to pass to this controller","        //     controller - the controller itself","        registerController: function(key, controller) {","            this.controllers[key] = controller;","        },","","","        // Process a message from the server","        processResponse: function(data) {","            for (c in data) {","                if (!(c in this.controllers)) {","                    console.error(\"Unknown controller \" + c);","                    continue;","                }","","                // Let the controller process its data","                var controller = this.controllers[c];","                controller.process(this, data[c]);","            }","        },","    };","","    Achilles.fn.init.prototype = Achilles.fn;","","","    /* JSON TRANSPORT */","    /* Default messages transport, using JQuery.ajax */","    function JSONTransport(achilles, endpoint) {","        this.endpoint = endpoint;","        this.achilles = achilles;","    }","","    JSONTransport.fn = JSONTransport.prototype = {","        // Send the given message to the server","        send: function(msg) {","            // Server processes array of dicts","            if (!(msg instanceof Array)) msg = [msg];","","            var _achilles = this.achilles;","            return $.ajax({","                url: this.endpoint,","                crossDomain: false,","                type: 'POST',","                beforeSend: this.setCSRFHeader,","                data: JSON.stringify(msg),","            })","            // Send success data back to achilles","            .success(function(data) {","                _achilles.processResponse(data)","            });","        },","","        setCSRFHeader: function(xhr, settings) {","            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) {","                var csrftoken = getCookie('csrftoken');","                xhr.setRequestHeader(\"X-CSRFToken\", csrftoken);","            }","        },","    };","","    // getCookie helper","    function getCookie(name) {","        var cookieValue = null;","        if (document.cookie && document.cookie != '') {","            var cookies = document.cookie.split(';');","            for (var i = 0; i < cookies.length; i++) {","                var cookie = $.trim(cookies[i]);","                // Does this cookie string begin with the name we want?","                if (cookie.substring(0, name.length + 1) == (name + '=')) {","                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));","                    break;","                }","            }","        }","        return cookieValue;","    }","","","","    /* ACTIONS */","","    // Register the response controller","    var actions_controller = {","","        init: function(achilles) {","            // Actions metadata","            achilles._actions = {","                count: 0,","                pending: Array(),","                error_observers: Array(),","            }","        },","","        process: function(achilles, actions) {","            for (action_id in actions) {","                var action_deferred = achilles._actions.pending[action_id];","                var result = actions[action_id];","                if (result.error) {","                    action_deferred.reject(result.error,","                                           result.message,","                                           result.trace);","","                    for (cb in achilles._actions.error_observers) {","                        cb = achilles._actions.error_observers[cb];","                        cb(result.error, result.message, result.trace);","                    }","                }","                else {","                    action_deferred.resolve(result.value);","                }","","                // Already processed, forget it:","                delete achilles._actions.pending[action_id];","            }","        },","    };","","    // Register an error observer","    Achilles.fn.onError = function(callback) {","        this._actions.error_observers.push(callback);","    }","","    // Remote action call","    Achilles.fn.action = function(name, args, kwargs) {","        // Save action deferred to trigger it when the response comes","        var action_id = this._actions.count++;","        var action_deferred = $.Deferred();","        this._actions.pending[action_id] = action_deferred;","","        // Launch the action","        this.transport.send({","            name: name,","            id: action_id,","            args: args,","            kwargs: kwargs","        }).error(function(jqXHR, textStatus) {","            // Reject in case of ajax error","            action_deferred.reject('TransportError', textStatus);","            for (cb in achilles._actions.error_observers) {","                cb = achilles._actions.error_observers[cb];","                cb('TransportError', textStatus);","            }","        });","","        return action_deferred;","    };","","    // Register the controller","    Achilles.fn.registerController('actions', actions_controller);","","","","    /* BLOCKS */","","    // Register the response controller","    var blocks_controller = {","        init: function(achilles) {","            achilles.block_updaters = {","                HTML: function (block, data) {","                    block.html(data)","                },","            };","","            // load lazy blocks","            var lazyblocks = $('[data-ablock][data-ablock-lazy]');","            achilles.update(lazyblocks);","        },","","        process: function(achilles, data) {","            for (b in data) {","                var block = data[b];","                var updater = achilles.block_updaters[block.updater || 'HTML'];","                var blocks = achilles.blocks(block.name, block.args, block.kwargs);","                updater(blocks, block.data);","            }","        },","    };","","    // Look for blocks matching the given criteria","    Achilles.fn.blocks = function(name, args, kwargs) {","        var blocks = $('[data-ablock]');","","        if (name) blocks = blocks.filter('[data-ablock=\"'+name+'\"]');","","        if (args) {","            blocks = blocks.filter(function(index) {","                bargs = $.parseJSON(blocks.attr('data-ablock-args') || '[]');","                for (k in args) {","                    if (args[k] !== bargs[k]) return false;","                }","                return true;","            });","        }","","        if (kwargs) {","            blocks = blocks.filter(function(index) {","                bkwargs = $.parseJSON(blocks.attr('data-ablock-kwargs') || '{}');","                for (k in kwargs) {","                    if (kwargs[k] !== bkwargs[k]) return false;","                }","                return true;","            });","        }","","        return blocks;","    };","","    // Look for the block matching the given criteria","    Achilles.fn.block = function(name, args, kwargs) {","        return this.blocks(name, args, kwargs).first();","    };","","    // Update the given blocks","    Achilles.fn.update = function(blocks) {","        var _achilles = this;","        blocks.each(function(block) {","            var name = $(this).attr('data-ablock');","            var args = $.parseJSON($(this).attr('data-ablock-args') || '[]');","            var kwargs = $.parseJSON($(this).attr('data-ablock-kwargs') || '{}');","            _achilles.action('blocks:update', [name].concat(args), kwargs)","        });","    };","","    // Load a block into the given element, if the given element is not a block,","    // this method will convert it to one","    Achilles.fn.loadInto = function(block, name, args, kwargs) {","        // Prepare the element wrapper","        block.attr('data-ablock', name);","        if (args) block.attr('data-ablock-args', JSON.stringify(args));","        if (kwargs) block.attr('data-ablock-kwargs', JSON.stringify(kwargs));","","        // Call for update","        this.update(block);","    };","","    // Register the controller","    Achilles.fn.registerController('blocks', blocks_controller);","","","    /* LOGS */","","    var console_controller = {","","        process: function(achilles, logs) {","            // Avoid unsupported browsers","            if (!window.console) return;","","            for (i in logs) {","                console.log(logs[i]);","            }","        },","    };","","    // Register the controller","    Achilles.fn.registerController('console', console_controller);","","","    /* REDIRECT */","","    var redirect_controller = {","","        process: function(achilles, redirect) {","            if (redirect.url) {","                window.location.href = redirect.url;","            }","        },","    };","","    // Register the controller","    Achilles.fn.registerController('redirect', redirect_controller);","","","    /* MESSAGES */","","    var messages_controller = {","","        init: function(achilles) {","","            // Default message implementation","            achilles.show_message = function(msg) {","                messages = $('#messages');","                if (messages) {","                    var li = '<li class=\"' + msg.tags + '\">' + msg.message + '</li>';","                    messages.append(li);","                }","            };","        },","","        process: function(achilles, messages) {","            for (msg in messages) {","                msg = messages[msg]","                achilles.show_message(msg);","            }","        },","    };","","    // Register the controller","    Achilles.fn.registerController('messages', messages_controller);","","","    // Expose achilles","    window.Achilles = Achilles;","})(window);","",""]);
/*
 * Achilles - Django AJAX framework
 *
 * This file provides the javascript framework to communicate with
 * Django Achilles backend
 *
 */
_$jscmd("achilles/static/js/achilles.js", "line", 8);

(function(window) {
    _$jscmd("achilles/static/js/achilles.js", "line", 11);
    // Make sure jquery is in the correct namespace
    var $ = window.jQuery;
    _$jscmd("achilles/static/js/achilles.js", "line", 16);
    /* CORE */
    // Main constructor
    var Achilles = function(endpoint) {
        _$jscmd("achilles/static/js/achilles.js", "line", 17);
        return new Achilles.fn.init(endpoint);
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 20);
    Achilles.fn = Achilles.prototype = {
        // Init achilles instance, set the server endpoint URL
        init: function(endpoint) {
            _$jscmd("achilles/static/js/achilles.js", "line", 24);
            this.transport = new JSONTransport(this, endpoint);
            // Init controllers for this instance
            for (c in this.controllers) {
                _$jscmd("achilles/static/js/achilles.js", "line", 28);
                controller = this.controllers[c];
                if (controller.init) controller.init(this);
            }
            _$jscmd("achilles/static/js/achilles.js", "line", 31);
            return this;
        },
        // Response controllers
        controllers: {},
        // Register a response controller
        //     key - key from the response data to pass to this controller
        //     controller - the controller itself
        registerController: function(key, controller) {
            _$jscmd("achilles/static/js/achilles.js", "line", 42);
            this.controllers[key] = controller;
        },
        // Process a message from the server
        processResponse: function(data) {
            for (c in data) {
                if (!(_$jscmd("achilles/static/js/achilles.js", "cond", "49_22_1", c) in _$jscmd("achilles/static/js/achilles.js", "cond", "49_27_16", this.controllers))) {
                    _$jscmd("achilles/static/js/achilles.js", "line", 50);
                    console.error("Unknown controller " + _$jscmd("achilles/static/js/achilles.js", "cond", "50_58_1", c));
                    _$jscmd("achilles/static/js/achilles.js", "line", 51);
                    continue;
                }
                _$jscmd("achilles/static/js/achilles.js", "line", 55);
                // Let the controller process its data
                var controller = this.controllers[c];
                _$jscmd("achilles/static/js/achilles.js", "line", 56);
                controller.process(this, data[c]);
            }
        }
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 61);
    Achilles.fn.init.prototype = Achilles.fn;
    /* JSON TRANSPORT */
    /* Default messages transport, using JQuery.ajax */
    function JSONTransport(achilles, endpoint) {
        _$jscmd("achilles/static/js/achilles.js", "line", 67);
        this.endpoint = endpoint;
        _$jscmd("achilles/static/js/achilles.js", "line", 68);
        this.achilles = achilles;
    }
    _$jscmd("achilles/static/js/achilles.js", "line", 71);
    JSONTransport.fn = JSONTransport.prototype = {
        // Send the given message to the server
        send: function(msg) {
            // Server processes array of dicts
            if (!(_$jscmd("achilles/static/js/achilles.js", "cond", "75_18_3", msg) instanceof _$jscmd("achilles/static/js/achilles.js", "cond", "75_33_5", Array))) msg = [ msg ];
            _$jscmd("achilles/static/js/achilles.js", "line", 77);
            var _achilles = this.achilles;
            _$jscmd("achilles/static/js/achilles.js", "line", 78);
            return $.ajax({
                url: this.endpoint,
                crossDomain: false,
                type: "POST",
                beforeSend: this.setCSRFHeader,
                data: JSON.stringify(msg)
            }).success(function(data) {
                _$jscmd("achilles/static/js/achilles.js", "line", 87);
                _achilles.processResponse(data);
            });
        },
        setCSRFHeader: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) {
                _$jscmd("achilles/static/js/achilles.js", "line", 93);
                var csrftoken = getCookie("csrftoken");
                _$jscmd("achilles/static/js/achilles.js", "line", 94);
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    };
    // getCookie helper
    function getCookie(name) {
        _$jscmd("achilles/static/js/achilles.js", "line", 101);
        var cookieValue = null;
        if (_$jscmd("achilles/static/js/achilles.js", "cond", "102_12_15", document.cookie) && _$jscmd("achilles/static/js/achilles.js", "cond", "102_31_21", _$jscmd("achilles/static/js/achilles.js", "cond", "102_31_15", document.cookie) != "")) {
            _$jscmd("achilles/static/js/achilles.js", "line", 103);
            var cookies = document.cookie.split(";");
            for (var i = 0; _$jscmd("achilles/static/js/achilles.js", "cond", "104_28_1", i) < _$jscmd("achilles/static/js/achilles.js", "cond", "104_32_14", cookies.length); i++) {
                _$jscmd("achilles/static/js/achilles.js", "line", 105);
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (_$jscmd("achilles/static/js/achilles.js", "cond", "107_20_36", cookie.substring(0, _$jscmd("achilles/static/js/achilles.js", "cond", "107_40_11", name.length) + 1)) == _$jscmd("achilles/static/js/achilles.js", "cond", "107_60_12", _$jscmd("achilles/static/js/achilles.js", "cond", "107_61_4", name) + "=")) {
                    _$jscmd("achilles/static/js/achilles.js", "line", 108);
                    cookieValue = decodeURIComponent(cookie.substring(_$jscmd("achilles/static/js/achilles.js", "cond", "108_70_11", name.length) + 1));
                    _$jscmd("achilles/static/js/achilles.js", "line", 109);
                    break;
                }
            }
        }
        _$jscmd("achilles/static/js/achilles.js", "line", 113);
        return cookieValue;
    }
    _$jscmd("achilles/static/js/achilles.js", "line", 121);
    /* ACTIONS */
    // Register the response controller
    var actions_controller = {
        init: function(achilles) {
            _$jscmd("achilles/static/js/achilles.js", "line", 125);
            // Actions metadata
            achilles._actions = {
                count: 0,
                pending: Array(),
                error_observers: Array()
            };
        },
        process: function(achilles, actions) {
            for (action_id in actions) {
                _$jscmd("achilles/static/js/achilles.js", "line", 134);
                var action_deferred = achilles._actions.pending[action_id];
                _$jscmd("achilles/static/js/achilles.js", "line", 135);
                var result = actions[action_id];
                if (result.error) {
                    _$jscmd("achilles/static/js/achilles.js", "line", 137);
                    action_deferred.reject(result.error, result.message, result.trace);
                    for (cb in achilles._actions.error_observers) {
                        _$jscmd("achilles/static/js/achilles.js", "line", 142);
                        cb = achilles._actions.error_observers[cb];
                        _$jscmd("achilles/static/js/achilles.js", "line", 143);
                        cb(result.error, result.message, result.trace);
                    }
                } else {
                    _$jscmd("achilles/static/js/achilles.js", "line", 147);
                    action_deferred.resolve(result.value);
                }
                _$jscmd("achilles/static/js/achilles.js", "line", 151);
                // Already processed, forget it:
                delete achilles._actions.pending[action_id];
            }
        }
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 157);
    // Register an error observer
    Achilles.fn.onError = function(callback) {
        _$jscmd("achilles/static/js/achilles.js", "line", 158);
        this._actions.error_observers.push(callback);
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 162);
    // Remote action call
    Achilles.fn.action = function(name, args, kwargs) {
        _$jscmd("achilles/static/js/achilles.js", "line", 164);
        // Save action deferred to trigger it when the response comes
        var action_id = this._actions.count++;
        _$jscmd("achilles/static/js/achilles.js", "line", 165);
        var action_deferred = $.Deferred();
        _$jscmd("achilles/static/js/achilles.js", "line", 166);
        this._actions.pending[action_id] = action_deferred;
        _$jscmd("achilles/static/js/achilles.js", "line", 169);
        // Launch the action
        this.transport.send({
            name: name,
            id: action_id,
            args: args,
            kwargs: kwargs
        }).error(function(jqXHR, textStatus) {
            _$jscmd("achilles/static/js/achilles.js", "line", 176);
            // Reject in case of ajax error
            action_deferred.reject("TransportError", textStatus);
            for (cb in achilles._actions.error_observers) {
                _$jscmd("achilles/static/js/achilles.js", "line", 178);
                cb = achilles._actions.error_observers[cb];
                _$jscmd("achilles/static/js/achilles.js", "line", 179);
                cb("TransportError", textStatus);
            }
        });
        _$jscmd("achilles/static/js/achilles.js", "line", 183);
        return action_deferred;
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 187);
    // Register the controller
    Achilles.fn.registerController("actions", actions_controller);
    _$jscmd("achilles/static/js/achilles.js", "line", 194);
    /* BLOCKS */
    // Register the response controller
    var blocks_controller = {
        init: function(achilles) {
            _$jscmd("achilles/static/js/achilles.js", "line", 196);
            achilles.block_updaters = {
                HTML: function(block, data) {
                    _$jscmd("achilles/static/js/achilles.js", "line", 198);
                    block.html(data);
                }
            };
            _$jscmd("achilles/static/js/achilles.js", "line", 203);
            // load lazy blocks
            var lazyblocks = $("[data-ablock][data-ablock-lazy]");
            _$jscmd("achilles/static/js/achilles.js", "line", 204);
            achilles.update(lazyblocks);
        },
        process: function(achilles, data) {
            for (b in data) {
                _$jscmd("achilles/static/js/achilles.js", "line", 209);
                var block = data[b];
                _$jscmd("achilles/static/js/achilles.js", "line", 210);
                var updater = achilles.block_updaters[_$jscmd("achilles/static/js/achilles.js", "cond", "210_54_13", block.updater) || "HTML"];
                _$jscmd("achilles/static/js/achilles.js", "line", 211);
                var blocks = achilles.blocks(block.name, block.args, block.kwargs);
                _$jscmd("achilles/static/js/achilles.js", "line", 212);
                updater(blocks, block.data);
            }
        }
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 218);
    // Look for blocks matching the given criteria
    Achilles.fn.blocks = function(name, args, kwargs) {
        _$jscmd("achilles/static/js/achilles.js", "line", 219);
        var blocks = $("[data-ablock]");
        if (name) blocks = blocks.filter(_$jscmd("achilles/static/js/achilles.js", "cond", "221_41_21", '[data-ablock="' + _$jscmd("achilles/static/js/achilles.js", "cond", "221_58_4", name)) + '"]');
        if (args) {
            _$jscmd("achilles/static/js/achilles.js", "line", 224);
            blocks = blocks.filter(function(index) {
                _$jscmd("achilles/static/js/achilles.js", "line", 225);
                bargs = $.parseJSON(_$jscmd("achilles/static/js/achilles.js", "cond", "225_36_31", blocks.attr("data-ablock-args")) || "[]");
                for (k in args) {
                    if (_$jscmd("achilles/static/js/achilles.js", "cond", "227_24_7", args[k]) !== _$jscmd("achilles/static/js/achilles.js", "cond", "227_36_8", bargs[k])) return false;
                }
                _$jscmd("achilles/static/js/achilles.js", "line", 229);
                return true;
            });
        }
        if (kwargs) {
            _$jscmd("achilles/static/js/achilles.js", "line", 234);
            blocks = blocks.filter(function(index) {
                _$jscmd("achilles/static/js/achilles.js", "line", 235);
                bkwargs = $.parseJSON(_$jscmd("achilles/static/js/achilles.js", "cond", "235_38_33", blocks.attr("data-ablock-kwargs")) || "{}");
                for (k in kwargs) {
                    if (_$jscmd("achilles/static/js/achilles.js", "cond", "237_24_9", kwargs[k]) !== _$jscmd("achilles/static/js/achilles.js", "cond", "237_38_10", bkwargs[k])) return false;
                }
                _$jscmd("achilles/static/js/achilles.js", "line", 239);
                return true;
            });
        }
        _$jscmd("achilles/static/js/achilles.js", "line", 243);
        return blocks;
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 247);
    // Look for the block matching the given criteria
    Achilles.fn.block = function(name, args, kwargs) {
        _$jscmd("achilles/static/js/achilles.js", "line", 248);
        return this.blocks(name, args, kwargs).first();
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 252);
    // Update the given blocks
    Achilles.fn.update = function(blocks) {
        _$jscmd("achilles/static/js/achilles.js", "line", 253);
        var _achilles = this;
        _$jscmd("achilles/static/js/achilles.js", "line", 254);
        blocks.each(function(block) {
            _$jscmd("achilles/static/js/achilles.js", "line", 255);
            var name = $(this).attr("data-ablock");
            _$jscmd("achilles/static/js/achilles.js", "line", 256);
            var args = $.parseJSON(_$jscmd("achilles/static/js/achilles.js", "cond", "256_35_32", $(this).attr("data-ablock-args")) || "[]");
            _$jscmd("achilles/static/js/achilles.js", "line", 257);
            var kwargs = $.parseJSON(_$jscmd("achilles/static/js/achilles.js", "cond", "257_37_34", $(this).attr("data-ablock-kwargs")) || "{}");
            _$jscmd("achilles/static/js/achilles.js", "line", 258);
            _achilles.action("blocks:update", [ name ].concat(args), kwargs);
        });
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 264);
    // Load a block into the given element, if the given element is not a block,
    // this method will convert it to one
    Achilles.fn.loadInto = function(block, name, args, kwargs) {
        _$jscmd("achilles/static/js/achilles.js", "line", 266);
        // Prepare the element wrapper
        block.attr("data-ablock", name);
        if (args) block.attr("data-ablock-args", JSON.stringify(args));
        if (kwargs) block.attr("data-ablock-kwargs", JSON.stringify(kwargs));
        _$jscmd("achilles/static/js/achilles.js", "line", 271);
        // Call for update
        this.update(block);
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 275);
    // Register the controller
    Achilles.fn.registerController("blocks", blocks_controller);
    _$jscmd("achilles/static/js/achilles.js", "line", 280);
    /* LOGS */
    var console_controller = {
        process: function(achilles, logs) {
            // Avoid unsupported browsers
            if (!window.console) return;
            for (i in logs) {
                _$jscmd("achilles/static/js/achilles.js", "line", 287);
                console.log(logs[i]);
            }
        }
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 293);
    // Register the controller
    Achilles.fn.registerController("console", console_controller);
    _$jscmd("achilles/static/js/achilles.js", "line", 298);
    /* REDIRECT */
    var redirect_controller = {
        process: function(achilles, redirect) {
            if (redirect.url) {
                _$jscmd("achilles/static/js/achilles.js", "line", 302);
                window.location.href = redirect.url;
            }
        }
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 308);
    // Register the controller
    Achilles.fn.registerController("redirect", redirect_controller);
    _$jscmd("achilles/static/js/achilles.js", "line", 313);
    /* MESSAGES */
    var messages_controller = {
        init: function(achilles) {
            _$jscmd("achilles/static/js/achilles.js", "line", 318);
            // Default message implementation
            achilles.show_message = function(msg) {
                _$jscmd("achilles/static/js/achilles.js", "line", 319);
                messages = $("#messages");
                if (messages) {
                    _$jscmd("achilles/static/js/achilles.js", "line", 321);
                    var li = _$jscmd("achilles/static/js/achilles.js", "cond", "321_29_45", _$jscmd("achilles/static/js/achilles.js", "cond", "321_29_31", _$jscmd("achilles/static/js/achilles.js", "cond", "321_29_24", '<li class="' + _$jscmd("achilles/static/js/achilles.js", "cond", "321_45_8", msg.tags)) + '">') + _$jscmd("achilles/static/js/achilles.js", "cond", "321_63_11", msg.message)) + "</li>";
                    _$jscmd("achilles/static/js/achilles.js", "line", 322);
                    messages.append(li);
                }
            };
        },
        process: function(achilles, messages) {
            for (msg in messages) {
                _$jscmd("achilles/static/js/achilles.js", "line", 329);
                msg = messages[msg];
                _$jscmd("achilles/static/js/achilles.js", "line", 330);
                achilles.show_message(msg);
            }
        }
    };
    _$jscmd("achilles/static/js/achilles.js", "line", 336);
    // Register the controller
    Achilles.fn.registerController("messages", messages_controller);
    _$jscmd("achilles/static/js/achilles.js", "line", 340);
    // Expose achilles
    window.Achilles = Achilles;
})(window);