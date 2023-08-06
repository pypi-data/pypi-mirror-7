define([
  'bootstrap-carousel'
], function($, Registry, Base) {
  'use strict';

  // initialize only if we are in top frame
  if (window.parent === window) {
    $(document).ready(function() {
      $('body').addClass('top-frame');
      Registry.scan($('body'));
    });
  }

  return Requirejs;
});

