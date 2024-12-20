function getSchedule(data, callback) {
    $.ajax({
        type: 'POST',
        url: window.location.href.split('#')[0]+'/update',
        data: data,
        success: function(response) {
            if ('error' in response)
                error_alert_box(response.error)
            else{
                updateSchedule(response.data, response.col)
                empty_alert_box()
                callback(response);
            }
        },
        error: function(error) {
            error_alert_box(error.responseText);
        }
    });
}


$(document).ready(function(){

    //booking request form
    for(i = 0; i < categories.length; i++){
        $("select[name='CATEGORY']").append("<option value=\"" + categories[i] + "\">"+categories[i] + "</option>");
    };
    for(i = 0; i < units.length; i++){
        $("select[name='UNIT']").append("<option value=" + units[i][0] + ">"+units[i][1] + "</option>");
    };
    $(document).on('change',"select[name='CATEGORY']", function(){
        $("select[name='UNIT']").empty();
        for(i = 0; i < units.length; i++){
            if (units[i][2]==$(this).val()){
                $("select[name='UNIT']").append("<option value=" + units[i][0] + ">"+units[i][1] + "</option>");
            }
        }
    });
    $(document).on('click',"button.book-btn", function(){
        $('#bookModal').modal('show');
    })
    $(document).on('change',"input[name='STIME']", function(){
        $("input[name='ETIME']").val($(this).val()); 
    });
    //change data of schedule
    $(document).on('change',"input[name='week']", function(){
        var weeknum = $(this).val();
        loading_alert_box();
        console.log(weeknum)
        getSchedule({week: weeknum}, function(response){})
        
    })
    $(document).on('click',"input[name='previous']", function(){
        var weeknum = $("input[name='week']").val();
        loading_alert_box();
        getSchedule({week: weeknum, previous: true}, function(response){
            $("input[name='week']").val(response.week);
        })
    })
    $(document).on('click',"input[name='next']", function(){
        var weeknum = $("input[name='week']").val();
        loading_alert_box();
        getSchedule({week: weeknum, next: true}, function(response){
            $("input[name='week']").val(response.week);
        })
    })


    //schedule stuff
    $(document).on('click', '.event-box:not(.toggle)', function(){
        $(this).find(".mask, .description, .close-button").css("display","block");
        $(this).find(".event").css("height","");
        $(this).find(".event").addClass('toggle');
        $(this).addClass('toggle');
    });

    $(document).on('click', '.close-button', function(){
        $(this).css({"display": "none"});
        $(this).parent().find(".mask, .description").css("display","none");
        $(this).parent().find(".event").removeClass('toggle');
        $(this).parent().find(".event").css("height",$(this).parent().height());
        $(this).parent().removeClass('toggle');
    });

    //submit form
    $(document).on('click', "button.book", function(){
        var stime = $("input[name='STIME']").val();
        var etime = $("input[name='ETIME']").val();
        var unit = $("select[name='UNIT']").val();
        var description = $("textarea[name='DESCRIPTION']").val();
        loading_alert_box();
        $.ajax({
            type: 'POST',
            url: window.location.href,
            data: {
                "stime": stime, 
                "etime": etime, 
                "unit": unit,
                "description": description,
            },
            success: function(response) {
                if ('error' in response)
                    error_alert_box(response.error); 
                else{
                    var weeknum = $("input[name='week']").val();
                    getSchedule({week: weeknum}, function(response){
                        success_alert_box();
                        $("input[name='week']").val(response.week);
                    })
                }
                
            },
            error: function(error) {
                error_alert_box(error.responseText);
            }
        });
    })
});