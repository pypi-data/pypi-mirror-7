this["jade"] = this["jade"] || {};
this["jade"]["templates"] = this["jade"]["templates"] || {};

this["jade"]["templates"]["adminConsole"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<ul class=\"g-admin-options\"><li class=\"g-server-config\"><i class=\"icon-cog-alt\"></i> Server configuration</li><li class=\"g-plugins-config\"><i class=\"icon-puzzle\"></i> Plugins</li><li class=\"g-assetstore-config\"><i class=\"icon-box-1\"></i> Assetstores</li></ul>");;return buf.join("");
};

this["jade"]["templates"]["assetstores"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),assetstores = locals_.assetstores,types = locals_.types;
buf.push("<div class=\"g-current-assetstores-container\"><div class=\"g-body-title\">Assetstores</div>");
if ( !assetstores.length)
{
buf.push("<div class=\"g-bottom-message\">You must create an assetstore before you can upload files to the server.\nSelect from the options below to create one.</div>");
}
else
{
buf.push("<div class=\"g-bottom-message\">Below is a list of all of the assetstores available to the server. The\none set as \"current\" is the one that uploaded files will be written to.</div>");
}
// iterate assetstores
;(function(){
  var $$obj = assetstores;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var assetstore = $$obj[$index];

buf.push("<div class=\"g-assetstore-container panel panel-default\"><div class=\"panel-body\"><div><b>Name:</b><span class=\"g-assetstore-name\"> " + (jade.escape((jade_interp = assetstore.get('name')) == null ? '' : jade_interp)) + "</span>");
if ( assetstore.get('current'))
{
buf.push(" (Current assetstore)");
}
buf.push("</div>");
if ( assetstore.get('type') == types.FILESYSTEM)
{
buf.push("<div><b>Type:</b><span class=\"g-assetstore-type\"> Filesystem</span></div><div><b>Root path:</b><span class=\"g-assetstore-root\"> " + (jade.escape((jade_interp = assetstore.get('root')) == null ? '' : jade_interp)) + "</span></div>");
}
else if ( assetstore.get('type') == types.GRIDFS)
{
buf.push("<div><b>Type:</b><span class=\"g-assetstore-type\"> GridFS</span></div><div><b>Database name:</b><span class=\"g-assetstore-root\"> " + (jade.escape((jade_interp = assetstore.get('db')) == null ? '' : jade_interp)) + "</span></div>");
}
else if ( assetstore.get('type') == types.S3)
{
buf.push("<div><b>Type:</b><span class=\"g-assetstore-type\"> S3</span></div><div><b>Bucket:</b><span class=\"g-assetstore-bucket\"> " + (jade.escape((jade_interp = assetstore.get('bucket')) == null ? '' : jade_interp)) + "</span></div>");
if ( assetstore.get('prefix'))
{
buf.push("<div><b>Path prefix:</b><span class=\"g-assetstore-prefix\"> " + (jade.escape((jade_interp = assetstore.get('prefix')) == null ? '' : jade_interp)) + "</span></div>");
}
buf.push("<div><b>Access key ID:</b><span class=\"g-access-key-id\"> " + (jade.escape((jade_interp = assetstore.get('accessKeyId')) == null ? '' : jade_interp)) + "</span></div><div><b>Secret access key:</b><span class=\"g-secret-key\"> " + (jade.escape((jade_interp = assetstore.get('secret')) == null ? '' : jade_interp)) + "</span></div>");
}
buf.push("<div><b>Capacity:</b><span class=\"g-assetstore-capacity\"> " + (jade.escape((jade_interp = assetstore.capacityString()) == null ? '' : jade_interp)) + "</span></div>");
if ( assetstore.capacityKnown())
{
buf.push("<div" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-assetstore-capacity-chart\"></div>");
}
buf.push("<div class=\"g-assetstore-buttons\"><button" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-edit-assetstore btn btn-sm btn-default\">Edit</button><button" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-delete-assetstore btn btn-sm btn-danger\">Delete</button>");
if ( !assetstore.get('current'))
{
buf.push("<button" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-set-current btn btn-sm btn-primary\">Set as current</button>");
}
buf.push("</div></div></div>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var assetstore = $$obj[$index];

buf.push("<div class=\"g-assetstore-container panel panel-default\"><div class=\"panel-body\"><div><b>Name:</b><span class=\"g-assetstore-name\"> " + (jade.escape((jade_interp = assetstore.get('name')) == null ? '' : jade_interp)) + "</span>");
if ( assetstore.get('current'))
{
buf.push(" (Current assetstore)");
}
buf.push("</div>");
if ( assetstore.get('type') == types.FILESYSTEM)
{
buf.push("<div><b>Type:</b><span class=\"g-assetstore-type\"> Filesystem</span></div><div><b>Root path:</b><span class=\"g-assetstore-root\"> " + (jade.escape((jade_interp = assetstore.get('root')) == null ? '' : jade_interp)) + "</span></div>");
}
else if ( assetstore.get('type') == types.GRIDFS)
{
buf.push("<div><b>Type:</b><span class=\"g-assetstore-type\"> GridFS</span></div><div><b>Database name:</b><span class=\"g-assetstore-root\"> " + (jade.escape((jade_interp = assetstore.get('db')) == null ? '' : jade_interp)) + "</span></div>");
}
else if ( assetstore.get('type') == types.S3)
{
buf.push("<div><b>Type:</b><span class=\"g-assetstore-type\"> S3</span></div><div><b>Bucket:</b><span class=\"g-assetstore-bucket\"> " + (jade.escape((jade_interp = assetstore.get('bucket')) == null ? '' : jade_interp)) + "</span></div>");
if ( assetstore.get('prefix'))
{
buf.push("<div><b>Path prefix:</b><span class=\"g-assetstore-prefix\"> " + (jade.escape((jade_interp = assetstore.get('prefix')) == null ? '' : jade_interp)) + "</span></div>");
}
buf.push("<div><b>Access key ID:</b><span class=\"g-access-key-id\"> " + (jade.escape((jade_interp = assetstore.get('accessKeyId')) == null ? '' : jade_interp)) + "</span></div><div><b>Secret access key:</b><span class=\"g-secret-key\"> " + (jade.escape((jade_interp = assetstore.get('secret')) == null ? '' : jade_interp)) + "</span></div>");
}
buf.push("<div><b>Capacity:</b><span class=\"g-assetstore-capacity\"> " + (jade.escape((jade_interp = assetstore.capacityString()) == null ? '' : jade_interp)) + "</span></div>");
if ( assetstore.capacityKnown())
{
buf.push("<div" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-assetstore-capacity-chart\"></div>");
}
buf.push("<div class=\"g-assetstore-buttons\"><button" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-edit-assetstore btn btn-sm btn-default\">Edit</button><button" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-delete-assetstore btn btn-sm btn-danger\">Delete</button>");
if ( !assetstore.get('current'))
{
buf.push("<button" + (jade.attr("cid", "" + (assetstore.cid) + "", true, false)) + " class=\"g-set-current btn btn-sm btn-primary\">Set as current</button>");
}
buf.push("</div></div></div>");
    }

  }
}).call(this);

buf.push("</div><div id=\"g-new-assetstore-container\"></div>");;return buf.join("");
};

this["jade"]["templates"]["collectionList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),girder = locals_.girder,collections = locals_.collections;
buf.push("<div class=\"g-collection-list-header\"><div class=\"g-collection-pagination\"></div><form role=\"form\" class=\"g-collection-search-form form-inline\"><div class=\"form-group g-collections-search-container\"></div></form>");
if ( (girder.currentUser && girder.currentUser.get('admin')))
{
buf.push("<button class=\"g-collection-create-button btn btn-sm btn-default\"><i class=\"icon-plus-squared\"></i> Create Collection</button>");
}
buf.push("</div>");
// iterate collections
;(function(){
  var $$obj = collections;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var collection = $$obj[$index];

buf.push("<div class=\"g-collection-list-entry\"><div class=\"g-collection-right-column\"><div class=\"g-collection-created\"><i class=\"icon-clock\"></i>Created on<span class=\"g-collection-created-date\"> " + (jade.escape((jade_interp = girder.formatDate(collection.get('created'), girder.DATE_MINUTE)) == null ? '' : jade_interp)) + "</span></div><div class=\"g-collection-updated\"><i class=\"icon-clock\"></i>Updated on<span class=\"g-collection-updated-date\"> " + (jade.escape((jade_interp = girder.formatDate(collection.get('updated'), girder.DATE_MINUTE)) == null ? '' : jade_interp)) + "</span></div></div><div class=\"g-collection-title\"><a" + (jade.attr("g-collection-cid", "" + (collection.cid) + "", true, false)) + " class=\"g-collection-link\"><b>" + (jade.escape((jade_interp = collection.get('name')) == null ? '' : jade_interp)) + "</b></a></div><div class=\"g-collection-subtitle\"><span class=\"g-collection-description\"> " + (jade.escape((jade_interp = collection.get('description')) == null ? '' : jade_interp)) + "</span></div><div class=\"g-clear-right\"></div></div>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var collection = $$obj[$index];

buf.push("<div class=\"g-collection-list-entry\"><div class=\"g-collection-right-column\"><div class=\"g-collection-created\"><i class=\"icon-clock\"></i>Created on<span class=\"g-collection-created-date\"> " + (jade.escape((jade_interp = girder.formatDate(collection.get('created'), girder.DATE_MINUTE)) == null ? '' : jade_interp)) + "</span></div><div class=\"g-collection-updated\"><i class=\"icon-clock\"></i>Updated on<span class=\"g-collection-updated-date\"> " + (jade.escape((jade_interp = girder.formatDate(collection.get('updated'), girder.DATE_MINUTE)) == null ? '' : jade_interp)) + "</span></div></div><div class=\"g-collection-title\"><a" + (jade.attr("g-collection-cid", "" + (collection.cid) + "", true, false)) + " class=\"g-collection-link\"><b>" + (jade.escape((jade_interp = collection.get('name')) == null ? '' : jade_interp)) + "</b></a></div><div class=\"g-collection-subtitle\"><span class=\"g-collection-description\"> " + (jade.escape((jade_interp = collection.get('description')) == null ? '' : jade_interp)) + "</span></div><div class=\"g-clear-right\"></div></div>");
    }

  }
}).call(this);
;return buf.join("");
};

this["jade"]["templates"]["collectionPage"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),collection = locals_.collection,girder = locals_.girder;
buf.push("<div class=\"g-collection-header\"><div class=\"btn-group pull-right\"><button data-toggle=\"dropdown\" title=\"Collection actions\" class=\"g-collection-actions-button btn btn-default dropdown-toggle\"><i class=\"icon-sitemap\"></i> Actions<i class=\"icon-down-dir\"></i></button><ul role=\"menu\" class=\"g-collection-actions-menu dropdown-menu pull-right\"><li role=\"presentation\"><a role=\"menuitem\" class=\"g-download-collection\"><i class=\"icon-download\"></i>Download collection</a></li>");
if ( (collection.getAccessLevel() >= girder.AccessType.WRITE))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-edit-collection\"><i class=\"icon-edit\"></i>Edit collection</a></li>");
}
if ( (collection.getAccessLevel() >= girder.AccessType.ADMIN))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-collection-access-control\"><i class=\"icon-lock\"></i>Access control</a></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-delete-collection\"><i class=\"icon-trash\"></i>Delete collection</a></li>");
}
buf.push("</ul></div><div class=\"g-collection-name g-body-title\">" + (jade.escape((jade_interp = collection.get('name')) == null ? '' : jade_interp)) + "</div><div class=\"g-collection-description g-body-subtitle\">" + (jade.escape((jade_interp = collection.get('description')) == null ? '' : jade_interp)) + "</div><div class=\"g-clear-right\"></div></div><div class=\"g-collection-hierarchy-container\"></div>");;return buf.join("");
};

