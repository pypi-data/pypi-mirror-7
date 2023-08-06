/**
 * This widget is for creating new assetstores. The parent view is responsible
 * for checking admin privileges before rendering this widget.
 */
girder.views.NewAssetstoreWidget = girder.View.extend({
    events: {
        'submit #g-new-fs-form': function (e) {
            this.createAssetstore(e, this.$('#g-new-fs-error'), {
                type: girder.AssetstoreType.FILESYSTEM,
                name: this.$('#g-new-fs-name').val(),
                root: this.$('#g-new-fs-root').val()
            });
        },

        'submit #g-new-gridfs-form': function (e) {
            this.createAssetstore(e, this.$('#g-new-gridfs-error'), {
                type: girder.AssetstoreType.GRIDFS,
                name: this.$('#g-new-gridfs-name').val(),
                db: this.$('#g-new-gridfs-db').val()
            });
        },

        'submit #g-new-s3-form': function (e) {
            this.createAssetstore(e, this.$('#g-new-s3-error'), {
                type: girder.AssetstoreType.S3,
                name: this.$('#g-new-s3-name').val()
            });
        }
    },

    render: function () {
        this.$el.html(jade.templates.newAssetstore());
        return this;
    },

    /**
     * Call this to make the request to the server to create the assetstore.
     * @param e The submit event from the form.
     * @param container The element to write the error message into.
     * @param data The form data to POST to /assetstore
     */
    createAssetstore: function (e, container, data) {
        e.preventDefault();
        this.$('.g-new-assetstore-submit').addClass('disabled');
        container.empty();

        var assetstore = new girder.models.AssetstoreModel();
        assetstore.set(data);
        assetstore.on('g:saved', function () {
            this.$('.g-new-assetstore-submit').removeClass('disabled');
            this.trigger('g:created', assetstore);
        }, this).on('g:error', function (err) {
            this.$('.g-new-assetstore-submit').removeClass('disabled');
            container.text(err.responseJSON.message);
        }, this).save();
    }
});
