// JavaScript Document
$(document).bind("mobileinit", function(){
  //apply overrides here
      $.mobile.page.prototype.options.addBackBtn = false;
      $.mobile.page.prototype.options.domCache = true;
      $.mobile.defaultPageTransition = "fade";
  

});

	