this["jade"]["templates"]["frontPage"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),staticRoot = locals_.staticRoot,apiRoot = locals_.apiRoot,currentUser = locals_.currentUser;
buf.push("<div class=\"g-frontpage-header\"><img" + (jade.attr("src", "" + (staticRoot) + "/img/Girder_Mark.png", true, false)) + " width=\"82\" class=\"g-frontpage-logo\"/><div class=\"g-frontpage-title-container\"><div class=\"g-frontpage-title\">Girder</div><div class=\"g-frontpage-subtitle\">High performance data management</div></div></div><div class=\"g-frontpage-body\"><p class=\"g-frontpage-paragraph\"><b>Welcome to Girder!</b> If this is your first time here, you might want to check out the<a target=\"_blank\" href=\"http://girder.readthedocs.org/en/latest/user-guide.html\"> User Guide</a> to learn the basics of how to use the application.\n To browse the data hosted on this server, start on the<a class=\"g-collections-link\"> Collections</a> page. If you want to search for specific data on this server, use the<a class=\"g-quicksearch-link\"> Quick Search</a> box at the top of the screen. Developers who want to use the Girder REST API\n should check out the<a" + (jade.attr("href", "" + (apiRoot) + "", true, false)) + "> interactive web API docs</a>.");
if ( !currentUser)
{
buf.push("<p class=\"g-frontpage-paragraph\"> You are currently browsing anonymously. If you want to create a user\n account on this server, click the<a class=\"g-register-link\"> Register</a> link in the upper right corner. If you already have a user, click the<a class=\"g-login-link\"> Log In</a> link. Otherwise, you will only be able to see publicly visible data\n in the system.</p>");
}
else
{
buf.push("<p class=\"g-frontpage-paragraph\"> You are currently logged in as<b> " + (jade.escape((jade_interp = currentUser.get('login')) == null ? '' : jade_interp)) + "</b>. You can view your<a class=\"g-my-folders-link\"> personal data space</a> or go to your<a class=\"g-my-account-link\"> user account page.</a></p>");
}
buf.push("</p></div>");;return buf.join("");
};

this["jade"]["templates"]["groupList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),girder = locals_.girder,groups = locals_.groups;
buf.push("<div class=\"g-groups-list-header\"><div class=\"g-group-pagination\"></div><form role=\"form\" class=\"g-group-search-form form-inline\"><div class=\"form-group g-groups-search-container\"></div></form>");
if ( (girder.currentUser && girder.currentUser.get('admin')))
{
buf.push("<button class=\"g-group-create-button btn btn-sm btn-default\"><i class=\"icon-plus-squared\"></i> Create Group</button>");
}
buf.push("</div>");
// iterate groups
;(function(){
  var $$obj = groups;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var group = $$obj[$index];

buf.push("<div class=\"g-group-list-entry\"><div class=\"g-group-right-column\"><div class=\"g-group-created\"><i class=\"icon-clock\"></i>Created on<span class=\"g-group-created-date\"> " + (jade.escape((jade_interp = girder.formatDate(group.get('created'), girder.DATE_DAY)) == null ? '' : jade_interp)) + "</span></div><div class=\"g-group-privacy\">");
if ( (group.get('public')))
{
buf.push("<i class=\"icon-globe\"></i>Public group");
}
else
{
buf.push("<i class=\"icon-lock\"></i>Private group");
}
buf.push("</div></div><div class=\"g-group-title\"><a" + (jade.attr("g-group-cid", "" + (group.cid) + "", true, false)) + " class=\"g-group-link\"><b>" + (jade.escape((jade_interp = group.get('name')) == null ? '' : jade_interp)) + "</b></a></div><div class=\"g-group-subtitle\"><span class=\"g-group-description\"> " + (jade.escape((jade_interp = group.get('description')) == null ? '' : jade_interp)) + "</span></div><div class=\"g-clear-right\"></div></div>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var group = $$obj[$index];

buf.push("<div class=\"g-group-list-entry\"><div class=\"g-group-right-column\"><div class=\"g-group-created\"><i class=\"icon-clock\"></i>Created on<span class=\"g-group-created-date\"> " + (jade.escape((jade_interp = girder.formatDate(group.get('created'), girder.DATE_DAY)) == null ? '' : jade_interp)) + "</span></div><div class=\"g-group-privacy\">");
if ( (group.get('public')))
{
buf.push("<i class=\"icon-globe\"></i>Public group");
}
else
{
buf.push("<i class=\"icon-lock\"></i>Private group");
}
buf.push("</div></div><div class=\"g-group-title\"><a" + (jade.attr("g-group-cid", "" + (group.cid) + "", true, false)) + " class=\"g-group-link\"><b>" + (jade.escape((jade_interp = group.get('name')) == null ? '' : jade_interp)) + "</b></a></div><div class=\"g-group-subtitle\"><span class=\"g-group-description\"> " + (jade.escape((jade_interp = group.get('description')) == null ? '' : jade_interp)) + "</span></div><div class=\"g-clear-right\"></div></div>");
    }

  }
}).call(this);
;return buf.join("");
};

this["jade"]["templates"]["groupPage"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),isMember = locals_.isMember,isInvited = locals_.isInvited,girder = locals_.girder,group = locals_.group,isRequested = locals_.isRequested;
buf.push("<div class=\"g-group-header\"><div class=\"btn-group pull-right\"><button data-toggle=\"dropdown\" title=\"Group actions\" class=\"g-group-actions-button btn btn-default dropdown-toggle\"><i class=\"icon-users\"></i> Actions<i class=\"icon-down-dir\"></i></button><ul role=\"menu\" class=\"g-group-actions-menu dropdown-menu pull-right\">");
if ( (isMember))
{
buf.push("<li role=\"presentation\"><a role=\"menuitem\" class=\"g-group-leave\"><i class=\"icon-block\"></i>Leave group</a></li>");
}
else if ( (isInvited))
{
buf.push("<li role=\"presentation\"><a role=\"menuitem\" class=\"g-group-join\"><i class=\"icon-login\"></i>Join group</a></li>");
}
else if ( (girder.currentUser))
{
buf.push("<li role=\"presentation\"><a role=\"menuitem\" class=\"g-group-request-invite\"><i class=\"icon-export\"></i>Request membership</a></li>");
}
if ( (group.get('_accessLevel') >= girder.AccessType.WRITE))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-edit-group\"><i class=\"icon-edit\"></i>Edit group</a></li>");
}
if ( (group.get('_accessLevel') >= girder.AccessType.ADMIN))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-group-delete\"><i class=\"icon-trash\"></i>Delete group</a></li>");
}
buf.push("</ul></div><div class=\"g-group-name g-body-title\">" + (jade.escape((jade_interp = group.get('name')) == null ? '' : jade_interp)) + "</div><div class=\"g-group-description g-body-subtitle\">" + (jade.escape((jade_interp = group.get('description')) == null ? '' : jade_interp)) + "</div><div class=\"g-clear-right\"></div></div>");
if ( (girder.currentUser))
{
if ( (isMember))
{
buf.push("<div class=\"g-group-status-container g-member\"><i class=\"icon-ok\"></i>");
if ( (group.get('_accessLevel') < girder.AccessType.WRITE))
{
buf.push(" You are a <b>member</b> of this group.");
}
else if ( (group.get('_accessLevel') < girder.AccessType.ADMIN))
{
buf.push(" You are a <b>moderator</b> of this group.");
}
else
{
buf.push(" You are an <b>administrator</b> of this group.");
}
buf.push("</div>");
}
else if ( (isInvited))
{
buf.push("<div class=\"g-group-status-container g-invited\"><i class=\"icon-mail-alt\"></i> You have been invited to this group.<a class=\"g-group-join\"> Join group</a></div>");
}
else if ( (isRequested))
{
buf.push("<div class=\"g-group-status-container g-requested-invite\"><i class=\"icon-comment\"></i> You have requested to join this group.</div>");
}
else
{
buf.push("<div class=\"g-group-status-container g-nonmember\"><i class=\"icon-minus-circled\"></i> You are not a member of this group.<a class=\"g-group-request-invite\"> Request membership</a></div>");
}
}
buf.push("<ul class=\"g-group-tabs nav nav-tabs\"><li class=\"active\"><a href=\"#g-group-tab-roles\" data-toggle=\"tab\" name=\"roles\"><i class=\"icon-th-list\"></i> Roles</a></li><li><a href=\"#g-group-tab-pending\" data-toggle=\"tab\" name=\"pending\"><i class=\"icon-inbox\"></i>Pending</a></li></ul><div class=\"tab-content\"><div id=\"g-group-tab-roles\" class=\"tab-pane active\"><div class=\"g-group-members-container\"></div><div class=\"g-group-mods-container\"></div><div class=\"g-group-admins-container\"></div></div><div id=\"g-group-tab-pending\" class=\"tab-pane\"><div class=\"g-group-requests-container\"><div class=\"g-group-requests-header g-group-list-header\"><i class=\"icon-comment\"></i> Requests for membership</div><div class=\"g-group-requests-body\"><ul class=\"g-group-requests\">");
// iterate group.get('requests')
;(function(){
  var $$obj = group.get('requests');
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var user = $$obj[$index];

buf.push("<li" + (jade.attr("userid", "" + (user.id) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = user.name) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = user.login) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( group.get('_accessLevel') >= girder.AccessType.WRITE)
{
buf.push("<a title=\"Add to group\" class=\"g-group-request-accept\"><i class=\"icon-thumbs-up\"></i></a><a title=\"Deny request\" class=\"g-group-request-deny\"><i class=\"icon-thumbs-down\"></i></a>");
}
buf.push("</div></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var user = $$obj[$index];

buf.push("<li" + (jade.attr("userid", "" + (user.id) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = user.name) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = user.login) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( group.get('_accessLevel') >= girder.AccessType.WRITE)
{
buf.push("<a title=\"Add to group\" class=\"g-group-request-accept\"><i class=\"icon-thumbs-up\"></i></a><a title=\"Deny request\" class=\"g-group-request-deny\"><i class=\"icon-thumbs-down\"></i></a>");
}
buf.push("</div></li>");
    }

  }
}).call(this);

if ( (!group.get('requests').length))
{
buf.push("<div class=\"g-member-list-empty\"><i class=\"icon-info-circled\"></i> There are no outstanding invitation requests for this group.</div>");
}
buf.push("</ul></div></div><div class=\"g-group-invites-container\"><div class=\"g-group-invites-header g-group-list-header\"><i class=\"icon-mail-alt\"></i> Sent invitations</div><div class=\"g-group-invites-body\"></div></div></div></div>");;return buf.join("");
};

