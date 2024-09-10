function filterable() {
    $('table.filterable').each(function(){
        $(this).removeClass('filterable').addClass('filterable_enabled');
        var columnCount = $(this).find('th').length;
        $(this).find('thead').append('<tr><th><input class="filter" type="text" placeholder="Search.."></th></th>')
        $(this).find("input.filter").parent().attr('colspan',columnCount);
    });
}
/* source code: https://www.w3schools.com/JQuery/jquery_filters.asp */
$(document).ready(function(){
    filterable();
    $("input.filter").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $(this).parent().parent().parent().parent().find('tbody').find('tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});