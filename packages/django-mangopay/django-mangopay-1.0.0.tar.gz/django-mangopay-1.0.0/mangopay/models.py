import base64
from datetime import datetime
from decimal import Decimal, ROUND_FLOOR

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import default_storage

from money.contrib.django.models.fields import MoneyField
from model_utils.managers import InheritanceManager
from mangopaysdk.entities.usernatural import UserNatural
from mangopaysdk.entities.userlegal import UserLegal
from mangopaysdk.entities.bankaccount import BankAccount
from mangopaysdk.entities.kycdocument import KycDocument
from mangopaysdk.entities.wallet import Wallet
from mangopaysdk.entities.kycpage import KycPage
from mangopaysdk.entities.payout import PayOut
from mangopaysdk.entities.payin import PayIn
from mangopaysdk.entities.refund import Refund
from mangopaysdk.entities.cardregistration import CardRegistration
from mangopaysdk.types.money import Money
from mangopaysdk.types.payoutpaymentdetailsbankwire import (
    PayOutPaymentDetailsBankWire)
from mangopaysdk.types.payinexecutiondetailsdirect import (
    PayInExecutionDetailsDirect)
from mangopaysdk.types.payinpaymentdetailscard import PayInPaymentDetailsCard
from django_countries.fields import CountryField
from django_iban.fields import IBANField, SWIFTBICField
from money import Money as PythonMoney

from .constants import (INCOME_RANGE_CHOICES,
                        STATUS_CHOICES, DOCUMENT_TYPE_CHOICES,
                        CREATED, STATUS_CHOICES_DICT, NATURAL_USER,
                        DOCUMENT_TYPE_CHOICES_DICT, USER_TYPE_CHOICES,
                        VALIDATED, IDENTITY_PROOF, VALIDATION_ASKED,
                        REGISTRATION_PROOF, ARTICLES_OF_ASSOCIATION,
                        SHAREHOLDER_DECLARATION, TRANSACTION_STATUS_CHOICES,
                        REFUSED, BUSINESS, ORGANIZATION,
                        USER_TYPE_CHOICES_DICT)
from .client import get_mangopay_api_client


def python_money_to_mangopay_money(python_money):
    amount = python_money.amount.quantize(Decimal('.01'),
                                          rounding=ROUND_FLOOR) * 100
    return Money(amount=int(amount), currency=str(python_money.currency))


def get_execution_date_as_datetime(mangopay_entity):
    execution_date = mangopay_entity.ExecutionDate
    if execution_date:
        return datetime.fromtimestamp(int(execution_date))


class MangoPayUser(models.Model):
    objects = InheritanceManager()

    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, related_name="mangopay_users")
    type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES,
                            null=True)

    # Light Authenication Field:
    birthday = models.DateField(blank=True, null=True)
    country_of_residence = CountryField()
    nationality = CountryField()

    # Regular Authenication Fields:
    address = models.CharField(blank=True, null=True, max_length=254)

    def create(self):
        client = get_mangopay_api_client()
        mangopay_user = self._build()
        created_mangopay_user = client.users.Create(mangopay_user)
        self.mangopay_id = created_mangopay_user.Id
        self.save()

    def update(self):
        client = get_mangopay_api_client()
        return client.users.Update(self._build())

    def is_legal(self):
        return self.type in [BUSINESS, ORGANIZATION]

    def is_natural(self):
        return self.type == NATURAL_USER

    def has_regular_authenication(self):
        return (self.has_light_authenication()
                and self._are_required_documents_validated())

    def required_documents_types_that_need_to_be_reuploaded(self):
        return [t for t in self._required_documents_types() if
                self._document_needs_to_be_reuploaded(t)]

    def _document_needs_to_be_reuploaded(self, t):
        return (self.mangopay_documents.filter(
                type=t, status=REFUSED).exists()
                and not self.mangopay_documents.filter(
                    type=t,
                    status__in=[VALIDATED, VALIDATION_ASKED]).exists()
                and not self.mangopay_documents.filter(
                    type=t, status__isnull=True).exists())

    def _build(self):
        return NotImplementedError

    def _birthday_fmt(self):
        return int(self.birthday.strftime("%s"))

    def _are_required_documents_validated(self):
        are_validated = True
        for type in self._required_documents_types():
            are_validated = self.mangopay_documents.filter(
                type=type, status=VALIDATED).exists() and are_validated
        return are_validated


