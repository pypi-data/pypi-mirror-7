(function($) {
  $(document).ready(function($) {

      /* This is basic - uses default settings */

      $("a#single_image").fancybox();

      /* Using custom settings */
      $("a.iframe").live('click', function() {
	  $.fancybox({
	      'hideOnContentClick': false,
	      'width' : 1000,
	      'height' : 500,
	      'href' : this.href,
	      'type': 'iframe'
	  });
	  return false;
      });

      /* Apply fancybox to multiple items */
      $("a.group").fancybox({
	  'transitionIn'  :   'elastic',
	  'transitionOut' :   'elastic',
	  'speedIn'       :   600, 
	  'speedOut'      :   200, 
	  'overlayShow'   :   false
      });

      $("a.iframe_internal").fancybox({
	      'hideOnContentClick': true,
	      'width' : 1000,
	      'height' : 500,
	      'type': 'inline'
	  });
  });
})(django.jQuery);
