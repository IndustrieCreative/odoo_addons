odoo.define("ir_attachment_orphan_gc/static/src/js/thread.js", function (require) {
    "use strict";

    const {
        registerFieldPatchModel,
        registerInstancePatchModel
    } = require("mail/static/src/model/model_core.js");
    const {attr} = require("mail/static/src/model/model_field.js");

    registerInstancePatchModel(
        "mail.thread",
        "ir_attachment_orphan_gc/static/src/js/thread.js",
        {
            // Method to update the field "attachmentGCActive" of the Thread,
            // used to show or hide the Attachments button and counter
            // on the Chatter Topbar
            async getAttachmentGCActive() {
                var model = this.__values.model;
                const attachmentGCActive = await this.async(() =>
                    this.env.services.rpc(
                        {
                            model: "ir.model",
                            method: "get_attachment_gc_active",
                            args: [model],
                        },
                        {
                            shadow: true,
                        }
                    )
                );
                console.log(attachmentGCActive);
                let attachmentGCActiveRes = attachmentGCActive;
                this.update({
                    attachmentGCActive: attachmentGCActiveRes,
                });
            },
        }
    );

    registerFieldPatchModel(
        "mail.thread",
        "ir_attachment_orphan_gc/static/src/js/thread.js",
        {
            // Field to know if the Thread's Model has
            // the field "attachment_gc_active" set to True or False
            // on its "ir.model" record
            attachmentGCActive: attr(),
        }
    );
});