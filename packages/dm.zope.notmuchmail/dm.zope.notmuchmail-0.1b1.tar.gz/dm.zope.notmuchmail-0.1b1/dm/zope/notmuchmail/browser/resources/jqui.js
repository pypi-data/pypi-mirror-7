var jq = jQuery.noConflict();
function handle_click(event) {
  var e = jq(this).closest(".jqui");
  if (e.has(".notmuchmail-open").size()) {
    // open
    var url = e.find("a").attr("href");
    jq.ajax(
      { url: url,
	data: {ajax_load: 1},
	dataType: "html",
	success: function(data) {
	  var info = jq(data).find("#main").removeAttr("id");
	  var frame = jq("<tr><td></td><td colspan='10'></td></tr>");
	  frame.insertAfter(e); frame = e.next();
	  info.appendTo(frame.children("td").eq(1));
	  e.find(".notmuchmail-open").removeClass("notmuchmail-open").addClass("notmuchmail-close");
	}
      });
  } else {
    // close
    e.next().remove();
    e.find(".notmuchmail-close").removeClass("notmuchmail-close").addClass("notmuchmail-open");
  }
  return false;
};

jq(document).on("click", ".notmuchmail-open", handle_click);
jq(document).on("click", ".notmuchmail-close", handle_click);
jq(document).on("click", ".jqui a", handle_click);
