jQuery(function($) {

  if ($('#content-views #contentview-featured-listings-config').length > 0) {
    // Show the featured listing configuration form with a nice overlay.
    $('#content-views #contentview-featured-listings-config > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }

});
