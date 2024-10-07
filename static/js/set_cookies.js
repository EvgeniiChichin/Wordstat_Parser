$(document).ready(function() {
    function checkCookieStatus(taskId) {
      $.ajax({
        url: "{% url 'check_cookies_status' %}",
        data: { 'task_id': taskId },
        success: function(data) {
          if (data.status === 'completed') {
            window.location.href = "{% url 'home' %}";
          } else if (data.status === 'error') {
            $('#cookie-status').html('<p class="alert alert-danger">Ошибка: ' + data.message + '</p>').show();
          } else {
            setTimeout(function() {
              checkCookieStatus(taskId);
            }, 2000);
          }
        },
        error: function() {
          $('#cookie-status').html('<p class="alert alert-danger">Ошибка при проверке статуса.</p>').show();
        }
      });
    }
  
    var taskId = "{{ request.session.cookie_check_task_id|default_if_none:'' }}";
    if (taskId) { 
      checkCookieStatus(taskId);
    }
  });
  