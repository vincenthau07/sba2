var flag = 0;
$("#deleteModal").ready(function () {
    var code = '<div class="container">';
    for(let i=0; i<fields.length; i++){
        
        code += '<div class="mb-3"><label for="'+fields[i]+'">'+col[i]+'</label>'

        if(fields[i] in input_format == false){
            code += "<input class='form-control' type=\"text\" name=\""+ fields[i]+"\"></div>"
        }
        else{
            switch(input_format[fields[i]][0]){
                case "select":
                    code += "<select class='form-select' name=\""+fields[i]+"\">";
                    for(j=0; j < input_format[fields[i]][1].length; j++){
                        code += "<option value=\""+input_format[fields[i]][1][j]+'\">'+input_format[fields[i]][1][j]+"</option>";
                    }
                    code += "</select></div>";
                    break;
                case "number":
                    code += "<input class='form-control' type=\"number\"></div>";
                    break;
                case "checkbox":
                    code += "<div class='form-control'><input class='form-check-input' type=\"checkbox\"></div></div>";
                    break;
                case "datetime":
                    code += "<input class='form-control' type=\"datetime-local\"></div>";
                    break;
            }
        }

    }
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
            type: 'POST',
            url: window.location.href,
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
                console.log($elements.eq(i).attr("type"))
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
        if (type=='update')
            type+='/'+tableinfo.rows( { selected: true } ).data()[0][pk_index]
        $.ajax({
            type: 'POST',
            data: submit_data,
            url: window.location.href+'/'+type,
            success: function(response) {
                tableinfo.ajax.reload(null, false);
                //console.log(response)
                
                if ('error' in response){
                    $('.alert-box').append(`
                        <div class="alert alert-danger alert-dismissible">
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            <strong>Error!</strong>`+response.error+`
                        </div>
                    `);
                }
                else{
                    $('.alert-box').append(
                        `<div class="alert alert-success alert-dismissible">
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            <strong>Success!</strong> Action succeeded.
                        </div>`
                    );
                }
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    });
});