this["jade"]["templates"]["itemPage"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),girder = locals_.girder,item = locals_.item,accessLevel = locals_.accessLevel;
buf.push("<div class=\"g-item-breadcrumb-container\"></div><div class=\"g-item-header\"><div class=\"btn-group pull-right\"><button data-toggle=\"dropdown\" title=\"Item actions\" class=\"g-item-actions-button btn btn-default dropdown-toggle\"><i class=\"icon-sitemap\"></i> Actions<i class=\"icon-down-dir\"></i></button><ul role=\"menu\" class=\"g-item-actions-menu dropdown-menu pull-right\"><li role=\"presentation\"><a role=\"menuitem\"" + (jade.attr("href", "" + (girder.apiRoot + '/item/' + item.get('_id') + '/download') + "", true, false)) + " class=\"g-download-item\"><i class=\"icon-download\"></i>Download item</a></li>");
if ( (accessLevel >= girder.AccessType.WRITE))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-edit-item\"><i class=\"icon-edit\"></i>Edit item</a></li>");
}
if ( (accessLevel >= girder.AccessType.WRITE))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-delete-item\"><i class=\"icon-trash\"></i>Delete item</a></li>");
}
buf.push("</ul></div><div class=\"g-item-name g-body-title\">" + (jade.escape((jade_interp = item.get('name')) == null ? '' : jade_interp)) + "</div><div class=\"g-item-description g-body-subtitle\">" + (jade.escape((jade_interp = item.get('description')) == null ? '' : jade_interp)) + "</div></div><div class=\"g-item-info\"><div class=\"g-item-info-header\"><i class=\"icon-info\"></i>Info</div><div class=\"g-item-size g-info-list-entry\"><i class=\"icon-hdd\"></i>" + (jade.escape((jade_interp = girder.formatSize(item.get('size'))) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = item.get('size')) == null ? '' : jade_interp)) + " bytes)</div><div class=\"g-item-created g-info-list-entry\"><i class=\"icon-clock\"></i>Created on " + (jade.escape((jade_interp = girder.formatDate(item.get('created'), girder.DATE_SECOND)) == null ? '' : jade_interp)) + "</div><div class=\"g-item-updated g-info-list-entry\"><i class=\"icon-clock\"></i>Updated on " + (jade.escape((jade_interp = girder.formatDate(item.get('updated'), girder.DATE_SECOND)) == null ? '' : jade_interp)) + "</div></div><div class=\"g-item-metadata\"></div><div class=\"g-item-files\"><div class=\"g-item-files-header\"><i class=\"icon-docs\"></i> Files &amp; links</div><div class=\"g-item-files-container\"></div></div>");;return buf.join("");
};

this["jade"]["templates"]["plugins"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),allPlugins = locals_.allPlugins,undefined = locals_.undefined;
buf.push("<div class=\"g-body-title\">Plugins</div><div class=\"g-plugin-list-container\">");
// iterate allPlugins
;(function(){
  var $$obj = allPlugins;
  if ('number' == typeof $$obj.length) {

    for (var key = 0, $$l = $$obj.length; key < $$l; key++) {
      var plugin = $$obj[key];

buf.push("<div class=\"g-plugin-list-item\"><input type=\"checkbox\"" + (jade.attr("key", "" + (key) + "", true, false)) + (jade.attr("checked", (plugin.enabled ? "checked" : undefined), true, false)) + " class=\"g-plugin-switch\"/><div class=\"g-plugin-name\">" + (jade.escape((jade_interp = plugin.name) == null ? '' : jade_interp)) + "");
if ((plugin.configRoute))
{
buf.push("<a" + (jade.attr("g-route", "" + (plugin.configRoute) + "", true, false)) + " title=\"Configure Plugin\" class=\"g-plugin-config-link\"><i class=\"icon-cog\"></i></a>");
}
buf.push("</div><div class=\"g-plugin-description\">" + (jade.escape((jade_interp = plugin.description) == null ? '' : jade_interp)) + "</div></div>");
    }

  } else {
    var $$l = 0;
    for (var key in $$obj) {
      $$l++;      var plugin = $$obj[key];

buf.push("<div class=\"g-plugin-list-item\"><input type=\"checkbox\"" + (jade.attr("key", "" + (key) + "", true, false)) + (jade.attr("checked", (plugin.enabled ? "checked" : undefined), true, false)) + " class=\"g-plugin-switch\"/><div class=\"g-plugin-name\">" + (jade.escape((jade_interp = plugin.name) == null ? '' : jade_interp)) + "");
if ((plugin.configRoute))
{
buf.push("<a" + (jade.attr("g-route", "" + (plugin.configRoute) + "", true, false)) + " title=\"Configure Plugin\" class=\"g-plugin-config-link\"><i class=\"icon-cog\"></i></a>");
}
buf.push("</div><div class=\"g-plugin-description\">" + (jade.escape((jade_interp = plugin.description) == null ? '' : jade_interp)) + "</div></div>");
    }

  }
}).call(this);

buf.push("</div>");;return buf.join("");
};

this["jade"]["templates"]["systemConfiguration"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),settings = locals_.settings;
buf.push("<div class=\"g-body-title\">System configuration</div><form role=\"form\" class=\"g-settings-form\"><div class=\"form-group\"><label for=\"g-cookie-lifetime\">Cookie duration (days)</label><input id=\"g-cookie-lifetime\" type=\"text\"" + (jade.attr("value", "" + (settings['core.cookie_lifetime'] || '') + "", true, false)) + " placeholder=\"Default: 180\" title=\"How long users will stay logged in.\" class=\"form-control input-sm\"/></div><div class=\"form-group\"><label for=\"g-smtp-host\">SMTP host</label><input id=\"g-smtp-host\" type=\"text\"" + (jade.attr("value", "" + (settings['core.smtp_host'] || '') + "", true, false)) + " placeholder=\"Default: localhost:25\" title=\"The address of the SMTP server used to send emails.\" class=\"form-control input-sm\"/></div><div class=\"form-group\"><label for=\"g-email-from-address\">Email from address</label><input id=\"g-email-from-address\" type=\"text\"" + (jade.attr("value", "" + (settings['core.email_from_address'] || '') + "", true, false)) + " placeholder=\"Default: no-reply@girder.org\" title=\"The email address the system will use when sending emails.\" class=\"form-control input-sm\"/></div><div class=\"form-group\"><label for=\"g-registration-policy\">Registration policy</label><select id=\"g-registration-policy\" class=\"form-control input-sm\"><option value=\"open\">Open registration</option><option value=\"closed\">Closed registration</option></select></div><div class=\"form-group\"><button class=\"g-submit-settings btn btn-default btn-sm\"><i class=\"icon-ok\"></i> Save</button></div><div id=\"g-settings-error-message\" class=\"g-validation-failed-message\"></div></form>");;return buf.join("");
};

this["jade"]["templates"]["userList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),users = locals_.users,girder = locals_.girder,undefined = locals_.undefined;
buf.push("<div class=\"g-user-list-header\"><div class=\"g-user-pagination\"></div><form role=\"form\" class=\"g-user-search-form form-inline\"><div class=\"form-group g-users-search-container\"></div></form></div>");
// iterate users
;(function(){
  var $$obj = users;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var user = $$obj[$index];

buf.push("<div class=\"g-user-list-entry\"><div class=\"g-user-right-column\"><div class=\"g-user-joined\"><i class=\"icon-clock\"></i>Joined on<span class=\"g-user-joined-date\"> " + (jade.escape((jade_interp = girder.formatDate(user.get('created'), girder.DATE_DAY)) == null ? '' : jade_interp)) + "</span></div>");
if ( (user.get('size') !== undefined))
{
buf.push("<div class=\"g-space-used\"><i class=\"icon-floppy\"></i>Currently using<span class=\"g-user-space-used\"> " + (jade.escape((jade_interp = girder.formatSize(user.get('size'))) == null ? '' : jade_interp)) + "</span></div>");
}
buf.push("</div><div class=\"g-user-title\"><a" + (jade.attr("g-user-cid", "" + (user.cid) + "", true, false)) + " class=\"g-user-link\"><b>" + (jade.escape((jade_interp = user.get('firstName')) == null ? '' : jade_interp)) + " " + (jade.escape((jade_interp = user.get('lastName')) == null ? '' : jade_interp)) + "</b></a></div><div class=\"g-user-subtitle\"><span class=\"g-user-login\"> " + (jade.escape((jade_interp = user.get('login')) == null ? '' : jade_interp)) + "</span></div><div class=\"g-clear-right\"></div></div>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var user = $$obj[$index];

buf.push("<div class=\"g-user-list-entry\"><div class=\"g-user-right-column\"><div class=\"g-user-joined\"><i class=\"icon-clock\"></i>Joined on<span class=\"g-user-joined-date\"> " + (jade.escape((jade_interp = girder.formatDate(user.get('created'), girder.DATE_DAY)) == null ? '' : jade_interp)) + "</span></div>");
if ( (user.get('size') !== undefined))
{
buf.push("<div class=\"g-space-used\"><i class=\"icon-floppy\"></i>Currently using<span class=\"g-user-space-used\"> " + (jade.escape((jade_interp = girder.formatSize(user.get('size'))) == null ? '' : jade_interp)) + "</span></div>");
}
buf.push("</div><div class=\"g-user-title\"><a" + (jade.attr("g-user-cid", "" + (user.cid) + "", true, false)) + " class=\"g-user-link\"><b>" + (jade.escape((jade_interp = user.get('firstName')) == null ? '' : jade_interp)) + " " + (jade.escape((jade_interp = user.get('lastName')) == null ? '' : jade_interp)) + "</b></a></div><div class=\"g-user-subtitle\"><span class=\"g-user-login\"> " + (jade.escape((jade_interp = user.get('login')) == null ? '' : jade_interp)) + "</span></div><div class=\"g-clear-right\"></div></div>");
    }

  }
}).call(this);
;return buf.join("");
};

this["jade"]["templates"]["userPage"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),user = locals_.user,girder = locals_.girder;
buf.push("<div class=\"g-user-header\">");
if ( (user.getAccessLevel() >= girder.AccessType.WRITE))
{
buf.push("<div class=\"btn-group pull-right\"><button data-toggle=\"dropdown\" title=\"Item actions\" class=\"g-user-actions-button btn btn-default dropdown-toggle\"><i class=\"icon-sitemap\"></i> Actions<i class=\"icon-down-dir\"></i></button><ul role=\"menu\" class=\"g-item-actions-menu dropdown-menu pull-right\"><li role=\"presentation\"><a role=\"menuitem\" class=\"g-edit-user\"><i class=\"icon-edit\"></i>Edit user</a></li>");
if ( (user.getAccessLevel() >= girder.AccessType.ADMIN))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-delete-user\"><i class=\"icon-trash\"></i>Delete user</a></li>");
}
buf.push("</ul></div>");
}
buf.push("<div class=\"g-user-name g-body-title\">" + (jade.escape((jade_interp = user.get('firstName')) == null ? '' : jade_interp)) + " " + (jade.escape((jade_interp = user.get('lastName')) == null ? '' : jade_interp)) + "</div><div class=\"g-user-login g-body-subtitle\">" + (jade.escape((jade_interp = user.get('login')) == null ? '' : jade_interp)) + "</div></div><div class=\"g-user-hierarchy-container\"></div>");;return buf.join("");
};

