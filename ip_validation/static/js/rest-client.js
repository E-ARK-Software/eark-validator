/**
* Document ready function, loaded up on start
*/
$(document).ready(function () {
  /**
  * Event handler for the file selector
  */
  $('input:file').on('change', function () {
    // Disable the submit button
    $('button').prop('disabled', true)
    // Grab the label component
    var fileLabel = $(this).siblings('.custom-file-label')
    // Get filename without the fake path prefix
    var fileName = $(this).val().split('\\').pop()
    // Set the filename selection, a little tricksy
    fileLabel.addClass('selected').html(fileName)
    // Calculate and display the SHA1 of the file
    calcFileSha1(this.files[0])
  })

  /**
  * Event handler for submit button
  */
  // $('button').click(function () {
  //   // Grab the data from the form object
  //   var formData = new FormData($('form')[0])
  //   // Call the validator, with result renderer as callback
  //   ipValidator.validate(formData, function () {
  //     renderResult()
  //   })
  // })
})

/**
* Calculates the SHA-1 of selected file and displays the result
*/
function calcFileSha1 (file) {
  // New checksum calculator instance
  var rusha = new Rusha()
  // File reader to get data
  var reader = new FileReader()
  // Register reader onload event
  reader.onload = function (e) {
    // Calculate the checksum from the reader result
    var digest = rusha.digest(reader.result)
    // Set the label when finished
    $('#digest').val(digest)
    // Enable the submit button
    $('button').prop('disabled', false)
  }
  // Signal checkcum calculation and load reader
  $('#digest').val('Calcluating package checksum...')
  reader.readAsBinaryString(file)
}

/**
* Render the validation result to screen
*/
function renderResult () {
  $('#results').empty()
  $('#results').append($('<h2>').text('Validation Result'))
  var transforms = {
    status: {
      '<>': 'div',
      html: [
        {
          '<>': 'div',
          text: function (obj, index) { var date = new Date(obj.date); return 'Date:' + date.toUTCString() }
        },
        {
          '<>': 'div',
          class: function (obj, index) { return 'alert ' + (obj.valid ? 'alert-success' : 'alert-danger') },
          text: 'Validation Result: ${valid}'
        }
      ]
    },
    entries: {
      '<>': 'div',
      class: 'card',
      html: [
        {
          '<>': 'div',
          class: function (obj, index) { return 'card-body ' + (obj.level === 'ERROR' ? 'alert-danger' : obj.level === 'WARNING' ? 'alert-warning' : 'alert-info') },
          html: [
            {
              '<>': 'h5',
              class: 'card-heading',
              text: function (obj, index) { return (index + 1) + '. ' + obj.level + ': ' + obj.message }
            },
            {
              '<>': 'p',
              text: function (obj, index) { return obj.description }
            }
          ]
        }
      ]
    }
  }
  $('#results').json2html(ipValidator.result, transforms.status)
  $('#results').append($('<h3>').text('Validation Entries'))
  $('#results').json2html(ipValidator.result.validationEntries, transforms.entries)
}
