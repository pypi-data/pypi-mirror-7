(function () {

    /**
     * This view shows a single user's page.
     */
    girder.views.UserView = girder.View.extend({
        initialize: function (settings) {
            this.folderId = settings.folderId || null;
            this.upload = settings.upload || false;
            this.folderAccess = settings.folderAccess || false;
            this.folderEdit = settings.folderEdit || false;

            if (settings.user) {
                this.model = settings.user;

                if (settings.folderId) {
                    this.folder = new girder.models.FolderModel();
                    this.folder.set({
                        _id: settings.folderId
                    }).on('g:fetched', function () {
                        this.render();
                    }, this).on('g:error', function () {
                        this.folder = null;
                        this.render();
                    }, this).fetch();
                }
                else {
                    this.render();
                }
            }
            else if (settings.id) {
                this.model = new girder.models.UserModel();
                this.model.set('_id', settings.id);

                this.model.on('g:fetched', function () {
                    this.render();
                }, this).fetch();
            }

            // This page should be re-rendered if the user logs in or out
            girder.events.on('g:login', this.userChanged, this);
        },

        render: function () {
            this.$el.html(jade.templates.userPage({
                user: this.model
            }));

            this.hierarchyWidget = new girder.views.HierarchyWidget({
                parentModel: this.folder || this.model,
                el: this.$('.g-user-hierarchy-container'),
                upload: this.upload,
                edit: this.folderEdit,
                access: this.folderAccess
            });

            return this;
        },

        userChanged: function () {
            // When the user changes, we should refresh the model to update the
            // accessLevel attribute on the viewed user, then re-render the page.
            this.model.off('g:fetched').on('g:fetched', function () {
                this.render();
            }, this).on('g:error', function () {
                // Current user no longer has read access to this user, so we
                // send them back to the user list page.
                girder.router.navigate('users', {trigger: true});
            }, this).fetch();
        }
    });

    /**
     * Helper function for fetching the user and rendering the view with
     * an arbitrary set of extra parameters.
     */
    var _fetchAndInit = function (userId, params) {
        var user = new girder.models.UserModel();
        user.set({
            _id: userId
        }).on('g:fetched', function () {
            girder.events.trigger('g:navigateTo', girder.views.UserView, _.extend({
                user: user
            }, params || {}));
        }, this).on('g:error', function () {
            girder.events.trigger('g:navigateTo', girder.views.UsersView);
        }, this).fetch();
    };

    girder.router.route('user/:id', 'user', function (userId) {
        _fetchAndInit(userId);
    });

    girder.router.route('user/:id/folder/:id', 'userFolder', function (userId, folderId, params) {
        _fetchAndInit(userId, {
            folderId: folderId,
            upload: params.dialog === 'upload',
            folderAccess: params.dialog === 'folderaccess',
            folderEdit: params.dialog === 'folderedit'
        });
    });

}) ();
