odoo.define('sale_order_line_image_wizard.widget', function (require) {
"use strict";

var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc')
var Widget = require('web.Widget');
var Context = require('web.Context');
var data_manager = require('web.data_manager');
var widget_registry = require('web.widget_registry');
var config = require('web.config');

var _t = core._t;
var time = require('web.time');

var SaleProductImage = Widget.extend({
    template: 'sale_order_line_image_wizard.image_wizard',
    events: _.extend({}, Widget.prototype.events, {
        'click .fa-file-o': '_onClickButton',
    }),

    /**
     * @override
     * @param {Widget|null} parent
     * @param {Object} params
     */
    init: function (parent, params) {
        this.data = params.data;
        this._super(parent);
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._setPopOver();
        });
    },

    updateState: function (state) {
        this.$el.popover('dispose');
        var candidate = state.data[this.getParent().currentRow];
        if (candidate) {
            this.data = candidate.data;
            this.renderElement();
            this._setPopOver();
        }
    },
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * Set a bootstrap popover on the current QtyAtDate widget that display available
     * quantity.
     */
    _setPopOver: function () {
        var self = this;

        if (!this.data.has_image) {
            return;
        }
        this.data.debug = config.isDebug();
        var $content = $(QWeb.render('sale_order_line_image_wizard.DetailPopOver', {
            data: this.data,
        }));
        var $forecastButton = $content.find('.action_open_image');
        var product = this.data.product_template_id.res_id;
        $forecastButton.on('click', function(ev) {
            ev.stopPropagation();
            self._rpc({
                model: 'product.template',
                method: 'open_image_wizard',
                args: [[product]],
            }).then(function(result) {

                self.do_action(result);
            });
            return;

        });
        var options = {
            content: $content,
            html: true,
            placement: 'right',
            title: _t('Image'),
            trigger: 'focus',
            delay: {'show': 0, 'hide': 100 },
        };
        this.$el.popover(options);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    _onClickButton: function () {
        // We add the property special click on the widget link.
        // This hack allows us to trigger the popover (see _setPopOver) without
        // triggering the _onRowClicked that opens the order line form view.
        this.$el.find('.fa-file-o').prop('special_click', true);
    },
});

widget_registry.add('sale_product_template_image', SaleProductImage);

return QtyAtDateWidget;
});
