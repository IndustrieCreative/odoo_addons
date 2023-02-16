# M2M and M2O orphan Attachments garbage collector

A garbage collector for orphaned attachments from Many2many and Many2one fields.

---

## PURPOSE OF USE

This is a tool that allows you to mark and/or delete all orphaned attachments after all
relationships (with any other model in the environment) have been broken due to records
being deleted or fields pointing to the attachment being changed. This problem occurs
particularly when using the ``many2many_binary`` widget.

When run as a cron, this garbage collector only marks and/or deletes orphan attachments
with the fields ``res_field`` empty, ``res_model`` pointing to a model whose
``_attachment_garbage_collector`` attribute is set to ``True`` and ``create_date`` and
``write_date`` older than one day so as to exclude files uploaded via the Chatter,
via "many2many_binary" or reports created on-the-fly.


## HOW TO USE IT

You can use this module in two ways:

**Manually**, by opening the model records (``ir.model``) from
"Settings >> Technical >> Database Structure >> **Models**" and executing the actions with
the appropriate buttons in the "**Attachment GC**" tab. Further explanations on the manual
mode are given above the action buttons, in the form view.

**Automatically**, by changing the System Parameter
``ir.autovacuum.attachment.orphan.active`` from ``False`` to ``True`` (strings are case
sensitive!). In this way, the method of this garbage collector will be executed just before
the main cron "Settings >> Technical >> Automation >> Scheduled Actions >> **Base: Auto-vacuum internal data**".
By default, the automatic execution of this garbage collector is disabled. So when
installing this module, no actions will be executed automatically.


## CRON SETTINGS

### Activation of the automatic mode
As mentioned above, to activate the cron you must change the System Parameter
``ir.autovacuum.attachment.orphan.active`` from ``False`` to ``True``.

In the Python definition of the model you want to monitor for orphans, add the
``_attachment_garbage_collector`` attribute and set it to ``True``.

### Marking/deleting attachments
By default, attachments are not deleted but only marked. Changing the System Parameter
``ir.autovacuum.attachment.orphan.unlink`` from ``False`` to ``True`` activates the
"**delete mode**". In "delete mode", the first time it detects orphaned attachments it
only marks them (field ``maybe_orphan``). The second time this method is executed, if it
finds that they are the same records, it deletes them (this is to reduce possible errors
when the number of attachments is very large). Those previously marked and no longer
orphaned are de-marked.

### Limitation on weekly day
It is also possible to limit the execution of the method to a certain day of the week.
By default this function is deactivated and therefore the method will be triggered evry time
the main Cron **Base: Auto-vacuum internal data** is execuded, without any day limitation.
To indicate a specific day, it is possible to change the System parameter
``ir.autovacuum.attachment.orphan.weekday`` from ``False`` to a number between ``0`` and
``6`` according to the encoding of ``datetime.date.weekday()``.


## PRECAUTIONS FOR USE

This tool only handles **Many2any** and **Many2one** fields pointing to records in
``ir.attachment`` and with domain ``[('res_model', '=', _name)]`` where ``_name`` is the
technincal name of one of the models you wish to keep "clean". In other words, if you
activate the function on a model and want ALL orphaned attachments to be detected, <ins>you
should not point to attachments whose ``res_model`` is not also a module with
``_attachment_garbage_collector`` set to ``True``</ins>.

For **Many2many** fields you are supposed to use the ``many2many_binary`` widget which
takes care of correctly managing the domain of the displayed attachments and the default
values of the created ones (especially ``res_model``).

With the **Many2one** fields, it is possible to add (&amp;) the condition
``('res_id', '=', id)`` to the previous domain (which is essential).

Some models have a non standard attachment handling and so, unexpected effects may occur if
this garbage collector is activated on them. In this case, simply add the name of the
models to be ignored to the ``CG_MODEL_NAME_SAFELIST`` dict to avoid erroneous activation
on them. E.g. ``self.env['ir.attachment'].CG_MODEL_NAME_SAFELIST.append('model.to.add')``


## NOTE WELL

All models starting with 'ir.' are already in the CG_MODEL_NAME_SAFELIST, as their
attachments are system ones and are handled automatically by Odoo (at least I hope so).

When an image is deleted, you can see in the log that two records are deleted instead of
one. The other record is the thumbnail, which is handled automatically and hidden by
default in the Attachments tree view.

If you are not in Superuser Mode, you cannot display all the attachments in "ir.attachment".
For this reason, if you need to debug, I suggest to login as Superuser (from the Debug menu
in the systray when you are in Developer Mode).

By default, Attachments with ``res_field`` set to value are not displayed and are not managed
by this garbage collector. So see all all the Attachments in tree view, you can use the preset
filter "SHOW ALL".

---

## Examples

System Parameters (ir.config_parameter)

    ir.autovacuum.attachment.orphan.active  :  "True"
    ir.autovacuum.attachment.orphan.unlink  :  "True"
    ir.autovacuum.attachment.orphan.weekday :  "6"

