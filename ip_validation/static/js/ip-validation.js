/**
* JavaScript wrapper for Information Package validation
*/
var ipValidator = {
  result: null,
  status: null,
  validate: function (formData, callback, contentType = 'json') {
    console.log(formData)
    $.ajax({
      url: 'api/validate/',
      type: 'POST',
      data: formData,
      dataType: contentType,
      contentType: false,
      processData: false,
      success: function (data, textStatus, jqXHR) {
        console.log(jqXHR)
        ipValidator.result = data
        callback()
      },
      // HTTP Error handler
      error: function (jqXHR, textStatus, errorThrown) {
        // Log full error to console
        console.log('Validation Error: ' + textStatus + errorThrown)
        console.log(jqXHR)
        // Alert the user with details
        alert('Something has gone wrong!!\n\nHTTP ' + jqXHR.status + ': ' + jqXHR.statusText)
      }
    })
  }
}
