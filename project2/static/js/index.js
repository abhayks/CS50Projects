document.addEventListener('DOMContentLoaded', () => {
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    //once connected perform these
    socket.on('connect', () => {
        console.log("in Connect"); 
        socket.emit('request-all-rooms');
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
        $('#messagebox').append('<tr> <td>'+data+ '</td> </tr>'); 
    });
    socket.on('broadcast-to-channels', data => {
        console.log(data)
        console.log("Message ")
        console.log(data)
        $('#messagebox').append('<tr> <td>'+data+ '</td> </tr>'); 
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
    
    document.querySelector('#leaveChannelbutton').onsubmit = () => {
        console.log("Leaving channel")
        let textboxChannel= localStorage.gettItem("channel");
        socket.emit('leave-channel', textboxChannel);
        localStorage.setItem("channel", "");
        document.querySelector('#communicateBox').style.visibility= "hidden";
        $('#messagebox').clear();
        return false;
    };

    function code_join_button()
    {
       document.querySelectorAll('#btn-join-channel').forEach(button => {
            button.onclick = () => {
                var channel = button.dataset.channel;
                socket.emit('join-channel', channel)
            };
        });

    }
});
