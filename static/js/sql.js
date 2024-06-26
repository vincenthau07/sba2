$(document).ready(function(){
    $(document).on('click',"input[name='submit']", function(){
        var sql = $("textarea[name='sql']").val();
        $.ajax({
            type: 'POST',
            url: "",
            data: {"sql": sql},
            success: function(response) {
                $('.code').html(response.code);
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    })
})