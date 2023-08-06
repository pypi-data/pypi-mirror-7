this["jade"] = this["jade"] || {};
this["jade"]["templates"] = this["jade"]["templates"] || {};

this["jade"]["templates"]["oauth_config"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),google = locals_.google;
buf.push("<div class=\"g-config-breadcrumb-container\"></div><div class=\"g-oauth-provider-list-title\">Configure supported providers below</div><div id=\"g-oauth-provider-accordion\" class=\"panel-group\"><div class=\"panel panel-default\"><div class=\"panel-heading\"><div class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#g-oauth-provider-accordion\" href=\"#g-oauth-provider-google\"><i class=\"icon-gplus\"></i> Google</a></div></div><div id=\"g-oauth-provider-google\" class=\"panel-collapse collapse in\"><div class=\"panel-body\"><p>Client IDs and secret keys are managed in the Google Developer Console. When\ncreating your client ID there, use the following values:</p><div class=\"g-oauth-value-container\"><b>Authorized javascript origins:</b><span class=\"g-oauth-value\">" + (jade.escape((jade_interp = google.jsOrigin) == null ? '' : jade_interp)) + "</span></div><div class=\"g-oauth-value-container\"><b>Authorized redirect URI:</b><span class=\"g-oauth-value\">" + (jade.escape((jade_interp = google.redirectUri) == null ? '' : jade_interp)) + "</span></div><form id=\"g-oauth-provider-google-form\" role=\"form\"><div class=\"form-group\"><label for=\"g-oauth-provider-google-client-id\" class=\"control-label\">Google client ID</label><input id=\"g-oauth-provider-google-client-id\" type=\"text\" placeholder=\"Client ID\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-oauth-provider-google-client-secret\" class=\"control-label\">Google client secret</label><input id=\"g-oauth-provider-google-client-secret\" type=\"text\" placeholder=\"Client secret\" class=\"input-sm form-control\"/></div><p id=\"g-oauth-provider-google-error-message\" class=\"g-validation-failed-message\"></p><input type=\"submit\" value=\"Save\" class=\"btn btn-sm btn-primary\"/></form></div></div></div></div>");;return buf.join("");
};

this["jade"]["templates"]["oauth_login"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),buttons = locals_.buttons;
buf.push("<div class=\"g-oauth-container\"><div class=\"g-oauth-section-header\"><div class=\"g-oauth-section-header-text\">Or log in with</div></div>");
// iterate buttons
;(function(){
  var $$obj = buttons;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var button = $$obj[$index];

buf.push("<div" + (jade.attr("g-provider", "" + (button.provider) + "", true, false)) + (jade.cls(['g-oauth-button',"" + (button.class) + ""], [null,true])) + "><div class=\"g-oauth-button-icon\"><i" + (jade.cls(["icon-" + (button.icon) + ""], [true])) + "></i></div><div class=\"g-oauth-button-text\">" + (jade.escape((jade_interp = button.text || button.provider) == null ? '' : jade_interp)) + "</div></div>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var button = $$obj[$index];

buf.push("<div" + (jade.attr("g-provider", "" + (button.provider) + "", true, false)) + (jade.cls(['g-oauth-button',"" + (button.class) + ""], [null,true])) + "><div class=\"g-oauth-button-icon\"><i" + (jade.cls(["icon-" + (button.icon) + ""], [true])) + "></i></div><div class=\"g-oauth-button-text\">" + (jade.escape((jade_interp = button.text || button.provider) == null ? '' : jade_interp)) + "</div></div>");
    }

  }
}).call(this);

buf.push("</div>");;return buf.join("");
};