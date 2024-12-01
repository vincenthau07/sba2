var flag = 0;
$(document).ready(function () {
    var code = '<div class="container">';
    for(let i=0; i<fields.length; i++){
        
        code += '<div class="form-floating mb-3">'

        if(fields[i] in input_format == false){
            code += "<input class='form-control' placeholder='any' type=\"text\" name=\""+ fields[i]+"\">"
            
        }
        else{
            switch(input_format[fields[i]][0]){
                case "select":
                    code += "<select class='form-select' name=\""+fields[i]+"\">";
                    for(j=0; j < input_format[fields[i]][1].length; j++){
                        code += "<option value=\""+input_format[fields[i]][1][j]+'\">'+input_format[fields[i]][1][j]+"</option>";
                    }
                    code += "</select>";
                    break;
                case "number":
                    code += "<input class='form-control' placeholder='any' type=\"number\">";
                    break;
                case "checkbox":
                    code += "<div class='form-control'><input class='form-check-input' type=\"checkbox\"></div>";
                    break;
                case "datetime":
                    code += "<input class='datetime form-control' type=\"datetime-local\">";
                    break;
            }
        }
        code += '<label>'+col[i]+'</label></div>'
    }
    $('.datetime').each(function(){
        $(this).datetimepicker();
    })
    $('.editcontent, .addcontent').html(code);

    for (let i = 0; i < col.length; i++) {
        col[i] = { title: col[i] };
    };
    var tableinfo = $('#tableinfo').DataTable({
        layout: {
            top2End: {
                buttons: [
                    {
                        text: 'New',
                        className: 'addbtn btn btn-outline-dark',
                        action: function (){
                            $('#addModal').modal('show');
                        }
                    },
                    {
                        text: 'Edit',
                        className: 'editbtn btn btn-outline-primary disabled',
                        action: function (){
                            
                            var rcd = tableinfo.rows( { selected: true } ).data()[0]
                            //console.log(rcd)

                            $ec = $('.editcontent').children()
                            for(let i=0; i<fields.length; i++){
                                if(rcd[i] === null){
                                    rcd[i] = "None"
                                }
                                if(fields[i] in input_format && input_format[fields[i]][0] == "checkbox"){
                                    $ec.children().eq(i).find("input").attr("checked",(rcd[i]!=0));
                                }
                                else{
                                    $ec.children().eq(i).find("input, select").val(rcd[i])
                                }
                            }
                            $('#editModal').modal('show');
                        }
                    },
                    {
                        text: 'Delete',
                        className: 'deletebtn btn btn-outline-danger disabled',
                        action: function () {

                            $('#deleteModal').modal('show');
                            // console.log(tableinfo.rows( { selected: true } ).data());
                        }
                    }
                ]
            },
            topStart: 'pageLength',
            topEnd: 'search',
            bottomStart: 'info',
            bottom2End: 'paging',
            bottomEnd: {
                buttons: [
                    {
                        extend: 'copy',
                        className: 'btn btn-outline-secondary'
                    },
                    {
                        extend: 'excel',
                        className: 'btn btn-outline-success'
                    }
                ]
            }
        },
        ajax: {
            type: 'GET',
            url: window.location.href.split('#')[0]+'/update',
            dataSrc: 'data',
        },
        columns: col,
        scrollX: true,
        select: true,
        initComplete: function () {
            var btns = $('.dt-button');
            btns.removeClass('dt-button');
        }
    })
    $('#tableinfo').on( 'click', 'tbody tr', function (){
        if ($(this).hasClass('selected')){
            $('.editbtn,.deletebtn').addClass('disabled');
            flag = 0;
        }
        else if (flag==0){
            $('.editbtn,.deletebtn').removeClass('disabled');
            flag = 1;
        }
    })
    $(document).on('click', 'button.delete, button.add, button.edit', function (){
        var type = '';
        $('.editbtn,.deletebtn').addClass('disabled');
        flag = 0;
        if ($(this).hasClass('delete'))
            type = 'delete';
        else if($(this).hasClass('add'))
            type = 'insert';
        else if($(this).hasClass('edit'))
            type = 'update';
        var submit_data = {}
        if (type!='delete'){
            var data = [];
            if (type=='insert')
                $elements = $('.addcontent').find('input,select');
            else
                $elements = $('.editcontent').find('input,select');
            for (let i = 0; i < fields.length; i++){
                if ($elements.eq(i).attr("type")=="checkbox"){
                    data.push(0+$elements.eq(i).is(':checked'));
                }
                else if($elements.eq(i).attr("type")=="datetime-local"){
                    data.push($elements.eq(i).val().split('T').join(' ')+':00');
                }
                else{
                    data.push($elements.eq(i).val());
                }
            }
            submit_data['data'] = data;
        };
        if (type == 'update' || type == 'delete')
            submit_data['id'] = tableinfo.rows( { selected: true } ).data()[0][pk_index]
        submit_data['type'] = type;
        loading_alert_box()
        $.ajax({
            type: 'POST',
            url: window.location.href.split('#')[0],
            data: submit_data,
            success: function(response) {
                tableinfo.ajax.reload(null, false);
                
                if ('error' in response){
                    error_alert_box(response.error);
                }
                else{
                    success_alert_box();
                }
            },
            error: function(error) {
                error_alert_box(error.responseText);
            }
        });
    });
});