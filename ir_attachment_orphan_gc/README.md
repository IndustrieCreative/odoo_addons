# M2M and M2O orphan Attachments garbage collector

Garbage collector for orphaned attachments from Many2many and Many2one fields.


## Usage

Deletes all orphaned attachments after the relationship with a given model has been terminated due to either deletion of the record or modification of the field pointing to the attachment.
The garbage collector is only activated in models where there is an attribute "_attachment_garbage_collector" set to True.
WARNING:
It only handles Many2any and Many2one fields pointing to "ir.attachment" and with domain [('res_model', '=', _name)]. In other words, if you activate the function on a module, you should not point to attachments whose "res_model" is not the module itself.
For Many2many fields you are supposed to use the 'many2many_binary' widget which takes care of correctly managing the domain of the displayed attachments and the default values of the created ones (especially 'res_model').
With the many2one fields, you can add the condition [('res_id', '=', id)] to the previous domain (which is unavoidable); in this case, you must inherit the "mail.thread" mixin which will take care of deleting attachments with [('res_id', '!=', 0)].
Some models have a non-standard attachment handling and unexpected effects may occur if this garbage collector is activated on them. In this case, it is sufficient to add the name of the models to be ignored to the CG_MODULE_BLACKLIST dict to avoid erroneous activation on them.
The first time it detects orphan attachments it only marks them. The second time this method is executed, if it finds that they are the same, it deletes them. Marked attachments that are no longer orphaned are de-marked.


## Example

Model (Python file)

    class ExampleModel(models.Model):
        _name = 'example.model'
        _inherit = ['mail.thread']

        _attachment_garbage_collector = True

        # ...

        # MANY2MANY
        m2m_attachment_ids = fields.Many2many(
            comodel_name = 'ir.attachment',
            relation = 'example_model_ir_attachment_rel',
            column1 = 'example_id',
            column2 = 'attachment_id',
            string = 'Many2many attachments'
        )

        # MANY2ONE mode 1
        m2o_attachment_1_id = fields.Many2one(
            comodel_name = 'ir.attachment',
            string= 'Many2one attachment'
        )
        # MANY2ONE mode 2
        m2o_attachment_1_id = fields.Many2one(
            comodel_name = 'ir.attachment',
            domain = [('res_model', '=', _name)],
            context = {'default_res_model': _name},
            string= 'Many2one attachment'
        )

        # ONE2MANY
        # This type is not managed by this garbage collector but here you can show
        # the same available records for the "m2o_attachment_1_id" field.
        # It is the same as the attachment button in the chatter of "mail.thread".
        # Useful just for testing purposes.
        o2m_attachment_ids = fields.One2many(
            comodel_name = 'ir.attachment',
            inverse_name = 'res_id',
            domain = [('res_model', '=', _name)],
            context = {'default_res_model': _name},
            string = 'One2many attachments'
        )


View (XML file)

    <record id="example_model_view_form" model="ir.ui.view">
        <field name="name">example.model.view.form</field>
        <field name="model">example.model</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <!-- MANY2MANY -->
                    <field name="m2m_attachment_ids"
                           widget="many2many_binary"
                    />  

                    <!-- MANY2ONE mode 1 -->
                    <field name="m2o_attachment_1_id"
                           context="{
                             'default_res_model': 'example.model',
                             'default_res_id': id,
                           }"
                           domain="[
                             ('res_model', '=', 'example.model'),
                             ('res_id', '=', id),
                           ]"
                    />

                    <!-- MANY2ONE mode 2 -->
                    <field name="m2o_attachment_2_id" />

                    <!-- ONE2MANY -->
                    <field name="o2m_attachment_ids" />

                </sheet>
                <div class="oe_chatter">
                  <field name="message_follower_ids" widget="mail_followers"/>
                  <field name="message_ids" widget="mail_thread"/>
                </div>
            </form>
        </field>
    </record>
