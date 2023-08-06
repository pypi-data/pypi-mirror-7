var typeaheadTemplate = '<li><a href="#"><span class="status"></span>' +
  '<span class="data"></span></a></li>'

var typeaheadOptions = {
  source: [],
  item: typeaheadTemplate
}


function updateTypeaheadSource(typeaheadInput, data) {
  var source = [];

  $.each(data.items, function(id, item) {
    source.push({
      id: id,
      name: item[0],  // series name
      status: item[1] // series status: 0 -> normal, 1 -> abnormal
    })
  });

  typeaheadInput.data('typeahead').source = source;
}


function renderStatus(statusTable, data) {
  var abnormalStatusColor = '#c03', normalStatusColor = 'green';
  var template = '<td><span class="status" style="background-color:{0};">' +
    '</span><a rel="tooltip" href="{2}" title="{1}">{1}</a></td>';

  var tdCounter = 0, html = '<tr>';
  var tdCap = 5; // td count per tr

  $.each(data.items, function(id, item){
    var seriesName = item[0];
    var backgroundColor = item[1] == 1 ? abnormalStatusColor : normalStatusColor;
    var seriesUri = item[2];

    html += template.format(backgroundColor, seriesName, seriesUri);
    tdCounter += 1;

    if (tdCounter == tdCap) {
      html += '</tr><tr>';  // end this tr and open a new tr tag
      tdCounter = 0;
    }

    // update status color in typeaheadInput if it exists
    $('ul.typeahead.dropdown-menu')
    .find('li[data-value="' + id + '"]')
    .find('.status')
    .css('background-color', backgroundColor);
  });

  if (tdCounter < tdCap) html += '</tr>';  // close tr if tdCounter dosent touch cap

  statusTable.html(html);
  $('img.spinner, div.spinner-box').hide();
  $('[rel="tooltip"]').tooltip();  // refresh tooltip on statusTable
}


function fire(indexApiUri, statusTable, typeaheadInput) {
  typeaheadInput.typeahead(typeaheadOptions);

  setIntervalAndExecuteRightNow(function() {
    $.getJSON(indexApiUri, function(data){
      renderStatus(statusTable, data);
      updateTypeaheadSource(typeaheadInput, data);
    });
  }, 10000);  // updata data each 10 secs
}
