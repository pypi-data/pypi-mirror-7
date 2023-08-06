this["jade"] = this["jade"] || {};
this["jade"]["templates"] = this["jade"]["templates"] || {};

this["jade"]["templates"]["vega_config"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div class=\"g-config-breadcrumb-container\"></div><p>This plugin uses the<a target=\"_blank\" href=\"http://trifacta.github.io/vega\"> Vega library</a> to render vega-formatted JSON objects directly in the Girder application.</p><p>This plugin requires no configuration. Simply upload the JSON file as an item,\nand then set a \"vega: true\" metadata field on the item. The visualization will\nthen be rendered directly in the item view any time it is viewed.</p>");;return buf.join("");
};

this["jade"]["templates"]["vega_render"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div class=\"g-item-vega\"><div class=\"g-item-vega-header\"><i class=\"icon-chart-bar\"></i> Vega</div><div class=\"g-item-vega-container\"><div class=\"g-item-vega-vis\"></div></div></div>");;return buf.join("");
};