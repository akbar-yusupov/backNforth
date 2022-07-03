$( document ).ready(function() {
  $('#id_phone_number_0 option[value=""]').remove();
  $('#id_phone_number_0').val("+998").change();
});