this["jade"]["templates"]["userSettings"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),user = locals_.user,girder = locals_.girder;
buf.push("<div class=\"g-account-header\"><div class=\"g-user-name g-body-title\">" + (jade.escape((jade_interp = user.name()) == null ? '' : jade_interp)) + "</div><div class=\"g-user-description g-body-subtitle\">" + (jade.escape((jade_interp = user.get('login')) == null ? '' : jade_interp)) + "</div></div><ul class=\"g-account-tabs nav nav-tabs\"><li class=\"active\"><a href=\"#g-account-tab-info\" data-toggle=\"tab\" name=\"info\"><i class=\"icon-info-circled\"></i> Profile</a></li><li><a href=\"#g-account-tab-password\" data-toggle=\"tab\" name=\"password\"><i class=\"icon-lock\"></i>Password</a></li></ul><div class=\"tab-content\"><div id=\"g-account-tab-info\" class=\"tab-pane active\"><div class=\"g-user-info-container\"><form id=\"g-user-info-form\" role=\"form\"><div class=\"form-group\"><label for=\"g-login\">Login</label><p class=\"form-control-static\">" + (jade.escape((jade_interp = user.get('login')) == null ? '' : jade_interp)) + "</p></div><div class=\"form-group\"><label for=\"g-email\">Email</label><input id=\"g-email\" type=\"text\"" + (jade.attr("value", "" + (user.get('email')) + "", true, false)) + " class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-firstName\">First name</label><input id=\"g-firstName\" type=\"text\"" + (jade.attr("value", "" + (user.get('firstName')) + "", true, false)) + " class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-lastName\">Last name</label><input id=\"g-lastName\" type=\"text\"" + (jade.attr("value", "" + (user.get('lastName')) + "", true, false)) + " class=\"input-sm form-control\"/></div>");
if ( girder.currentUser.get('admin'))
{
buf.push("<div class=\"form-group\"><label for=\"g-admin\">User is site admin</label>");
if ( user.get('admin'))
{
buf.push("<input id=\"g-admin\" type=\"checkbox\" checked=\"checked\" class=\"input-sm-form-control\"/>");
}
else
{
buf.push("<input id=\"g-admin\" type=\"checkbox\" class=\"input-sm-form-control\"/>");
}
buf.push("</div>");
}
buf.push("<button type=\"submit\" class=\"btn btn-default btn-sm\"><i class=\"icon-edit\"></i>Save</button><div id=\"g-user-info-error-msg\" class=\"g-validation-failed-message\"></div></form></div></div><div id=\"g-account-tab-password\" class=\"tab-pane\"><div class=\"g-password-change-container\"><form id=\"g-password-change-form\" role=\"form\"><div class=\"form-group\"><label for=\"g-password-old\">Current password</label><input id=\"g-password-old\" type=\"password\" placeholder=\"Enter current password\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-password-new\">New password</label><input id=\"g-password-new\" type=\"password\" placeholder=\"Enter new password\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-password-retype\">Retype new password</label><input id=\"g-password-retype\" type=\"password\" placeholder=\"Retype new password\" class=\"input-sm form-control\"/></div><button type=\"submit\" class=\"btn btn-default btn-sm\"><i class=\"icon-lock\"></i>Change</button><div id=\"g-password-change-error-msg\" class=\"g-validation-failed-message\"></div></form></div></div></div>");;return buf.join("");
};

this["jade"]["templates"]["alert"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),type = locals_.type,icon = locals_.icon,text = locals_.text;
buf.push("<div" + (jade.cls(['alert','alert-dismissable',"alert-" + (type) + ""], [null,null,true])) + "><button type=\"button\" data-dismiss=\"alert\" aria-hidden=\"true\" class=\"close\">&times;</button>");
if ( icon)
{
buf.push("<i" + (jade.cls(["icon-" + (icon) + ""], [true])) + "></i>");
}
buf.push(" " + (jade.escape((jade_interp = text) == null ? '' : jade_interp)) + "</div>");;return buf.join("");
};

this["jade"]["templates"]["layout"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div id=\"g-app-header-container\"></div><div id=\"g-global-nav-container\"></div><div id=\"g-app-body-container\"></div><div id=\"g-app-footer-container\"></div><div id=\"g-dialog-container\" class=\"modal fade\"></div><div id=\"g-alerts-container\"></div>");;return buf.join("");
};

this["jade"]["templates"]["layoutFooter"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),apiRoot = locals_.apiRoot;
buf.push("<div class=\"g-footer-links\"><a id=\"g-about-link\" href=\"http://girder.readthedocs.org/en/latest/user-guide.html\">About</a><a id=\"g-contact-link\" href=\"mailto:kitware@kitware.com\">Contact</a><a" + (jade.attr("href", "" + (apiRoot) + "", true, false)) + ">Web API</a><a id=\"g-bug-link\" href=\"https://github.com/girder/girder/issues/new\">Report a bug</a></div><div class=\"g-footer-info\">&copy; Kitware, Inc.</div>");;return buf.join("");
};

this["jade"]["templates"]["layoutGlobalNav"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),navItems = locals_.navItems;
buf.push("<div class=\"g-global-nav-main\"><ul class=\"g-global-nav\">");
// iterate navItems
;(function(){
  var $$obj = navItems;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var navItem = $$obj[$index];

buf.push("<li class=\"g-global-nav-li\"><a" + (jade.attr("g-target", "" + (navItem.target) + "", true, false)) + (jade.attr("g-name", "" + (navItem.name) + "", true, false)) + " class=\"g-nav-link\"><i" + (jade.cls(["" + (navItem.icon) + ""], [true])) + "></i><span>" + (jade.escape((jade_interp = navItem.name) == null ? '' : jade_interp)) + "</span></a></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var navItem = $$obj[$index];

buf.push("<li class=\"g-global-nav-li\"><a" + (jade.attr("g-target", "" + (navItem.target) + "", true, false)) + (jade.attr("g-name", "" + (navItem.name) + "", true, false)) + " class=\"g-nav-link\"><i" + (jade.cls(["" + (navItem.icon) + ""], [true])) + "></i><span>" + (jade.escape((jade_interp = navItem.name) == null ? '' : jade_interp)) + "</span></a></li>");
    }

  }
}).call(this);

buf.push("</ul></div><div class=\"g-global-nav-fade\"></div>");;return buf.join("");
};

this["jade"]["templates"]["layoutHeader"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div class=\"g-header-wrapper\"><div class=\"g-app-title\">Girder</div><form role=\"form\" class=\"g-quick-search-form form-inline\"><div class=\"form-group g-quick-search-container\"></div></form><div class=\"g-current-user-wrapper navbar-right\"></div><div class=\"g-clear-both\"></div></div>");;return buf.join("");
};

this["jade"]["templates"]["layoutHeaderUser"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),user = locals_.user;
buf.push("<div class=\"g-user-text\">");
if ( (user))
{
buf.push("<a data-toggle=\"dropdown\" data-target=\"#g-user-action-menu\">" + (jade.escape((jade_interp = user.get('firstName')) == null ? '' : jade_interp)) + " " + (jade.escape((jade_interp = user.get('lastName')) == null ? '' : jade_interp)) + "<i class=\"icon-down-open\"></i></a><div id=\"g-user-action-menu\" class=\"dropdown\"><ul role=\"menu\" class=\"dropdown-menu\"><li role=\"presentation\"><a class=\"g-my-folders\"><i class=\"icon-folder\"></i>My folders</a></li><li role=\"presentation\"><a class=\"g-my-settings\"><i class=\"icon-cog\"></i>My account</a></li><li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a class=\"g-logout\"><i class=\"icon-logout\"></i>Log out</a></li></ul></div>");
}
else
{
buf.push("<a class=\"g-register\">Register</a> or<a class=\"g-login\"> Log In<i class=\"icon-login\"></i></a>");
}
buf.push("</div>");;return buf.join("");
};

this["jade"]["templates"]["loginDialog"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-login-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">Log in</h4></div><div class=\"modal-body\"><div class=\"form-group\"><label for=\"g-login\" class=\"control-label\">Login or email</label><input id=\"g-login\" type=\"text\" placeholder=\"Enter login\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-password\" class=\"control-label\">Password</label><input id=\"g-password\" type=\"password\" placeholder=\"Enter password\" class=\"input-sm form-control\"/></div><div class=\"g-validation-failed-message\"></div><div class=\"g-bottom-message\">Don't have an account yet?<a class=\"g-register-link\"> Register here.</a> |<a class=\"g-forgot-password\"> Forgot your password?</a></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-default\">Close</a><button id=\"g-login-button\" type=\"submit\" class=\"btn btn-primary\"><i class=\"icon-login\"></i> Login</button></div></form></div></div>");;return buf.join("");
};

this["jade"]["templates"]["registerDialog"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-register-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">Sign up</h4></div><div class=\"modal-body\"><div id=\"g-group-login\" class=\"form-group\"><label for=\"g-login\" class=\"control-label\">Choose a login name</label><input id=\"g-login\" type=\"text\" placeholder=\"Login\" class=\"input-sm form-control\"/></div><div id=\"g-group-email\" class=\"form-group\"><label for=\"g-email\" class=\"control-label\">Enter your email address</label><input id=\"g-email\" type=\"text\" placeholder=\"Email\" class=\"input-sm form-control\"/></div><div id=\"g-group-firstName\" class=\"form-group\"><label for=\"g-firstName\" class=\"control-label\">Enter your first name</label><input id=\"g-firstName\" type=\"text\" placeholder=\"First Name\" class=\"input-sm form-control\"/></div><div id=\"g-group-lastName\" class=\"form-group\"><label for=\"g-lastName\" class=\"control-label\">Enter your last name</label><input id=\"g-lastName\" type=\"text\" placeholder=\"Last Name\" class=\"input-sm form-control\"/></div><div id=\"g-group-password\" class=\"form-group\"><label for=\"g-password\" class=\"control-label\">Choose a password</label><input id=\"g-password\" type=\"password\" placeholder=\"Password\" class=\"input-sm form-control\"/></div><div id=\"g-group-password2\" class=\"form-group\"><label for=\"g-password2\" class=\"control-label\">Retype your password</label><input id=\"g-password2\" type=\"password\" placeholder=\"Password\" class=\"input-sm form-control\"/></div><div class=\"g-validation-failed-message\"></div><div class=\"g-bottom-message\">Already have an account?<a class=\"g-login-link\"> Log in here.</a></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-default\">Close</a><button id=\"g-register-button\" type=\"submit\" class=\"btn btn-primary\"><i class=\"icon-plus-circled\"></i> Register</button></div></form></div></div>");;return buf.join("");
};

this["jade"]["templates"]["resetPasswordDialog"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-reset-password-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">Reset password</h4></div><div class=\"modal-body\"><div class=\"g-password-reset-explanation\">If you have forgotten your password, you can enter your email address\nhere. Your password will be reset and an email will be sent to that\naddress with the new password.</div><div class=\"form-group\"><label for=\"g-email\" class=\"control-label\">Email</label><input id=\"g-email\" type=\"text\" placeholder=\"Enter your email\" class=\"input-sm form-control\"/></div><div class=\"g-validation-failed-message\"></div><div class=\"g-bottom-message\"><a class=\"g-register-link\"> Register</a> |<a class=\"g-login-link\"> Login</a></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-default\">Close</a><button id=\"g-reset-password-button\" type=\"submit\" class=\"btn btn-primary\"><i class=\"icon-mail\"></i> Reset</button></div></form></div></div>");;return buf.join("");
};

