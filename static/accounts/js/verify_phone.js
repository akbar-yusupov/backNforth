$( document ).ready(function () {
  $("#code").on('keypress',function(e) {
    var $that = $(this),
    maxlength = $that.attr('maxlength')
    if($.isNumeric(maxlength)){
      if($that.val().length == maxlength) { e.preventDefault(); return; }
      $that.val($that.val().substr(0, maxlength));
    };
  });

});