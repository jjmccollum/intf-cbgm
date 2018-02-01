'use strict';

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

/**
 * This module implements the toolbar that is on most of the panels.
 *
 * @module toolbar
 *
 * @author Marcello Perathoner
 */

define(['jquery', 'lodash', 'bootstrap', 'bootstrap-slider', 'css!bootstrap-slider-css', 'css!toolbar-css'], function ($, _) {
    function get_control_type($input) {
        return $input.attr('data-type') || $input.attr('type') || 'button';
    }

    function connectivity_formatter(s) {
        return s === 21 ? 'All' : s;
    }

    /**
     * Read the status of the toolbar buttons after event
     *
     * @function handle_toolbar_events
     *
     * @param {Object} event - The event.  The status is saved in
     *                         event.data.data
     */

    function handle_toolbar_events(event) {
        if (event.type === 'click' || event.type === 'slideStop') {
            var opts = event.data.data;
            var $target = $(event.target);
            var $group = $target.closest('.btn-group');
            var name = $target.attr('name');
            var type = get_control_type($target);

            switch (type) {
                case 'checkbox':
                    opts[name] = [];
                    $group.find('input:checked').each(function (i, btn) {
                        opts[name].push($(btn).attr('data-opt'));
                    });
                    break;
                case 'radio':
                    opts[name] = $target.attr('data-opt');
                    break;
                case 'slider':
                    opts[name] = $target.bootstrapSlider('getValue');
                    break;
                case 'dropdown':
                    opts[name] = $target.attr('data-opt');
                    var $dropdown = $group.parent().closest('.btn-group').find('button[data-toggle="dropdown"]');
                    $dropdown.dropdown('toggle'); // close
                    break;
                default:
            }
        }
    }

    function on_toolbar(event) {
        var instance = event.data;

        handle_toolbar_events(event);
        instance.load(instance.data.passage);

        event.stopPropagation();
    }

    /**
     * Set the status of the toolbar buttons
     *
     * @function set_toolbar_buttons
     *
     * @param {jQuery} $toolbar   - The toolbar
     * @param {Object} new_status - The new status of the toolbar buttons
     */

    function set_toolbar_buttons($toolbar, new_status) {
        var $panel = $toolbar.closest('div.panel');

        _.forEach(new_status, function (value, key) {
            var $input = $panel.find('input[name="' + key + '"]');
            var $group = $input.closest('.btn-group');
            var type = get_control_type($input);

            switch (type) {
                case 'checkbox':
                    $group.find('label.btn').removeClass('active');
                    $group.find('input').prop('checked', false);

                    _.forEach(value, function (v) {
                        $input = $group.find('input[name="' + key + '"][data-opt="' + v + '"]');
                        $input.prop('checked', true);
                        $input.closest('label.btn').addClass('active');
                    });
                    break;
                case 'radio':
                    $input = $group.find('input[name="' + key + '"][data-opt="' + value + '"]');
                    $input.checked = true;
                    $group.find('label.btn').removeClass('active');
                    $input.closest('label.btn').addClass('active');
                    break;
                case 'slider':
                    $input.bootstrapSlider('setValue', +value);
                    $panel.find('span.connectivity-label').text(connectivity_formatter(value));
                    break;
                case 'dropdown':
                    if (key === 'hyp_a') {
                        key = 'labez';
                    }
                    var $dropdown = $group.parent().closest('.btn-group').find('button[data-toggle="dropdown"]');
                    $dropdown.attr('data-' + key, value);
                    var i18n = $.trim($group.find('label.btn[data-' + key + '="' + value + '"]').text());
                    $dropdown.find('span.btn_text').text(i18n);
                    break;
                default:
            }
        });
    }

    /**
     * Loads the buttons in the labez dropdown.
     *
     * Loads the buttons in the labez dropdown with the labez of the readings of
     * the passage.
     *
     * @function load_labez_dropdown
     *
     * @param {jQuery} $group      - The button group
     * @param {Object} passage     - The passage
     * @param {string} input_name  - <input name=name ...>
     * @param {Array} prefixes     - Strings to prepend to the list.
     * @param {Array} suffixes     - Strings to append to the list.
     *
     * @return {Promise} Promise, resolved when the buttons are loaded.
     */

    function load_labez_dropdown($group, passage, input_name, prefixes, suffixes) {
        var deferred = $.Deferred();
        var $menu = $group.find('div[data-toggle="buttons"]');

        $.getJSON('passage.json/' + passage.pass_id, function (json) {
            $menu.empty();
            var readings = prefixes.concat(json.data.readings).concat(suffixes);
            var _iteratorNormalCompletion = true;
            var _didIteratorError = false;
            var _iteratorError = undefined;

            try {
                for (var _iterator = readings[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                    var _ref = _step.value;

                    var _ref2 = _slicedToArray(_ref, 2);

                    var labez = _ref2[0];
                    var labez_i18n = _ref2[1];

                    if (labez[0] !== 'z') {
                        $menu.append('<label class="btn btn-primary btn-labez bg_labez" data-labez="' + labez + '">\n                                     <input type="radio" data-type="dropdown" name="' + input_name + '"\n                                            data-opt="' + labez + '">' + labez_i18n + '</input>\n                                   </label>');
                    }
                }
            } catch (err) {
                _didIteratorError = true;
                _iteratorError = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion && _iterator.return) {
                        _iterator.return();
                    }
                } finally {
                    if (_didIteratorError) {
                        throw _iteratorError;
                    }
                }
            }

            deferred.resolve();
        });
        return deferred.promise();
    }

    /**
     * Loads the buttons in the cliques dropdown.
     *
     * Loads the buttons in the cliques dropdown with the cliques of the
     * passage.
     *
     * @function load_cliques_dropdown
     *
     * @param {jQuery} $group      - The button group
     * @param {Object} passage     - The passage
     * @param {string} input_name  - <input name=name ...>
     * @param {Array} prefixes     - Strings to prepend to the list.
     * @param {Array} suffixes     - Strings to append to the list.
     *
     * @return {Promise} Promise, resolved when the buttons are loaded.
     */

    function load_cliques_dropdown($group, passage, input_name, prefixes, suffixes) {
        var deferred = $.Deferred();
        var $menu = $group.find('div[data-toggle="buttons"]');

        $.getJSON('passage.json/' + passage.pass_id, function (json) {
            $menu.empty();
            var cliques = prefixes.concat(json.data.cliques).concat(suffixes);
            var _iteratorNormalCompletion2 = true;
            var _didIteratorError2 = false;
            var _iteratorError2 = undefined;

            try {
                for (var _iterator2 = cliques[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                    var _ref3 = _step2.value;

                    var _ref4 = _slicedToArray(_ref3, 3);

                    var labez = _ref4[0];
                    var clique = _ref4[2];

                    if (labez[0] !== 'z') {
                        $menu.append('<label class="btn btn-primary btn-labez bg_labez" data-labez="' + labez + '">\n                                     <input type="radio" data-type="dropdown" name="' + input_name + '"\n                                            data-opt="' + clique + '">' + clique + '</input>\n                                   </label>');
                    }
                }
            } catch (err) {
                _didIteratorError2 = true;
                _iteratorError2 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion2 && _iterator2.return) {
                        _iterator2.return();
                    }
                } finally {
                    if (_didIteratorError2) {
                        throw _iteratorError2;
                    }
                }
            }

            deferred.resolve();
        });
        return deferred.promise();
    }

    /**
     * Loads the buttons in the range dropdown.
     *
     * Loads the buttons in the range dropdown with the ranges of the book.
     *
     * @function load_range_dropdown
     *
     * @param {jQuery} $group      - The button group
     * @param {Object} passage     - The passage
     * @param {string} input_name  - The button(s) name
     * @param {Array} prefixes     - Strings to prepend to the list.
     * @param {Array} suffixes     - Strings to append to the list.
     *
     * @return {Promise} Promise, resolved when the buttons are loaded.
     */

    function load_range_dropdown($group, passage, input_name, prefixes, suffixes) {
        var deferred = $.Deferred();
        var $menu = $group.find('div[data-toggle="buttons"]');

        $.getJSON('ranges.json/' + passage.pass_id, function (json) {
            $menu.empty();
            var ranges = prefixes.concat(json.data.ranges).concat(suffixes);
            var _iteratorNormalCompletion3 = true;
            var _didIteratorError3 = false;
            var _iteratorError3 = undefined;

            try {
                for (var _iterator3 = ranges[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
                    var range = _step3.value;

                    $menu.append('<label class="btn btn-primary btn-range" data-range="' + range.value + '">\n                                 <input type="radio" data-type="dropdown" name="' + input_name + '"\n                                        data-opt="' + range.value + '">' + range.range + '</input>\n                               </label>');
                }
            } catch (err) {
                _didIteratorError3 = true;
                _iteratorError3 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion3 && _iterator3.return) {
                        _iterator3.return();
                    }
                } finally {
                    if (_didIteratorError3) {
                        throw _iteratorError3;
                    }
                }
            }

            deferred.resolve();
        });
        return deferred.promise();
    }

    /**
     * Initialize the module.
     *
     * @function init
     *
     * @param {Object} instance - The panel instance
     * @param {Object} $toolbar - The toolbar element
     *
     * @returns {Object} The module instance object
     */

    function init(instance, $toolbar) {
        instance.$toolbar = $toolbar;

        // Init toolbar.
        $toolbar.find('.dropdown-toggle').dropdown();

        $toolbar.find('input[name="connectivity"]').bootstrapSlider({
            'value': 5,
            'ticks': [1, 5, 10, 20, 21],
            'ticks_positions': [0, 25, 50, 90, 100],
            'formatter': connectivity_formatter
        });

        // Answer toolbar activity.
        $toolbar.on('click slideStop', 'input', instance, on_toolbar);
        return instance;
    }

    return {
        'init': init,
        'set_toolbar_buttons': set_toolbar_buttons,
        'load_labez_dropdown': load_labez_dropdown,
        'load_cliques_dropdown': load_cliques_dropdown,
        'load_range_dropdown': load_range_dropdown
    };
});

//# sourceMappingURL=toolbar.js.map