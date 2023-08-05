/**
 * Djinn core defines some handlers for inline editing.
 */

// Use djinn namespace
if (djinn === undefined) {
  var djinn = {};
}


djinn.settings = {
  ALERT_MAP: {25: "success"}
};


djinn.get_target = function(elt) {

  if (elt.attr("target")) {
    return $(elt.attr("target"));
  } else {
    return self;
  }
};


djinn.handle_messages = function() {

  var name = "messages=";
  var ca = document.cookie.split(';');
  var messages = "";

  for(var i=0; i<ca.length; i++) {

    var c = ca[i].trim();
    if (c.indexOf(name) === 0) {
      messages = c.substring(name.length, c.length - 1);
    }
  }

  if (messages) {

    messages = messages.split("$")[1].replace(/\\054/g, ',').replace(/\\"/g, '"');

    messages = JSON.parse(messages);

    djinn.show_message(messages[0][3],
                       djinn.settings.ALERT_MAP[messages[0][2]] || "info");
  }
};


djinn.show_message = function(mesg, type) {

  $("body").append('<div id="message" class="alert alert-' + type + '"><a class="close" data-dismiss="alert">&times;</a>' + mesg + '</div>');
  
  setTimeout('$("#message").hide("slow")', 5000);
  
  $("#message").alert();
};


/**
 * Handle links with the update inline-class. This assumes that a GET
 * can be called with the URL provided in the href attribute. The
 * response should be either status 202 in case of errors, or 200.
 * @param e The event that triggered the call.
 */
djinn.update_inline = function(e) {

  var link = $(e.currentTarget);
  var target = djinn.get_target(link);

  e.preventDefault();

  $.get(link.attr("href"), function(data, status, xhr) {

    if (xhr.status == 202) {
      // nasty
    } else {
      target.replaceWith(data);
    }

    djinn.handle_messages();
  });
};


$(document).ready(function() {

  
  $(document).on("click", "a.update-inline", djinn.update_inline);

});
