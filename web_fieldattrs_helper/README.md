# Web Field Attrs Helper (FAH)

This module provides an abstract model that offers a new way to handle the ``attrs``
attribute of fields and elements in XML views.
Any key of the ``attrs`` attribute (``invisible``, ``readonly``, ``required`` and
``column_invisible``) of any XML element present on the views can be handled
directly by Python code, thus having direct access to the Odoo environment at runtime.

It is also possible to manage the access operations to records (CRUD) in the same way.

With this module you can:
- Avoid writing domains in the ``attrs`` attribute of the fields.
- Avoid writing *record rules*.

This module is not intended as a replacement for the traditional methods, but as an
alternative that can be used only in appropriate situations.

Use cases:
- Wizards.
- Very dynamic and complex form views.
- Quick development.

In any circumstance, for models with a high number of records the use of this module is
discouraged because of the reduction of the performances that it could cause, if compared
with the tools we have available by default.

NOTE: Performance depends largely on how you implement the function that computes the
attributes and/or permissions.

ATTENTION! The prefix ``web_`` in the name of the module would suggest a module that acts
only on the on the client. However, it can also modify the behavior of the ORM even
outside the view. This module therefore is between a web module and a server module. I
chose to use the prefix ``web_`` because if you don't use the ``web`` module, this module
becomes useless, since the ORM already offers everything a developer needs.


## Table of contents

