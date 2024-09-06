$(document).ready(function(){

    $(document).on('click',"button.submit1", function(){
        let submit_data = {};
        const type = $(this).val();
        if (confirm("Are you sure you want to save the changes?")){
            submit_data["SEX"] = $("select[name='SEX']").val();
            submit_data["EMAIL"] = $("input[name='EMAIL']").val();
            submit_data["UNAME"] = $("input[name='UNAME']").val();
        }
        else{
            return;
        }
        $.ajax({
            type: 'POST',
            url: window.location.href + "/update1",
            data: submit_data,
            success: function(response) {
                if("table" in response){
                    $("select[name='SEX']").val(response.data[0]).change();
                    $("input[name='EMAIL']").val(response.data[1]).change();
                    $("input[name='UNAME']").val(response.data[2]).change();
                }
                $('#error.e1').text(response.error)
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    });
    $(document).on('click',"button.submit2", function(){
        let submit_data = {}
        const type = $(this).val();
        if (confirm("Are you sure you want to update your password?")){
            submit_data["OLD_PASSWORD"] = $("input[name='OLD_PASSWORD']").val();
            submit_data["PASSWORD1"] = $("input[name='PASSWORD1']").val();
            submit_data["PASSWORD2"] = $("input[name='PASSWORD2']").val();
        }
        else{
            return;
        }
        $.ajax({
            type: 'POST',
            url: window.location.href + "/update2",
            data: submit_data,
            success: function(response) {
                $("input[name='OLD_PASSWORD']").val('');
                $("input[name='PASSWORD1']").val('');
                $("input[name='PASSWORD2']").val('');
                $('#error.e2').text(response.error)
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    });
});