this["jade"]["templates"]["accessEditor"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),modelType = locals_.modelType,model = locals_.model,public = locals_.public,undefined = locals_.undefined;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">Access control</h4><div class=\"g-dialog-subtitle\">");
if ( (modelType == 'folder'))
{
buf.push("<i class=\"icon-folder\"></i>");
}
else if ( (modelType == 'collection'))
{
buf.push("<i class=\"icon-sitemap\"></i>");
}
buf.push("" + (jade.escape((jade_interp = model.name()) == null ? '' : jade_interp)) + "</div></div><div class=\"modal-body g-access-modal-body\"><div class=\"g-public-container\"><div class=\"radio\"><label><input id=\"g-access-private\" type=\"radio\" name=\"privacy\"" + (jade.attr("checked", (public ? undefined : "checked"), true, false)) + "/><i class=\"icon-lock\"></i>Private &mdash; Access is required to view this resource</label></div><div class=\"radio\"><label><input id=\"g-access-public\" type=\"radio\" name=\"privacy\"" + (jade.attr("checked", (public ? "checked" : undefined), true, false)) + "/><i class=\"icon-globe\"></i>Public &mdash; Anyone can view this resource</label></div></div><div class=\"g-ac-list-title\"><i class=\"icon-key-1\"></i> Permissions</div><div class=\"g-ac-list\"><div id=\"g-ac-list-groups\"></div><div id=\"g-ac-list-users\"></div></div><div class=\"g-grant-access-container\"><form role=\"form\"><div class=\"form-group\"><label for=\"addAccess\">Grant access to another group or user</label><div class=\"g-search-field-container\"></div></div></form></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">Close</a><button type=\"submit\" class=\"g-save-access-list btn btn-small btn-primary\"><i class=\"icon-ok\"></i> Save</button></div></div></div>");;return buf.join("");
};

this["jade"]["templates"]["accessEntry"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),entry = locals_.entry,type = locals_.type,accessTypes = locals_.accessTypes;
buf.push("<div" + (jade.attr("resourceid", "" + (entry.id) + "", true, false)) + (jade.cls(["g-" + (type) + "-access-entry"], [true])) + "><div class=\"g-access-col-left\">");
var icon = type == 'group' ? 'users' : 'user';
buf.push("<div class=\"g-access-icon\"><i" + (jade.cls(["icon-" + (icon) + ""], [true])) + "></i></div><div class=\"g-access-desc\"><div class=\"g-desc-title\">" + (jade.escape((jade_interp = entry.title) == null ? '' : jade_interp)) + "</div><div class=\"g-desc-subtitle\">" + (jade.escape((jade_interp = entry.subtitle) == null ? '' : jade_interp)) + "</div></div></div><div class=\"g-access-col-right\"><select>");
var sel=null; if (entry.level == accessTypes.READ) sel='selected';
buf.push("<option" + (jade.attr("value", "" + (accessTypes.READ) + "", true, false)) + (jade.attr("selected", sel, true, false)) + ">Can view</option>");
var sel=null; if (entry.level == accessTypes.WRITE) sel='selected';
buf.push("<option" + (jade.attr("value", "" + (accessTypes.WRITE) + "", true, false)) + (jade.attr("selected", sel, true, false)) + ">Can edit</option>");
var sel=null; if (entry.level == accessTypes.ADMIN) sel='selected';
buf.push("<option" + (jade.attr("value", "" + (accessTypes.ADMIN) + "", true, false)) + (jade.attr("selected", sel, true, false)) + ">Is owner</option></select><a title=\"Remove access\" class=\"g-action-remove-access\"><i class=\"icon-block\"></i></a></div></div>");;return buf.join("");
};

this["jade"]["templates"]["checkedActionsMenu"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),folderCount = locals_.folderCount,itemCount = locals_.itemCount,minFolderLevel = locals_.minFolderLevel,AccessType = locals_.AccessType,minItemLevel = locals_.minItemLevel;
buf.push("<li role=\"presentation\" class=\"g-checked-menu-header dropdown-header\">");
if ( (folderCount))
{
buf.push("<i class=\"icon-folder\"></i><span class=\"g-checked-folder-count\">" + (jade.escape((jade_interp = folderCount) == null ? '' : jade_interp)) + "</span>");
}
if ( (itemCount))
{
buf.push("<i class=\"icon-doc-text-inv\"></i><span class=\"g-checked-item-count\">" + (jade.escape((jade_interp = itemCount) == null ? '' : jade_interp)) + "</span>");
}
buf.push("</li><li><a class=\"g-download-checked\"><i class=\"icon-download\"></i>Download checked resources</a></li>");
if ( (minFolderLevel >= AccessType.ADMIN && minItemLevel >= AccessType.WRITE))
{
buf.push("<li class=\"g-admin divider\"></li><li class=\"g-admin\"><a class=\"g-delete-checked\"><i class=\"icon-trash\"></i>Delete checked resources</a></li>");
};return buf.join("");
};

this["jade"]["templates"]["confirmDialog"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),params = locals_.params;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><div class=\"modal-body\"><p></p></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">" + (jade.escape((jade_interp = params.noText) == null ? '' : jade_interp)) + "</a><a id=\"g-confirm-button\"" + (jade.cls(['btn','btn-small',"" + (params.yesClass) + ""], [null,null,true])) + ">" + (jade.escape((jade_interp = params.yesText) == null ? '' : jade_interp)) + "</a></div></div></div>");;return buf.join("");
};

this["jade"]["templates"]["editCollectionWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),collection = locals_.collection;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-collection-edit-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">");
if ( (collection))
{
buf.push("Edit collection");
}
else
{
buf.push("Create collection");
}
buf.push("</h4></div><div class=\"modal-body\"><div class=\"form-group\"><label for=\"g-name\" class=\"control-label\">Name</label><input id=\"g-name\" type=\"text\" placeholder=\"Enter collection name\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-description\" class=\"control-label\">Description (optional)</label><textarea id=\"g-description\" placeholder=\"Enter collection description\" class=\"input-sm form-control\"></textarea></div><div class=\"g-validation-failed-message\"></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">Cancel</a><button type=\"submit\" class=\"g-save-collection btn btn-small btn-primary\">");
if ( (collection))
{
buf.push("<i class=\"icon-edit\"></i>Save");
}
else
{
buf.push("<i class=\"icon-plus-squared\"></i>Create");
}
buf.push("</button></div></form></div></div>");;return buf.join("");
};

this["jade"]["templates"]["editFolderWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),folder = locals_.folder;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-folder-edit-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">");
if ( (folder))
{
buf.push("Edit folder");
}
else
{
buf.push("Create folder");
}
buf.push("</h4></div><div class=\"modal-body\"><div class=\"form-group\"><label for=\"g-name\" class=\"control-label\">Name</label><input id=\"g-name\" type=\"text\" placeholder=\"Enter folder name\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-description\" class=\"control-label\">Description (optional)</label><textarea id=\"g-description\" placeholder=\"Enter folder description\" class=\"input-sm form-control\"></textarea></div><div class=\"g-validation-failed-message\"></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">Cancel</a><button type=\"submit\" class=\"g-save-folder btn btn-small btn-primary\">");
if ( (folder))
{
buf.push("<i class=\"icon-edit\"></i>Save");
}
else
{
buf.push("<i class=\"icon-plus-squared\"></i>Create");
}
buf.push("</button></div></form></div></div>");;return buf.join("");
};

this["jade"]["templates"]["editGroupWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),group = locals_.group,public = locals_.public,undefined = locals_.undefined;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-group-edit-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">");
if ( (group))
{
buf.push("Edit group");
}
else
{
buf.push("Create group");
}
buf.push("</h4></div><div class=\"modal-body\"><div class=\"g-public-container\"><div class=\"radio\"><label><input id=\"g-access-private\" type=\"radio\" name=\"privacy\"" + (jade.attr("checked", (public ? undefined : "checked"), true, false)) + "/><i class=\"icon-lock\"></i>Private &mdash; Only members can see this group</label></div><div class=\"radio\"><label><input id=\"g-access-public\" type=\"radio\" name=\"privacy\"" + (jade.attr("checked", (public ? "checked" : undefined), true, false)) + "/><i class=\"icon-globe\"></i>Public &mdash; Anyone can see this group</label></div></div><div class=\"form-group\"><label for=\"g-name\" class=\"control-label\">Name</label><input id=\"g-name\" type=\"text\" placeholder=\"Enter group name\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-description\" class=\"control-label\">Description (optional)</label><textarea id=\"g-description\" placeholder=\"Enter group description\" class=\"input-sm form-control\"></textarea></div><div class=\"g-validation-failed-message\"></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">Cancel</a><button type=\"submit\" class=\"g-save-group btn btn-small btn-primary\">");
if ( (group))
{
buf.push("<i class=\"icon-edit\"></i>Save");
}
else
{
buf.push("<i class=\"icon-plus-squared\"></i>Create");
}
buf.push("</button></div></form></div></div>");;return buf.join("");
};

this["jade"]["templates"]["editItemWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),item = locals_.item;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-item-edit-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">");
if ( (item))
{
buf.push("Edit item");
}
else
{
buf.push("Create item");
}
buf.push("</h4></div><div class=\"modal-body\"><div class=\"form-group\"><label for=\"g-name\" class=\"control-label\">Name</label><input id=\"g-name\" type=\"text\" placeholder=\"Enter item name\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-description\" class=\"control-label\">Description (optional)</label><textarea id=\"g-description\" placeholder=\"Enter item description\" class=\"input-sm form-control\"></textarea></div><div class=\"g-validation-failed-message\"></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">Cancel</a><button type=\"submit\" class=\"g-save-item btn btn-small btn-primary\">");
if ( (item))
{
buf.push("<i class=\"icon-edit\"></i>Save");
}
else
{
buf.push("<i class=\"icon-plus-squared\"></i>Create");
}
buf.push("</button></div></form></div></div>");;return buf.join("");
};

this["jade"]["templates"]["fileList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),files = locals_.files,girder = locals_.girder,hasMore = locals_.hasMore;
buf.push("<ul class=\"g-file-list\">");
// iterate files
;(function(){
  var $$obj = files;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var file = $$obj[$index];

buf.push("<li class=\"g-file-list-entry\"><a" + (jade.attr("href", "" + (girder.apiRoot + '/file/' + file.get('_id') + '/download/' + file.get('name')) + "", true, false)) + " target=\"{file.get('linkUrl') ? '_blank' : '_self'}\" class=\"g-file-list-link\">");
if ( (file.get('linkUrl')))
{
buf.push("<i class=\"icon-link\"></i><span class=\"g-file-name\">" + (jade.escape((jade_interp = file.get('name')) == null ? '' : jade_interp)) + "</span><i class=\"icon-link-ext\"></i>");
}
else
{
buf.push("<i class=\"icon-doc-inv\"></i>" + (jade.escape((jade_interp = file.get('name')) == null ? '' : jade_interp)) + "");
}
buf.push("</a></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var file = $$obj[$index];

buf.push("<li class=\"g-file-list-entry\"><a" + (jade.attr("href", "" + (girder.apiRoot + '/file/' + file.get('_id') + '/download/' + file.get('name')) + "", true, false)) + " target=\"{file.get('linkUrl') ? '_blank' : '_self'}\" class=\"g-file-list-link\">");
if ( (file.get('linkUrl')))
{
buf.push("<i class=\"icon-link\"></i><span class=\"g-file-name\">" + (jade.escape((jade_interp = file.get('name')) == null ? '' : jade_interp)) + "</span><i class=\"icon-link-ext\"></i>");
}
else
{
buf.push("<i class=\"icon-doc-inv\"></i>" + (jade.escape((jade_interp = file.get('name')) == null ? '' : jade_interp)) + "");
}
buf.push("</a></li>");
    }

  }
}).call(this);

if ( (hasMore))
{
buf.push("<li class=\"g-show-more\"><a class=\"g-show-more-files\"><i class=\"icon-level-down\"></i>Show more files...</a></li>");
}
buf.push("</ul>");;return buf.join("");
};

