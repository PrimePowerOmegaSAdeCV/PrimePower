odoo.define('bi_website_rma.return_order_js', function(require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var _t = core._t;
    var rma_name = false
    
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
        })

    });

});