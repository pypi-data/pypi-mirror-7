/* 
 * bdajax v1.5.1
 * 
 * Author: Robert Niederreiter
 * License: GPL
 * 
 * Requires:
 * - jQuery 1.6.4+
 * - jQuery Tools overlay.js
 */

(function($) {

    $(document).ready(function() {
        bdajax.spinner.hide();
        $(document).bdajax();
    });

    $.fn.bdajax = function() {
        var context = $(this);
        $('*', context).each(function() {
            for (var i in this.attributes) {
                var attr = this.attributes[i];
                if (attr && attr.nodeName) {
                    var name = attr.nodeName;
                    if (name.indexOf('ajax:bind') > -1) {
                        var events = attr.nodeValue;
                        var ajax = $(this);
                        ajax.unbind(events);
                        if (ajax.attr('ajax:action')
                         || ajax.attr('ajax:event')
                         || ajax.attr('ajax:overlay')) {
                            ajax.bind(events, bdajax._dispatching_handler);
                        }
                    }
                    if (name.indexOf('ajax:form') > -1) {
                        bdajax.prepare_ajax_form($(this));
                    }
                }
            }
        });
        // B/C: Ajax forms have a dedicated ``ajax:form`` directive now.
        bdajax.bind_ajax_form(context);
        for (var binder in bdajax.binders) {
            bdajax.binders[binder](context);
        }
        return context;
    }

    bdajax = {

        // By default, we redirect to the login page on 403 error.
        // That we assume at '/login'.
        default_403: '/login',

        // object for hooking up JS binding functions after ajax calls
        binders: {},

        // ajax spinner handling
        spinner: {

            _elem: null,
            _request_count: 0,

            elem: function() {
                if (this._elem == null) {
                    this._elem = $('#ajax-spinner');
                }
                return this._elem;
            },

            show: function() {
                this._request_count++;
                if (this._request_count > 1) {
                    return;
                }
                this.elem().show();
            },

            hide: function(force) {
                this._request_count--;
                if (force) {
                    this._request_count = 0;
                    this.elem().hide();
                    return;
                } else if (this._request_count <= 0) {
                    this._request_count = 0;
                    this.elem().hide();
                }
            }
        },

        parseurl: function(url) {
            var idx = url.indexOf('?');
            if (idx != -1) {
                url = url.substring(0, idx);
            }
            if (url.charAt(url.length - 1) == '/') {
                url = url.substring(0, url.length - 1);
            }
            return url;
        },

        parsequery: function(url) {
            var params = {};
            var idx = url.indexOf('?');
            if (idx != -1) {
                var parameters = url.slice(idx + 1).split('&');
                for (var i = 0;  i < parameters.length; i++) {
                    var param = parameters[i].split('=');
                    params[param[0]] = param[1];
                }
            }
            return params;
        },

        parsetarget: function(target) {
            var url = this.parseurl(target);
            var params = this.parsequery(target);
            if (!params) { params = {}; }
            return {
                url: url,
                params: params
            };
        },

        request: function(options) {
            if (options.url.indexOf('?') != -1) {
                var addparams = options.params;
                options.params = this.parsequery(options.url);
                options.url = this.parseurl(options.url);
                for (var key in addparams) {
                    options.params[key] = addparams[key];
                }
            } else {
                if (!options.params) { options.params = {}; }
            }
            if (!options.type) { options.type = 'html'; }
            if (!options.error) {
                options.error = function(req, status, exception) {
                    if (parseInt(status, 10) === 403) {
                        window.location.pathname = bdajax.default_403;
                    } else {
                        var message = '<strong>' + status + '</strong> ';
                        message += exception;
                        bdajax.error(message);
                    }
                };
            }
            if (!options.cache) { options.cache = false; }
            var wrapped_success = function(data, status, request) {
                options.success(data, status, request);
                bdajax.spinner.hide();
            }
            var wrapped_error = function(request, status, error) {
                if (request.status == 0) {
                    bdajax.spinner.hide(true);
                    return;
                }
                var status = request.status || status;
                var error = request.statusText || error;
                options.error(request, status, error);
                bdajax.spinner.hide(true);
            }
            this.spinner.show();
            $.ajax({
                url: options.url,
                dataType: options.type,
                data: options.params,
                success: wrapped_success,
                error: wrapped_error,
                cache: options.cache
            });
        },

        action: function(options) {
            options.success = this._ajax_action_success;
            this._perform_ajax_action(options);
        },

        fiddle: function(payload, selector, mode) {
            if (mode == 'replace') {
                $(selector).replaceWith(payload);
                var context = $(selector);
                if (context.length) {
                    context.parent().bdajax();
                } else {
                    $(document).bdajax();
                }
            } else if (mode == 'inner') {
                $(selector).html(payload);
                $(selector).bdajax();
            }
        },

        continuation: function(definitions) {
            if (!definitions) {
                return;
            }
            this.spinner.hide();
            var definition, target;
            for (var idx in definitions) {
                definition = definitions[idx];
                if (definition.type == 'action') {
                    target = this.parsetarget(definition.target);
                    this.action({
                        url: target.url,
                        params: target.params,
                        name: definition.name,
                        mode: definition.mode,
                        selector: definition.selector
                    });
                } else if (definition.type == 'event') {
                    this.trigger(definition.name,
                                 definition.selector,
                                 definition.target);
                } else if (definition.type == 'overlay') {
                    if (definition.close) {
                        var elem = $(definition.selector);
                        var overlay = elem.data('overlay');
                        if (overlay) {
                            overlay.close();
                        }
                    } else {
                        var target = this.parsetarget(definition.target);
                        this.overlay({
                            action: definition.action,
                            selector: definition.selector,
                            content_selector: definition.content_selector,
                            url: target.url,
                            params: target.params
                        });
                    }
                } else if (definition.type == 'message') {
                    if (definition.flavor) {
                        var flavors = ['message', 'info', 'warning', 'error'];
                        if (flavors.indexOf(definition.flavor) == -1) {
                            throw "Continuation definition.flavor unknown";
                        }
                        switch (definition.flavor) {
                            case 'message':
                                this.message(definition.payload);
                                break;
                            case 'info':
                                this.info(definition.payload);
                                break;
                            case 'warning':
                                this.warning(definition.payload);
                                break;
                            case 'error':
                                this.error(definition.payload);
                                break;
                        }
                    } else {
                        if (!definition.selector) {
                            throw "Continuation definition.selector expected";
                        }
                        $(definition.selector).html(definition.payload);
                    }
                }
            }
        },

        trigger: function(name, selector, target) {
            var create_event = function() {
                var evt = $.Event(name);
                if (target.url) {
                    evt.ajaxtarget = target;
                } else {
                    evt.ajaxtarget = bdajax.parsetarget(target);
                }
                return evt;
            }
            // _dispatching_handler calls stopPropagation on event which is
            // fine in order to prevent weird behavior on parent DOM elements,
            // especially for standard events. Since upgrade to jQuery 1.9
            // stopPropagation seem to react on the event instance instead of
            // the trigger call for each element returned by selector, at least
            // on custom events, thus we create a separate event instance for
            // each elem returned by selector.
            $(selector).each(function() {
                $(this).trigger(create_event());
            });
        },

        overlay: function(options) {
            var selector = '#ajax-overlay';
            if (options.selector) {
                selector = options.selector;
            }
            var content_selector = '.overlay_content';
            if (options.content_selector) {
                content_selector = options.content_selector;
            }
            var elem = $(selector);
            elem.removeData('overlay');
            var url, params;
            if (options.target) {
                var target = this.parsetarget(options.target);
                url = target.url;
                params = target.params;
            } else {
                url = options.url;
                params = options.params;
            }
            this._perform_ajax_action({
                name: options.action,
                selector: selector + ' ' + content_selector,
                mode: 'inner',
                url: url,
                params: params,
                success: function(data) {
                    bdajax._ajax_action_success(data);
                    // overlays are not displayed if no payload is received.
                    if (!data.payload) {
                        return;
                    }
                    elem.overlay({
                        mask: {
                            color: '#fff',
                            loadSpeed: 200
                        },
                        onClose: function() {
                            var content = $(content_selector,
                                            this.getOverlay());
                            content.html('');
                        },
                        oneInstance: false,
                        closeOnClick: true,
                        fixed: false
                    });
                    var overlay = elem.data('overlay');
                    overlay.load();
                }
            });
        },

        message: function(message) {
            var elem = $('#ajax-message');
            elem.removeData('overlay');
            elem.overlay({
                mask: {
                    color: '#fff',
                    loadSpeed: 200
                },
                onBeforeLoad: function() {
                    var overlay = this.getOverlay();
                    $('.message', overlay).html(message);
                },
                onLoad: function() {
                    elem.find('button:first').focus();
                },
                onBeforeClose: function() {
                    var overlay = this.getOverlay();
                    $('.message', overlay).empty();
                },
                oneInstance: false,
                closeOnClick: false,
                fixed: false,
                top:'20%'
            });
            elem.data('overlay').load();
        },

        error: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('error');
            this.message(message);
        },

        info: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('info');
            this.message(message);
        },

        warning: function(message) {
            $("#ajax-message .message").removeClass('error warning info')
                                       .addClass('warning');
            this.message(message);
        },

        dialog: function(options, callback) {
            var elem = $('#ajax-dialog');
            elem.removeData('overlay');
            elem.overlay({
                mask: {
                    color: '#fff',
                    loadSpeed: 200
                },
                onBeforeLoad: function() {
                    var overlay = this.getOverlay();
                    var closefunc = this.close;
                    $('.text', overlay).html(options.message);
                    $('button', overlay).unbind();
                    $('button.submit', overlay).bind('click', function() {
                        closefunc();
                        callback(options);
                    });
                    $('button.cancel', overlay).bind('click', function() {
                        closefunc();
                    });
                },
                oneInstance: false,
                closeOnClick: false,
                fixed: false,
                top:'20%'
            });
            elem.data('overlay').load();
        },

        // B/C: bind ajax form handling to all forms providing ajax css class
        bind_ajax_form: function(context) {
            bdajax.prepare_ajax_form($('form.ajax', context));
        },

        // prepare form desired to be an ajax form
        prepare_ajax_form: function(form) {
            form.append('<input type="hidden" name="ajax" value="1" />');
            form.attr('target', 'ajaxformresponse');
            form.unbind().bind('submit', function(event) {
                bdajax.spinner.show();
            });
        },

        // called by iframe response, renders form (i.e. if validation errors)
        render_ajax_form: function(payload, selector, mode) {
            if (!payload) {
                return;
            }
            this.spinner.hide();
            this.fiddle(payload, selector, mode);
        },

        _dispatching_handler: function(event) {
            event.preventDefault();
            event.stopPropagation();
            var elem = $(this);
            var options = {
                elem: elem,
                event: event
            };
            if (elem.attr('ajax:confirm')) {
                options.message = elem.attr('ajax:confirm');
                bdajax.dialog(options, bdajax._do_dispatching);
            } else {
                bdajax._do_dispatching(options);
            }
        },

        _do_dispatching: function(options) {
            var elem = options.elem;
            var event = options.event;
            if (elem.attr('ajax:action')) {
                bdajax._handle_ajax_action(elem, event);
            }
            if (elem.attr('ajax:event')) {
                bdajax._handle_ajax_event(elem);
            }
            if (elem.attr('ajax:overlay')) {
                bdajax._handle_ajax_overlay(elem, event);
            }
        },

        _handle_ajax_event: function(elem) {
            var target = elem.attr('ajax:target');
            var defs = this._defs_to_array(elem.attr('ajax:event'));
            for (var i = 0; i < defs.length; i++) {
                var def = defs[i];
                def = def.split(':');
                this.trigger(def[0], def[1], target);
            }
        },

        _ajax_action_success: function(data) {
            if (!data) {
                bdajax.error('Empty response');
                bdajax.spinner.hide();
            } else {
                bdajax.fiddle(data.payload, data.selector, data.mode);
                bdajax.continuation(data.continuation);
            }
        },

        _perform_ajax_action: function(options) {
            options.params['bdajax.action'] = options.name;
            options.params['bdajax.mode'] = options.mode;
            options.params['bdajax.selector'] = options.selector;
            this.request({
                url: bdajax.parseurl(options.url) + '/ajaxaction',
                type: 'json',
                params: options.params,
                success: options.success
            });
        },

        _handle_ajax_action: function(elem, event) {
            var target;
            if (event.ajaxtarget) {
                target = event.ajaxtarget;
            } else {
                target = this.parsetarget(elem.attr('ajax:target'));
            }
            var actions = this._defs_to_array(elem.attr('ajax:action'));
            for (var i = 0; i < actions.length; i++) {
                var defs = actions[i].split(':');
                this.action({
                    name: defs[0],
                    selector: defs[1],
                    mode: defs[2],
                    url: target.url,
                    params: target.params
                });
            }
        },

        _handle_ajax_overlay: function(elem, event) {
            var target;
            if (event.ajaxtarget) {
                target = event.ajaxtarget;
            } else {
                target = this.parsetarget(elem.attr('ajax:target'));
            }
            var overlay_attr = elem.attr('ajax:overlay');
            if (overlay_attr.indexOf(':') > -1) {
                var defs = overlay_attr.split(':');
                var options = {
                    action: defs[0],
                    selector: defs[1],
                    url: target.url,
                    params: target.params
                };
                if (defs.length == 3) {
                    options.content_selector = defs[2];
                }
                this.overlay(options);
            } else {
                this.overlay({
                    action: overlay_attr,
                    url: target.url,
                    params: target.params
                });
            }
        },

        _defs_to_array: function(str) {
            // XXX: if space in selector when receiving def str, this will fail
            var arr = str.replace(/\s+/g, ' ').split(' ');
            return arr;
        }
    };

})(jQuery);