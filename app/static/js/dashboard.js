console.log(data)
function post_a_request() {
    return new Promise((resolve) => {
        $.ajax({
            type: 'GET',
            url: window.location.href.split('#')[0] + '/update',
            success: function (response) {
                resolve(response);
            },
            error: function () {
                error_alert_box(error.responseText);
                resolve({});
            }
        });
    });
}

// Progress bar animation
function update_bar(rp) {
    $(".progress").each(function () {
        var $bar = $(this).find(".progress-bar");
        var $val = $(this).find("small span");
        var perc = parseFloat(rp[$(this).attr("class").split(' ')[0]]);

        $({ p: parseFloat($val.text()) }).animate({ p: perc }, {
            duration: 1000,
            easing: "swing",
            step: function (p) {
                $bar.css({
                    transform: "scaleX("+p/100+")", 
                });
                $val.text(p.toFixed(1));
            }
        });
    });
}

const options = {
    responsive: true,
    interaction: {
        intersect: false,
        axis: 'x'
    },
    plugins: {
        legend: {
            position: 'top',
        },
    }
}
const options_bar = {
    responsive: true,
    interaction: {
        intersect: false,
    },
    plugins: {
        legend: {
            position: 'top',
        },
    }
}
// Chart configs
const config = {
    "login_times": {
        type: 'line',
        data: {
            labels: data['login'][1],
            datasets: [
                {
                    label: 'login times',
                    data: data.login[0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132, 0.5)',
                }
            ]
        },
        options: options
    },
    "month_r_f": {
        type: 'line',
        data: {
            labels: data.month_r_f[2],
            datasets: [
                {
                    label: 'room',
                    data: data.month_r_f[0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132, 0.5)',
                },
                {
                    label: 'facility',
                    data: data.month_r_f[1],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgb(54, 162, 235, 0.5)',
                }
            ]
        },
        options: options
    },
    "hour_r_f_am": {
        type: 'bar',
        data: {
            labels: ['00-01', '01-02', '02-03', '03-04', '04-05', '05-06', '06-07', '07-08', '08-09', '09-10', '10-11', '11-12'],
            datasets: [
                {
                    label: 'room',
                    data: data.hour_r_f_am[0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132, 0.5)',
                },
                {
                    label: 'facility',
                    data: data.hour_r_f_am[1],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgb(54, 162, 235, 0.5)',
                }
            ]
        },
        options: options_bar
    },
    "hour_r_f_pm": {
        type: 'bar',
        data: {
            labels: ['12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24'],
            datasets: [
                {
                    label: 'room',
                    data: data.hour_r_f_pm[0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132, 0.5)',
                },
                {
                    label: 'facility',
                    data: data.hour_r_f_pm[1],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgb(54, 162, 235, 0.5)',
                }
            ]
        },
        options: options_bar
    },
    "weekday_r_f": {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', "Sun"],
            datasets: [
                {
                    label: 'room',
                    data: data.weekday_r_f[0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132, 0.5)',
                },
                {
                    label: 'facility',
                    data: data.weekday_r_f[1],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgb(54, 162, 235, 0.5)',
                }
            ]
        },
        options: options_bar
    },
    "10_r": {
        type: 'bar',
        data: {
            labels: data['10_r'][1],
            datasets: [
                {
                    label: 'room',
                    data: data['10_r'][0],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132, 0.5)',
                }
            ]
        },
        options: options_bar
    },
    "10_f": {
        type: 'bar',
        data: {
            labels: data['10_f'][1],
            datasets: [
                {
                    label: 'facility',
                    data: data['10_f'][0],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgb(54, 162, 235, 0.5)',
                }
            ]
        },
        options: options_bar
    }
}
var selection = 0;
$(document).ready(function () {

    post_a_request().then(response => {
        update_bar(response);
    })

    setInterval(function () {
        post_a_request()
            .then(response => {
                update_bar(response);
            })
    }, 3000);

    for (key in config) {
        new Chart(document.getElementById(key), config[key]);
    }
});
