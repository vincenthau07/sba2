function alert_box(bold_text, text, color_type, dissappear=true){
    $('.alert-box').html(
        `<div class="alert alert-`+color_type+`">
            <strong>`+bold_text+`</strong> `+text+`
        </div>`
    );
    if(dissappear){
        $('.alert').each(function(){
            setTimeout(function() {
                $('.alert').animate({opacity: 0}, 500,
                    function(){
                        $(this).remove();
                    }
                );
            }, 3*1000); //3 seconds
        });
    };
}
function success_alert_box(text='Action succeeded.'){
    alert_box('Success!',text, 'success')
}
function error_alert_box(error){
    alert_box('Error!',error, 'danger')
}
function loading_alert_box(){
    alert_box('Info!','Waiting for response...<div class="spinner-border spinner-border-sm text-info"></div>', 'info', false)
}
function empty_alert_box(){
    $('.alert-box').html('');
}