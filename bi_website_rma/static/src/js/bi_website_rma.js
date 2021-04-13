odoo.define('bi_website_rma.return_order_js', function(require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var _t = core._t;
    var rma_name = false
    require("web.dom_ready");

    $(document).ready(function(){
        $("#submit_rma").click(function(ev){
            
            var sale_order = false
            var delivery_order = false
            var ord_line = []
            var ret_qty = []
            var rma_reason = []
            var rma_motivo = []
            var ret_dict = []
            var wrong_qty = false
            var $form = $(ev.currentTarget).parents('form');
            var wrong_motivo= false
            var wrong_reason = false
            var selected_line=false

            $('#mytable input[type="checkbox"]:checked').each(function(){
                selected_line=true
                var is_rma_motivo =  parseInt($(this).closest('div').find('select[name="rma_motivo"]').val(),10)
                var del_qty = parseInt($(this).closest('tr').find('#delivered_qty input').val(), 10)
                var back_qty = parseInt($(this).closest('tr').find('#return_quantity').val(),10)
                var is_rma_reason =  parseInt($(this).closest('tr').find('select[name="rma_reason_id"]').val(),10)

                    if(!back_qty){
                    wrong_qty = true
                }else if(back_qty > del_qty){
                    wrong_qty = true

                }else if(is_rma_motivo == 99){
                    wrong_motivo = true
                }else if(is_rma_reason == 99){
                    wrong_reason = true

                }

                sale_order = $(this).closest('tr').attr('so')
                delivery_order = $(this).closest('tr').attr('do')
                ret_dict.push({
                    'ord_line' : $(this).closest('tr').attr('line_id'),
                    'ret_qty': $(this).closest('tr').find('#return_quantity').val(),
                    'rma_reason' : $(this).closest('tr').find('select[name="rma_reason_id"]').val(),
                })
                ord_line.push($(this).closest('tr').attr('line_id'))
                ret_qty.push($(this).closest('tr').find('#return_quantity').val())
                rma_reason.push($(this).closest('tr').find('select[name="rma_reason_id"]').val())
                rma_motivo.push($(this).closest('div').find('select[name="rma_motivo"]').val())
            })
            if(wrong_qty){
                alert("Return quantity should be less or equal to delivered quantity.")
                return false
            }else if(wrong_motivo){
                    alert("Please choose a valid motive for the order.")
                    return false
            }else if(wrong_reason){
                    alert("Please choose a valid return reason for the order.")
                    return false
            }else if(!selected_line){
                alert("Please select at least one line.")
                    return false
            }


            ajax.jsonRpc("/thankyou","call",{
                'sale_order' : sale_order,
                'delivery_order' : delivery_order,
                'ord_line': ord_line,
                'ret_qty' : ret_qty,
                'rma_reason' : rma_reason,
                'rma_motivo' : rma_motivo,
                'ret_dict' : ret_dict,
            }).then(function(order){
                rma_name = order
                $form.submit();
            });
        });

        $("#submit_sale_rma").click(function(ev){
            var button = $(this);
            var sale_order = false;
            var has_qty_error = false;
            var rma_motivo = $('select#rma_motivo');
            var $motive_error = $('div#motive_error');
            var $qty_error = $('div#qty_error');
            var rma_value = rma_motivo.val();
            var $form = $(ev.currentTarget).parents('form');
            if (rma_value === ''){
                rma_motivo.addClass('has-error');
                rma_motivo.focus();
                if ($motive_error.hasClass('o_hidden')){
                    $motive_error.removeClass('o_hidden');

                }
                return;
            }else if (rma_motivo.hasClass('has-error')){
                rma_motivo.removeClass('has-error');
                if ($motive_error.hasClass('o_hidden') === false){
                    $motive_error.addClass('o_hidden');
                }
            }
            var $form = $(ev.currentTarget).parents('form');
            var list_line = [];

            $('#request-rma-table tr[line_id]').each(function(){
                var qty = parseInt($(this).find('#return_quantity').val(), 10);
                var max_qty = parseInt($(this).attr('max_qty'), 10);
                if (qty > max_qty){
                    if (has_qty_error === false){
                        has_qty_error = true;
                    }
                }
                sale_order = $(this).attr('so');
                list_line.push({
                    'move_id' : $(this).attr('line_id'),
                    'product_id' : $(this).attr('product'),
                    'picking_id' : $(this).attr('picking'),
                    'quantity': $(this).find('#return_quantity').val(),
                    'rma_reason_id' : $(this).find('select[name="rma_reason_id"]').val(),
                })
            });

            if (has_qty_error){
               if($qty_error.hasClass('o_hidden')){
                    $qty_error.removeClass('o_hidden');
                    return;
               }
            }else{
                if($qty_error.hasClass('o_hidden') === false){
                    $qty_error.addClass('o_hidden');
                    }
               }

            button.attr("disabled", true);
            ajax.jsonRpc("/my/orders/requestrma","call",{
                'sale_order' : sale_order,
                'motive' : rma_value,
                'access_token': false,
                'values' : list_line,
            }).then(function(order){
                console.log(order);
                button.attr("disabled", false);
                if (order === true){
                    $form.submit();
                }
            });
        });
    });

    $("#rma_request_form input[name='product_id']").select2({
        width: "100%",
        placeholder: "Select a product",
        allowClear: true,
        selection_data: false,
        ajax: {
            url: "/website_rma/get_products",
            dataType: "json",
            data: function(term) {
                return {
                    q: term,
                    l: 50,
                };
            },
            results: function(data) {
                var res = [];
                _.each(data, function(x) {
                    res.push({
                        id: x.id,
                        text: x.display_name,
                        uom_id: x.uom_id[0],
                        uom_name: x.uom_id[1],
                    });
                });
                return {results: res};
            },
        },
    });
    // Set UoM on selected onchange
    $("#rma_request_form input[name='product_id']").change(function() {
        var select2_data = $(this).select2("data");
        var uom_id = select2_data ? select2_data.uom_id : "";
        var uom_name = select2_data ? select2_data.uom_name : "";
        $("input[name='product_uom']").val(uom_id);
        $("input[name='product_uom_name']").val(uom_name);
    });

});