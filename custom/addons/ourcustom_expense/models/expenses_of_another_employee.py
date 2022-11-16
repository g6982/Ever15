from odoo import api, fields, Command, models, _


class HrExpenseIH(models.Model):

    _inherit = "hr.expense.sheet"

    #Enable adding expenses of another employee
    @api.constrains('expense_line_ids', 'employee_id')
    def _check_employee(self):
        return True