class MangoPayNaturalUser(MangoPayUser):
    # Regular Authenication Fields:
    occupation = models.CharField(blank=True, null=True, max_length=254)
    income_range = models.SmallIntegerField(
        blank=True, null=True, choices=INCOME_RANGE_CHOICES)

    def _build(self):
        mangopay_user = UserNatural()
        mangopay_user.FirstName = self.user.first_name
        mangopay_user.LastName = self.user.last_name
        mangopay_user.Email = self.user.email
        mangopay_user.Birthday = self._birthday_fmt()
        mangopay_user.CountryOfResidence = self.country_of_residence.code
        mangopay_user.Nationality = self.nationality.code
        mangopay_user.Occupation = self.occupation
        mangopay_user.IncomeRange = self.income_range
        mangopay_user.Address = self.address
        mangopay_user.Id = self.mangopay_id
        return mangopay_user

    def __unicode__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        self.type = NATURAL_USER
        return super(MangoPayNaturalUser, self).save(*args, **kwargs)

    def has_light_authenication(self):
        return (self.user
                and self.country_of_residence
                and self.nationality
                and self.birthday)

    def has_regular_authenication(self):
        return (self.address
                and self.occupation
                and self.income_range
                and super(MangoPayNaturalUser,
                          self).has_regular_authenication())

    def _required_documents_types(self):
        return [IDENTITY_PROOF]