- [Why this module?](#why-this-module)
- [Current situation](#current-situation)
  - [Using *record rules*](#using-record-rules)
  - [Using direct attributes and context reading](#using-direct-attributes-and-context-reading)
  - [Traditional use of ``attrs``](#traditional-use-of-attrs)
  - [Using ``attrs`` in combination with onchange or computed field](#using-attrs-in-combination-with-onchange-or-computed-field)
  - [Using ``states`` argument](#using-states-argument)
  - [Using ``states`` argument in combination with onchange method or computed field](#using-states-argument-in-combination-with-onchange-method-or-computed-field)
  - [Hack proposed by this module](#hack-proposed-by-this-module)
  - [Recap](#recap)
- [Module overview](#module-overview)
- [Abstract model](#abstract-model)
- [Triggers](#triggers)
- [Targets: fields, nodes](#targets-fields-nodes)
- [Modifications to the model and its views](#modifications-to-the-model-and-its-views)
  - [Helper fields added](#helper-fields-added)
  - [Injection of the ``attrs``](#injection-of-attrs)
- [Helper Tags](#helper-tags)
- [FahAttrRegistry *(attr_reg)*](#fahattrregistry-attr_reg)
- [super() and Method Resolution Order (MRO)](#super-e-method-resolution-order-mro)
  - [Wrong implementation](#wrong-implementation)
  - [Correct implementation](#correct-implementation)
- [Writing the "compute" method of the helper fields](#writing-the-compute-method-of-the-helper-fields)
- [Checking for rules compliance on targets feature](#checking-for-rules-compliance-on-targets-feature)
- [Declaration of the fields "force save" and "force null"](#declaration-of-force-save-and-force-null-fields)
- [Special message ``_FAH_FORCE_COMMAND``](#special-message-_fah_force_command)
- [Alternative to *record rules*](#alternative-to-record-rules)
  - [Helper fields for ops](#helper-fields-for-ops)
- [Default settings and customizations](#default-settings-and-customizations)
- [Group-and-bypass-function](#group-and-bypass-function)
- [Backend Debugging Tools](#backend-debugging-tools)
- [The eval_mode argument of the compute method](#the-eval_mode-argument-of-the-compute-method)
- [Appendix](#appendix)
  - [Contraindications](#contraindications)
  - [Ethical and economic issues](#ethical-and-economic-issues)
  - [To the Odoo Community](#to-the-odoo-community)
  - [To-Do](#to-do)
  - [Decisions to make and ideas for future developments](#decisions-to-make-and-ideas-for-future-developments)
  - [Tests to implement](#tests-to-implement)


## Why this module?

This module is intended for Odoo developers.

Odoo allows you to define the possibilities of interaction the user has with the view in
various ways. The main tools are the keys of the ``attrs`` attribute of XML fields,
defined with *domains*.

The domain is a static tool, extremely elegant and solid but when the fields are numerous,
unfortunately the rules to implement can become complex and the view architecture becomes
more difficult to read.

Moreover, the domain can only "use" information present on the view and, more precisely,
only the fields present on the view. Unfortunately, sometimes we need to make a decision
based on data that is only accessible through the Odoo environment.

To deal with these situations we usually implement an ad-hoc solution for that specific
specific circumstance, often using hybrid solutions between domain, computed fields,
onchange methods, record rules, and ORM method overrides.
This means that the logic that governs views is "scattered" here and there in different
ways, depending on the circumstances. In short, there is no standard procedure for when
you need to go outside the standard!

This module proposes a standard method to deal with these extreme situations,
if you really can't do otherwise.


## Current situation

Before seeing the proposed solution, it may be useful to summarize the methods
traditionally used to regulate and describe the interaction that the user can have with
records and their fields.

This section serves to contextualize the purpose and scope of this module and
provide a theoretical foundation on view manipulation techniques.
If you don't need that, you can skip directly to the 
["Module Overview"](#module-overview) section.

These first sections are hidden by default because they are only useful for propedeutic
purposes. Click to expand:
<details>
<summary>Hide/show propedeutic sections.</summary>

### Using *record rules*

*Record rules* allow you to inhibit ``create``, ``write``, ``read``, and ``unlink`` on
the basis of the value of one or more fields and optionally, based on the groups to which
the user belongs.

They have no effect on the interactivity of the view elements, but may limit precisely the
opening, saving, creation, and deletion of the entire record.

```xml

    <record model="ir.rule" id="rule_archived_task_no_access">
      <field name="name">No access to archived tasks</field>
      <field name="model_id" ref="model_project_task"/>
      <field name="domain_force">[('active', '=', True)]</field>
      <field name="perm_read" eval="1"/>
      <field name="perm_write" eval="1"/>
      <field name="perm_create" eval="1"/>
      <field name="perm_unlink" eval="1"/>
    </record>
```

With this rule we inhibit to all users any operation on records whose field ``active`` is
not equal to ``True``. So all archived records will no longer be accessible. Perhaps, a
bit excessive... maybe we need reading!

> NOTE: The fields ``perm_read``, ``perm_write``, ``perm_create`` and ``perm_unlink`` are
> set to ``True`` by default. The *record rules* (global) then block any operation by
> default. We have to specify which operations are allowed.

If we want to allow reading, but not the others, we can do this:

```xml

    <record model="ir.rule" id="rule_archived_task_readonly">
      <field name="name">Archived tasks are readonly</field>
      <field name="model_id" ref="model_project_task"/>
      <field name="domain_force">[('active', '=', True)]</field>
      <field name="perm_read" eval="0"/>
      <field name="perm_write" eval="1"/>
      <field name="perm_create" eval="1"/>
      <field name="perm_unlink" eval="1"/>
    </record>
```

With this rule, if the ``active`` field is not equal to ``True``, the ``read`` operation
on the record will not be inhibited, and all other operations (``write``, ``create``, and
``unlink``) will be inhibited. This is for all users.

These first type of rules are called "**global record rules**" because they do not have
the ``groups`` field set and therefore they are applied independently from the groups the
user belongs to.

> :scream: ATTENTION: I remind you that the nomenclature of permissions (``perm_read``,
> ``perm_write``, ``perm_create``, ``perm_unlink``) has a completely different meaning
> than "ir.model.access".
> - In "ir.model.access" True/False have the meaning of granting or not granting access
>   to a certain CRUD operation. 
> - In "ir.rule" True/False indicate for which CRUD operation the rule must be applied.

But if we want to allow users of the group ``my_module.group_admin`` to perform
all operations, instead of the previous rule, we must write this:

```xml
    
    <record model="ir.rule" id="rule_archived_task_readonly">
      <field name="name">Archived tasks are readonly</field>
      <field name="model_id" ref="model_project_task"/>
      <field name="domain_force">[('active', '=', True)]</field>
      <field name="groups" eval="[(4, ref('base.group_user'))]"/>
      <field name="perm_read" eval="0"/>
      <field name="perm_write" eval="1"/>
      <field name="perm_create" eval="1"/>
      <field name="perm_unlink" eval="1"/>
    </record>

    <record model="ir.rule" id="rule_archived_task_admin_full_access">
      <field name="name">Admin have full perms on tasks</field>
      <field name="model_id" ref="model_project_task"/>
      <field name="domain_force">[(1,'=',1)]</field>
      <field name="groups" eval="[(4,ref('my_module.group_admin'))]"/>
      <field name="perm_read" eval="1"/>
      <field name="perm_write" eval="1"/>
      <field name="perm_create" eval="1"/>
      <field name="perm_unlink" eval="1"/>
    </record>
```

With these two rules, if the ``active`` field is not equal to ``True`` and the user
belongs to the group ``base.group_user``, all operations except ``read`` will be
inhibited. If the user belongs to the group ``my_module.group_admin``, no operations will
be inhibited.

This second type of rules are called "**group record rules**" because they have the field
``groups`` set and therefore are applied only to users who belong to the groups
specified.

> :scream: WARNING: If you didn't understand this, it's normal. Although
> *group record rules* are a very powerful, secure, and effective tool, they combine with
> each other in ways complex, and their syntax is extremely counterintuitive and seemingly
> absurd. For this reason, it is difficult to explain how they work in detail, and this is
> not the place to do it.

> :warning: let's imagine to set a *record rule* that allows only ``reading``
> on a given model. If we open a record of that model via a relational field
> in a form (of another model) when we are in edit mode, the form that will be opened
> (in window/popup) will also be editable. Even if there is the *record rule*! But just
> because there is the *record rule*, if the user edits the form-popup, only when he goes
> to save the main record he will be warned that he could not edit the linked record.

One good thing is that we can use dot.notation fields in domains, thus being able to
retrieve data from linked models via Many2one fields.

Limitations of this method:

- Even if a record does not have write permission it is still possible, under certain
  circumstances, to open a form in edit mode.The record will not be able to be modified,
  but this is only discovered later (and having wasted time!).
- When you have to interact between several rules it can be difficult to imagine the final
  behavior, so writing and debugging rules can become extremely complex.
- No access to the Odoo environment.


### Using "direct" attributes and context reading

When Odoo returns a view to the client, the ``invisible``, ``readonly`` and ``required``
attributes of the XML elements are subjected to a ``safe_eval()`` in whose scope the
``context`` is also present. In this way, in an action view, we can decide to insert a key
in order to be read by an attribute. be read by an attribute.
If the action view is defined in Python rather than XML, we can have access to Odoo's
environment at runtime.

```xml

    <field name="field_name1" readonly="context.get('readonly_field_name1', 0)"/>
```

Or, in the field definition in the model:


```python

    field_name1 = fields.Integer(readonly="context.get('readonly_field_name1', 0)")
```

The action that passes the key into the context:

```python

    def action_open_view(self):
        self.ensure_one()
        readonly_field = 0
        if self.env... == 'xyz': # <-- Access to the environment
            readonly_field = 1
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'my.model',
            'res_id': self.id,
            'view_mode': 'form',
            'context': {'readonly_field_name1': readonly_field},
        }
```

In this example, at the opening of the form, if the key ``readonly_field_name1`` is
present in the ``context`` and its value is ``1``, the field ``field_name1`` will become
readonly.

By the line ``if self.env...== 'xyz':`` is meant a decision made on the basis of a datum
in the environment.

Limitations of this method:
- Once the view is loaded, it is no longer possible to trigger context re-evaluation with
  the ``context.get()`` present as the attribute value, even if you modify the context.


### Traditional use of ``attrs``

Normally Odoo expects that the ``attrs`` are statically defined by domains written
directly in the XML view. For example:

```xml

    <field name="field_name1" attrs="{'readonly': [('field_name2', '=', True)]}"/>
```

The example above means that when field ``field_name2`` takes value ``True``, the field
``field_name1`` must become ``readonly``.

The "attrs" are: *invisible*, *readonly*, *required* and, for embedded trees, also.
*column_invisible*.

In this "classic" way, all the logic for managing XML elements is written directly in the
view and, because of the way the JavaScript client is currently implemented, there is no
way to access directly to the Odoo environment to use (in domains) data not present in the
view.

Limitations of this method:
- No access to the Odoo environment; domains can only point to fields present in the view.


### Using ``attrs`` in combination with onchange or computed field

A currently available solution to exploit information from the environment in order to
manage ``attrs`` inside the vew is to write their domains in such a way that they point to
computed fields or fields that can be modified by onchange methods.
At this point, to manage the attribute of an XML element, it is just a matter of changing
the values of the fields to which the domain of this "attr" points on the view.
Referring to the previous example, it could be done like this:

```python

    field_name2 = fields.Boolean(
        compute = '_compute_field_name2',
        store = False
    )

    field_name3 = fields.Char()

    @api.depends('field_name3')
    def _compute_field_name2()
        for r in self:
            if r.field_name3 == 'abc':
                if self.env... == 'xyz': # <-- Access to the environment
                    r.field_name2 = True
```

By the line ``if self.env... == 'xyz':`` is meant that we can vary the value of the field
``field_name2`` by conditions that can evaluate any data in the Odoo environment;
consequently also the attribute ``readonly`` of the field ``field_name1`` will depend on
this condition.
Whether you choose to manually modify the value of the field ``field_name2`` or to compute
it automatically, you must in any case manually add the domain in the ``attrs`` of the XML
``field`` tag, as shown above in the previous section.

If the purpose of this computed field is only to activate the ``readonly`` ``attrs`` of
one or more specific fields, we can call it a "helper field".

If you wanted to handle all attributes with this method, there would be some drawbacks:
- You have to create a computed field for each attribute and for each field you want to
  manage.

This means that to manage the 3 attributes, for example for 10 fields, you would have to
create 30 additional computed fields and write as many domains.


### Using ``states`` argument

In order to define the ``attrs`` of a field from the server side, Odoo makes also
available the ``states`` argument in the definition of the fields of the model.
For example:

```python

    state = fields.Selection(
        selection = [('value1', 'Value 1'), ('value2', 'Value 2')]
    )
    
    field_name1 = fields.Char(
        states = {'value1': [('readonly', False)]}
    )
```

The example above means that when the field ``state`` takes on the value ```value1``,
the field ``field_name1`` must become ``readonly``.
With the ``states`` argument it is possible to define a logic for the behavior of each
field in the view directly from the Python code, but the conditions depend exclusively on
the value of the field named ``state``.
In this way it is **as if** Odoo would insert the following ``attrs`` automatically:

```xml

    <field name="field_name1" attrs="{'readonly': [('state', '=', 'value1')]}"/>
```

The job Odoo does for us is to automatically write the domains for the ``attrs`` so that
they point to the ``state`` field; thus we no longer have to manually enter domains into
``attrs`, as in the first example.

However, using the ``states`` argument has a number of limitations:
- There is no way to use another field except ``state`` to define conditions.
- The field name ``state`` must be "sacrificed" to this function.
- It is not possible to implement ``states`` freely if we extend a model that already uses
  the ``state`` field for other purposes.
- Only XML elements of type ``field`` can be handled.
- No access to the Odoo environment, everything depends on the value of the ``state``
  field.


### Using ``states`` argument in combination with onchange method or computed field

It is also possible to combine the two solutions just exposed by computing the value of
the field ``states`` and consequently the ``attrs`` of the fields.
Referring to our example, it is possible to use a method decorated with ``@api.onchange``
or to make the field ``state`` computed to dynamically modify the value, and consequently
also the ``readonly`` attribute of the field ``field_name1`` (on the view).

```python

    state = fields.Selection(
        selection = [('value1', 'Value 1'), ('value2', 'Value 2')],
        compute = '_compute_state',
    )
    
    field_name1 = fields.Char(
        states = {'value1': [('readonly', False)]}
    )

    @api.depends('field_name3')
    def _compute_state()
        for r in self:
            if r.field_name3 == 'abc':
                if self.env... == 'xyz': # <-- Accesso all'environment
                    r.state = 'value1'
```

In this way you can define the behavior of the fields via Python (server side) and save
the effort of writing the domains of the ``attrs`` on the views. But all the limitations
of the previous section still remain.

</details>


### Hack proposed by this module

Let's take the ``readonly`` attribute as an example.
We create a ``Char`` field in our model. For example:
``fah_readonly_targets``.

Go to the definition of the ``field`` tag in the XML view and write this domain in the
``attrs``:

```xml

    <field name="field_name1" attrs="{'readonly': [('fah_readonly_targets', 'like', 'field_name1')]}"/>
```
This means that when inside the field ``fah_readonly_targets`` the string
``'field_name1'`` appears, the field ``field_name1`` must become ``readonly``.
To avoid false positives, however, it is best to delimit the field name with a character
that is not allowed in field names, for example ``@``.
The previous example would become:

```xml

    <field name="field_name1" attrs="{'readonly': [('fah_readonly_targets', 'like', '@field_name1@')]}"/>
```

At this point, if inside the field ``fah_readonly_targets`` we write ``'@field_name1@'``,
the field ``field_name1`` will become ``readonly``.

Now, if we set the field ``fah_readonly_targets`` as computed, we can decide server-side
when the string ``@field_name1@`` should appear.
For example:

```python

    fah_readonly_targets = fields.Char(
        compute = '_fah_compute_helper_fields',
        store = True,
    ))

    @api.depends('field_name2')
    def _fah_compute_helper_fields(self):
        for r in self:
            if r.field_name2 == True:
                r.fah_readonly_targets == '@field_name1@'
```

In this way, when the field ``field_name2`` becomes ``True``, in the field
``fah_readonly_targets`` will appear the string ``'@field_name1@'`` and the field
``field_name1`` will become readonly.

With the same principle, writing other field names inside the field
``fah_readonly_targets`` and adding their domains in the ``attrs`` of those fields, it
becomes possible to manage the ``readonly`` attribute of multiple fields using only one
"helper" field.

> In other words, inside ``fah_readonly_targets`` there is the list of all the fields
> which must become readonly.

This method can also be applied to the other attributes ``invisible``, ``required`` and
``column_invisible``.


### Recap

Before proceeding, it is good to establish a terminological convention to be adopted from
here on. Taking the names of the fields from the examples seen so far, we have:
- ``field_name1``: **TARGET** field
- ``field_name2``: **TRIGGER** field
- ``fah_readonly_targets``: **HELPER** field

Now, the main problems are:
- Create a "helper" field for each attribute we want to manage.
- Create a method to add and remove target field names from helper fields.
- Insert all the domains in the attrs of the target fields we want to manage.

This module offers an out-of-the-box solution to handle all of this automatically and
gives the developer the possibility to write just one method that determines which fields
should have which attribute.


## Module Overview

This module consists of:
- Abstract model ``web.fieldattrs.helper``.
- Decorator ``@api.fah_depends``.
- Class ``FahAttrRegistry``.
- Extension of method ``odoo.models.Model._fields_view_get()``.
- Extension of ``ir.model`` and ``ir.ui.view`` models.

To activate the features available in this module and start using them on a new or
existing model the following actions are required:
1. Inherit the abstract model ``web.fieldattrs.helper``.
2. Declare the trigger fields.
3. Declare the target elements (nodes).
4. Write the method ``_fah_compute_helper_fields()``.

You can then perform the following actions:
- Declare fields for which ignore attr *readonly* or *invisible*.
- Declare the fields for which to ignore the *required* attr.
- Modify the default settings to customize the behavior of the helper.

Now let's take a closer look at what the module does and what the developer must do in
order to use its features.


## Abstract model

Let's inherit the abstract model ``web.fieldattrs.helper``:

```python

from odoo import models

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['web.fieldattrs.helper']
```

We then continue with the declaration of the trigger fields.


## Triggers

Triggers are the fields that, when modified, must trigger the re-computation of the attrs.

> NOTE: Currently the triggers can be only fields of the model. Fields in dot.notation
> are not allowed.

Triggers must also be declared in the model definition, in the appropriate slot:

```python

    _fah_trigger_fields = { # set
        'field_name3',         # str
        'field_name4'
    }
```


## Targets: fields, nodes

We said that ***targets*** are the XML elements whose attrs can be managed.  
They can be of two types:

- FIELD: the ``<field>`` tags.
- NODE: all other XML elements (e.g. ``<group>``, ``<button>``, ``<div>`` etc.).

For **fields** it is possible to handle all attrs:
- *readonly*
- *required*
- *invisible* (+ *column_invisible* in case of embedded/inline tree)

For **node** only the visibility attributes make sense:
- invisible (+ *column_invisible* in the case of embedded/inline tree).

For domains to be injected into the ``attrs`` of targets, these targets must be declared
in the model definition.

Since Odoo allows to create "embedded/inline views" within the from, it is possible to
declare elements in these sub-views. All embedded views are associated with a relational
field of type One2many or Many2many. The connected model is called *comodel*.

For this reason there are 4 "slots" for the declaration of targets:
- Fields of the model: ``_fah_model_target_fields``.
- Nodes of the model: ``_fah_model_target_nodes``.
- Embedded fields (comodels): ``_fah_embedded_target_fields``
- Embedded nodes (comodels): ``_fah_embedded_target_nodes``

<ins>**Model fields and optional tags**</ins>.
Attributes that can be managed: ``readonly``, ``required``, ``invisible``. 
```python

    _fah_model_target_fields = {  # set
        'field_a',                   # str
        ('field_b'),                 # tuple(str)
        ('field_c', '#DEMOTAG#')     # tuple(str, str)
    }
```

<ins>**Comodel fields linked to the model in dot.notation and optional tag.**</ins>.  
Attributes that can be managed: ``readonly``, ``required``, ``invisible``,
``column_invisible``.
```python

    _fah_embedded_target_fields = {          # set
        'item1_ids.item1_field',                # str
        ('item2_ids.item2_field'),              # tuple(str)
        ('item3_ids.item3_field', '#DEMOTAG#')  # tuple(str, str)
    }
```

> NOTE: For fields the tags are optional.

<ins>**Generic elements in model views**</ins>.  
Set of tuples, each with 4 elements: (tag, attribute, value, tag).  
Attributes that can be managed: ``invisible``.
```python

    _fah_model_target_nodes = {                     # set
        ('group', 'name', 'group-1', '#DEMOTAG#')       # tuple(str,str,str,str)
        ('button', 'name', 'button-1', '#DEMOTAG#')
        ('div', 'id', 'section-1', '#FOO#')
    }
```

> It means that when the ``#DEMOTAG#`` tag appears in the ``fah_invisible_targets`` helper
> field, the elements ``<group name="group-1">`` and ``<button name="button-1">`` should
> become invisible.  

> Tested with tags: ``group``, ``div``, ``button``. For ``field`` tags use the appropriate
> slots ``_fah_model_target_fields`` or ``_fah_embedded_target_fields``.  
> Tested with attributes: ``id``, ``name``.

<ins>**Generic elements in embedded views (currently only embedded tree).**</ins>.  
Set of tuples, each with 5 elements:(rel_field, HTML tag, attribute, value, helper tag).  
Attributes that can be managed: ``invisible``, ``column_invisible``.
```python

    _fah_embedded_target_nodes = {                                     # set
        ('item_ids', 'button', 'name', 'action_demo', '#HIDE-BUTTON#')    # tuple(str,str,str,str,str)
    }
```

> NOTE: Tags are mandatory for nodes. This is because, unlike the fields that are easily
> identifiable by their name, the other XML elements must be defined by the combination of
> *tag*, *attribute* and *value*, which complicates the writing and makes it difficult to
> understand the function of the element that you want to declare and then manage. Tags
> add a bit of semantics, which never hurts.


## Modifications to the model and its views

At this point of the setup, if we start Odoo and update the module of our model, we can
see that a few things have already changed.


### Helper fields added
By default, in a model that inherits the abstract model ``web.fieldattrs.helper``, 4
computed Char fields are automatically created, the "helper fields":

- ``fah_readonly_targets``
- ``fah_required_targets``
- ``fah_invisible_targets``
- ``fah_column_invisible_targets``

> NOTE: The prefix ``fah_`` is customizable in each model, to avoid possible collisions.

All these helper fields will be automatically injected into all views of the model.
The helper fields are by default *invisible* and *readonly*.
To make them visible you can activate the debug mode as explained in the section
[Default settings and customizations](#default-settings-and-customizations).


### Injection of ``attrs``
In the targets, which are XML elements whose attributes we want to manage, will be
automatically injected an attribute ``attrs`` whose keys (readonly, required etc...) will
have a domain that will point to the relative helper field. 

```xml

    <field name="field_name1"
           attrs="{
               'readonly': [('fah_readonly_targets', 'like', '@field_name1@')],
               'required': [('fah_required_targets', 'like', '@field_name1@')],
               'invisible': [('fah_invisible_targets', 'like', '@field_name1@')]
           }"/>
```

For fields in an embedded tree, we also have the ``column_invisible`` attribute.
For example, if our field is displayed via a One2many field that we call ``item_ids``,
we might have:

```xml

    <field name="item_ids">
      <tree>
        <field name="field_name1"
               attrs="{
                   'readonly': [('parent.fah_readonly_targets', 'like', '@item_ids.field_name1@')],
                   'required': [('parent.fah_required_targets', 'like', '@item_ids.field_name1@')],
                   'invisible': [('parent.fah_invisible_targets', 'like', '@item_ids.field_name1@')],
                   'column_invisible': [('parent.fah_column_invisible_targets', 'like', '@item_ids.field_name1@')]
               }"/>
      </tree>
    </field>

```

If also the comodel passing through ``item_ids`` implements this helper, then domains to
the comodel helper fields will be injected as well.

```xml

    <field name="item_ids">
      <tree>
        <field name="field_name1"
               attrs="{
                   'readonly': [
                     '|',
                        ('fah_readonly_targets', 'like', '@field_name1@'),
                        ('parent.fah_readonly_targets', 'like', '@item_ids.field_name1@')
                   ],
                   'required': [
                     '|',
                        ('fah_required_targets', 'like', '@field_name1@'),
                        ('parent.fah_required_targets', 'like', '@item_ids.field_name1@')
                   ],
                   'invisible': [
                     '|',
                        ('fah_invisible_targets', 'like', '@field_name1@'),
                        ('parent.fah_invisible_targets', 'like', '@item_ids.field_name1@')
                   ],
                   'column_invisible': [('parent.fah_column_invisible_targets', 'like', '@item_ids.field_name1@')]
               }"/>
      </tree>
    </field>

```

As we said, all this is handled automatically.

> :warning: NOTE: If a target field in the view already contains ``attrs``, an error
> message will be raised by default. To bypass the block and override the attrs, just set
> the ``_FAH_XML_INJECT_SAFE`` attribute of the model to ``False``. Currently it is not
> possible to merge with domains of existing attrs.

> NOTE: Currently all injected domains are composed of operands concatenated by ``'|'``
> (or) operators.

From Odoo v13 onwards there is a mechanism that automatically injects a domain into the
relational fields when the feature that controls the company-cosistency is active. No
tests have been done yet as the module has just been migrated from version 12.0. 

> :warning: No tests have been done yet using the ``_check_company_auto`` feature.

Let's now look at the concept of helper tag and how to use it in the declaration of XML
elements.


## Helper Tags

When we are going to set an attribute, we must indicate what our target is. If the target
is a field, we can just indicate the name of the field directly. But in the case of a node,
it is easier and more intuitive to assign a tag/keyword to the element and call this when
we want to manage the element's attribute.

This approach offers an additional advantage: by assigning the same tag to multiple
elements, when we go to act on an attribute by recalling that tag, all the tagged elements
will assume that attribute.  

Considering this advantage, it is possible to tag the fields as well, using the same
approach.

> Let's imagine we have a series of fields that must all be hidden when the same condition
> occurs. If we tag all fields with the same tag, for example "#FOO#", the command
> ``attr_reg.set(['#FOO#'], 'invisible', True, r)`` will hide all the fields at the same
> time.

Finally, an element can have multiple tags. To do this, simply repeat the declaration of
the element and indicate the new tag.

```python

    _fah_model_target_fields = {    # set
        ('field_c', '#DEMOTAG#')       # tuple(str,str)
        ('field_c', '#FOO#')
        ('field_c', '#BAR#')
    }
```

Each declaration can only contain one tag.

By default tags must be delimited by the ``#`` character to avoid homonyms with fields.
It is possible to customize this feature at the template level, to do so see section
[Default settings and customizations](#default-settings-and-customizations).


## FahAttrRegistry *(attr_reg)*

To keep track of all the attributes that each target field must take on each record, a
registry is available. We can call it the Attribute Registry, or more conveniently
``attr_reg``. It is the abstract model and the decorator ``@api.fah_depends()`` that take
care of creating the register, so the developer can just set the attributes.

> NOTE: You can create a new ``attr_reg`` from the ``FahAttrRegistry`` class, located in
> ``odoo.addons.web_fieldattrs_helper.attr_registry.FahAttrRegistry``.

Each instance of FahAttrRegistry has ``set()`` and ``get()`` methods for writing and read
on the registry.

```python

    FahAttrRegistry.set(target_names, attr, value, record, msg=False)
    """ Set a boolean value to an attr on specific target names of a record.
    :param list target_names:  list of strings containing the names of the targets (fields or tags)
    :param str attr:           the attribute; available values are the attrs ('readonly', 'required', 'invisible', 'column_invisible')
                               or the ops ('no_read', 'no_write', 'no_create', 'no_unlink')
    :param bool value:         the value to be set
    :param record:             the record (must be a record of the model that created the registry object)
    :param str msg:            optional message for the user, if this rule is supposed to raise an error during write, create or unlink.
    """ 

    FahAttrRegistry.get(target_name, attr, record)
    """ Get the current value of an attr of a specific target name and record.
    :param str target_name:  the name of a field or tag
    :param str attr:         the attribute; available values are the attrs ('readonly', 'required', 'invisible', 'column_invisible')
                             or the ops ('no_read', 'no_write', 'no_create', 'no_unlink')
    :param record:           the record (must be a record of the model that created the registry object)
    :return:                 dict containing the keys 'val' (bool) and 'msg' (str)
    :rtype:                  dict
    """
```

That is, an instance of FahAttrRegistry serves as a container for passing informations
between methods in the MRO chain via the ``super()`` command.


## super() e Method Resolution Order (MRO)

To set the attrs of a field when a trigger is modified, you have to override the
``_fah_compute_helper_fields()`` method (which is present in the abstract model).

Normally it is enough to put a single ``super()`` in a certain position to decide exactly
in which sequence the code within the various methods of the MRO chain should be executed.
In particular, for the methods that write in the computed fields it is expected that each 
overridden method writes directly into the fields what it needs. In doing so, it becomes
necessary to insert the ``super()`` at the beginning of the method, before the writes, so
that the "new" code is executed after the "old" one. If we did it in the opposite way, the
old code could overwrite the new data.

During the override of the ``_fah_compute_helper_fields()`` method, however, we are
expected to interact only with the FahAttrRegistry object, and do not write anything to
the helper fields. It is the last method in the MRO, the one in the abstract model, that
writes to the helper fields.

However, this way of implementing the methods of the computed fields makes things a bit
tricky.


### Wrong implementation

If we could predict with certainty that our model would never be extended, we could do the
override in this way:
```python

    @api.fah_depends(*_fah_trigger_fields)
    def _fah_compute_helper_fields(self, attr_reg, eval_mode=False):
        
        for r in self:
            ...        #  <-- The "rules" must be put here

        super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode)
```

We would write our rules and then with ``super()`` execute the method in the abstract
model, which would write to the helper fields.

But since Odoo and Python are based on extensibility, we are forced to write our module
with the expectation that it can be extended.


### Correct implementation

Our case is a bit more complicated and the current solution is to use a double ``super()``
call, one at the beginning and one at the end.

```python

    @api.fah_depends(*_fah_trigger_fields)
    def _fah_compute_helper_fields(self, attr_reg, eval_mode=False, override=False):
        
        if override != 'finish': # -> in [False, 'compute']
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='compute')
            for r in self:
                ...        #  <-- The "rules" must be put here

        if override != 'compute': # -> in [False, 'finish']
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='finish')
```

Basically we need to perform the attrs computations backwards compared to the MRO, passing
the argument "attr_reg" from one method to another and finally returning to the last method
to write into the fields.

The following diagram represents how the call stack should proceed from when the
``Field._compute_value()`` method starts the first method in the MRO, until the last one
method updates the computed helper fields.

![This is an image](./documentation/dia1.png)

To avoid writing to the computed fields the first time the MRO chain is ascended, we use
the argument ``override`` which, if it assumes the value ``'compute'``, stops the writing
on the last method which then terminates the execution. At this point, the attributes are
computed in reverse order, until the first method is reached which, after having computed
the last last attributes, can send the write signal with a new ``super()``, this time with
the attribute ``override`` set to ``'finish'``.  Each method will now simply pass the
register to the next method. When the last method is reached again, it can finally proceed
to write the computed fields.

> :interrobang: To avoid having to repeat these two conditions and the related ``super()``
> every time you override, we could move this part of code inside the decorator
> ``@api.fah_depends`` but, apparently, calling super() inside a decorator is quite
> complicated. For now, I haven't delved into this problem yet. Starting from
> [this discussion](https://mail.python.org/pipermail/python-ideas/2017-January/044498.html),
> I found these ideas:
> - Using the "*descriptor protocol*": https://gist.github.com/1st1/ebee935256c7cc35c38cc3f73f00461d
> - https://github.com/refi64/mirasu


## Writing the "compute" method of the helper fields

Having explained what the structure of the ``_fah_compute_helper_fields()`` method should
look like, let's see how to set the field attributes.

An example of using the method in overrides is as follows:
```python

    @api.fah_depends(*_fah_trigger_fields)
    def _fah_compute_helper_fields(self, attr_reg, eval_mode=False, override=False):

        if override != 'finish': # -> in [False, 'compute']
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='compute')
            for r in self:
                
                # For 'readonly', 'required', 'invisible'
                # (model fields)
                if ... :
                    attr_reg.set(['field_name'], 'readonly', True, r,
                        msg='You cannot edit the field because...')
                
                # For 'column_invisible', 'readonly', 'required', 'invisible' 
                # (comodel fields in embedded trees)
                if ... :
                    attr_reg.set(['items_ids.item_field'], 'column_invisible', True, r)
                
                # For 'invisible' TAG
                if ... :
                    attr_reg.set(['#DEMOTAG#'], 'invisible', True, r)

        if override != 'compute': # -> in [False, 'finish']
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='finish')
```

> :warning: CONSIDER THAT:
> - New rules overwrite old ones.
> - The message (optional) can be indicated only if the value is ``True``.
> - The last message for a target/attribute overwrites the previous one.

``@api.fah_depends()`` is a decorator written ad-hoc. It incorporates the normal
``@api.depends()`` inside it, but it also performs other useful operations, such as create
a new attr_reg if it is not passed as an argument.

The parameters, all of which are optional, are:
```python
    FieldAttrsHelper._fah_compute_helper_fields(attr_reg=False, eval_mode=False, override=False)
        """
        :param FahAttrRegistry attr_reg:  Attributes registry. If False, a new empty one will be created.
        :param bool eval_mode:            Whether it is necessary to write on the fields or not.
        :param str override:              Command to handle calls between methods in the MRO chain.
                                          The first external call to the overrided method on real models
                                          must ignore this argument (override==False). It should be for
                                          internal use only. 
        :return:  False
        """
```

Normally the developer should not need to call this method directly. It is used by
``Field._compute_value()`` when the recomputation of the fields is triggered; and by the
``write()``, ``create()``, ``read()`` and ``unlink()`` methods when they need to verify
that attrs and ops are complied with. In this second case, the fields are not written and
only the attr_reg is filled in.


## Checking for rules compliance on targets feature

By default, this module checks during ``write()`` and ``create()`` that the information
entered by the user complies with the ``attrs`` of the fields. If you alter a field on a
record that is expected to be *readonly* and/or *invisible*, an error will be raised
during the write.

Checks performed:
- ``readonly`` and ``invisible``: The value of the field cannot be modified.
- ``required``: The field cannot be left "empty".

Each model controls its own fields. It is not possible to check fields on embedded views,
which belong to their comodel. If you need to perform these checks but the comodel does
not implement this helper, you have to use the traditional ``@api.constrains()`` or
override ``create()`` and ``write()`` on the comodel.

You can disable this feature at the model level, to do so please refer to the
[Default settings and customizations](#default-settings-and-customizations) section.

However, if you prefer to force the writing of a given field, regardless of its attribute
in the views, you can declare the field in the "force save" and "force null" slots. See
next section.

If the check options during ``write()`` and/or ``create()`` are disabled, the client will
be the only one to validate the fields and check that the ``attrs`` are respected.

> NOTE: The check on the attr ``required`` verifies that the value of the field is not
> empty/zero. What is considered "null value" varies depending on the type of field. The
> case of fields of type ``Integer``, ``Float`` and ``Monetary``, which are considered
> null either if their value is ``0`` (zero) or ``False``, should be carefully considered.
> We also have to consider that the widgets on the views can modify the value of the
> fields before sending it to the server.

## Declaration of "force save" and "force null" fields

If the control functions are active during ``write()`` and/or ``create()``, it may be
necessary to ignore these controls only for some specific field.

To do this, there are two specific slots: one to allow editing even if the attribute is
``readonly`` and/or ``invisible``, and another to allow the "empty" value if the attribute
is ``required``.

Fields that can be modified regardless of whether they are ``readonly`` and/or
``invisible`` on views must be declared here:

```python

    _fah_force_save_fields = { # set
        'field_name2',            # str
    }
```

Fields that can be left "empty" regardless of whether they are ``required`` on views must
be declared here:
```python

    _fah_force_null_fields = { # set
        'field_name20',            # str
    }
```

On these fields only the client will be able to validate the content and check that the
``attrs`` are respected.

Since only fields belonging to the model can be checked, here fields in dot.notation are
not allowed.


## Special message ``_FAH_FORCE_COMMAND``

If the control functions are active during ``write()`` and/or ``create()``, you may need
to ignore these controls only in some specific situation, and only on some specific field.

If we put a field in the ``_fah_force_save_fields`` and/or ``_fah_force_null_fields``
slots, the checks for that field would always be ignored. This is not what we want. So if
we need that checks should not be done for a specific rule, when we set the attribute with
the ``FahAttrRegistry.set()`` command, we can send a special ``'no-check'`` message.

To do this, just enter as argument ``msg`` the keyword indicated in the attribute/parameter
``_FAH_FORCE_COMMAND`` of the model, which by default is ``'no-check'``.


```python

  attr_reg.set(['field_name'], 'readonly', True, r,
      msg='no-check')
```

This example means that if the field ``field_name`` is modified, even if it is readonly on
the view, it will be allowed to be written.

Also in this case only the client will validate the content and check that the ``attrs``
are respected.


## Alternative to *record rules*

What we have seen so far re-implements the use of the ``attrs`` of the fields on views.
Attrs control the interaction the user can have with the fields.

The *record rules* instead control the interaction the user can have with the whole record
(as we saw in the propedeutic sections).

So I thought to add some extra attributes in order to be able to write rules that can
inhibit the ``read()``, ``write()``, ``create()`` ad ``unlink()`` methods in the same way
as with attrs.

To distinguish them from "attrs", we call these attributes "**OPS**".

The **ops** are:
- ``no_read``: Prevents the record from being read.
- ``no_write``: Prevents the record from being updated.
- ``no_create``: Prevents the creation of a new record.
- ``no_unlink``: Prevents the deletion of the record.


Unlike *attrs* which refer to the **fields** of a given record, *ops* refer to the
**record** itself.

```python

  attr_reg.set(0, 'no_unlink', True, r,
      msg='You cannot delete the record because...')
```

> NOTE: If the command passed with the second argument is an ops, first argument becomes
> irrelevant and will be ignored; so we can write a simple "zero".

As for *record rules*, the rules do not apply if the operation is performed in
"superuser-mode" (check done with ``is_superuser()``).


### Helper fields for ops

It is not expected that ops have direct consequences on view interactivity, so you
shouldn't need dedicated helper fields for them. The status of ops is present in the
``FahAttrRegistry`` (attr_reg) and is read directly from there during checks.

But it could be useful to show something on the view when the record takes a certain ops,
for example a symbol or a warning.

Currently, the ``_FAH_CREATE_OPS_FIELDS`` option (by default set to ``False``) allows you
to create 4 boolean helper fields to represent the status of each ops plus another 4 char
fields that contain the relative message to be shown to the user (attribute ``msg`` of
the method ``FahAttrRegistry.set()``).

The ops helper fields can therefore also serve to manage the ``attrs`` of XML elements.
For example: if the record cannot be deleted, we want a closed padlock symbol to appear
at the top right of a form. Currently we can do it "manually", by putting our icon among
the targets and remembering to make it visible or not each time we set ``no_unlink``.

Or we want all target fields to be ``readonly`` if ``no_write`` is ``True``.

> :bulb: For each ops' helper field (boolean) we could create a unique id to be assigned to
> the XML elements we want to be made visible when that ops becomes True on that record.
> In this way we can automatically inject the domain that points to the ops helper field
> into these elements.


## Group and Bypass Function

Since it is possible to declare a field as both a trigger and a target, it becomes
theoretically possible to create a recursion that locks a field and no longer allows it to
be modified. In this case, it is possible to disable the helper functionality for a
specific record only, at runtime, without needing to restart the server.

Users who belong to the ``web_fieldattrs_helper.fah_global_bypass_group``, when they
activate the "developer mode", will find at the bottom of each form, the field
``fah_bypass``. By setting the value to ``True``, attribute computation will be disabled
on that record.

This allows you to "unlock" an unexpected situation, in case of an emergency.

You can then restore the normal operation of that record by resetting the same field to
``False``.

:warning: ATTENTION: This is to be considered only as an emergency solution, because these
situations, normally, MUST NOT happen. When this happens, it is usually a programming
error, which must be corrected as soon as possible to avoid the problem from happening
again.


## Default settings and customizations

The abstract model ``web.fieldattrs.helper`` contains a number of attributes which can be
overridden in order to customize the behavior of the helper on a specific model.

All attributes are documented in detail as comments in the code.
For practicality, I report here the most relevant ones, with the relative default values.

---
List of attrs to be managed by the helper, as a list.
- ``_FAH_ATTRS = ['readonly', 'required', 'invisible', 'column_invisible']``
---
List of ops to be managed by the helper, in list form.
- ``_FAH_OPS = ['no_read', 'no_write', 'no_create', 'no_unlink']``

> NOTE: If the op is present in the list, it will be checked during the corresponding
> method.

---
Prefix of helper fields, customizable to avoid name collisions.
- ``_FAH_FIELDS_PREFIX = 'fah_'``
---
Target field name delimiter, to avoid false positives in the "like" (e.g. "name" and
"surname")
- ``_FAH_ATTRS_FIELDS_DELIMITER = '@'``
---
Tag name delimiter
- ``_FAH_ATTRS_TAG_DELIMITER = '#'``

> Warning the *fields delimiter* and the *tag delimiter* must be different.
> Use only ASCII symbols, not alphanumeric characters and not uderscore (_).
> Ex. ``@ # $`` (tested)

---
Additional groups (besides ``web_fieldattrs_helper.fah_global_bypass_group``) which can
activate bypass on a single record.
- ``_FAH_BYPASS_GROUPS_ADD = []``
---
Enables/disables the injection of helper fields and "attrs" into target fields.
- ``_FAH_XML_INJECT = True``
---
Blocks if in the views there are already values in the ``attrs`` of the fields into which
the new "attrs" pointing to the helpers fields are to be injected. If ``False``,
overwrites the pre-existing "attrs" in the rendered view.
- ``_FAH_XML_INJECT_SAFE = True``
---
Creates non-stored fields showing the status of the "ops" and their related messages.
For now, useful for experiments on new features.
- ``_FAH_CREATE_OPS_FIELDS = False``
---
Keyword to be used as ``msg`` argument in ``FahAttrRegistry.set()`` to ignore
checks at ``write()`` and ``create()`` for that specific rule.
- ``_FAH_FORCE_COMMAND = 'no-check'``
---
Checks during ``create()``
- ``_FAH_READONLY_CREATE_CHECK = True``
- ``_FAH_INVISIBLE_CREATE_CHECK = True``
- ``_FAH_REQUIRED_CREATE_CHECK = True``
---
Checks during ``write()``
- ``_FAH_READONLY_WRITE_CHECK = True``
- ``_FAH_REQUIRED_WRITE_CHECK = True``
- ``_FAH_INVISIBLE_WRITE_CHECK = True``
---
Check during ``unlink()``
- ``_FAH_NO_UNLINK_CHECK = True``
---
Activates the "debug mode" on the model. The helper fields are displayed on the view and
in the log there are additional debug level information.
- ``_FAH_DEBUG_MODE = False``


## Backend debugging tools

Since this helper can only be active on specific models, it can be difficult after a while
to remember which models use the helper and especially which settings are active on each
one.

Activating the "developer mode" and going to "Edit view: Form" or "Edit view: Tree"
through the "developer menu" we can see at a glance if the helper is active. We can do the
same by going to Settings > Technical > User Interface > Views and then opening the view.

If the helper is active there will be a blinking icon and a new page in the form notebook
of ``ir.ui.view``. This page contains two sub-pages where you can see the view arch after
injections and the state of implementation on the model.

On ``ir.model`` (Settings > Technical > Database Structure > Models) there is the
possibility to filter for the field "FAH Actve?" in order to see the list of all models
that implement this helper.

When you open a model, if it implements this helper, you will find the field "FAH Active?"
checked and in the notebook page "Field Attrs Helper (FAH)" there is the field "FAH Status
on this model" that shows (as in ir.ui.view) the status of implementation on the model.


## The ``eval_mode`` argument of the compute method

The ``eval_mode`` argument of the ``_fah_compute_helper_fields()`` method is used to make
the ``attr_reg`` compiled but then prevent writing to the fields.

It is currently used by the control functions during ``write()`` ``create()`` and
``unlink()`` to get a compiled ``attr_reg`` so that checks can proceed.

Since the function called is the same as the one used to compute the helper fields, to
effectively avoid writing to them, with the parameter ``eval_mode=True`` we communicate
that the method must stop after compiling the register.


## Appendix

### Contraindications

This module offers more freedom than the traditional way of implementing view logic but
more freedom, as we know, implies more responsibility.

I believe that if Odoo S.A. and the community have never implemented a solution like this,
there must have been a good reason. First of all Odoo claims to follow a *three-tier*
architecture. This really means that the view logic (*presentation tier*) is separated by
choice from the actual business logic (*logic tier*).

This new proposed solution tends to move part of the *presentation tier* in the
*logic tier*, in particular the part that regulates the interaction the user can have with
the view.

With the traditional Odoo paradigm, you prefer to declare the rules for interacting with
the view statically, within the view description itself.
In this way you have to decide first what information from the environment must be brought
to the view, because otherwise it will not be accessible. This is definitely a limitation
and we have seen that to get around it you can use:
- Passing information via the context, but this is only evaluated when the view is loaded.
- Passing information through computed fields.


The traditional paradigm has multiple advantages:

- It makes the view logic (theoretically) more robust, because by greatly reducing the 
  variables on which the view's behavior can potentially depend, it also reduces the
  number of cases that can be generated. This forces the developer to adapt, but the views
  may be less buggy.

- The computational load on the server is reduced because the clients manage the view. 

- When the module is updated, all views and all record rules are evaluated and checked. If
  something is wrong, it is discovered immediately.

- The view logic does not actively interact with the business logic, especially it cannot
  block it.

The penultimate point highlights the fact that with the method proposed here, until a
certain condition occurs, a particular command will never be executed. But if that command
hides an error, for example of syntax, we will never know it unless we test all the
conditions. This highlights that, in order to have reliability with the proposed method, we
have to write ad hoc tests for each implementation of the _fah_compute_helper_fields()
method.

The last point instead must make us think about the fact that the control features on
attrs and ops that block the write/create/read/unlink operations can create serious
problems if the logical conditions depend on information not present on the model and/or
on the view and therefore not available to the user to understand the reason of a blocking
error.

Let's take an example:

> Let's take two models: "Mod1" and "Mod2".
> On "Mod1" we take a field "X" which becomes "required" based on a trigger "Y" which is a
> computed field. This computed field "Y" is based on an external field "Z", belonging to
> the comodel "Mod2", through a Many2one field. When "Z" is modified, the "Y" field must
> be recomputed and a write() will be performed on "Mod1". At this point, before the actual
> write, the check on the field attributes starts and the "X" could become "required" for
> whatever reason. If this happened, an error would be raised and the user would not be
> able to edit the "Z" field, for a reason that APPARENTLY has nothing to do with the "Z"
> field.

In this case, also setting a message in the rule, it could be difficult to go back to what
is the problem and above all why it is generated.

It is necessary therefore to have extreme caution when we write rules that are based on
data not present directly in the model.


### Ethical and economic issues

The computational load caused by the algorithms we developers write has an impact on the
Environment. You should be aware that implementing this module risks being less
environmentally friendly than the traditional solution adopted by Odoo. Not to mention the
economic aspect: keeping the computational load under control in certain contexts means
saving on the electricity bill.

For each user interaction with a target field, the "compute" method is re-executed on the
server. This means that in addition to making the server perform computations potentially
more complex than those that can be allowed with the domain in the view,
all the network infrastructure is activated to make the client communicate with the server.

If it is necessary to do all this for every click of the user, it is clear that the energy
and environmental impact is much greater.

Put your hand on your heart and/or your wallet and decide if you want to use this module
*on that model too*.


### To the Odoo community

I wrote all this to explain the issues I faced, the reasoning I did and the ways I used
and to overcome them. I believe that all of this is very much improvable. Also because of
my still partial knowledge of Python and Odoo, I certainly may have made naive choices if
not blatant mistakes.

I openly ask the community what they think about this and I invite to contribute to the
improvement of what I started. Thank you.


### To-Do

- Study if the new decorator @api.context_depends can be useful for new features or to
  simplify existing logic.

- Implement the tests.

- Reformat all strings that should be translatable and insert the wrapping function ( _() ).


### Decisions to make and ideas for future developments

- Give possibility in XML views to manually insert ``attrs`` pointing to helper fields.
  This is not possible now because when a module is updated, the views are loaded without
  going through ``fields_view_get()``. Doing so the helper fields are not injected and the
  methods ``postprocess_and_fields()`` and ``postprocess()`` in ``ir.ui.view`` raise a
  ``ValueError``: ``Field XXX does not exist``. The solution is to inject the fields by
  intercepting the ``node`` attribute of the ``postprocess()`` or
  ``postprocess_and_fields()`` method. Here, however, it is better not to inject ``attrs``
  as they are recursive functions that call each other and are executed several times.
  Injecting attrs is a bit heavy!

- If we decide to give the possibility to inject ``attrs`` by hand we have to transfer the
  injection of the helper fields to ``postprocess()`` or to ``postprocess_and_fields()``
  (on ``ir.ui.view``) because during installation/upgrade of the module the views are
  validated without using ``fields_view_get()``.

- If we decide not to give the possibility to manually insert ``attrs``, the option
  ``_FAH_XML_INJECT_ATTRS`` can be removed and only ``_FAH_XML_INJECT`` kept. Currently
  ``_FAH_XML_INJECT_ATTRS`` has to be left on True all the time, so it is useless.

- Move in the decorator ``@api.fah_depends`` the two ``super()`` calls with related control
  logic, which currently must always be reproduced in the overrides of
  ``_fah_compute_helper_fields()``.



### Tests to implement

- Generation and concatenation of domains: ``_fah_compose_domain_or()`` @ models.py
- Creating, writing and reading in the ``FahAttrRegistry``.
- What is written in the helper fields.
- Reading slots and creating data structures for targets and triggers.
- Errors that need to be raised.
- Check attrs @ create() and write().
- Check ops @ create(), write(), read() and unlink().
- "Forced fields" must be ignored.
