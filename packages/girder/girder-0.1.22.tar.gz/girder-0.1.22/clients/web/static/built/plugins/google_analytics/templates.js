this["jade"] = this["jade"] || {};
this["jade"]["templates"] = this["jade"]["templates"] || {};

this["jade"]["templates"]["google_analytics_config"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div class=\"g-config-breadcrumb-container\"></div><div class=\"g-google-analytics-description\">To track pageviews in Girder, enter your Google Analytics tracking ID here.</div><form id=\"g-google_analytics-form\" role=\"form\"><div class=\"form-group\"><label for=\"google_analytics.tracking_id\" class=\"control-label\">Google Analytics Tracking ID</label><input id=\"google_analytics\" type=\"text\" placeholder=\"Tracking ID\" class=\"input-sm form-control tracking_id\"/></div><p id=\"g-oauth-provider-google-error-message\" class=\"g-validation-failed-message\"></p><input type=\"submit\" value=\"Save\" class=\"btn btn-sm btn-primary\"/></form>");;return buf.join("");
};