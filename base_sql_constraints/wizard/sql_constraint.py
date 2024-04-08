from odoo import models, fields, api
from odoo.tools import sql
from odoo.exceptions import UserError  # , ValidationError

class SqlConstraintWizard(models.TransientModel):
    _name = 'sql.constraint.manager'
    _description = 'SQL Constraint Manager'

    CONSTRAINT_TYPES = [
        ('all', 'All'),  # Option to show all constraints
        ('u', 'UNIQUE'),
        ('c', 'CHECK'),
        ('f', 'FOREIGN KEY'),
        ('p', 'PRIMARY KEY'),
    ]

    model_id = fields.Many2one('ir.model', string='Model', required=True)
    constraint_type = fields.Selection(CONSTRAINT_TYPES, string='Constraint Type', default='all', required=True)
    constraint_info = fields.Html(string='SQL Constraints', compute='_compute_constraint_info')
    constraint_key_to_remove = fields.Char(string='Constraint Key to remove', help='You can only remove UNIQUE or CHECK constraints.')

    @api.depends('model_id', 'constraint_type')
    def _compute_constraint_info(self):
        self.ensure_one()
        # Query to get the _sql_constraints
        self.constraint_info = self._get_sql_constraints()

    def _get_sql_constraints(self):
        # Execute the query to get the SQL constraints
        # and format the result in monospaced HTML text
        self.ensure_one()

        if not self.model_id:
            return 'No model selected.'

        constraint_type_filter = " AND pg_constraint.contype = %s" if self.constraint_type != 'all' else ""

        query = """
            SELECT conname AS constraint_name, pg_get_constraintdef(pg_constraint.oid) AS definition
            FROM pg_constraint
            JOIN pg_class ON pg_constraint.conrelid = pg_class.oid
            WHERE pg_class.relname = %s{}
        """.format(constraint_type_filter)

        model_table_name = self.env[self.model_id.model]._table
        params = [model_table_name]
        if self.constraint_type != 'all':
            params.append(self.constraint_type)

        self.env.cr.execute(query, tuple(params))
        constraints = self.env.cr.fetchall()

        # Create the HTML table
        html_result = "<table style='width:100%; border: 1px solid black; border-collapse: collapse;'>"
        html_result += "<tr style='border: 1px solid black;'><th style='border: 1px solid black;'>Constraint Name</th><th style='border: 1px solid black;'>Definition</th></tr>"

        for constraint in constraints:
            html_result += "<tr style='border: 1px solid black;'><td style='border: 1px solid black;'><pre>{}</pre></td><td style='border: 1px solid black;'><pre>{}</pre></td></tr>".format(*constraint)

        html_result += "</table>"
        return html_result


    def action_remove_constraint(self):
        # Execute the query to remove the constraint.

        if not self.model_id or not self.constraint_key_to_remove:
            raise UserError('Model and Constraint Key are required.')

        # Check the constraint type before removing it
        check_query = """
            SELECT contype
            FROM pg_constraint
            WHERE conname = %s AND conrelid = (SELECT oid FROM pg_class WHERE relname = %s)
        """
        self.env.cr.execute(check_query, (self.constraint_key_to_remove, self.env[self.model_id.model]._table))
        constraint_type = self.env.cr.fetchone()

        if not constraint_type or constraint_type[0] not in ['u', 'c']:
            raise UserError(
                'The constraint you are trying to remove is not UNIQUE or CHECK, '
                'or it does not exist.'
            )

        # Using drop_constraint() in /odoo/tools/sql.py
        sql.drop_constraint(
            self.env.cr,
            self.env[self.model_id.model]._table,
            self.constraint_key_to_remove
        )

        # Manually executing the query to remove the constraint
        # remove_query = "ALTER TABLE {} DROP CONSTRAINT {}"
        # self.env.cr.execute(
        #     remove_query.format(
        #         self.env[self.model_id.model]._table,
        #         self.constraint_key_to_remove
        #     )
        # )

        # Reload the same wizard to show the updated constraints list
        return {
            'type': 'ir.actions.act_window',
            'name': self._description,
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }
