$(document).ready(function() {
  $('#uploadForm').on('submit', function(e) {
      e.preventDefault();
      var formData = new FormData(this);
      $.ajax({
          url: uploadUrl,  
          type: 'POST',
          data: formData,
          processData: false,
          contentType: false,
          success: function(data) {
              showStatus('Обработка начата...', 'info');
              checkTaskStatus(data.task_id);
          },
          error: function() {
              showStatus('Ошибка при отправке формы', 'error');
          }
      });
  });

  function checkTaskStatus(taskId, attempt = 1) {
    $.ajax({
        url: checkTaskStatusUrl,
        data: { 'task_id': taskId },
        success: function(data) {
            if (data.status === 'completed') {
                showStatus('Обработка завершена!', 'success');
                $('#downloadButton')
                  .attr('href', data.file_url)
                  .attr('download', '')
                  .show();
            } else if (data.status === 'error') {
                showStatus('Ошибка: ' + data.message, 'error');
            } else {
                showStatus('Обработка начата, подождите завершение.', 'info');
                setTimeout(function() {
                    checkTaskStatus(taskId);
                }, 2000);
            }
        },
        error: function() {
            if (attempt < 3) {
                setTimeout(function() {
                    checkTaskStatus(taskId, attempt + 1);
                }, 2000);
            } else {
                showStatus('Ошибка при проверке статуса задачи после нескольких попыток', 'error');
            }
        }
    });
}

  function showStatus(message, type) {
      $('#status')
          .removeClass('alert-success alert-error alert-info')
          .addClass('alert alert-' + type)
          .show()
          .text(message);
  }

  var startYearSelect = document.getElementById('id_start_year');
  var endYearSelect = document.getElementById('id_end_year');
  var startMonthSelect = document.getElementById('id_start_month');
  var endMonthSelect = document.getElementById('id_end_month');

  function updateMonths() {
      var startYear = parseInt(startYearSelect.value);
      var endYear = parseInt(endYearSelect.value);
      var currentYear = new Date().getFullYear();
      var currentMonth = new Date().getMonth() + 1;

      for (var i = 0; i < startMonthSelect.options.length; i++) {
          var month = parseInt(startMonthSelect.options[i].value);
          startMonthSelect.options[i].disabled = (startYear === currentYear && month > currentMonth);
      }

      for (var i = 0; i < endMonthSelect.options.length; i++) {
          var month = parseInt(endMonthSelect.options[i].value);
          endMonthSelect.options[i].disabled = (endYear === currentYear && month > currentMonth);
      }
  }

  startYearSelect.addEventListener('change', updateMonths);
  endYearSelect.addEventListener('change', updateMonths);

  updateMonths();
});