this["jade"]["templates"]["folderList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),folders = locals_.folders,hasMore = locals_.hasMore;
buf.push("<ul class=\"g-folder-list\">");
// iterate folders
;(function(){
  var $$obj = folders;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var folder = $$obj[$index];

buf.push("<li class=\"g-folder-list-entry\"><input type=\"checkbox\"" + (jade.attr("g-folder-cid", "" + (folder.cid) + "", true, false)) + " class=\"g-list-checkbox\"/><a" + (jade.attr("g-folder-cid", "" + (folder.cid) + "", true, false)) + " class=\"g-folder-list-link\"><i class=\"icon-folder\"></i>" + (jade.escape((jade_interp = folder.get('name')) == null ? '' : jade_interp)) + "<i class=\"icon-right-dir\"></i></a><div class=\"g-folder-privacy\">");
if ( folder.get('public'))
{
buf.push("<i class=\"icon-globe\"></i>Public");
}
else
{
buf.push("<i class=\"icon-lock\"></i>Private");
}
buf.push("</div></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var folder = $$obj[$index];

buf.push("<li class=\"g-folder-list-entry\"><input type=\"checkbox\"" + (jade.attr("g-folder-cid", "" + (folder.cid) + "", true, false)) + " class=\"g-list-checkbox\"/><a" + (jade.attr("g-folder-cid", "" + (folder.cid) + "", true, false)) + " class=\"g-folder-list-link\"><i class=\"icon-folder\"></i>" + (jade.escape((jade_interp = folder.get('name')) == null ? '' : jade_interp)) + "<i class=\"icon-right-dir\"></i></a><div class=\"g-folder-privacy\">");
if ( folder.get('public'))
{
buf.push("<i class=\"icon-globe\"></i>Public");
}
else
{
buf.push("<i class=\"icon-lock\"></i>Private");
}
buf.push("</div></li>");
    }

  }
}).call(this);

if ( (hasMore))
{
buf.push("<li class=\"g-show-more\"><a class=\"g-show-more-folders\"><i class=\"icon-level-down\"></i>Show more folders...</a></li>");
}
buf.push("</ul>");;return buf.join("");
};

this["jade"]["templates"]["groupAdminList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),admins = locals_.admins,level = locals_.level,accessType = locals_.accessType;
buf.push("<div class=\"g-group-admins-header g-group-list-header\"><i class=\"icon-star\"></i> Administrators</div><div class=\"g-group-admins-body\"><ul class=\"g-group-admins\">");
// iterate admins
;(function(){
  var $$obj = admins;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var userAccess = $$obj[$index];

buf.push("<li" + (jade.attr("userid", "" + (userAccess.id) + "", true, false)) + (jade.attr("username", "" + (userAccess.name) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = userAccess.name) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = userAccess.login) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.ADMIN)
{
buf.push("<a title=\"Demote to member\" class=\"g-group-admin-demote\"><i class=\"icon-down-big\"></i></a>");
}
buf.push("</div></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var userAccess = $$obj[$index];

buf.push("<li" + (jade.attr("userid", "" + (userAccess.id) + "", true, false)) + (jade.attr("username", "" + (userAccess.name) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = userAccess.name) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = userAccess.login) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.ADMIN)
{
buf.push("<a title=\"Demote to member\" class=\"g-group-admin-demote\"><i class=\"icon-down-big\"></i></a>");
}
buf.push("</div></li>");
    }

  }
}).call(this);

if ( (!admins.length))
{
buf.push("<div class=\"g-member-list-empty\"><i class=\"icon-info-circled\"></i> There are no administrators in this group.</div>");
}
buf.push("</ul></div>");;return buf.join("");
};

this["jade"]["templates"]["groupInviteDialog"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),user = locals_.user,level = locals_.level,accessType = locals_.accessType;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">Invite user to group</h4><div class=\"g-dialog-subtitle\"><i class=\"icon-user\"></i>" + (jade.escape((jade_interp = user.text) == null ? '' : jade_interp)) + "</div></div><div class=\"modal-body\"><label for=\"g-role\" class=\"control-label\">Select a role for this user</label><div id=\"g-invite-role-container\" class=\"panel-group\"><div class=\"panel panel-default\"><div class=\"panel-heading\"><div class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#g-invite-role-container\" href=\"#g-invite-role-member\">Invite as member</a></div></div><div id=\"g-invite-role-member\" class=\"panel-collapse collapse in\"><div class=\"panel-body\"><p>Group members are able to gain all privileges granted to\nthe group itself on other resources. They are able to view the\ngroup, but may not change properties of the group.</p><div class=\"g-invite-as-member btn btn-primary\"><i class=\"icon-mail\"></i> Invite as member</div></div></div></div><div class=\"panel panel-default\"><div class=\"panel-heading\"><div class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#g-invite-role-container\" href=\"#g-invite-role-moderator\">Invite as moderator</a></div></div><div id=\"g-invite-role-moderator\" class=\"panel-collapse collapse\"><div class=\"panel-body\"><p>Group moderators are members of the group who are also granted\nthe power to add and remove users from the group, and edit\ngroup properties.</p><div class=\"g-invite-as-moderator btn btn-primary\"><i class=\"icon-mail\"></i> Invite as moderator</div></div></div></div>");
if ( (level > accessType.WRITE))
{
buf.push("<div class=\"panel panel-default\"><div class=\"panel-heading\"><div class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#g-invite-role-container\" href=\"#g-invite-role-admin\">Invite as administrator</a></div></div><div id=\"g-invite-role-admin\" class=\"panel-collapse collapse\"><div class=\"panel-body\"><p>Group administrators have all the power of group moderators,\nand additionally can also promote group members to moderators\nor administrators, and also have the power to delete the\ngroup itself.</p><div class=\"g-invite-as-admin btn btn-primary\"><i class=\"icon-mail\"></i> Invite as administrator</div></div></div></div>");
}
buf.push("</div><div class=\"g-validation-failed-message\"></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">Cancel</a></div></div></div>");;return buf.join("");
};

this["jade"]["templates"]["groupInviteList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),invitees = locals_.invitees,level = locals_.level,accessType = locals_.accessType;
buf.push("<ul class=\"g-group-invites\">");
// iterate invitees
;(function(){
  var $$obj = invitees;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var user = $$obj[$index];

buf.push("<li" + (jade.attr("cid", "" + (user.cid) + "", true, false)) + (jade.attr("username", "" + (user.name()) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = user.name()) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = user.get('login')) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.WRITE)
{
buf.push("<a title=\"Uninvite this user\" class=\"g-group-uninvite\"><i class=\"icon-block\"></i></a>");
}
buf.push("</div></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var user = $$obj[$index];

buf.push("<li" + (jade.attr("cid", "" + (user.cid) + "", true, false)) + (jade.attr("username", "" + (user.name()) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = user.name()) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = user.get('login')) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.WRITE)
{
buf.push("<a title=\"Uninvite this user\" class=\"g-group-uninvite\"><i class=\"icon-block\"></i></a>");
}
buf.push("</div></li>");
    }

  }
}).call(this);

if ( (!invitees.length))
{
buf.push("<div class=\"g-member-list-empty\"><i class=\"icon-info-circled\"></i> There are no pending invitations to this group.</div>");
}
buf.push("</ul>");;return buf.join("");
};

this["jade"]["templates"]["groupMemberList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),level = locals_.level,accessType = locals_.accessType,members = locals_.members;
buf.push("<div class=\"g-group-members-header g-group-list-header\"><i class=\"icon-users\"></i> Members");
if ( level >= accessType.WRITE)
{
buf.push("<form role=\"form\" class=\"g-group-invite-form form-inline\"><span><i class=\"icon-mail-alt\"></i></span><div class=\"form-group g-group-invite-container\"></div></form>");
}
buf.push("<div class=\"g-member-pagination\"></div></div><div class=\"g-group-members-body\"><ul class=\"g-group-members\">");
// iterate members
;(function(){
  var $$obj = members;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var member = $$obj[$index];

buf.push("<li" + (jade.attr("cid", "" + (member.cid) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = member.name()) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = member.get('login')) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.ADMIN)
{
buf.push("<span class=\"dropdown\"><a title=\"Promote user\" data-toggle=\"dropdown\" class=\"g-group-member-promote dropdown-toggle\"><i class=\"icon-up-big\"></i><i class=\"icon-down-dir\"></i></a><ul role=\"menu\" class=\"dropdown-menu pull-right\"><li role=\"presentation\"><a role=\"menuitem\" class=\"g-promote-moderator\"><i class=\"icon-plus\"></i>Promote to moderator</a></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-promote-admin\"><i class=\"icon-plus\"></i>Promote to administrator</a></li></ul></span>");
}
if ( level >= accessType.WRITE)
{
buf.push("<a title=\"Remove user from the group\" class=\"g-group-member-remove\"><i class=\"icon-block\"></i></a>");
}
buf.push("</div></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var member = $$obj[$index];

buf.push("<li" + (jade.attr("cid", "" + (member.cid) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = member.name()) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = member.get('login')) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.ADMIN)
{
buf.push("<span class=\"dropdown\"><a title=\"Promote user\" data-toggle=\"dropdown\" class=\"g-group-member-promote dropdown-toggle\"><i class=\"icon-up-big\"></i><i class=\"icon-down-dir\"></i></a><ul role=\"menu\" class=\"dropdown-menu pull-right\"><li role=\"presentation\"><a role=\"menuitem\" class=\"g-promote-moderator\"><i class=\"icon-plus\"></i>Promote to moderator</a></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-promote-admin\"><i class=\"icon-plus\"></i>Promote to administrator</a></li></ul></span>");
}
if ( level >= accessType.WRITE)
{
buf.push("<a title=\"Remove user from the group\" class=\"g-group-member-remove\"><i class=\"icon-block\"></i></a>");
}
buf.push("</div></li>");
    }

  }
}).call(this);

buf.push("</ul></div>");;return buf.join("");
};

this["jade"]["templates"]["groupModList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),moderators = locals_.moderators,level = locals_.level,accessType = locals_.accessType;
buf.push("<div class=\"g-group-mods-header g-group-list-header\"><i class=\"icon-shield\"></i> Moderators</div><div class=\"g-group-mods-body\"><ul class=\"g-group-mods\">");
// iterate moderators
;(function(){
  var $$obj = moderators;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var userAccess = $$obj[$index];

buf.push("<li" + (jade.attr("userid", "" + (userAccess.id) + "", true, false)) + (jade.attr("username", "" + (userAccess.name) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = userAccess.name) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = userAccess.login) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.ADMIN)
{
buf.push("<a title=\"Demote to member\" class=\"g-group-mod-demote\"><i class=\"icon-down-big\"></i></a>");
}
buf.push("</div></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var userAccess = $$obj[$index];

buf.push("<li" + (jade.attr("userid", "" + (userAccess.id) + "", true, false)) + (jade.attr("username", "" + (userAccess.name) + "", true, false)) + "><a class=\"g-member-name\"><i class=\"icon-user\"></i> " + (jade.escape((jade_interp = userAccess.name) == null ? '' : jade_interp)) + " (" + (jade.escape((jade_interp = userAccess.login) == null ? '' : jade_interp)) + ")</a><div class=\"g-group-member-controls pull-right\">");
if ( level >= accessType.ADMIN)
{
buf.push("<a title=\"Demote to member\" class=\"g-group-mod-demote\"><i class=\"icon-down-big\"></i></a>");
}
buf.push("</div></li>");
    }

  }
}).call(this);

if ( (!moderators.length))
{
buf.push("<div class=\"g-member-list-empty\"><i class=\"icon-info-circled\"></i> There are no moderators in this group.</div>");
}
buf.push("</ul></div>");;return buf.join("");
};

