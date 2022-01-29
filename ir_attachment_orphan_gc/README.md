# M2M and M2O orphan Attachments garbage collector

A garbage collector for orphaned attachments from Many2many and Many2one fields.


---

> English

## PURPOSE OF USE

This is a tool that allows you to mark and/or delete all orphaned attachments after all relationships (with any other model in the environment) have been broken due to records being deleted or fields pointing to the attachment being changed. This problem occurs particularly when using the ``many2many_binary`` widget.

When run as a cron, this garbage collector only marks and/or deletes attachments with the fields ``res_id`` empty and ``res_model`` pointing to a model whose ``_attachment_garbage_collector`` attribute is set to ``True``.


## HOW TO USE IT

You can use this module in two ways:

**Manually**, by opening the model records (``ir.model``) from "Settings >> Technical >> Database Structure >> **Models**" and executing the actions with the appropriate buttons in the "**Attachment GC**" tab. Further explanations on the manual mode are given above the action buttons, in the form view.

**Automatically**, by changing the System Parameter ``ir.autovacuum.attachment.orphan.active`` from ``False`` to ``True`` (strings are case sensitive!). In this way, the method of this garbage collector will be executed just before the main cron "Settings >> Technical >> Automation >> Scheduled Actions >> **Base: Auto-vacuum internal data**". By default, the automatic execution of this garbage collector is disabled. So when installing this module, no actions will be executed automatically.

## CRON SETTINGS

### Activation
As mentioned above, to activate the cron you must change the System Parameter ``ir.autovacuum.attachment.orphan.active`` from ``False`` to ``True``.

In the Python definition of the model you want to monitor, add the ``_attachment_garbage_collector`` attribute and set it to ``True``.

### Marking/deleting attachments
By default, attachments are not deleted but only marked. Changing the System Parameter ``ir.autovacuum.attachment.orphan.unlink`` from ``False`` to ``True`` activates the "**delete mode**". In "delete mode", the first time it detects orphaned attachments it only marks them (field ``maybe_orphan``). The second time this method is executed, if it finds that they are the same records, it deletes them (this is to reduce possible errors when the number of attachments is very large). Those previously marked and no longer orphaned are de-marked.

### Limitation on weekly day
It is also possible to limit the execution of the method to a certain day of the week. By default this function is deactivated and therefore the method will be executed without day limitation. To indicate a specific day, it is possible to change the System parameter ``ir.autovacuum.attachment.orphan.weekday`` from ``False`` to a number between ``0`` and ``6`` according to the encoding of ``datetime.date.weekday()``.


## PRECAUTIONS FOR USE

This tool only handles **Many2any** and **Many2one** fields pointing to records in ``ir.attachment`` and with domain ``[('res_model', '=', _name)]`` where ``_name`` is the internal name of one of the models you wish to keep "clean". In other words, if you activate the function on a model and want ALL orphaned attachments to be detected, you should not point to attachments whose ``res_model`` is not also a module with ``_attachment_garbage_collector`` set to ``True``.

For **Many2many** fields you are supposed to use the ``many2many_binary`` widget which takes care of correctly managing the domain of the displayed attachments and the default values of the created ones (especially ``res_model``).

With the **Many2one** fields, it is possible to add the condition ``[('res_id', '=', id)]`` to the previous domain (which is essential); in this case, it is necessary to inherit the ``mail.thread`` mixin which will take care of the correct management/deletion of attachments with ``[('res_id', '!=', 0)]``.

Some models have a non standard attachment handling and unexpected effects may occur if this garbage collector is activated on them. In this case, simply add the name of the models to be ignored to the ``CG_MODEL_NAME_SAFELIST`` dict to avoid erroneous activation on them. E.g. ``self.env['ir.attachment'].CG_MODEL_NAME_SAFELIST.append('model.to.add')``

## NOTE WELL
When an image is deleted, you can see in the log that two records are deleted instead of one. The other record is the thumbnail, which is handled automatically and hidden by default in the Attachments tree view.

---

> Italiano

## FINALITÀ DI UTILIZZO

