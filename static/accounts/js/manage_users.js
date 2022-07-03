$( document ).ready(function() {

  $( ".friend-message" ).click(function() {

    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", friend_message_url);

    var csrfmiddlewaretoken = document.createElement("input");
    csrfmiddlewaretoken.setAttribute("type", "hidden")
    csrfmiddlewaretoken.setAttribute("name", "csrfmiddlewaretoken");
    csrfmiddlewaretoken.setAttribute("value", CSRF_TOKEN);
    form.appendChild(csrfmiddlewaretoken);

    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("type", "hidden");
    hiddenField.setAttribute("name", "pk");
    hiddenField.setAttribute("value", $(this).attr("data-pk"));

    form.appendChild(hiddenField);

    document.body.appendChild(form);
    form.submit();

  });

  $( ".friend-delete" ).click(function() {
    if(confirm("Are you sure you want to remove your friend?")){
      pk = $(this).attr("data-pk");
      $.ajax({
        url: friend_delete_url,
        type: 'POST',
        data: {
          csrfmiddlewaretoken: CSRF_TOKEN,
          pk: pk
        },
        success: function(json){
          $("#friend-" + pk).remove()
        }
      });
    }
    else{
      return false;
    }
  });

  $( ".from-you-delete" ).click(function() {
    pk = $(this).attr("data-pk");
    $.ajax({
      url: from_you_delete_url,
      type: 'POST',
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        pk: pk
      },
      success: function(json){
        $("#from-you-" + pk).remove()
      }
    });
  });

  $( ".to-you-confirm" ).click(function() {
    pk = $(this).attr("data-pk");
    $.ajax({
      url: to_you_confirm_url,
      type: 'POST',
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        pk: pk
      },
      success: function(json){
        $("#to-you-" + pk).remove()
      }
    });
  });

  $( ".to-you-delete" ).click(function() {
    pk = $(this).attr("data-pk");
    $.ajax({
      url: to_you_delete_url,
      type: 'POST',
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        pk: pk
      },
      success: function(json){
        $("#to-you-" + pk).remove()
      }
    });
  });

});