# Dynamic views inheritance

A technical module to dynamically load inherited views according to the user's group.

The feature that allows you to load inherited views dynamically according to the
user's groups, [was deprecated since Odoo 16.0](https://github.com/odoo/odoo/pull/98551). This module is a sort of backport that provides a way to achieve the same result.

Useful especially to conditionally override a view arch root node like `tree`
or `form` because it could be very inconvenient to use the `groups` attribute on
these types of nodes since it would require to duplicate the whole view/subview
even if you just want to change a simple attribute.

For all other cases, [it is recommended](https://github.com/odoo/odoo/pull/98551)
to use the `groups` attribute on the target node directly in the main view.

## Example

Inherited view (XML file)

    <?xml version="1.0" encoding="utf-8"?>
    <odoo> 

      <record id="my_dynamic_inherit_tree_view" model="ir.ui.view">
        <field name="name">Example of dynamically inherited tree view</field>
        <field name="model">my.model</field>
        <!-- The view to override -->
        <field name="inherit_id" ref="my_module.my_tree_view"/>
        <!-- Inherits this view only if the users is in the group 'my_module.my_group' -->
        <field name="inheritance_group_ids" eval="[(4, ref('my_module.my_group'))]"/>
        <field name="arch" type="xml">

          <!-- Your overrides here ... -->

          <!-- Example -->
          <tree position="attributes">
            <attribute name="create">false</attribute>
            <attribute name="delete">false</attribute>
            <attribute name="import">false</attribute>
          </tree>

        </field>
      </record>

    </odoo> 

