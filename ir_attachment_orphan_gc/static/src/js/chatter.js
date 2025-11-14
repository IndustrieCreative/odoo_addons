import { registerPatch } from '@mail/model/model_core';
import {attr} from "@mail/model/model_field";

registerPatch({
    name: 'Chatter',
    recordMethods: {
        _onThreadIdOrThreadModelChanged() {
            this._super(...arguments);
            if (this.thread) this.thread.getAttachmentGCMode();
        },
    },
    fields: {
        // Related field to re-trigger the rendering of
        // the qweb chatter template after the "attachmentGCMode"
        // has been refreshed on the Thread
        threadModelAttachmentGCMode: attr({
            related: 'thread.attachmentGCMode',
        }),
    },
});
