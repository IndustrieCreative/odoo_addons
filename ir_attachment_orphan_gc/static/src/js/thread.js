odoo.define("ir_attachment_orphan_gc/static/src/js/thread.js", function (require) {
    "use strict";

    const {
        registerFieldPatchModel,
        registerInstancePatchModel
    } = require("@mail/model/model_core");
    const {attr} = require("@mail/model/model_field");

    registerInstancePatchModel(
        "mail.thread",
        "ir_attachment_orphan_gc/static/src/js/thread.js",
        {
            // Method to update the field "attachmentGCMode" of the Thread,
            // used to show or hide the Attachments button and counter
            // on the Chatter Topbar
            async getAttachmentGCMode() {
                var model = this.__values.model;
                const resAttachmentGCMode = await this.async(() =>
                    this.env.services.rpc(
                        {
                            model: "ir.model",
                            method: "get_attachment_gc_mode",
                            args: [model],
                        },
                        {
                            shadow: true,
                        }
                    )
                );
                console.log(
                    'ASC: The model ' + model + ' has the Attachment GC Mode set to "'
                    + resAttachmentGCMode + '".'
                ); 
                this.update({
                    attachmentGCMode: resAttachmentGCMode,
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
            attachmentGCMode: attr(),
        }
    );
});