Questo è uno strumento che consente di marcare e/o eliminare tutti gli attachment rimasti orfani dopo che tutte le relazioni (con qualunque altro modello nell'environment) sono state interrotte a causa dell'eliminazione dei record oppure per la modifica dei campi che puntavano all'attachment. Questo problema si presenta in particolar modo utilizzando il widget ``many2many_binary``.

Se eseguito come cron, questo garbage collector marca e/o elimina solo gli attachment con i campi ``res_id`` vuoto e ``res_model`` che punta ad un modello il cui attributo ``_attachment_garbage_collector`` è impostato a ``True``.


## COME SI USA

È possibile utilizzare questo modulo in due modi:

**Manualmente**, aprendo i record dei modelli (``ir.model``) da "Impostazioni >> Funzioni tecniche >> Struttura database >> **Modelli**" ed eseguendo le azioni con gli appositi pulsanti nella linguetta "**Attachment GC**". Ulteriori spiegazioni sulla modalità manuale sono indicate sopra i pulsanti di azione, nel form view.

**Automaticamente**, modificando il Parametro di Sistema ``ir.autovacuum.attachment.orphan.active`` da ``False`` a ``True`` (string are case sensitive!). In questo modo, il metodo di questo garbage collector sarà eseguito subito prima del cron principale "Impostazioni >> Funzioni tecniche >> Automazione >> Azioni pianificate >> **Base: pulizia automatica dati interni**". Di default, l'esecuzione automatica di questo garbage collector è disattivata. Dunque al momento dell'installazione di questo modulo nessuna azione verrà eseguita automaticamente.

## CRON SETTINGS

### ATTIVAZIONE
Come detto sopra, per attivare il cron bisogna modificare il Parametro di Sistema ``ir.autovacuum.attachment.orphan.active`` da ``False`` a ``True``.

Nella definizione Python del modello che si desidera monitorare, aggiungere l'attributo ``_attachment_garbage_collector`` ed impostarlo a ``True``.

### MARCATURA/ELIMINAZIONE ATTACHMENT
Di default gli attachment non vengono eliminati ma soltanto marcati. Modificando il Parametro di Sistema ``ir.autovacuum.attachment.orphan.unlink`` da ``False`` a ``True``, si attiva la **"modalità elimina"**. In "modalità elimina", la prima volta che individua degli attachment orfani li marchia solo (campo ``maybe_orphan``). La seconda volta che questo metodo viene eseguito, se trova che sono gli stessi record, li elimina (questo per ridurre possibili errori quando il numero di attachment sarà molto grande). Quelli marchiati precedentemente e che non risultano più orfani, vengono de-marchiati.

### LIMITAZIONE SU GIORNO SETTIMANALE
È inoltre possibile limitare l'esecuzione del metodo solo in un certo giorno della settimana. Di default questa funzione è disattivata e dunque il metodo sarà eseguito senza limitazioni di giorno. Per indicare un giorno specifico, è possibile modificare il Paramentro di Sistema ``ir.autovacuum.attachment.orphan.weekday`` da ``False`` a un numero tra ``0`` e ``6`` in accordo con la codifica di ``datetime.date.weekday()``.


## PRECAUZIONI PER L'USO

Questo strumento gestisce solo campi **Many2any** e **Many2one** che puntano a record in ``ir.attachment`` e con dominio ``[('res_model', '=', _name)]`` dove ``_name`` è il nome interno di uno dei modelli che si desidera mantenere "puliti". In altre parole, se attivi la funzione su un modello e vuoi che vengano individuati TUTTI gli attachment rimesti orfani, non dovresti puntare ad attachment il cui ``res_model`` non sia anche esso un modulo con  ``_attachment_garbage_collector`` impostato a ``True``.

Per i campi **Many2many** si presume di usare il widget ``many2many_binary`` il quale si occupa di gestire correttamente il dominio degli attachment visualizzati e i valori di default di quelli creati (soprattutto ``res_model``).

Con i campi **Many2one** si può aggiungere eventualmente la condizione ``[('res_id', '=', id)`` al dominio precedente (il quale resta imprescindibile); in questo caso è necessario ereditare il ``mail.thread`` mixin il quale si occuperà lui di gestire/eliminare nel modo corretto gli attachment con ``[('res_id', '!=', 0)]``.

Alcuni modelli hanno una gestione degli attachment non standard e potrebbero verificarsi effetti inattesi se questo garbage collector venisse attivato su di essi. In questo caso basta aggiungere il nome dei modelli da ignorare al dict ``CG_MODEL_NAME_SAFELIST`` per evitare un'attivazione erronea su di essi. Es. ``self.env['ir.attachment'].CG_MODEL_NAME_SAFELIST.append('model.to.add')``

## NOTA BENE
Quando un'immagine viene cancellata, si può vedere nel log che vengono cancellati due record anziché uno. L'altro record è il thumbnail, che è gestito automaticamente e viene nascosto di default nella tree view degli Attachemnt.


---


## Examples

System Parameters (ir.config_parameter)

    ir.autovacuum.attachment.orphan.active  :  "True"
    ir.autovacuum.attachment.orphan.unlink  :  "True"
    ir.autovacuum.attachment.orphan.weekday :  "6"


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
            string= 'Many2one attachment 1'
        )
        # MANY2ONE mode 2
        m2o_attachment_1_id = fields.Many2one(
            comodel_name = 'ir.attachment',
            domain = [('res_model', '=', _name)],
            context = {'default_res_model': _name},
            string= 'Many2one attachment 2'
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
                  <field name="message_follower_ids" widget="mail_followers" />
                  <field name="message_ids" widget="mail_thread" />
                </div>
            </form>
        </field>
    </record>
