from odoo import api, fields, models


class HrExpenseAttID(models.Model):
    _inherit = "hr.expense.sheet"

    attachment_id = fields.Char(string="Attachment ID")
    attachment_name = fields.Char(string="Attachment Name") #used to link "unlinked pdf files" sith there expenses report


    def link_attachment_to_expens(self):
        for exp in self:
            if exp.attachment_id:
                pdf_name = str(exp.attachment_id)+'.pdf'
                ir_attchment = self.env['ir.attachment'].search([('name','=',pdf_name)])
                if ir_attchment:
                    ir_attchment.res_id = exp.id

#link "Unlinked pdf Files"
    def process_unlinked_attachments(self):
        for exp in self:
            if exp.attachment_name:
                pdf_name = str(exp.attachment_name) + '.pdf'
                ir_attchment = self.env['ir.attachment'].search([('name', '=', pdf_name)])
                if ir_attchment:
                    ir_attchment.res_id = exp.id

#Set EXepneses as Paid
    def action_set_Exp_paid(self):
        for report in self:
            for exp in report.expense_line_ids:
                exp.state = 'done'

#Set REPORT Amount residual : 0 / status : Paid / PAyment state : Paid
    def action_set_rep_done(self):
        for report in self:
            report.amount_residual = 0
            report.state = 'done'
            report.payment_state = 'paid'