In order to be correctly managed by this garbage collector, the fields that are using
Attachments should be implemented in the following way:

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
        m2o_attachment_2_id = fields.Many2one(
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

---

> NOTE: The following section is intended as literature on the topic of attachment.

## ATTACHMENTS ON CHATTER TOPBAR

On Odoo 14.0 (maybe from 13), the ``many2many_binary`` and the chatter have a new way of handling
attachments. For this reason, the Attachment button and counter are disabled on the Chatter's
topbar for all the Models whose ``_attachment_garbage_collector`` attribute is set to ``True``.
Users cannot upload Attachments directly via Chatter because in this way they seem to be orphan
because no real field is pointing to them (except for ``message_main_attachment_id``, read more below).


### SE IL MODELLO IMPLEMENTA IL MIXIN ``MAIL.THREAD``.
Viene aggiunto al modello il campo ``message_main_attachment_id`` con la funzione di mostrare
l'attachment più "rilevante". Se solo un attachment punta al nostro record, allora sarà quello.
Altrimenti la priorità viene stabilita tramite il ``mimetype`` del file col seguente ordine:
per mimetype: ``pdf`` --> ``image`` --> other mimetypes.
Se ci sono più file del medesimo mimetype (es. pdf), allora prende automaticamente il primo.
Dato che il modello ``ir.attachment`` è ordinato per ``'id desc'``, allora presimo prenderà
l'ultimo file caricato (almeno... non mi sembra che vengano riordinati in altro modo).
Per modificare il criterio di selezione del campo, è possibile fare l'override del metodo
``_message_set_main_attachment_id()``.
Per impostare invece il campo ``my_attachment_field_ids`` del nostro record è possibile eseguire
la suddetta funzione passando gli ``id`` in formato ``command 4`` (link).

```
    # Un singolo attachment
    record._message_set_main_attachment_id([(4, my_attachment.id)])
    
    # Oppure una serie di attachment
    record._message_set_main_attachment_id([(4, id) for id in record.my_attachment_field_ids.ids])
```

Nel chatter vengono automaticamente computati dal client javascript tutti gli attachment che
puntano al record corrente tramite la combinazione di ``res_model`` e ``res_id``.

Il campo ``message_main_attachment_id`` è di default escluso dalle relazioni rilevanti;
quindi se l'unica relazione di un Attachment è tramite questo campo, l'Attachment verrà comunque
considerato orfano e di conseguenza eliminabile.

### POSSIBILI MODI DI CREAZIONE (UPLOAD) DEGLI ATTACHMENT IN ``ir.attachment``

1. In un campo HTML, tramite l'apposita funzione del "web_editor".
   Crea un attachment con ``res_model`` e ``res_id`` che puntano al nostro record.

2. Caricando un file in un campo di tipo ``Binary`` definito con l'argomento ``attachment=True``
   Crea un attachment con ``res_model``, ``res_id`` e ``res_field`` che puntano al nostro record
   e in particolare al campo con cui abbiamo caricato il file.

3. Caricando un file in un campo di tipo Many2one o, più frequentemente, Many2many tramite il
   widget ``many2many_binary``.
   Crea un attachment con ``res_model`` e ``res_id`` che puntano al nostro record.
   In caso di campo Many2many viene anche creato un record nella tabella di relazione che collega
   il nostro campo con ``ir.attachment``.

Se abbiamo installato il modulo ``mail``:

4. Creando un nuovo messaggio tramite l'IM box o in un "Mail channel" (Discuss) e allegando un
   file.
   La modalità è la stessa del punto 3.
   Crea un attachment con ``res_model=='mail.channel'`` e ``res_id`` che punta al canale.
   Inviare messaggi in un Channel ``mail.channel`` è esattamente come inviare messaggi nel chatter
   di un qualunque record di un modello che eredita il mixin ``mail.thread``.
   In altre parole, ciascun canale è un record di ``mail.channel`` e ciascun messaggio è come
   un messaggio nel suo chatter.
   Dato che gli attachment di ciascun messaggio vengono caricati nel campo Many2many
   ``attachment_ids``, come nel punto 3 viene creato anche un nuovo record nella tabella di
   relazione, che in questo caso è ``message_attachment_rel``.
   NB: in questo caso, se è il primo messaggio del canale, viene anche creato l'attachment
   ``image_128`` automaticamente con ``res_model=='mail.channel'``, ``res_id`` che punta al nostro
   messaggio e ``res_field`` che punta al campo ``image_128``.

Se il modello implementa il mixin "mail.thread":

5. Caricando un file tramite l'apposita funzione nel chatter (icona allegato).
   Crea un attachment con ``res_model`` e ``res_id`` che puntano al nostro record.

6. Creando un nuovo messaggio nel chatter di un modello e allegando un file.
   Crea un attachment con ``res_model`` e ``res_id`` che puntano al nostro record.
   Nel messaggio invece, come al punto 4, ci sarà il campo ``attachment_ids`` che punterà al
   nostro attachment questo vuol dire che è stato creato anche un nuovo record nella tabella di
   relazione che, anche in questo caso, in questo caso è ``message_attachment_rel``.


### COME ODOO TIENE PULITO IL FILESTORE

Per ciascun file del filestore, controlla se esiste un record in ``ir.attachment`` che ha
l'hash SHA1 corrispondente al proprio. Se non ne viene trovato nessuno, vuol dire che
il file non è più utilizzato da nessun attachment e quindi viene eliminato.
Questa operazione viene eseguita dal cron "Base: pulizia automatica dati interni".
