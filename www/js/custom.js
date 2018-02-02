
$(document).ready(function () {


$('#ajax_message').hide();


    function ajax_message_alert(response) {
        var box_class = 'success';
        var message = 'SUCCESS: JSON updated';
        if (response == 'error') {
            box_class = 'error';
            message = 'ERROR: Something went wrong...';
        }
        $('#ajax_message').addClass(box_class).find('.ajax_response').html(message);
        $('#ajax_message').fadeIn(200).delay(2000).fadeOut(200);
    }
    ;




    // -------------------------------------------------------
    // SETTINGS PAGE
    // -------------------------------------------------------

    $("button#update").click(function () {

        var form = $('form#settings')

        var disabled = form.find(':input:disabled').removeAttr('disabled'); // enable disabled field(s) so serializeJSON can find them

        var json = form.serializeJSON(); // using the serialize-object library

        disabled.attr('disabled', 'disabled'); // re-disable disabled field(s)

        $.ajax({
            type: 'GET',
            url: 'JSON_Handler.php',
            data: {json: json}
            //                        dataType: 'json' // << causes issues
        })
                .done(function (data) {
                    ajax_message_alert('success');
                    console.log('done');
                    console.log(data);
                })
                .fail(function (data) {
                    ajax_message_alert('error');
                    console.log('fail');
                    console.log(data);
                });
    });


    $("button#reboot").click(function () {

        $.ajax({
            type: 'GET',
            url: 'functions.php',
            data: {reboot: 'reboot'}
        })
                .done(function (data) {

                    console.log('done');
                    console.log(data);
                })
                .fail(function (data) {
                    alert('Something went wrong...')
                    console.log('fail');
                    console.log(data);
                });
    });



    // -------------------------------------------------------
    // COIN MANAGEMENT PAGE
    // -------------------------------------------------------


    



    function checkbox_click(cb_elem, event) {

        event.stopImmediatePropagation(); // @todo: fix multiple triggers

        var is_checked = cb_elem.is(':checked');
        var id = cb_elem.parents('form').attr('id');
        var form = $('form#' + id);
        cb_elem.next('.coin-hodl-hidden').attr('value', is_checked);
        var json = form.serializeJSON();
        $.ajax({
            type: 'GET',
            url: 'JSON_Handler.php',
            data: {json: json, json_file: id}
            //                        dataType: 'json' // << causes issues
        })
                .done(function (data) {
                    ajax_message_alert('success');
                    console.log('done');
                    console.log(data);
                })
                .fail(function (data) {
                    ajax_message_alert('error');
                    console.log('fail');
                    console.log(data);
                });

    }

    $(".coin-hodl").click(function (event) {

        checkbox_click($(this), event);

    });
    function remove_coin(button, event) {

        event.stopImmediatePropagation(); // @todo: fix multiple triggers

        var id = button.parents('form').attr('id');
        var form = $('form#' + id);
        var coin = button.attr('remove-coin');
        var row = button.parents('tr');
        row.remove();
        var json = form.serializeJSON(); // using the serialize-object library

        $.ajax({
            type: 'GET',
            url: 'JSON_Handler.php',
            data: {blackwish_remove: coin, blackwish_json: json, blackwish_form: id}
            //                        dataType: 'json' // << causes issues
        })
                .done(function (data) {
                    ajax_message_alert('success');
                    console.log('done');
                    console.log(data);
                })
                .fail(function (data) {
                    ajax_message_alert('error');
                    console.log('fail');
                    console.log(data);
                });
    }


    $("button.remove").click(function (event) {

        remove_coin($(this), event);
    });
    function make_row(coin_name, hodl, id) {

        var hodl_checked = '';
        var table_class = '';
        var hodl_element = '';
        if (hodl == true) {
            hodl_checked = ' checked';
        }

        if (id == 'wishlist_form') {
            table_class = 'table-success';
            hodl_element = '<td><input class="coin-hodl" type="checkbox"' + hodl_checked + ' />';
            hodl_element += '<input class="coin-hodl-hidden" type="hidden" name="' + coin_name + '[hodl]" value="' + hodl + '" /></td>';
        } else if (id == 'blacklist_form') {
            table_class = 'table-danger';
        }




        var str = '<tr class="' + table_class + ' coin-row" name="' + coin_name + '"><td>' + coin_name + '</td>'
                + '<input class="coin" type="hidden" name="' + coin_name + '[Symbol]" value="' + coin_name + '" />'
                + hodl_element
                + '<td><button type="button" class="btn btn-secondary remove" remove-coin="' + coin_name + '">Remove</button></td></tr>';
        return str;
    }



    $("button.add-coin").click(function () {


        var id = $(this).parents('form').attr('id');
        var form = $('form#' + id);
        $('form#' + id + ' .coin-name').val(function (i, val) {
            return val.toUpperCase();
        });
        var coin_name = $('form#' + id + ' .coin-name').val();
        if (coin_name != '') {

            var checked_status = form.find('.new-coin').find('input.coin-hodl').prop('checked'); //.is(':checked');
            var new_row = form.find('tr.new-coin').before(make_row(coin_name, checked_status, id));
            var json = form.serializeJSON(); // using the serialize-object library
            console.log(json);
            $.ajax({
                type: 'GET',
                url: 'JSON_Handler.php',
                data: {blackwish_add: coin_name, blackwish_json: json, blackwish_form: id}
                //                        dataType: 'json' // << causes issues
            })
                    .done(function (data) {
                        ajax_message_alert('success');

                        console.log('done');
                        console.log(data);
                        $("button.remove").on('click', new_row.find('button.remove'), function (event) {

                            remove_coin($(this), event);
                        });
                        $("input.coin-hodl").on('click', new_row.find('input.coin-hodl'), function (event) {

                            checkbox_click($(this), event);
                        });
                    })
                    .fail(function (data) {
                        ajax_message_alert('error');
                        console.log('fail');
                        console.log(data);
                    });
        }
        ;
    });



    // -------------------------------------------------------
    // OPEN ORDERS PAGE
    // -------------------------------------------------------

    $("button.cancel").click(function () {

        var orderid = $(this).attr('orderid');
        var row = $(this).parents('tr');

        row.css('opacity', 0.5);
        $(this).attr('disabled', 'disabled');


        $.ajax({
            type: 'GET',
            url: 'functions.php',
            data: {orderid: orderid}
        })
                .done(function (data) {
                    console.log('done');
                    row.fadeOut(500);
                })
                .fail(function (data) {
                    alert('Something went wrong...')
                    $(this).removeAttr('disabled');
                });

    });




});
