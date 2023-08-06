#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import time
from decimal import Decimal
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateAction
from trytond.backend import TableHandler
from trytond.pyson import Eval, PYSONEncoder
from trytond.transaction import Transaction
from trytond.pool import Pool


class Line(ModelSQL, ModelView):
    'Analytic Line'
    _name = 'analytic_account.line'
    _description = __doc__

    name = fields.Char('Name', required=True)
    debit = fields.Numeric('Debit', digits=(16, Eval('currency_digits', 2)),
        required=True, depends=['currency_digits'])
    credit = fields.Numeric('Credit', digits=(16, Eval('currency_digits', 2)),
        required=True, depends=['currency_digits'])
    currency = fields.Function(fields.Many2One('currency.currency', 'Currency',
        on_change_with=['move_line']), 'get_currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits',
        on_change_with=['move_line']), 'get_currency_digits')
    account = fields.Many2One('analytic_account.account', 'Account',
            required=True, select=True, domain=[('type', '!=', 'view')])
    move_line = fields.Many2One('account.move.line', 'Account Move Line',
            ondelete='CASCADE', required=True)
    journal = fields.Many2One('account.journal', 'Journal', required=True,
            select=True)
    date = fields.Date('Date', required=True)
    reference = fields.Char('Reference')
    party = fields.Many2One('party.party', 'Party')
    active = fields.Boolean('Active', select=True)

    def __init__(self):
        super(Line, self).__init__()
        self._sql_constraints += [
            ('credit_debit',
                'CHECK((credit * debit = 0.0) AND (credit + debit >= 0.0))',
                'Wrong credit/debit values!'),
        ]
        self._constraints += [
            ('check_account', 'line_on_view_inactive_account'),
        ]
        self._error_messages.update({
            'line_on_view_inactive_account': 'You can not create move line\n' \
                    'on view/inactive account!',
        })
        self._order.insert(0, ('date', 'ASC'))

    def init(self, module_name):
        super(Line, self).init(module_name)
        cursor = Transaction().cursor
        table = TableHandler(cursor, self, module_name)

        # Migration from 1.2 currency has been changed in function field
        table.not_null_action('currency', action='remove')

    def default_date(self):
        date_obj = Pool().get('ir.date')
        return date_obj.today()

    def default_active(self):
        return True

    def default_debit(self):
        return Decimal(0)

    def default_credit(self):
        return Decimal(0)

    def on_change_with_currency(self, vals):
        move_line_obj = Pool().get('account.move.line')
        if vals.get('move_line'):
            move_line = move_line_obj.browse(vals['move_line'])
            return move_line.account.company.currency.id

    def get_currency(self, ids, name):
        res = {}
        for line in self.browse(ids):
            res[line.id] = line.move_line.account.company.currency.id
        return res

    def on_change_with_currency_digits(self, vals):
        move_line_obj = Pool().get('account.move.line')
        if vals.get('move_line'):
            move_line = move_line_obj.browse(vals['move_line'])
            return move_line.account.company.currency.digits
        return 2

    def get_currency_digits(self, ids, name):
        res = {}
        for line in self.browse(ids):
            res[line.id] = line.move_line.account.company.currency.digits
        return res

    def query_get(self, obj='l'):
        '''
        Return SQL clause for analytic line depending of the context.
        obj is the SQL alias of the analytic_account_line in the query.
        '''
        res = obj + '.active'
        if Transaction().context.get('start_date'):
            # Check start_date
            time.strptime(str(Transaction().context['start_date']), '%Y-%m-%d')
            res += ' AND ' + obj + '.date >= date(\'' + \
                    str(Transaction().context['start_date']) + '\')'
        if Transaction().context.get('end_date'):
            # Check end_date
            time.strptime(str(Transaction().context['end_date']), '%Y-%m-%d')
            res += ' AND ' + obj + '.date <= date(\'' + \
                    str(Transaction().context['end_date']) + '\')'
        return res

    def check_account(self, ids):
        for line in self.browse(ids):
            if line.account.type == 'view':
                return False
            if not line.account.active:
                return False
        return True

Line()


class MoveLine(ModelSQL, ModelView):
    _name = 'account.move.line'
    analytic_lines = fields.One2Many('analytic_account.line', 'move_line',
            'Analytic Lines')

MoveLine()


class OpenAccount(Wizard):
    'Open Account'
    _name = 'analytic_account.line.open_account'
    start_state = 'open_'
    open_ = StateAction('analytic_account.act_line_form')

    def do_open_(self, session, action):
        action['pyson_domain'] = [
            ('account', '=', Transaction().context['active_id']),
            ]
        if Transaction().context.get('start_date'):
            action['pyson_domain'].append(
                ('date', '>=', Transaction().context['start_date'])
                )
        if Transaction().context.get('end_date'):
            action['pyson_domain'].append(
                ('date', '<=', Transaction().context['end_date'])
                )
        action['pyson_domain'] = PYSONEncoder().encode(action['pyson_domain'])
        return action, {}

    def transition_open_(self, session):
        return 'end'

OpenAccount()
