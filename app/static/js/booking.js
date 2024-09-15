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
    $(document).on('change',"input[name='STIME']", function(){
        $("input[name='ETIME']").val($(this).val()); 
    });
    //change data of schedule
    $(document).on('change',"input[name='week']", function(){
        var weeknum = $(this).val();
        $.ajax({
            type: 'POST',
            url: window.location.href.split('#')[0]+'/update',
            data: {week: weeknum},
            success: function(response) {
                $('.field-bar').html(response.field);
                for(i=0;i<7;i++){
                    $('.event'+i).html(response.events[i]);
                }
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    })
    $(document).on('click',"input[name='previous']", function(){
        var weeknum = $("input[name='week']").val();
        $.ajax({
            type: 'POST',
            url: window.location.href.split('#')[0]+'/update',
            data: {week: weeknum, previous: true},
            success: function(response) {
                $('.field-bar').html(response.field);
                for(i=0;i<7;i++){
                    $('.event'+i).html(response.events[i]);
                }
                $("input[name='week']").val(response.week);
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    })
    $(document).on('click',"input[name='next']", function(){
        var weeknum = $("input[name='week']").val();
        $.ajax({
            type: 'POST',
            url: window.location.href.split('#')[0]+'/update',
            data: {week: weeknum, next: true},
            success: function(response) {
                $('.field-bar').html(response.field);
                for(i=0;i<7;i++){
                    $('.event'+i).html(response.events[i]);
                }
                $("input[name='week']").val(response.week);
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
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
    $(document).on('click', "input[name='submit']", function(){
        var stime = $("input[name='STIME']").val();
        var etime = $("input[name='ETIME']").val();
        var unit = $("select[name='UNIT']").val();
        var description = $("input[name='DESCRIPTION']").val();
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
                $('#error').text(response.message);
                var weeknum = $("input[name='week']").val();
                $.ajax({
                    type: 'POST',
                    url: window.location.href.split('#')[0]+'/update',
                    data: {week: weeknum},
                    success: function(response) {
                        $('.field-bar').html(response.field);
                        for(i=0;i<7;i++){
                            $('.event'+i).html(response.events[i]);
                        }
                        $("input[name='week']").val(response.week);
                    },
                    error: function(error) {
                        console.log("Error:", error);
                    }
                });
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });

        
        window.location.replace("#error");
    })
});