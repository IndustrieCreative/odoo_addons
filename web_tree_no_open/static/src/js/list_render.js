/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";

patch(ListRenderer.prototype, "web_tree_no_open_list_renderer", {
    async onCellClicked(record, column, ev) {
        const $target = $(ev.target);
        if ($target.closest('.tree_no_open').length > 0) {
            console.log("Click on a tree_no_open element");
            ev.stopPropagation();
            ev.preventDefault();
        } else {
            this._super.apply(this, arguments);
        }  
    }
});
