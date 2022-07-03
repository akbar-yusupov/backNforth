$( document ).ready(function() {
  if (request_path.includes('recommendations')) {
    $('#recommendations').css("color", '#FFFFFF');
  } else if (request_path.includes('chat')) {
    $('#chat').css("color", '#FFFFFF');
  } else if (request_path.includes('manage-users')) {
    $('#manage-users').css("color", '#FFFFFF');
  } else if (request_path.includes('profile')) {
    $('#profile').css("color", '#FFFFFF');
  }
});