class MangoPayLegalUser(MangoPayUser):
    business_name = models.CharField(max_length=254)
    generic_business_email = models.EmailField(max_length=254)
    # first_name, last_name, and email belong to the Legal Representative
    # who is not always the same person as the linked user
    first_name = models.CharField(max_length=99)
    last_name = models.CharField(max_length=99)

    # Regular Authenication Fields:
    headquaters_address = models.CharField(blank=True, max_length=254,
                                           null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

    def _build(self):
        mangopay_user = UserLegal()
        mangopay_user.Email = self.generic_business_email
        mangopay_user.Name = self.business_name
        mangopay_user.LegalPersonType = USER_TYPE_CHOICES_DICT[self.type]
        mangopay_user.HeadquartersAddress = self.headquaters_address
        mangopay_user.LegalRepresentativeFirstName = self.first_name
        mangopay_user.LegalRepresentativeLastName = self.last_name
        mangopay_user.LegalRepresentativeAddress = self.address
        mangopay_user.LegalRepresentativeEmail = self.email
        mangopay_user.LegalRepresentativeBirthday = self._birthday_fmt()
        mangopay_user.LegalRepresentativeNationality = self.nationality.code
        mangopay_user.LegalRepresentativeCountryOfResidence =\
            self.country_of_residence.code
        mangopay_user.Id = self.mangopay_id
        return mangopay_user

    def __unicode__(self):
        if self.business_name:
            return self.business_name
        else:
            return super(MangoPayLegalUser, self).__unicode__()

    def has_light_authenication(self):
        return (self.type
                and self.business_name
                and self.generic_business_email
                and self.first_name
                and self.last_name
                and self.country_of_residence
                and self.nationality
                and self.birthday)

    def has_regular_authenication(self):
        return (self.address
                and self.headquaters_address
                and self.address
                and self.email
                and super(MangoPayLegalUser, self).has_regular_authenication())

    def _required_documents_types(self):
        types = [REGISTRATION_PROOF]
        if self.type == BUSINESS:
            types.append(SHAREHOLDER_DECLARATION)
        elif self.type == ORGANIZATION:
            types.append(ARTICLES_OF_ASSOCIATION)
        return types


class MangoPayDocument(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser,
                                      related_name="mangopay_documents")
    type = models.CharField(max_length=2,
                            choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(blank=True, null=True, max_length=1,
                              choices=STATUS_CHOICES)
    refused_reason_message = models.CharField(null=True, blank=True,
                                              max_length=255)

    def create(self, tag=''):
        document = KycDocument()
        document.Tag = tag
        document.Type = DOCUMENT_TYPE_CHOICES_DICT[self.type]
        client = get_mangopay_api_client()
        created_document = client.users.CreateUserKycDocument(
            document, self.mangopay_user.mangopay_id)
        self.mangopay_id = created_document.Id
        self.status = STATUS_CHOICES_DICT[created_document.Status]
        self.save()

    def get(self):
        client = get_mangopay_api_client()
        document = client.users.GetUserKycDocument(
            self.mangopay_id, self.mangopay_user.mangopay_id)
        self.refused_reason_message = document.RefusedReasonMessage
        self.status = STATUS_CHOICES_DICT[document.Status]
        self.save()
        return self

    def ask_for_validation(self):
        if self.status == CREATED:
            document = KycDocument()
            document.Id = self.mangopay_id
            document.Status = "VALIDATION_ASKED"
            client = get_mangopay_api_client()
            updated_document = client.users.UpdateUserKycDocument(
                document, self.mangopay_user.mangopay_id, self.mangopay_id)
            self.status = STATUS_CHOICES_DICT[updated_document.Status]
            self.save()
        else:
            raise BaseException('Cannot ask for validation of a document'
                                'not in the created state')

    def __unicode__(self):
        return str(self.mangopay_id) + " " + str(self.status)


def page_storage():
    if settings.MANGOPAY_PAGE_DEFAULT_STORAGE:
        return default_storage
    else:
        from storages.backends.s3boto import S3BotoStorage
        return S3BotoStorage(
            headers={'Content-Disposition': 'attachment',
                     'X-Robots-Tag': 'noindex, nofollow, noimageindex'},
            bucket=settings.AWS_MEDIA_BUCKET_NAME,
            custom_domain=settings.AWS_MEDIA_CUSTOM_DOMAIN)


class MangoPayPage(models.Model):
    document = models.ForeignKey(MangoPayDocument,
                                 related_name="mangopay_pages")
    file = models.FileField(upload_to='mangopay_pages',
                            storage=page_storage())

    def create(self):
        page = KycPage()
        self.file.open(mode='rb')
        bytes = base64.b64encode(self.file.read())
        self.file.close()
        page.File = bytes.decode("utf-8")
        client = get_mangopay_api_client()
        client.users.CreateUserKycPage(page,
                                       self.document.mangopay_user.mangopay_id,
                                       self.document.mangopay_id)


class MangoPayBankAccount(models.Model):
    mangopay_user = models.ForeignKey(MangoPayUser,
                                      related_name="mangopay_bank_accounts")
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    iban = IBANField()
    bic = SWIFTBICField()
    address = models.CharField(max_length=254)

    def create(self):
        client = get_mangopay_api_client()
        mangopay_bank_account = BankAccount()
        mangopay_bank_account.UserId = self.mangopay_user.mangopay_id
        mangopay_bank_account.OwnerName = \
            self.mangopay_user.user.get_full_name()
        mangopay_bank_account.OwnerAddress = self.address
        mangopay_bank_account.IBAN = self.iban
        mangopay_bank_account.BIC = self.bic
        created_bank_account = client.users.CreateBankAccount(
            str(self.mangopay_user.mangopay_id), mangopay_bank_account)
        self.mangopay_id = created_bank_account.Id
        self.save()


class MangoPayWallet(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(
        MangoPayUser, related_name="mangopay_wallets")

    def create(self, currency, description=""):
        mangopay_wallet = Wallet()
        mangopay_wallet.Owners = [str(self.mangopay_user.mangopay_id)]
        mangopay_wallet.Description = description
        mangopay_wallet.Currency = currency
        client = get_mangopay_api_client()
        created_mangopay_wallet = client.wallets.Create(mangopay_wallet)
        self.mangopay_id = created_mangopay_wallet.Id
        self.save()

    def balance(self):
        wallet = self._get()
        return PythonMoney(wallet.Balance.Amount / 100,
                           wallet.Balance.Currency)

    def _get(self):
        client = get_mangopay_api_client()
        return client.wallets.Get(self.mangopay_id)


class MangoPayPayOut(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser,
                                      related_name="mangopay_payouts")
    mangopay_wallet = models.ForeignKey(MangoPayWallet,
                                        related_name="mangopay_payouts")
    mangopay_bank_account = models.ForeignKey(MangoPayBankAccount,
                                              related_name="mangopay_payouts")
    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                              blank=True, null=True)
    debited_funds = MoneyField(default=0, default_currency="EUR",
                               decimal_places=2, max_digits=12)
    fees = MoneyField(default=0, default_currency="EUR", decimal_places=2,
                      max_digits=12)

    def create(self, tag=''):
        pay_out = PayOut()
        pay_out.Tag = tag
        pay_out.AuthorId = self.mangopay_user.mangopay_id
        pay_out.DebitedFunds = python_money_to_mangopay_money(
            self.debited_funds)
        pay_out.Fees = python_money_to_mangopay_money(self.fees)
        pay_out.DebitedWalletId = self.mangopay_wallet.mangopay_id
        details = PayOutPaymentDetailsBankWire()
        details.BankAccountId = self.mangopay_bank_account.mangopay_id
        pay_out.MeanOfPaymentDetails = details
        client = get_mangopay_api_client()
        created_pay_out = client.payOuts.Create(pay_out)
        self.mangopay_id = created_pay_out.Id
        return self._update(created_pay_out)

    def get(self):
        client = get_mangopay_api_client()
        pay_out = client.payOuts.Get(self.mangopay_id)
        return self._update(pay_out)

    def _update(self, pay_out):
        self.execution_date = get_execution_date_as_datetime(pay_out)
        self.status = pay_out.Status
        self.save()
        return self


class MangoPayCard(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    expiration_date = models.CharField(blank=True, null=True, max_length=4)
    alias = models.CharField(blank=True, null=True, max_length=16)
    is_active = models.BooleanField(default=False)
    is_valid = models.NullBooleanField()

    def request_card_info(self):
        if self.mangopay_id:
            client = get_mangopay_api_client()
            card = client.cards.Get(self.mangopay_id)
            self.expiration_date = card.ExpirationDate
            self.alias = card.Alias
            self.is_active = card.Active
            if card.Validity == "UNKNOWN":
                self.is_valid = None
            else:
                self.is_valid = card.Validity == "VALID"


class MangoPayCardRegistration(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(
        MangoPayUser, related_name="mangopay_card_registrations")
    mangopay_card = models.OneToOneField(
        MangoPayCard, null=True, blank=True,
        related_name="mangopay_card_registration")

    def create(self, currency):
        client = get_mangopay_api_client()
        card_registration = CardRegistration()
        card_registration.UserId = str(self.mangopay_user.mangopay_id)
        card_registration.Currency = currency
        card_registration = client.cardRegistrations.Create(card_registration)
        self.mangopay_id = card_registration.Id
        self.save()

    def get_preregistration_data(self):
        client = get_mangopay_api_client()
        card_registration = client.cardRegistrations.Get(self.mangopay_id)
        preregistration_data = {
            "preregistrationData": card_registration.PreregistrationData,
            "accessKey": card_registration.AccessKey,
            "cardRegistrationURL": card_registration.CardRegistrationURL}
        return preregistration_data

    def save_mangopay_card_id(self, mangopay_card_id):
        self.mangopay_card.mangopay_id = mangopay_card_id
        self.mangopay_card.save()

    def save(self, *args, **kwargs):
        if not self.mangopay_card:
            mangopay_card = MangoPayCard()
            mangopay_card.save()
            self.mangopay_card = mangopay_card
        super(MangoPayCardRegistration, self).save(*args, **kwargs)


class MangoPayPayIn(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser,
                                      related_name="mangopay_payins")
    mangopay_wallet = models.ForeignKey(MangoPayWallet,
                                        related_name="mangopay_payins")
    mangopay_card = models.ForeignKey(MangoPayCard,
                                      related_name="mangopay_payins")
    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                              blank=True, null=True)
    result_code = models.CharField(null=True, blank=True, max_length=6)
    secure_mode_redirect_url = models.URLField(null=True, blank=True)

    def create(self, debited_funds, fees=None, secure_mode_return_url=None):
        pay_in = PayIn()
        pay_in.AuthorId = self.mangopay_user.mangopay_id
        pay_in.CreditedUserId = self.mangopay_wallet.mangopay_user.mangopay_id
        pay_in.CreditedWalletId = self.mangopay_wallet.mangopay_id
        pay_in.DebitedFunds = python_money_to_mangopay_money(debited_funds)
        if not fees:
            fees = PythonMoney(0, debited_funds.currency)
        pay_in.Fees = python_money_to_mangopay_money(fees)

        payment_details = PayInPaymentDetailsCard()
        payment_details.CardType = "CB_VISA_MASTERCARD"
        pay_in.PaymentDetails = payment_details

        execution_details = PayInExecutionDetailsDirect()
        execution_details.CardId = self.mangopay_card.mangopay_id
        execution_details.SecureModeReturnURL = secure_mode_return_url
        execution_details.SecureMode = "DEFAULT"
        pay_in.ExecutionDetails = execution_details

        client = get_mangopay_api_client()
        created_pay_in = client.payIns.Create(pay_in)

        self.mangopay_id = created_pay_in.Id
        self._update(created_pay_in)

    def get(self):
        client = get_mangopay_api_client()
        pay_in = client.payIns.Get(self.mangopay_id)
        self._update(pay_in)

    def _update(self, pay_in):
        self.status = pay_in.Status
        self.result_code = pay_in.ResultCode
        self.execution_date = get_execution_date_as_datetime(pay_in)
        self.secure_mode_redirect_url = pay_in.\
            ExecutionDetails.SecureModeRedirectURL
        self.save()


class MangoPayRefund(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser,
                                      related_name="mangopay_refunds")
    mangopay_pay_in = models.ForeignKey(MangoPayPayIn,
                                        related_name="mangopay_refunds")
    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                              blank=True, null=True)
    result_code = models.CharField(null=True, blank=True, max_length=6)

    def create_simple(self):
        pay_in_id = self.mangopay_pay_in.mangopay_id
        refund = Refund()
        refund.InitialTransactionId = pay_in_id
        refund.AuthorId = self.mangopay_user.mangopay_id
        client = get_mangopay_api_client()
        created_refund = client.payIns.CreateRefund(pay_in_id, refund)
        self.status = created_refund.Status
        self.result_code = created_refund.ResultCode
        self.mangopay_id = created_refund.Id
        self.execution_date = get_execution_date_as_datetime(refund)
        self.save()
        return self.status == "SUCCEEDED"
