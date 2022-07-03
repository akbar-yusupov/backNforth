$( document ).ready(function () {

  $('.send-request').on('click', function (){
    pk = $(this).attr("data-pk");
    $.ajax({
      url: send_request_url,
      type: 'POST',
      data: {
        csrfmiddlewaretoken: CSRF_TOKEN,
        pk: pk
      },
      success: function(json){
        $("#tr-" + pk).remove()
      }
    });
  })

});