document.addEventListener('DOMContentLoaded', () => {
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    //once connected perform these
    socket.on('connect', () => {
        console.log("in Connect"); 
        socket.emit('request-all-rooms');
        var channel = localStorage.channel;
        if (channel ){
            console.log ("Channel Exists, Joining " + channel);
            socket.emit('join-channel', channel);
        }
    });
    socket.on('show-all-rooms', data => {
        $('#rooms').empty();
        for (i = 0; i < data.length; ++i) {
            toappend='<tr> <td> <div class="row">  <div class="col-lg">'+   data[i] +' </div> <div class="col-sm">  <button class="btn btn-outline-primary" id="btn-join-channel" data-channel="' + data[i] +  '">  Join   </button> </div> </div></td> </tr>';
            //console.log(toappend); 
            $('#rooms').append(toappend); 
        }
        code_join_button(); // time to put a little code to all the buttons just created
    });
    socket.on('message', data => {
        $('#messages').append('<tr> <td>'+data+ '</td> </tr>'); 
    });
    socket.on('join-accepted', data => {
        localStorage.setItem("channel", data)
        document.querySelector('#communicateBox').style.visibility= "visible";
        document.querySelector('#messagebox').innerHTML="";
        document.querySelector('#channelname').innerHTML="";
        $('#channelname').append('<tr> <td> <p class="text-center"><h2> <b> <i> '+data+ ' </i></b> </h2></p></td> </tr>'); 
        // TODO :: Diable all other JOIN buttons
        document.querySelectorAll('#btn-join-channel').forEach(button => {
            button.disabled = true;
        });
    });
    socket.on('broadcast-to-channels', data => {
        $('#messagebox').append('<tr> <td>'+data+ '</td> </tr>'); 
    });
    socket.on('receive-message', message => {
        console.log(message);
        toappend=' <div class="border border-primary">';
        toappend=toappend+ ' <div class="row justify-content-between"  style="font-family: sans-serif;"><div class="col-md-auto bg-dark text-white text-capitalize"> '+ message.username+ ' </div> <div class="col-md-auto"> <small> '+message.mtime+' </small> </div>  </div> ';
        toappend=toappend+ ' <div class="row"> '+message.msg+ '</div>  </div>';
        $('#messagebox').append(toappend);
    });

    // Non Socket code
    document.querySelector('#create-channel-button').disabled = true;
    document.querySelector('#textbox-channel').onkeyup = () => {
        if (document.querySelector('#textbox-channel').value.length > 0)
            document.querySelector('#create-channel-button').disabled = false;
        else
            document.querySelector('#create-channel-button').disabled = true;
    };
    document.querySelector('#create_channel_form').onsubmit = () => {
        let textboxChannel= document.querySelector('#textbox-channel');
        console.log(textboxChannel.value);
        console.log(textboxChannel.id);
        socket.emit('create-channel', textboxChannel.value);
        textboxChannel.value="";
        document.querySelector('#create-channel-button').disabled = true;
        return false;
    };
    
    document.querySelector('#leaveChannelbutton').onclick = () => {
        console.log("Leaving channel")
        let textboxChannel= localStorage.getItem("channel");
        socket.emit('leave-channel', textboxChannel);
        localStorage.removeItem("channel");
        // Leaving a channel, so enable all others to be joined
        document.querySelectorAll('#btn-join-channel').forEach(button => {
            button.disabled = false;
        });
        document.querySelector('#communicateBox').style.visibility= "hidden";
        return false;
    };

    function code_join_button()
    {
       document.querySelectorAll('#btn-join-channel').forEach(button => {
            button.onclick = () => {
                var channel = button.dataset.channel;
                socket.emit('join-channel', channel);
            };
        });

    }

    document.querySelector('#send-message-button').onclick = () => {
        console.log("In Send message"); 
        let messagetext= document.querySelector('#textbox-message');
        let channel= localStorage.getItem("channel");
        data = {'msg': messagetext.value,'channel': channel};
        console.log(data);
        socket.emit('send-message', data);
        messagetext.value="";
        return false;
    };
    
});
