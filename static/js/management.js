$(document).ready(function(){
    console.log(input_format);
    $(document).on('click',"input[value='Edit'], input[name='add']", function(){
        if ($(this).attr("name") == 'add'){
            let code = "<tr class = 'insert'>";
            for(let i=0; i<field.length; i++){
                code+="<td></td>";
            }
            code+="<td><input type='submit' value = 'Add'></td><td><input type='submit' value = 'Cancel'></td></tr>";
            $("tbody").append(code);
            $(this).hide();
            var $parrent = $(".insert");
        }
        else{
            var $parrent = $(this).parent().parent();
        }

        for(let i=0; i<field.length; i++){
            let text = $parrent.children().eq(i).text();
            
            if(field[i] in input_format == false){
                $parrent.children().eq(i).html("<input type=\"text\" name=\""+ field[i]+"\" value = \""+ text +"\">");
            }
            else{
                switch(input_format[field[i]][0]){
                    case "select":
                        let code = "<select name=\""+field[i]+"\">";
                        for(j=0; j < input_format[field[i]][1].length; j++){

                            if(text==input_format[field[i]][1][j]){
                                code += "<option value=\""+input_format[field[i]][1][j]+'\" selected>'+input_format[field[i]][1][j]+"</option>";
                            }
                            else{
                                code += "<option value=\""+input_format[field[i]][1][j]+'\">'+input_format[field[i]][1][j]+"</option>";
                            }
                        }
                        code += "</select>";
                        $parrent.children().eq(i).html(code);
                        break;
                    case "number":
                        $parrent.children().eq(i).html("<input type=\"number\" value=\""+text+"\"1>");
                        break;
                    case "checkbox":
                        if (text == "0")
                            $parrent.children().eq(i).html("<input type=\"checkbox\">");
                        else
                            $parrent.children().eq(i).html("<input type=\"checkbox\" checked>");
                        
                        break;
                    case "datetime":
                        $parrent.children().eq(i).html("<input type=\"datetime-local\" value=\""+text+"\"1>");
                        break;
                }
            }
        }
        $parrent.children().eq(field.length).children().attr({"value": "Save"});
        $parrent.children().eq(field.length+1).children().attr({"value": "Cancel"});
        $('input[value="Edit"]').hide();
        $('input[value="Delete"]').hide();
        $('input[name="add"]').hide();
    });

    $(document).on('click',"input[value='Add'], input[value='Save'],input[value='Delete'],input[value='Cancel']", function(){
        
        const type = $(this).val();
        
        const path = {"Save": "/update", "Delete": "/delete", "Add": "/insert", "Cancel": "/reload"}
        let text = '';
        switch(type){
            case 'Save':
                text = "Are you sure you want to save the changes?";
                break;
            case 'Add':
                text = "Are you sure you want to add this record?";
                break;
            case 'Delete':
                text = "Are you sure you want to delete this record?";
                break;
        }
        let submit_data = {};
        if (type != 'Cancel'){
            if (confirm(text)){
                if ((type == 'Save') || (type == 'Add')){
                    let data = [];
                    $parrent = $(this).parent().parent();
                    for(let i=0; i<field.length; i++){
                        if ($parrent.children().eq(i).children().attr("type")=="checkbox"){
                            data.push(+$parrent.children().eq(i).children().is(':checked'));
                        }
                        else{
                            data.push($parrent.children().eq(i).children().val());
                        }
                    }
                    submit_data.data = data;
                }
                if ((type == 'Save') || (type == 'Delete')){
                    submit_data.id = $(this).attr("name");
                }
            }
            else{
                return;
            }
        }
        console.log(submit_data)
        $.ajax({
            type: 'POST',
            url: window.location.href + path[type],
            data: submit_data,
            success: function(response) {
                if("table" in response){
                    $('.table').html(response.table);
                }
                $('#error').text(response.error)
            },
            error: function(error) {
                console.log("Error:", error);
            }
        });
    });
});