this["jade"]["templates"]["hierarchyBreadcrumb"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),links = locals_.links,current = locals_.current;
var idx = 0
// iterate links
;(function(){
  var $$obj = links;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var obj = $$obj[$index];

buf.push("<li><a" + (jade.attr("g-index", "" + (idx) + "", true, false)) + " class=\"g-breadcrumb-link\">");
if ( (obj.resourceName == 'user'))
{
buf.push("<i class=\"icon-user\"></i>&nbsp;");
}
else if ((obj.resourceName == 'collection'))
{
buf.push("<i class=\"icon-sitemap\"></i>&nbsp;");
}
buf.push("" + (jade.escape((jade_interp = obj.get('name') || obj.name()) == null ? '' : jade_interp)) + "</a></li>");
idx += 1
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var obj = $$obj[$index];

buf.push("<li><a" + (jade.attr("g-index", "" + (idx) + "", true, false)) + " class=\"g-breadcrumb-link\">");
if ( (obj.resourceName == 'user'))
{
buf.push("<i class=\"icon-user\"></i>&nbsp;");
}
else if ((obj.resourceName == 'collection'))
{
buf.push("<i class=\"icon-sitemap\"></i>&nbsp;");
}
buf.push("" + (jade.escape((jade_interp = obj.get('name') || obj.name()) == null ? '' : jade_interp)) + "</a></li>");
idx += 1
    }

  }
}).call(this);

if ( current)
{
buf.push("<li class=\"active\">");
if ( (current.resourceName == 'user'))
{
buf.push("<i class=\"icon-user\"></i>&nbsp;");
}
else if ((current.resourceName == 'collection'))
{
buf.push("<i class=\"icon-sitemap\"></i>&nbsp;");
}
buf.push("" + (jade.escape((jade_interp = current.get('name') || current.name()) == null ? '' : jade_interp)) + "</li>");
}
if ( (idx > 0))
{
buf.push("<div class=\"pull-right\"><a title=\"Go up one level\" class=\"g-hierarchy-level-up\"><i class=\"icon-level-up\"></i></a></div>");
};return buf.join("");
};

this["jade"]["templates"]["hierarchyWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),type = locals_.type,level = locals_.level,AccessType = locals_.AccessType,model = locals_.model;
buf.push("<div class=\"g-hierarchy-widget\"><div class=\"g-hierarchy-breadcrumb-bar\"><ol class=\"breadcrumb\"></ol></div><div class=\"g-hierarchy-actions-header\"><input type=\"checkbox\" data-toggle=\"tooltip\" title=\"Select / Unselect all\" class=\"g-select-all\"/><div class=\"btn-group\"><button data-toggle=\"dropdown\" disabled=\"disabled\" title=\"Checked actions\" class=\"g-checked-actions-button btn btn-sm btn-default dropdown-toggle\"><i class=\"icon-check\"></i><i class=\"icon-down-dir\"></i></button><ul role=\"menu\" class=\"g-checked-actions-menu dropdown-menu\"></ul></div><div class=\"g-folder-header-buttons\">");
if ( (type == 'folder'))
{
if ( (level >= AccessType.WRITE))
{
buf.push("<button title=\"Upload here\" class=\"g-upload-here-button btn btn-sm btn-success\"><i class=\"icon-upload\"></i></button>");
}
if ( (level >= AccessType.ADMIN))
{
buf.push("<button title=\"Access control\" class=\"g-folder-access-button btn btn-sm btn-warning\"><i class=\"icon-lock\"></i></button>");
}
}
buf.push("<div class=\"btn-group\"><button data-toggle=\"dropdown\" title=\"Folder actions\" class=\"g-folder-actions-button btn btn-sm btn-default dropdown-toggle\"><i class=\"icon-folder-open\"></i><i class=\"icon-down-dir\"></i></button><ul role=\"menu\" class=\"g-folder-actions-menu dropdown-menu pull-right\"><li role=\"presentation\" class=\"dropdown-header\"><i class=\"icon-folder-open\"></i> " + (jade.escape((jade_interp = model.get('name') || model.name()) == null ? '' : jade_interp)) + "</li>");
if ( (type == 'folder'))
{
buf.push("<li role=\"presentation\"><a role=\"menuitem\" class=\"g-download-folder\"><i class=\"icon-download\"></i>Download folder</a></li>");
}
if ( (level >= AccessType.WRITE))
{
buf.push("<li role=\"presentation\"><a role=\"menuitem\" class=\"g-create-subfolder\"><i class=\"icon-folder\"></i>Create folder here</a></li>");
if ( (type == 'folder'))
{
buf.push("<li role=\"presentation\"><a role=\"menuitem\" class=\"g-create-item\"><i class=\"icon-doc\"></i>Create item here</a></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-edit-folder\"><i class=\"icon-edit\"></i>Edit folder</a></li>");
}
}
if ( (type =='folder' && level >= AccessType.ADMIN))
{
buf.push("<li role=\"presentation\" class=\"divider\"></li><li role=\"presentation\"><a role=\"menuitem\" class=\"g-delete-folder\"><i class=\"icon-trash\"></i>Delete this folder</a></li>");
}
buf.push("</ul></div></div><div class=\"g-clear-right\"></div></div><div class=\"g-folder-list-container\"></div><div class=\"g-item-list-container\"></div><div class=\"g-empty-parent-message g-info-message-container hide\"><i class=\"icon-info-circled\"></i> This folder is empty.</div></div>");;return buf.join("");
};

this["jade"]["templates"]["itemBreadcrumb"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),parentChain = locals_.parentChain;
buf.push("<ol class=\"breadcrumb\">");
// iterate parentChain
;(function(){
  var $$obj = parentChain;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var parent = $$obj[$index];

buf.push("<li><a" + (jade.attr("data-id", "" + (parent.object._id) + "", true, false)) + (jade.attr("data-type", "" + (parent.type) + "", true, false)) + " class=\"g-item-breadcrumb-link\">");
if ( (parent.type == "user"))
{
buf.push("<i class=\"icon-user\"></i>" + (jade.escape((jade_interp = parent.object.login) == null ? '' : jade_interp)) + "");
}
else if ( (parent.type == "collection"))
{
buf.push("<i class=\"icon-sitemap\"></i>" + (jade.escape((jade_interp = parent.object.name) == null ? '' : jade_interp)) + "");
}
else
{
buf.push("" + (jade.escape((jade_interp = parent.object.name) == null ? '' : jade_interp)) + "");
}
buf.push("</a></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var parent = $$obj[$index];

buf.push("<li><a" + (jade.attr("data-id", "" + (parent.object._id) + "", true, false)) + (jade.attr("data-type", "" + (parent.type) + "", true, false)) + " class=\"g-item-breadcrumb-link\">");
if ( (parent.type == "user"))
{
buf.push("<i class=\"icon-user\"></i>" + (jade.escape((jade_interp = parent.object.login) == null ? '' : jade_interp)) + "");
}
else if ( (parent.type == "collection"))
{
buf.push("<i class=\"icon-sitemap\"></i>" + (jade.escape((jade_interp = parent.object.name) == null ? '' : jade_interp)) + "");
}
else
{
buf.push("" + (jade.escape((jade_interp = parent.object.name) == null ? '' : jade_interp)) + "");
}
buf.push("</a></li>");
    }

  }
}).call(this);

buf.push("<div class=\"pull-right\"><a title=\"Go to parent folder\" class=\"g-hierarchy-level-up\"><i class=\"icon-level-up\"></i></a></div></ol>");;return buf.join("");
};

this["jade"]["templates"]["itemList"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),items = locals_.items,girder = locals_.girder,hasMore = locals_.hasMore;
buf.push("<ul class=\"g-item-list\">");
// iterate items
;(function(){
  var $$obj = items;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var item = $$obj[$index];

buf.push("<li class=\"g-item-list-entry\"><input type=\"checkbox\"" + (jade.attr("g-item-cid", "" + (item.cid) + "", true, false)) + " class=\"g-list-checkbox\"/><a" + (jade.attr("g-item-cid", "" + (item.cid) + "", true, false)) + " class=\"g-item-list-link\"><i class=\"icon-doc-text-inv\"></i>" + (jade.escape((jade_interp = item.get('name')) == null ? '' : jade_interp)) + "</a><div class=\"g-item-size\">" + (jade.escape((jade_interp = girder.formatSize(item.get('size'))) == null ? '' : jade_interp)) + "</div></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var item = $$obj[$index];

buf.push("<li class=\"g-item-list-entry\"><input type=\"checkbox\"" + (jade.attr("g-item-cid", "" + (item.cid) + "", true, false)) + " class=\"g-list-checkbox\"/><a" + (jade.attr("g-item-cid", "" + (item.cid) + "", true, false)) + " class=\"g-item-list-link\"><i class=\"icon-doc-text-inv\"></i>" + (jade.escape((jade_interp = item.get('name')) == null ? '' : jade_interp)) + "</a><div class=\"g-item-size\">" + (jade.escape((jade_interp = girder.formatSize(item.get('size'))) == null ? '' : jade_interp)) + "</div></li>");
    }

  }
}).call(this);

if ( (hasMore))
{
buf.push("<li class=\"g-show-more\"><a class=\"g-show-more-items\"><i class=\"icon-level-down\"></i>Show more items...</a></li>");
}
buf.push("</ul>");;return buf.join("");
};

this["jade"]["templates"]["loadingAnimation"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div id=\"g-loading-animation\"><div id=\"g-loading-block-1\" class=\"g-loading-block\"></div><div id=\"g-loading-block-2\" class=\"g-loading-block\"></div><div id=\"g-loading-block-3\" class=\"g-loading-block\"></div></div>");;return buf.join("");
};

this["jade"]["templates"]["metadataWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),accessLevel = locals_.accessLevel,girder = locals_.girder,item = locals_.item;
jade_mixins["metadatum"] = function(key, value, accessLevel, girder){
var block = (this && this.block), attributes = (this && this.attributes) || {};
if ( (accessLevel >= girder.AccessType.WRITE))
{
buf.push("<button class=\"btn btn-sm btn-default g-item-metadata-edit-button\"><i class=\"icon-pencil\"></i></button>");
}
buf.push("<span class=\"g-item-metadata-key\">" + (jade.escape((jade_interp = key) == null ? '' : jade_interp)) + ":</span><span class=\"g-item-metadata-value\">" + (jade.escape((jade_interp = value) == null ? '' : jade_interp)) + "</span>");
};
if ( (accessLevel >= girder.AccessType.WRITE))
{
buf.push("<button title=\"Add Metadata\" class=\"btn btn-sm btn-primary g-item-metadata-add-button\"><i class=\"icon-plus\"></i></button>");
}
buf.push("<div class=\"g-item-metadata-header\"><i class=\"icon-tags\"></i> Metadata</div><div class=\"g-item-metadata-container\">");
if ( (item.get('meta')))
{
// iterate item.get('meta')
;(function(){
  var $$obj = item.get('meta');
  if ('number' == typeof $$obj.length) {

    for (var key = 0, $$l = $$obj.length; key < $$l; key++) {
      var value = $$obj[key];

buf.push("<div" + (jade.attr("g-key", "" + (key) + "", true, false)) + (jade.attr("g-value", "" + (value) + "", true, false)) + " class=\"g-item-metadata-row\">");
jade_mixins["metadatum"](key, value, accessLevel, girder);
buf.push("</div>");
    }

  } else {
    var $$l = 0;
    for (var key in $$obj) {
      $$l++;      var value = $$obj[key];

buf.push("<div" + (jade.attr("g-key", "" + (key) + "", true, false)) + (jade.attr("g-value", "" + (value) + "", true, false)) + " class=\"g-item-metadata-row\">");
jade_mixins["metadatum"](key, value, accessLevel, girder);
buf.push("</div>");
    }

  }
}).call(this);

}
buf.push("</div>");;return buf.join("");
};

