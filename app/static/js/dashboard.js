function post_a_request() {
    return new Promise((resolve) => {
        $.ajax({
            type: 'POST',
            url: window.location.href.split('#')[0] + '/update',
            success: function(response) {
                resolve(response);
            },
            error: function() {
                console.log(error);
                resolve({});
            }
        });
    });
}

function update_bar(rp){
    $(".progress").each(function(){
        var $bar = $(this).find(".bar");
        var $val = $(this).find("span");
        var perc = parseFloat( rp[$(this).parent().attr("class").split(' ').pop("box")]);

        $({p: parseFloat($val.text())}).animate({p: perc}, {
            duration: 1000,
            easing: "swing",
            step: function(p) {
                $bar.css({
                    transform: "rotate("+ (45+(p*1.8)) +"deg)", // 100%=180° so: ° = % * 1.8
                    // 45 is to add the needed rotation to have the green borders at the bottom
                });
                $val.text(p.toFixed(1));
            }

        });
    });
}

function update_values(sel){
    
    for(key in data){
        $(".value."+key).html(data[key][sel]);
    }
}

var selection = 0;
$(document).ready(function() {

    update_values(selection);

    post_a_request().then(response => {
        update_bar(response);
    })

    setInterval(function() {
        post_a_request()
        .then(response => {
            update_bar(response);
        })
    }, 3000);

    $(document).on('click',".pagination button", function(){
        $active = $(".active");
        $("."+$active.text().toLowerCase()).hide();
        $active.removeClass("active");
        $("."+$(this).text().toLowerCase()).show();
        $(this).addClass("active");
        selection = $(this).parent().index();
        update_values(selection);
    });
});
