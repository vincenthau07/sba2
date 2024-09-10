$(document).ready(function(){
    $(document).on('click',"input[value='Approve'], input[value='Deny']", function(){

        const type = $(this).val();
        
        const path = {"Approve": "/approve", "Deny": "/deny"}
        let text = '';

        let submit_data = {"id": $(this).attr("name")};
        $.ajax({
            type: 'POST',
            url: window.location.href + "/" + type.toLowerCase(),
            data: submit_data,
            success: function(response) {
                if("table" in response){
                    $('.table').html(response.table);
                }
                $('#error').text(response.error)
                filterable();
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    });
});