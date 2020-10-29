# Dynamic views inheritance

A technical module to load inherited views dynamically.


## Usage


The module create the new group ***base_view_dynamic_inheritance.dynamic_inheritance_void_group*** that should never be associated with any user.

Just associate to this specific group the inherit views that you want to load only under certain conditions (so by default odoo always ignores them because no user is in that group).

        <field name="groups_id" eval="[(4, ref('base_view_dynamic_inheritance.dynamic_inheritance_void_group'))]"/>

Then in the action window you pass in the context the id of the views you want to load the inherited view.

    'context': {
        'bvdi_force_add_inheriting_views': [{
            'view_id': view_form_id,
            'inherit_view_id': view_form_inherit_id,
            'inherit_position': 'append'
        }]
    }

## Example

Inherited view (XML file)

    <?xml version="1.0" encoding="utf-8"?> 
    <odoo> 

      <record id="my_dynamic_inherit_form_view" model="ir.ui.view">
        <field name="name">Example of dynamically inherited form view</field>
        <field name="model">my.model</field>
        <!-- The view to override -->
        <field name="inherit_id" ref="my_module.my_form_view"/>
        <!-- Limit this inherit to 'dynamic_inheritance_void_group' -->
        <field name="groups_id" eval="[(4, ref('base_view_dynamic_inheritance.dynamic_inheritance_void_group'))]"/>
        <field name="arch" type="xml">

          <!-- Your overrides here ... -->

        </field>
      </record>

    </odoo> 

Action (Python file)

    class ExampleModel(models.Model):
        # ...
        
        def action_open_my_view(self)

            view_tree_id = self.env.ref('my_module.my_tree_view').id
            view_form_id = self.env.ref('my_module.my_form_view').id
            view_form_inherit_id = self.env.ref('my_module.my_dynamic_inherit_form_view').id

            return {
	            'name': 'My view title',
	            'type': 'ir.actions.act_window',
	            'res_model': 'my.model',
	            'view_mode': 'tree, form',
	            'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
	            'context': {
	                # List of dict containing the views you want to force the intherit of.
	                # <!> You need to make sure that the relationship of inheritance between 'view_id' and 'inherit_view_id' is correct
	                # <!> and conforms to what is described in the inherited view (in this example 'my_dynamic_inherit_form_view')
	                'bvdi_force_add_inheriting_views': [{
	                    'view_id': view_form_id,
	                    'inherit_view_id': view_form_inherit_id,
	                    'inherit_position': 'append'
	                }]
	            },
		}

Action (XML File)

    <record id="my_action_window" model="ir.actions.act_window" >
        <field name="name">My view name</field>
        <field name="res_model">my.model</field>
        <field name="view_mode">tree,form</field>
        <field name="view_ids"
               eval="[(5, 0, 0),
                      (0, 0, {'view_mode': 'tree', 'view_id': ref('my_module.my_tree_view')}),
                      (0, 0, {'view_mode': 'form', 'view_id': ref('my_module.my_form_view')})]"/>
        <field name="context" eval="
            {
                'bvdi_force_add_inheriting_views': [{
                    'view_id': ref('my_module.my_form_view'),
                    'inherit_view_id': ref('my_module.my_dynamic_inherit_form_view'),
                    'inherit_position': 'append'
                }]
            }"
        />
    </record>

