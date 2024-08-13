$(document).ready(function(){
    $(document).on('click',"input[value='Cancel'], input[value='Restore']", function(){

        const type = $(this).val();

        let text = 'Are you sure you want to '+type.toLowerCase()+' this record?';

        if (confirm(text)){
            $.ajax({
                type: 'POST',
                url: window.location.href + '/' + type.toLowerCase(),
                data: {"BID": $(this).attr("name")},
                success: function(response) {
                    for(t in response.table){
                        $('.'+t).html(response.table[t]);
                    }
                    $('#error').text(response.error);
                },
                error: function(error) {
                    console.log("Error:", error);
                }
            });
        }
    });
    $(document).on('click',".pagination button", function(){
        $('#error').text('');
        $active = $(".active");
        $("."+$active.text().toLowerCase()).hide();
        $active.removeClass("active");
        $("."+$(this).text().toLowerCase()).show();
        $(this).addClass("active");
    });
});