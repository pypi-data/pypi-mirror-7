/* jshint strict: false, white: true */
/* global cw: false, Namespace: false, _: false */

cw.cubes.relationwidget = new Namespace('cw.cubes.relationwidget');

$.extend(cw.cubes.relationwidget, {

    toggleCheckboxes: function ($checkboxes) {
        $checkboxes.each(function (index, checkbox) {
            var $checkbox = $(checkbox);
            $checkbox.prop("checked", !$checkbox.prop("checked"));
        });
    }

});

(function ($) {
    $.fn.relationwidget = function (options) {
        var $widget = $(this),
            widgetuid = $widget.attr('id'),
            defaultSettings = {
                editOptions: {
                    required: false,
                    multiple: true,
                    searchurl: '<required-option>'
                },
                dialogOptions: {
                    modal: true,
                    width: 600,
                    height: 800,
                    buttons: [
                        {
                            id: 'button-validate',
                            text: _('button_ok'),
                            click: function () {
                                validate($(this));
                            }
                        },
                        {
                            id: 'button-cancel',
                            text: _('cancel'),
                            click: function () {
                                $(this).dialog('close');
                            }
                        }
                    ],
                    close: function () {
                        $widget.empty();
                        // unbind $widget
                        $widget.off('server-response');
                        $widget.off('click');
                        $(this).dialog('destroy');
                    }
                }
            };
        var editSettings = $.extend({}, defaultSettings.editOptions, options.editOptions),
            dialogSettings = $.extend({}, defaultSettings.dialogOptions, options.dialogOptions);

        function validate($modalDialog) {
            var $alert = $('#cw-relationwidget-alert');
            $alert.empty().addClass('hidden');
            var selected = getSelectedValues();
            if (editSettings.required && Object.keys(selected).length === 0) {
                $alert.text(_('required_error')).removeClass('hidden').addClass('alert-danger');
                return;
            }
            var $divgroup = $('ul#inputs-for-' + widgetuid);
            $divgroup.empty();
            var snippets = widgetuid.split('-');
            var inputname = snippets[1] + '-' + snippets[2] + ':' + snippets[3];
            for (var eid in selected) {
                var val = selected[eid];
                var escapedLabel = $('<div/>').text(' '+val).html();
                var $input = $('<input type="checkbox" checked="checked" name="' + inputname +
                               '" value="' + eid + '"id="' + inputname + '-' + eid +
                               '" data-label="' + escapedLabel + '">');
                var $label = $('<label>').append($input).append(escapedLabel);
                $divgroup.append($('<li>').append($label));
            }
            $modalDialog.dialog('close');
        }

        function initSelected() {
            // open entities link in new tab
            $('#cw-relationwidget-table table a').attr('target', '_blank');
            var $selected = $('#inputs-for-' + widgetuid + ' input');
            if ($selected.length === 0) {
                var label = $('<div/>').text(_('no selected entities'));
                $('#cw-relationwidget-linked-summary').append(label);
            } else {
                $selected.each(function (index, input) {
                    var $input = $(input);
                    if ($input.prop("checked")) {
                        var eid = $input.attr('value');
                        addOrUpdateCheckbox(eid, $input.data('label'), true);
                        $('#cw-relationwidget-table input[value='+eid+']').prop("checked", true);
                    }
                });
            }
        }

        function getSelectedValues() {
            var selected = {};
            $('#cw-relationwidget-linked-summary label').each(function () {
                var $this = $(this);
                var eid = $this.find('input:checked').attr('id');
                if (eid) {
                    selected[eid] = $this.text();
                }
            });
            return selected;
        }

        function syncCheckboxes() {
            // syncCheckboxes MUST be called after each pagination on 'server-response'
            // which alload to know when to refresh this for the prev/next pages,
            // open entities link in new tab
            $('#cw-relationwidget-table table a').attr('target', '_blank');
            var selected = getSelectedValues();
            for (var eid in selected) {
                var $input = $('#cw-relationwidget-table input[value='+eid+']');
                if ($input.length === 1) {
                    // this input can be on another page
                    $input.prop('checked', 'checked');}
            }
        }

        function emptyData() {
            $('#cw-relationwidget-linked-summary').empty();
            var label = $('<div/>').text(_('no selected entities'));
            $('#cw-relationwidget-linked-summary').append(label);
        }

        function toggleRelatedCheckbox(eid, check) {
            var $input = $('#cw-relationwidget-table input[value='+eid+']');
            $input.prop("checked", check);
        }

        function addOrUpdateCheckbox(eid, label, check) {
            $('#cw-relationwidget-linked-summary div').hide();
            var $input = $('input#' + eid);
            if ($input.length === 0) {
                $input = $('<input type="checkbox" checked="checked">').attr('id', eid);
                var escapedLabel = $('<div/>').text(' '+label).html();
                var $label = $('<label>').append($input).append(escapedLabel);
                var $item = $('<li>').attr('class', 'add_related').append($label);
                $('#cw-relationwidget-linked-summary').append($item);
                $input.click(function () {
                    toggleRelatedCheckbox(eid, $(this).prop('checked'));
                });
            }
            else {
                $input.prop("checked", check);
            }
        }

        // isntantiate dialog window
        $widget.dialog(dialogSettings);
        var d = $widget.loadxhtml(editSettings.searchurl);
        d.addCallback(function () {
            // bind the pagination response to synchronize the checked values
            // fix me me should only do this on the pagination callback, but
            // this is not possible for the moment
            $widget.bind('server-response', function (e) {syncCheckboxes();});
            var checkboxesSelector = '#cw-relationwidget-table input[type=checkbox]';
            $widget.on('click', checkboxesSelector, function (e) {
                var $input = $(this);
                var label = $input.closest('td').siblings('td').text();
                if (!editSettings.multiple) {
                    // only one value can be set on this relation
                    emptyData();
                }
                addOrUpdateCheckbox(this.value, label, $input.prop('checked'));
            });
            initSelected();
        });
    };
})(jQuery);
