let na;

function get_all_users(){
    $('#user').empty();
    $.getJSON("/current",function(data){
        template = '<span> Logged as @name fullname</span>'
        template = template.replace('name',data[0]['username']);
        template = template.replace('fullname',data[0]['name']);
        $('#user').append(template);
        na = data[0]['id'];
    });
    $("#contact").empty();
    $.getJSON("/users", function(data){
        var i = 0;
        $.each(data, function(){
            if (data[i]['id']!==na){
                template = '<div class="alert alert-success" role="alert" onclick="get_chat(user_to_id)"><span>username</span><span> </span><span>name</span></div>';
            template = template.replace('username', data[i]['username']);
            template = template.replace('name', data[i]['name']);
            template = template.replace('saludo', data[i]['name']);
            template = template.replace('saludo', data[i]['name']);
            template = template.replace('user_to_id', data[i]['id']);
            $("#contact").append(template);
            }
            else{
                template = '<div class="alert alert-success" role="alert" onclick="get_chat(na)"><span> Chat with myself</span></div>';
                template = template.replace('na',na);
                $("#contact").append(template);
            }
            i = i+1;
        });
    });

}
function saludar(name){

    alert("Hello " + name);
}

function get_chat(user_to_id){
    //document.getElementById('wsp').style.visibility="visible";

    let i =0;
    $("#messages").empty();

    $.getJSON("/get_chat/"+user_to_id,function (data) {
        $.each(data,function () {
            if(data[i]['user_from_id']!==na){template = '<div> <p style="text-align: right;"> content </p></div>';
            template = template.replace('content',data[i]['content']);
            $("#messages").append(template);
            }
            else{
                template = '<div> <p style="text-align: left;"> content </p></div>';
            template = template.replace('content',data[i]['content']);
            $("#messages").append(template);
            }
            i=i+1;
        });
    });
    $("#wsp").empty();
    let tobe;
    tobe = "http://localhost:8080/messages/" + user_to_id;
        $("#wsp").append('<form class="" action='+ tobe + ' method="post"> ' +
            '<table><td><div><input style="width: 500px;height: 50px;" type="text" name="content"> </div>' +
            '</td><td><div> <input style="width: 100px;height: 50px" type="submit" value="Send" name="submit" ></div></td></table>' +
            '</form>');
}

