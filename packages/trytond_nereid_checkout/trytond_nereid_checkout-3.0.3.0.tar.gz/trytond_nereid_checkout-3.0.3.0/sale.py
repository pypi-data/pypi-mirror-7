# -*- coding: utf-8 -*-
"""
    sale

    Additional Changes to sale

    :copyright: (c) 2011-2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from uuid import uuid4

from trytond.model import fields
from trytond.tools import get_smtp_server
from trytond.config import CONFIG
from trytond.pool import PoolMeta, Pool

from nereid import render_template, request, abort, login_required, \
    current_app, route, current_user, flash, redirect, url_for
from nereid.contrib.pagination import Pagination
from nereid.templating import render_email
from nereid.ctx import has_request_context
from trytond.transaction import Transaction

from .i18n import _

__all__ = ['Sale']
__metaclass__ = PoolMeta


class Sale:
    """Add Render and Render list"""
    __name__ = 'sale.sale'

    #: This access code will be cross checked if the user is guest for a match
    #: to optionally display the order to an user who has not authenticated
    #: as yet
    guest_access_code = fields.Char('Guest Access Code')

    per_page = 10

    @classmethod
    @route('/orders')
    @route('/orders/<int:page>')
    @login_required
    def render_list(cls, page=1):
        """Render all orders
        """
        domain = [
            ('party', '=', request.nereid_user.party.id),
            ('state', '!=', 'draft'),
        ]

        # Handle order duration

        sales = Pagination(cls, domain, page, cls.per_page)
        return render_template('sales.jinja', sales=sales)

    @route('/order/<int:active_id>')
    @route('/order/<int:active_id>/<confirmation>')
    def render(self, confirmation=None):
        """Render given sale order

        :param sale: ID of the sale Order
        :param confirmation: If any value is provided for this field then this
                             page is considered the confirmation page. This
                             also passes a `True` if such an argument is proved
                             or a `False`
        """
        # This Ugly type hack is for a bug in previous versions where some
        # parts of the code passed confirmation as a text
        confirmation = False if confirmation is None else True

        # Try to find if the user can be shown the order
        access_code = request.values.get('access_code', None)

        if request.is_guest_user:
            if not access_code:
                # No access code provided
                abort(403)
            if access_code != self.guest_access_code:
                # Invalid access code
                abort(403)
        else:
            if self.party.id != request.nereid_user.party.id:
                # Order does not belong to the user
                abort(403)

        return render_template(
            'sale.jinja', sale=self, confirmation=confirmation
        )

    def create_guest_access_code(self):
        """A guest access code must be written to the guest_access_code of the
        sale order so that it could be accessed wihtout a login

        :param sale: ID of the sale order
        """
        access_code = uuid4()
        self.write([self], {'guest_access_code': unicode(access_code)})
        return access_code

    def send_confirmation_email(self, silent=True):
        """An email confirming that the order has been confirmed and that we
        are waiting for the payment confirmation if we are really waiting for
        it.

        For setting a convention this email has to be sent by rendering the
        templates

           * Text: `emails/sale-confirmation-text.jinja`
           * HTML: `emails/sale-confirmation-html.jinja`

        """
        try:
            email_message = render_email(
                CONFIG['smtp_from'], self.invoice_address.email,
                'Order Completed',
                text_template='emails/sale-confirmation-text.jinja',
                html_template='emails/sale-confirmation-html.jinja',
                sale=self
            )
            server = get_smtp_server()
            server.sendmail(
                CONFIG['smtp_from'], [self.invoice_address.email],
                email_message.as_string()
            )
            server.quit()
        except Exception, exc:
            if not silent:
                raise
            current_app.logger.error(exc)

    @classmethod
    def confirm(cls, sales):
        "Send an email after sale is confirmed"
        super(Sale, cls).confirm(sales)

        if has_request_context():
            for sale in sales:
                sale.send_confirmation_email()

    def _complete_using_credit_card(self, credit_card_form):
        '''
        Complete using the given card.

        If the user is registered and the save card option is given, then
        first save the card and delegate to :meth:`_complete_using_profile`
        with the profile thus obtained.

        Otherwise a payment transaction is created with the given card data.
        '''
        AddPaymentProfileWizard = Pool().get(
            'party.party.payment_profile.add', type='wizard'
        )
        TransactionUseCardWizard = Pool().get(
            'payment_gateway.transaction.use_card', type='wizard'
        )
        PaymentTransaction = Pool().get('payment_gateway.transaction')

        gateway = request.nereid_website.credit_card_gateway

        if not request.is_guest_user and \
                credit_card_form.add_card_to_profiles.data and \
                request.nereid_website.save_payment_profile:
            profile_wiz = AddPaymentProfileWizard(
                AddPaymentProfileWizard.create()[0]     # Wizard session
            )

            profile_wiz.card_info.party = self.party
            profile_wiz.card_info.address = self.invoice_address
            profile_wiz.card_info.provider = gateway.provider
            profile_wiz.card_info.gateway = gateway
            profile_wiz.card_info.owner = credit_card_form.owner.data
            profile_wiz.card_info.number = credit_card_form.number.data
            profile_wiz.card_info.expiry_month = \
                credit_card_form.expiry_month.data
            profile_wiz.card_info.expiry_year = \
                unicode(credit_card_form.expiry_year.data)
            profile_wiz.card_info.csc = credit_card_form.cvv.data

            with Transaction().set_context(return_profile=True):
                profile = profile_wiz.transition_add()
                return self._complete_using_profile(profile.id)

        # Manual card based operation
        payment_transaction = PaymentTransaction(
            party=self.party,
            address=self.invoice_address,
            amount=self.amount_to_receive,
            currency=self.currency,
            gateway=gateway,
            sale=self,
        )
        payment_transaction.save()

        use_card_wiz = TransactionUseCardWizard(
            TransactionUseCardWizard.create()[0]        # Wizard session
        )
        use_card_wiz.card_info.owner = credit_card_form.owner.data
        use_card_wiz.card_info.number = credit_card_form.number.data
        use_card_wiz.card_info.expiry_month = \
            credit_card_form.expiry_month.data
        use_card_wiz.card_info.expiry_year = \
            unicode(credit_card_form.expiry_year.data)
        use_card_wiz.card_info.csc = credit_card_form.cvv.data

        with Transaction().set_context(active_id=payment_transaction.id):
            use_card_wiz.transition_capture()

    def _complete_using_alternate_payment_method(self, payment_form):
        '''
        :param payment_form: The validated payment_form to extract additional
                             info
        '''
        PaymentTransaction = Pool().get('payment_gateway.transaction')
        PaymentMethod = Pool().get('nereid.website.payment_method')

        payment_method = PaymentMethod(
            payment_form.alternate_payment_method.data
        )

        payment_transaction = PaymentTransaction(
            party=self.party,
            address=self.invoice_address,
            amount=self.amount_to_receive,
            currency=self.currency,
            gateway=payment_method.gateway,
            sale=self,
        )
        payment_transaction.save()

        return payment_method.process(payment_transaction)

    @login_required
    def _complete_using_profile(self, payment_profile_id):
        '''
        Complete the Checkout using a payment_profile. Only available to the
        registered users of the website.


        * payment_profile: Process the payment profile for the transaction
        '''
        PaymentProfile = Pool().get('party.payment_profile')
        PaymentTransaction = Pool().get('payment_gateway.transaction')

        payment_profile = PaymentProfile(payment_profile_id)

        if payment_profile.party != current_user.party:
            # verify that the payment profile belongs to the registered
            # user.
            flash(_('The payment profile chosen is invalid'))
            return redirect(
                url_for('nereid.checkout.payment_method')
            )

        payment_transaction = PaymentTransaction(
            party=self.party,
            address=self.invoice_address,
            payment_profile=payment_profile,
            amount=self.amount_to_receive,
            currency=self.currency,
            gateway=payment_profile.gateway,
            sale=self,
        )
        payment_transaction.save()

        PaymentTransaction.capture([payment_transaction])
