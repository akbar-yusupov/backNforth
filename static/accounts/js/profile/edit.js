$( document ).ready(function() {

  $( "#contact_button" ).click(function() {

    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", support_chat_url);

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

});