this["jade"]["templates"]["metadatumEditWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),key = locals_.key,value = locals_.value,newDatum = locals_.newDatum;
buf.push("<input type=\"text\"" + (jade.attr("value", key, true, false)) + " placeholder=\"Key\" class=\"input-sm form-control g-item-metadata-key-input\"/><input type=\"text\"" + (jade.attr("value", value, true, false)) + " placeholder=\"Value\" class=\"input-sm form-control g-item-metadata-value-input\"/><button title=\"Cancel\" class=\"btn btn-sm btn-warning g-item-metadata-cancel-button\"><i class=\"icon-cancel\"></i></button><button title=\"Accept\" class=\"btn btn-sm btn-primary g-item-metadata-save-button\"><i class=\"icon-ok\"></i></button>");
if ( !newDatum)
{
buf.push("<button title=\"Delete\" class=\"btn btn-sm btn-danger g-item-metadata-delete-button\"><i class=\"icon-trash\"></i></button>");
};return buf.join("");
};

this["jade"]["templates"]["metadatumView"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),key = locals_.key,value = locals_.value,accessLevel = locals_.accessLevel,girder = locals_.girder;
jade_mixins["metadatum"] = function(key, value, accessLevel, girder){
var block = (this && this.block), attributes = (this && this.attributes) || {};
if ( (accessLevel >= girder.AccessType.WRITE))
{
buf.push("<button class=\"btn btn-sm btn-default g-item-metadata-edit-button\"><i class=\"icon-pencil\"></i></button>");
}
buf.push("<span class=\"g-item-metadata-key\">" + (jade.escape((jade_interp = key) == null ? '' : jade_interp)) + ":</span><span class=\"g-item-metadata-value\">" + (jade.escape((jade_interp = value) == null ? '' : jade_interp)) + "</span>");
};
jade_mixins["metadatum"](key, value, accessLevel, girder);;return buf.join("");
};

this["jade"]["templates"]["metadatumViewMixin"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;








;return buf.join("");
};

this["jade"]["templates"]["newAssetstore"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;

buf.push("<div id=\"g-assetstore-accordion\" class=\"panel-group\"><div class=\"panel panel-default\"><div class=\"panel-heading\"><div class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#g-assetstore-accordion\" href=\"#g-create-fs-tab\"><i class=\"icon-hdd\"></i> Create new<b> Filesystem</b> assetstore</a></div></div><div id=\"g-create-fs-tab\" class=\"panel-collapse collapse\"><div class=\"panel-body\"><p>This type of assetstore will store files in a directory on the\nlocal filesystem, using content-addressed storage to ensure that\ndata is never duplicated on disk. Just specify the root directory\nthat files will be stored under.</p><p>If the specified root directory does not already exist, the server\nwill attempt to create it.</p><form id=\"g-new-fs-form\" role=\"form\"><div class=\"form-group\"><label for=\"g-new-fs-name\" class=\"control-label\">Assetstore name</label><input id=\"g-new-fs-name\" type=\"text\" placeholder=\"Name\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-new-fs-root\" class=\"control-label\">Root directory</label><input id=\"g-new-fs-root\" type=\"text\" placeholder=\"Root directory\" class=\"input-sm form-control\"/></div><p id=\"g-new-fs-error\" class=\"g-validation-failed-message\"></p><input type=\"submit\" value=\"Create\" class=\"g-new-assetstore-submit btn btn-sm btn-primary\"/></form></div></div></div><div class=\"panel panel-default\"><div class=\"panel-heading\"><div class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#g-assetstore-accordion\" href=\"#g-create-gridfs-tab\"><i class=\"icon-leaf\"></i> Create new<b> GridFS</b> assetstore</a></div></div><div id=\"g-create-gridfs-tab\" class=\"panel-collapse collapse\"><div class=\"panel-body\"><p>This type of assetstore uses mongoDB's<a target=\"_blank\" href=\"http://docs.mongodb.org/manual/core/gridfs/\"> GridFS</a> storage engine. The files should be stored in a separate database\n from the rest of the server's information to avoid locking issues.</p><form id=\"g-new-gridfs-form\" role=\"form\"><div class=\"form-group\"><label for=\"g-new-gridfs-name\" class=\"control-label\">Assetstore name</label><input id=\"g-new-gridfs-name\" type=\"text\" placeholder=\"Name\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-new-gridfs-db\" class=\"control-label\">Database name</label><input id=\"g-new-gridfs-db\" type=\"text\" placeholder=\"Database name\" class=\"input-sm form-control\"/></div><p id=\"g-new-gridfs-error\" class=\"g-validation-failed-message\"></p><input type=\"submit\" value=\"Create\" class=\"g-new-assetstore-submit btn btn-sm btn-primary\"/></form></div></div></div><div class=\"panel panel-default\"><div class=\"panel-heading\"><div class=\"panel-title\"><a data-toggle=\"collapse\" data-parent=\"#g-assetstore-accordion\" href=\"#g-create-s3-tab\"><i class=\"icon-upload-cloud\"></i> Create new<b> Amazon S3</b> assetstore</a></div></div><div id=\"g-create-s3-tab\" class=\"panel-collapse collapse\"><div class=\"panel-body\"><p>This type of assetstore keeps files in an<a target=\"_blank\" href=\"http://aws.amazon.com/s3/\"> Amazon S3</a> bucket.</p><form id=\"g-new-s3-form\" role=\"form\"><div class=\"form-group\"><label for=\"g-new-s3-name\" class=\"control-label\">Assetstore name</label><input id=\"g-new-s3-name\" type=\"text\" placeholder=\"Name\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-new-s3-bucket\" class=\"control-label\">S3 bucket name</label><input id=\"g-new-s3-bucket\" type=\"text\" placeholder=\"Bucket\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-new-s3-prefix\" class=\"control-label\">Path prefix (optional)</label><input id=\"g-new-s3-prefix\" type=\"text\" placeholder=\"Prefix\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-new-s3-access-key-id\" class=\"control-label\">Access key ID</label><input id=\"g-new-s3-access-key-id\" type=\"text\" placeholder=\"Access key ID\" class=\"input-sm form-control\"/></div><div class=\"form-group\"><label for=\"g-new-s3-secret\" class=\"control-label\">Secret access key</label><input id=\"g-new-s3-secret\" type=\"text\" placeholder=\"Secret access key\" class=\"input-sm form-control\"/></div><p id=\"g-new-s3-error\" class=\"g-validation-failed-message\"></p><input type=\"submit\" value=\"Create\" class=\"g-new-assetstore-submit btn btn-sm btn-primary\"/></form></div></div></div></div>");;return buf.join("");
};

this["jade"]["templates"]["paginateWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),collection = locals_.collection;
buf.push("<ul class=\"pagination pagination-sm\"><li class=\"g-page-prev disabled\"><a>&laquo; Prev</a></li><li class=\"active\"><a class=\"g-page-number\">Page " + (jade.escape((jade_interp = collection.pageNum() + 1) == null ? '' : jade_interp)) + "</a></li><li class=\"g-page-next disabled\"><a>Next &raquo;</a></li></ul>");;return buf.join("");
};

this["jade"]["templates"]["pluginConfigBreadcrumb"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),pluginName = locals_.pluginName;
buf.push("<div class=\"g-plugin-config-breadcrumbs\"><ol class=\"breadcrumb\"><li><a class=\"g-admin-console-link\"><i class=\"icon-wrench\"></i>Admin console</a></li><li><a class=\"g-plugins-link\"><i class=\"icon-puzzle\"></i>Plugins</a></li><li class=\"active\"><i class=\"icon-cog\"></i>" + (jade.escape((jade_interp = pluginName) == null ? '' : jade_interp)) + "</li></ol></div>");;return buf.join("");
};

this["jade"]["templates"]["searchField"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),placeholder = locals_.placeholder;
buf.push("<input type=\"text\"" + (jade.attr("placeholder", "" + (placeholder) + "", true, false)) + " class=\"g-search-field form-control input-sm\"/><div class=\"g-search-results dropdown\"><ul role=\"menu\" class=\"dropdown-menu\"></ul></div>");;return buf.join("");
};

this["jade"]["templates"]["searchResults"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),results = locals_.results;
// iterate results
;(function(){
  var $$obj = results;
  if ('number' == typeof $$obj.length) {

    for (var $index = 0, $$l = $$obj.length; $index < $$l; $index++) {
      var result = $$obj[$index];

buf.push("<li role=\"presentation\" class=\"g-search-result\"><a" + (jade.attr("resourceid", "" + (result.id) + "", true, false)) + (jade.attr("resourcetype", "" + (result.type) + "", true, false)) + " role=\"menuitem\" tabindex=\"-1\"><i" + (jade.cls(["icon-" + (result.icon) + ""], [true])) + "></i> " + (jade.escape((jade_interp = result.text) == null ? '' : jade_interp)) + "</a></li>");
    }

  } else {
    var $$l = 0;
    for (var $index in $$obj) {
      $$l++;      var result = $$obj[$index];

buf.push("<li role=\"presentation\" class=\"g-search-result\"><a" + (jade.attr("resourceid", "" + (result.id) + "", true, false)) + (jade.attr("resourcetype", "" + (result.type) + "", true, false)) + " role=\"menuitem\" tabindex=\"-1\"><i" + (jade.cls(["icon-" + (result.icon) + ""], [true])) + "></i> " + (jade.escape((jade_interp = result.text) == null ? '' : jade_interp)) + "</a></li>");
    }

  }
}).call(this);

if ( results.length == 0)
{
buf.push("<li role=\"presentation\" class=\"g-no-search-results disabled\"><a role=\"menuitem\" tabindex=\"-1\"><i class=\"icon-block\"></i> No results found</a></li>");
};return buf.join("");
};

this["jade"]["templates"]["uploadWidget"] = function template(locals) {
var buf = [];
var jade_mixins = {};
var jade_interp;
var locals_ = (locals || {}),folder = locals_.folder;
buf.push("<div class=\"modal-dialog\"><div class=\"modal-content\"><form id=\"g-upload-form\" role=\"form\" class=\"modal-form\"><div class=\"modal-header\"><button data-dismiss=\"modal\" aria-hidden=\"true\" type=\"button\" class=\"close\">&times;</button><h4 class=\"modal-title\">Upload Files</h4><div class=\"g-dialog-subtitle\"><i class=\"icon-folder-open\"></i>" + (jade.escape((jade_interp = folder.get('name')) == null ? '' : jade_interp)) + "</div></div><div class=\"modal-body\"><div class=\"g-drop-zone\"><i class=\"icon-docs\"></i> Browse or drop files</div><div class=\"form-group hide\"><input id=\"g-files\" type=\"file\" multiple=\"multiple\"/></div><div class=\"g-current-progress-message\"></div><div class=\"g-progress-current progress progress-striped hide\"><div role=\"progressbar\" class=\"progress-bar progress-bar-info\"></div></div><div class=\"g-overall-progress-message\">No files selected</div><div class=\"g-progress-overall progress progress-striped hide\"><div role=\"progressbar\" class=\"progress-bar progress-bar-info\"></div></div><div class=\"g-upload-error-message g-validation-failed-message\"></div></div><div class=\"modal-footer\"><a data-dismiss=\"modal\" class=\"btn btn-small btn-default\">Close</a><button type=\"submit\" class=\"g-start-upload btn btn-small btn-primary disabled\"><i class=\"icon-upload\"></i> Start Upload</button></div></form></div></div>");;return buf.join("");
};