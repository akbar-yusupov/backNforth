$( document ).ready(function() {
  let chat_id = $( ".messages-wrapper" ).attr( "chat-id" )
  $( "li[class^='person']").css("color", "#606060");
  $( ".li-" + chat_id).css("color", "#0080FF");

  function scroll_down(){
    var scroll = $('#chat-body');
    scroll.animate({scrollTop: scroll.prop("scrollHeight")});
  }

  scroll_down()

  let input_message = $('#input-message')
  let send_message_form = $('#send-message-form')
  const PROFILE_ID = $('#profile-id').val()
  let loc = window.location
  let wsStart = 'ws://'

  if(loc.protocol === 'https') {
      wsStart = 'wss://'
  }
  let endpoint = wsStart + loc.host + loc.pathname

  var socket = new WebSocket(endpoint)

  socket.onopen = async function(event){
      console.log('open', event)
      send_message_form.on('submit', function (event){
          event.preventDefault()
          let message = input_message.val()
          let send_to = $('.messages-wrapper').attr('other-user-id')
          let thread_id = $('.messages-wrapper').attr('chat-id')

          let data = {
              'message': message,
              'sent_by': PROFILE_ID,
              'send_to': send_to,
              'thread_id': thread_id
          }
          data = JSON.stringify(data)
          socket.send(data)
          $(this)[0].reset()
      })
  }

  socket.onmessage = async function(event){
      console.log('message', event)
      let data = JSON.parse(event.data)

      let message = data['message']
      let sent_by_id = data['sent_by']
      let thread_id = data['thread_id']
      let image = data['image']
      let updated_at = data['updated_at']
      let thread_updated_at = data['thread_updated_at']
      let username = data['username']

      newMessage(message, sent_by_id, username, thread_id, image, updated_at, thread_updated_at)
  }

  socket.onerror = async function(e){
      console.log('error', e)
  }

  socket.onclose = async function(e){
      console.log('close', e)
  }


  function newMessage(message, sent_by_id, username, thread_id, image, updated_at, thread_updated_at) {

    if ($( ".messages-wrapper" ).attr( "chat-id" ) == thread_id) {
      if ($.trim(message) === "") {
        return false;
      }

      let message_element;
      if(sent_by_id == PROFILE_ID){
          message_element = `
            <div class="message my-message">

              <img class="img-circle medium-image" src=${image}>

              <div class="message-body">
                <div class="message-body-inner">
                  <div class="message-info">
                    <h4> You </h4>
                    <h5>
                      <i class="fa fa-clock-o"></i>
                      ${updated_at}
                    </h5>
                  </div>
                  <hr>
                  <div class="message-text">
                    ${message}
                  </div>
                </div>
              </div>
              <br>
            </div>
          `
      }
      else {
          message_element = `
               <div class="message info">

                 <img class="img-circle medium-image" src=${image}>

                 <div class="message-body">
                   <div class="message-info">
                     <h4> ${username} </h4>
                     <h5>
                       <i class="fa fa-clock-o"></i>
                       ${updated_at}
                     </h5>
                   </div>
                   <hr>
                   <div class="message-text">
                     ${message}
                   </div>
                 </div>
                 <br>
               </div>
            `
      }

      $( "#thread_messages_count" ).html(parseInt($( "#thread_messages_count").html())+1);
      $( ".updated-at-" + thread_id ).html(`(${thread_updated_at})`);
      message_body = $( ".chat-body" ).append(message_element);
      scroll_down()
    } else {
      alert("New message from " + username)
    }
  }


  $( ".contact-li" ).on( "click" , function (){
    let chat_id = $(this).attr( "chat-id" )

    $( "li[class^='person']").css("color", "#606060");
    $( ".li-" + chat_id).css("color", "#0080FF");

    $.ajax({
      url: change_thread_url,
      type: "POST",
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        new_thread: chat_id
      },
      success: function(json){
        result = ""
        $.each(json["messages"], function( index, value ) {
          if (value["profile"] == PROFILE_ID){
            message_element = `<div class="message my-message">

              <img class="img-circle medium-image" src=${json["profile_image"]}>

              <div class="message-body">
                <div class="message-body-inner">
                  <div class="message-info">
                    <h4> You </h4>
                    <h5>
                      <i class="fa fa-clock-o"></i>
                      ${value.timestamp}
                    </h5>
                  </div>
                  <hr>
                  <div class="message-text">
                    ${value.message}
                  </div>
                </div>
              </div>
              <br>
            </div>
            `
          }
          else {
            message_element = `
              <div class="message info">

                <img class="img-circle medium-image" src=${json["friend_image"]}>

                <div class="message-body">
                  <div class="message-info">
                    <h4> ${json['friend_username']} </h4>
                    <h5>
                      <i class="fa fa-clock-o"></i>
                      ${value.timestamp}
                    </h5>
                  </div>
                  <hr>
                  <div class="message-text">
                    ${value.message}
                  </div>
                </div>
                <br>
             </div>
            `
          }
          result += message_element
        });
        $( ".chat-body" ).empty();
        $( ".chat-body" ).append(result);
        $( "#thread_created_at" ).html(json["created_at"]);
        $( "#thread_messages_count" ).html(json["messages"].length);
        $( ".messages-wrapper" ).attr("chat-id", chat_id);
        scroll_down()
      }
    });

  })

});