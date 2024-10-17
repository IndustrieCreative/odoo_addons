odoo.define("ir_attachment_orphan_gc/static/src/js/chatter.js", function (require) {
    "use strict";

    const {
        registerFieldPatchModel,
        registerInstancePatchModel
    } = require("@mail/model/model_core");
    const {attr} = require("@mail/model/model_field");

    registerInstancePatchModel(
        "mail.chatter",
        "ir_attachment_orphan_gc/static/src/js/chatter.js",
        {
            // Overrides to refresh the field "attachmentGCMode"
            // of the Thread
            // async refresh() {
            //     this._super(...arguments);
            //     this.thread.getAttachmentGCMode();
            // },
            _onThreadIdOrThreadModelChanged() {
                this._super(...arguments);
                this.thread.getAttachmentGCMode();
            }
        }
    );

    registerFieldPatchModel(
        "mail.chatter",
        "ir_attachment_orphan_gc/static/src/js/chatter.js",
        {
            // Related field to re-trigger the rendering of
            // the qweb chatter template after the "attachmentGCMode"
            // has been refreshed on the Thread
            threadModelAttachmentGCMode: attr({
                related: 'thread.attachmentGCMode',
            }),
        }
    );

});