/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import {attr} from "@mail/model/model_field";

registerPatch({
    name: 'Thread',
    recordMethods: {
        // Method to update the field "attachmentGCMode" of the Thread,
        // used to show or hide the Attachments button and counter
        // on the Chatter Topbar
        async getAttachmentGCMode() {
            var model = this.__values.get("model");
            const resAttachmentGCMode = await this.messaging.rpc(
                {
                    model: "ir.model",
                    method: "get_attachment_gc_mode",
                    args: [model],
                },
                {
                    shadow: true,
                }
            );
            console.log(
                'ASC: The model ' + model + ' has the Attachment GC Mode set to "'
                + resAttachmentGCMode + '".'
            ); 
            this.update({
                attachmentGCMode: resAttachmentGCMode,
            });
        },
    },
    fields: {
        // Field to know if the Thread's Model has
        // the field "attachment_gc_active" set to True or False
        // on its "ir.model" record
        attachmentGCMode: attr(),
    },
});