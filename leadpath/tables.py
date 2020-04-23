# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class AdvertiserDispositionBuyer(Base):
    __tablename__ = 'advertiser_disposition_buyers'

    id = Column(Integer, primary_key=True)
    buyer_id = Column(ForeignKey(u'buyers.id'), nullable=False, index=True)
    advertiser_disposition_id = Column(ForeignKey(u'advertiser_dispositions.id'), nullable=False, index=True)
    reservation_id = Column(String(100))
    price = Column(Numeric(12, 2))
    longitude = Column(String(15))
    latitude = Column(String(15))
    program_id = Column(String(20))
    buyer_code = Column(String(20))
    distance = Column(String(20))
    group_id = Column(String(100))
    max_posts = Column(Integer)
    external_lead_id = Column(String(50))
    status = Column(Integer, server_default=text("'0'"))
    is_preferred = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    advertiser_disposition = relationship(u'AdvertiserDisposition')
    buyer = relationship(u'Buyer')


class AdvertiserDispositionCode(Base):
    __tablename__ = 'advertiser_disposition_codes'

    id = Column(Integer, primary_key=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False, index=True)
    disposition_code_id = Column(ForeignKey(u'disposition_codes.id'), nullable=False, index=True)
    status = Column(Integer, nullable=False, server_default=text("'1'"))
    pixel_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')
    disposition_code = relationship(u'DispositionCode')


class AdvertiserDisposition(Base):
    __tablename__ = 'advertiser_dispositions'

    id = Column(Integer, primary_key=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False, index=True)
    lead_match_id = Column(ForeignKey(u'lead_matches.id'), nullable=False, index=True)
    status = Column(Integer, server_default=text("'0'"))
    category = Column(Integer)
    pony_phase = Column(Integer, nullable=False, server_default=text("'-1'"))
    price = Column(Numeric(12, 2))
    comment = Column(String(255))
    created_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')
    lead_match = relationship(u'LeadMatch')


class AdvertiserWriter(Base):
    __tablename__ = 'advertiser_writers'

    id = Column(Integer, primary_key=True)
    lead_type_id = Column(ForeignKey(u'lead_types.id'), nullable=False, index=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False, index=True)
    class_name = Column(String(255), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')
    lead_type = relationship(u'LeadType')


class Advertiser(Base):
    __tablename__ = 'advertisers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Arrival(Base):
    __tablename__ = 'arrivals'
    __table_args__ = (
        Index('idx_profile_publisher', 'user_profile_id', 'publisher_id', unique=True),
        Index('created_at', 'created_at', 'arrival_source_id', 'publisher_id'),
        Index('idx_external_id', 'publisher_id', 'publisher_list_id', 'external_id', unique=True)
    )

    id = Column(Integer, primary_key=True)
    publisher_id = Column(ForeignKey(u'publishers.id'), nullable=False, index=True)
    publisher_list_id = Column(ForeignKey(u'publisher_lists.id'), index=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'))
    arrival_source_id = Column(Integer)
    external_id = Column(String(72))
    ip_address = Column(String(30))
    user_agent = Column(String(255))
    referrer = Column(String(255))
    created_at = Column(DateTime)
    last_seen_at = Column(DateTime)
    validation_code = Column(Integer, nullable=False, server_default=text("'-1'"))

    publisher = relationship(u'Publisher')
    publisher_list = relationship(u'PublisherList')
    user_profile = relationship(u'UserProfile')


class Attribute(Base):
    __tablename__ = 'attributes'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    input_type = Column(String(50), nullable=False, server_default=text("'text'"))
    is_large = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)


class AutoCorrectDomain(Base):
    __tablename__ = 'auto_correct_domains'
    __table_args__ = (
        Index('from_mail_host_id', 'from_mail_host_id', 'to_mail_host_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    from_mail_host_id = Column(ForeignKey(u'mail_hosts.id'), nullable=False)
    to_mail_host_id = Column(ForeignKey(u'mail_hosts.id'), nullable=False, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    from_mail_host = relationship(u'MailHost', primaryjoin='AutoCorrectDomain.from_mail_host_id == MailHost.id')
    to_mail_host = relationship(u'MailHost', primaryjoin='AutoCorrectDomain.to_mail_host_id == MailHost.id')


class Bounce(Base):
    __tablename__ = 'bounces'
    __table_args__ = (
        Index('external_id', 'external_id', 'host_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'), nullable=False, index=True)
    message_id = Column(ForeignKey(u'messages.id'), index=True)
    host_id = Column(Integer, nullable=False)
    external_id = Column(Integer)
    status_code = Column(Integer)
    message = Column(String(255))
    created_at = Column(DateTime)
    external_created_at = Column(DateTime)

    message1 = relationship(u'Message')
    user_profile = relationship(u'UserProfile')


class Buyer(Base):
    __tablename__ = 'buyers'
    __table_args__ = (
        Index('buyer_id', 'buyer_id', 'zip', 'name', unique=True),
    )

    id = Column(Integer, primary_key=True)
    buyer_id = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    state = Column(String(3))
    zip = Column(String(15))
    city = Column(String(100))
    street = Column(String(150))
    contact_name = Column(String(100))
    contact_phone = Column(String(50))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)


class CallcenterBroker(Base):
    __tablename__ = 'callcenter_brokers'
    __table_args__ = (
        Index('advertiser_broker', 'advertiser_id', 'broker_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    email = Column(String(255))
    broker_id = Column(String(25))
    phone_number = Column(String(25))
    created_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')


class ClickRule(Base):
    __tablename__ = 'click_rules'

    id = Column(Integer, primary_key=True)
    click_source_id = Column(ForeignKey(u'click_sources.id'), nullable=False, index=True)
    click_target_id = Column(ForeignKey(u'click_targets.id'), nullable=False, index=True)
    status = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    click_source = relationship(u'ClickSource')
    click_target = relationship(u'ClickTarget')


class ClickSource(Base):
    __tablename__ = 'click_sources'

    id = Column(Integer, primary_key=True)
    publisher_id = Column(ForeignKey(u'publishers.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    pixel_back_url = Column(String(255))
    created_at = Column(DateTime)

    publisher = relationship(u'Publisher')


class ClickTarget(Base):
    __tablename__ = 'click_targets'

    id = Column(Integer, primary_key=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    destination_url = Column(String(255), nullable=False)
    created_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')


class Click(Base):
    __tablename__ = 'clicks'

    id = Column(Integer, primary_key=True)
    message_id = Column(ForeignKey(u'messages.id'), nullable=False, unique=True)
    external_id = Column(Integer, index=True)
    click_count = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    external_created_at = Column(DateTime)
    external_updated_at = Column(DateTime)

    message = relationship(u'Message')


class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'), nullable=False, index=True)
    message_id = Column(ForeignKey(u'messages.id'), index=True)
    external_id = Column(Integer, index=True)
    created_at = Column(DateTime)
    external_created_at = Column(DateTime)

    message = relationship(u'Message')
    user_profile = relationship(u'UserProfile')


class Creative(Base):
    __tablename__ = 'creatives'
    __table_args__ = (
        Index('from_address_id', 'from_address_id', 'subject_line_id', 'message_template_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    offer_id = Column(ForeignKey(u'offers.id'), nullable=False, index=True)
    status = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    subject_line_id = Column(ForeignKey(u'subject_lines.id'), index=True)
    message_template_id = Column(ForeignKey(u'message_templates.id'), index=True)
    from_address_id = Column(ForeignKey(u'from_addresses.id'))
    external_id = Column(String(64))

    from_address = relationship(u'FromAddress')
    message_template = relationship(u'MessageTemplate')
    offer = relationship(u'Offer')
    subject_line = relationship(u'SubjectLine')


class DayFilter(Base):
    __tablename__ = 'day_filters'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey(u'orders.id'), nullable=False, index=True)
    is_allow = Column(Integer, server_default=text("'1'"))
    pony_phase = Column(Integer)
    status = Column(Integer, server_default=text("'1'"))
    days = Column(String(15), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    order = relationship(u'Order')


class DispositionCode(Base):
    __tablename__ = 'disposition_codes'

    id = Column(Integer, primary_key=True)
    disposition_code = Column(Integer, nullable=False)
    description = Column(String(150), nullable=False)
    created_at = Column(DateTime)
    sort_order = Column(Integer, nullable=False, server_default=text("'0'"))


class Domain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    domain_label = Column(String(255), nullable=False)
    top_level_domain = Column(String(255), nullable=False)
    created_at = Column(DateTime)


class EmailTargetQueue(Base):
    __tablename__ = 'email_target_queues'
    __table_args__ = (
        Index('from_publisher_list_id', 'from_publisher_list_id', 'to_publisher_list_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    from_publisher_list_id = Column(ForeignKey(u'publisher_lists.id'), nullable=False)
    to_publisher_list_id = Column(ForeignKey(u'publisher_lists.id'), nullable=False, index=True)
    max_arrival_id = Column(Integer, nullable=False, server_default=text("'0'"))
    open_within_days = Column(Integer, server_default=text("'0'"))
    send_frequency_days = Column(Integer, server_default=text("'7'"))
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    from_publisher_list = relationship(u'PublisherList', primaryjoin='EmailTargetQueue.from_publisher_list_id == PublisherList.id')
    to_publisher_list = relationship(u'PublisherList', primaryjoin='EmailTargetQueue.to_publisher_list_id == PublisherList.id')


class FormImpression(Base):
    __tablename__ = 'form_impressions'
    __table_args__ = (
        Index('ip_address', 'ip_address', 'form_id', 'form_step_id', 'form_step_group_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_id = Column(ForeignKey(u'forms.id'), nullable=False, index=True)
    form_step_id = Column(ForeignKey(u'form_steps.id'), index=True)
    form_step_group_id = Column(ForeignKey(u'form_step_groups.id'), index=True)
    arrival_id = Column(ForeignKey(u'arrivals.id'), index=True)
    impression_count = Column(Integer, nullable=False, server_default=text("'0'"))
    ip_address = Column(String(30))
    user_agent = Column(String(255))
    referrer = Column(String(255))
    created_at = Column(DateTime)
    last_seen_at = Column(DateTime)
    last_uuid = Column(String(40))

    arrival = relationship(u'Arrival')
    form = relationship(u'Form')
    form_step_group = relationship(u'FormStepGroup')
    form_step = relationship(u'FormStep')


class FormSelectFilter(Base):
    __tablename__ = 'form_select_filters'
    __table_args__ = (
        Index('form_id', 'form_id', 'select_value_id', 'form_step_attribute_id', 'target_form_step_attribute_id', 'target_select_value_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_id = Column(ForeignKey(u'forms.id'), nullable=False)
    form_step_attribute_id = Column(ForeignKey(u'form_step_attributes.id'), nullable=False, index=True)
    select_value_id = Column(ForeignKey(u'select_values.id'), nullable=False, index=True)
    target_form_step_attribute_id = Column(ForeignKey(u'form_step_attributes.id'), nullable=False, index=True)
    target_select_value_id = Column(ForeignKey(u'select_values.id'), nullable=False, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    form = relationship(u'Form')
    form_step_attribute = relationship(u'FormStepAttribute', primaryjoin='FormSelectFilter.form_step_attribute_id == FormStepAttribute.id')
    select_value = relationship(u'SelectValue', primaryjoin='FormSelectFilter.select_value_id == SelectValue.id')
    target_form_step_attribute = relationship(u'FormStepAttribute', primaryjoin='FormSelectFilter.target_form_step_attribute_id == FormStepAttribute.id')
    target_select_value = relationship(u'SelectValue', primaryjoin='FormSelectFilter.target_select_value_id == SelectValue.id')


class FormStepAttributeFilter(Base):
    __tablename__ = 'form_step_attribute_filters'
    __table_args__ = (
        Index('form_id', 'form_id', 'select_value_id', 'target_form_step_attribute_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_id = Column(ForeignKey(u'forms.id'), nullable=False)
    select_value_id = Column(ForeignKey(u'select_values.id'), nullable=False, index=True)
    target_form_step_attribute_id = Column(ForeignKey(u'form_step_attributes.id'), nullable=False, index=True)
    enabled_state = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    form = relationship(u'Form')
    select_value = relationship(u'SelectValue')
    target_form_step_attribute = relationship(u'FormStepAttribute')


class FormStepAttribute(Base):
    __tablename__ = 'form_step_attributes'
    __table_args__ = (
        Index('form_step_id', 'form_step_id', 'attribute_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_step_id = Column(ForeignKey(u'form_steps.id'), nullable=False)
    form_step_group_id = Column(ForeignKey(u'form_step_groups.id'), nullable=False, index=True)
    attribute_id = Column(ForeignKey(u'attributes.id'), nullable=False, index=True)
    label = Column(String(255))
    required_flag = Column(Integer, nullable=False, server_default=text("'0'"))
    sort_order = Column(Integer, nullable=False, server_default=text("'0'"))
    initial_enabled_state = Column(Integer, nullable=False, server_default=text("'1'"))
    submit_on_change = Column(Integer, nullable=False, server_default=text("'0'"))
    default_value = Column(String(50))
    placeholder = Column(String(50))
    validation_message = Column(String(100))
    input_size = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    attribute = relationship(u'Attribute')
    form_step_group = relationship(u'FormStepGroup')
    form_step = relationship(u'FormStep')


class FormStepFilter(Base):
    __tablename__ = 'form_step_filters'
    __table_args__ = (
        Index('form_id', 'form_id', 'select_value_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_id = Column(ForeignKey(u'forms.id'), nullable=False)
    select_value_id = Column(ForeignKey(u'select_values.id'), nullable=False, index=True)
    target_form_step_id = Column(ForeignKey(u'form_steps.id'), nullable=False, index=True)
    enabled_state = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    form = relationship(u'Form')
    select_value = relationship(u'SelectValue')
    target_form_step = relationship(u'FormStep')


class FormStepGroupFilter(Base):
    __tablename__ = 'form_step_group_filters'
    __table_args__ = (
        Index('form_id', 'form_id', 'select_value_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_id = Column(ForeignKey(u'forms.id'), nullable=False)
    select_value_id = Column(ForeignKey(u'select_values.id'), nullable=False, index=True)
    target_form_step_group_id = Column(ForeignKey(u'form_step_groups.id'), nullable=False, index=True)
    enabled_state = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    form = relationship(u'Form')
    select_value = relationship(u'SelectValue')
    target_form_step_group = relationship(u'FormStepGroup')


class FormStepGroup(Base):
    __tablename__ = 'form_step_groups'
    __table_args__ = (
        Index('form_step_id', 'form_step_id', 'name', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_step_id = Column(ForeignKey(u'form_steps.id'), nullable=False)
    name = Column(String(255))
    sort_order = Column(Integer, nullable=False, server_default=text("'0'"))
    initial_enabled_state = Column(Integer, nullable=False, server_default=text("'1'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    form_step = relationship(u'FormStep')


class FormStep(Base):
    __tablename__ = 'form_steps'
    __table_args__ = (
        Index('form_id', 'form_id', 'name', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_id = Column(ForeignKey(u'forms.id'), nullable=False)
    name = Column(String(255))
    sort_order = Column(Integer, nullable=False, server_default=text("'0'"))
    initial_enabled_state = Column(Integer, nullable=False, server_default=text("'1'"))
    fade_enabled = Column(Integer, nullable=False, server_default=text("'1'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    form = relationship(u'Form')


class Form(Base):
    __tablename__ = 'forms'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    call_to_action = Column(String(255))
    submit_text = Column(String(255))
    publisher_list_id = Column(ForeignKey(u'publisher_lists.id'), nullable=False, index=True)
    publisher_id = Column(Integer, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    publisher_list = relationship(u'PublisherList')


class FromAddress(Base):
    __tablename__ = 'from_addresses'

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    from_address = Column(String(255), nullable=False)
    from_personal = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class HostLog(Base):
    __tablename__ = 'host_logs'

    id = Column(Integer, primary_key=True)
    host_id = Column(ForeignKey(u'hosts.id'), nullable=False, index=True)
    comment = Column(String(255), nullable=False)

    host = relationship(u'Host')


class Host(Base):
    __tablename__ = 'hosts'

    id = Column(Integer, primary_key=True)
    smtp_provider_id = Column(ForeignKey(u'smtp_providers.id'), nullable=False, index=True)
    domain_name = Column(String(255), nullable=False, unique=True)
    ip_address = Column(String(30))
    status = Column(Integer, server_default=text("'0'"))
    max_sends_daily = Column(Integer, nullable=False, server_default=text("'2000'"))
    smtp_host_name = Column(String(128), server_default=text("'smtp.sendgrid.net'"))
    smtp_auth_user = Column(String(128), server_default=text("'mholzner'"))
    smtp_port = Column(Integer, server_default=text("'587'"))
    smtp_auth_pwd = Column(String(128), server_default=text("'woodler'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    smtp_provider = relationship(u'SmtpProvider')


class KnownTrap(Base):
    __tablename__ = 'known_traps'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)


class LeadDisposition(Base):
    __tablename__ = 'lead_dispositions'

    id = Column(Integer, primary_key=True)
    lead_id = Column(ForeignKey(u'leads.id'), nullable=False, index=True)
    user_id = Column(ForeignKey(u'users.id'), nullable=False, index=True)
    advertiser_disposition_code_id = Column(ForeignKey(u'advertiser_disposition_codes.id'), nullable=False, index=True)
    created_at = Column(DateTime)
    comment = Column(String(512))

    advertiser_disposition_code = relationship(u'AdvertiserDispositionCode')
    lead = relationship(u'Lead')
    user = relationship(u'User')


class LeadMatch(Base):
    __tablename__ = 'lead_matches'
    __table_args__ = (
        Index('external_id', 'external_id', 'lead_id', 'order_id'),
        Index('order_id', 'order_id', 'created_at')
    )

    id = Column(Integer, primary_key=True)
    lead_id = Column(ForeignKey(u'leads.id'), nullable=False, index=True)
    order_id = Column(ForeignKey(u'orders.id'), nullable=False)
    status = Column(Integer, server_default=text("'0'"))
    price = Column(Numeric(12, 2), server_default=text("'0.00'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    external_id = Column(String(100))

    lead = relationship(u'Lead')
    order = relationship(u'Order')


class LeadPost(Base):
    __tablename__ = 'lead_posts'

    id = Column(Integer, primary_key=True)
    lead_match_id = Column(ForeignKey(u'lead_matches.id'), nullable=False, index=True)
    pony_phase = Column(Integer, nullable=False, server_default=text("'-1'"))
    sent_message = Column(Text)
    response_message = Column(Text)
    created_at = Column(DateTime)

    lead_match = relationship(u'LeadMatch')


class LeadType(Base):
    __tablename__ = 'lead_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Lead(Base):
    __tablename__ = 'leads'
    __table_args__ = (
        Index('user_profile_id', 'user_profile_id', 'lead_type_id', 'arrival_id', unique=True),
        Index('u_user_lead', 'user_profile_id', 'arrival_id', 'lead_type_id', unique=True)
    )

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'))
    arrival_id = Column(ForeignKey(u'arrivals.id'), nullable=False, index=True)
    lead_type_id = Column(ForeignKey(u'lead_types.id'), nullable=False, index=True, server_default=text("'1'"))
    status = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    arrival = relationship(u'Arrival')
    lead_type = relationship(u'LeadType')
    user_profile = relationship(u'UserProfile')


class LgExclusivePricing(Base):
    __tablename__ = 'lg_exclusive_pricing'
    __table_args__ = (
        Index('zip_code', 'zip_code', 'state', unique=True),
    )

    id = Column(Integer, primary_key=True)
    state = Column(String(3), nullable=False)
    county = Column(String(100))
    zip_code = Column(String(10), nullable=False)
    highest_rpt_100 = Column(Numeric(12, 2), server_default=text("'0.00'"))
    highest_rpt_150 = Column(Numeric(12, 2), server_default=text("'0.00'"))
    county_rpm = Column(Numeric(12, 2), server_default=text("'0.00'"))
    power_adj = Column(Numeric(12, 2), server_default=text("'0.00'"))
    rpt_adjusted = Column(Numeric(12, 2), server_default=text("'0.00'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class ListSplit(Base):
    __tablename__ = 'list_splits'

    id = Column(Integer, primary_key=True)
    publisher_list_id = Column(ForeignKey(u'publisher_lists.id'), nullable=False, index=True)
    offer_id = Column(ForeignKey(u'offers.id'), nullable=False, index=True)
    percentage = Column(Integer, server_default=text("'100'"))
    status = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    offer = relationship(u'Offer')
    publisher_list = relationship(u'PublisherList')


class MailHost(Base):
    __tablename__ = 'mail_hosts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email_suffix = Column(String(255))
    created_at = Column(DateTime)
    mx_validated = Column(Integer, server_default=text("'1'"))


class Md5Suppression(Base):
    __tablename__ = 'md5_suppressions'
    __table_args__ = (
        Index('md5_email', 'md5_email', 'advertiser_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    md5_email = Column(String(32), nullable=False)
    advertiser_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)


class MessageTemplate(Base):
    __tablename__ = 'message_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    html_content = Column(Text)
    text_content = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        Index('created_at', 'created_at', 'host_id', 'creative_id'),
        Index('external_id', 'external_id', 'host_id', unique=True),
        Index('external_id_2', 'external_id', 'host_id')
    )

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'), nullable=False, index=True)
    host_id = Column(ForeignKey(u'hosts.id'), nullable=False, index=True)
    creative_id = Column(ForeignKey(u'creatives.id'), nullable=False, index=True)
    status = Column(Integer, server_default=text("'0'"))
    external_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    creative = relationship(u'Creative')
    host = relationship(u'Host')
    user_profile = relationship(u'UserProfile')


class OfferSplit(Base):
    __tablename__ = 'offer_splits'

    id = Column(Integer, primary_key=True)
    list_split_id = Column(ForeignKey(u'list_splits.id'), nullable=False, index=True)
    creative_id = Column(ForeignKey(u'creatives.id'), nullable=False, index=True)
    host_id = Column(ForeignKey(u'hosts.id'), nullable=False, index=True)
    percentage = Column(Integer, server_default=text("'100'"))
    status = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    creative = relationship(u'Creative')
    host = relationship(u'Host')
    list_split = relationship(u'ListSplit')


class Offer(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False, index=True)
    lead_type_id = Column(ForeignKey(u'lead_types.id'), nullable=False, index=True)
    target_url = Column(String(255))
    click_url = Column(String(255))
    unsubscribe_url = Column(String(255))
    from_address = Column(String(255))
    from_personal = Column(String(255))
    bcc_address = Column(String(255))
    status = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')
    lead_type = relationship(u'LeadType')


class Open(Base):
    __tablename__ = 'opens'
    __table_args__ = (
        Index('message_id', 'message_id', 'ip_address', unique=True),
    )

    id = Column(Integer, primary_key=True)
    message_id = Column(ForeignKey(u'messages.id'), nullable=False)
    external_id = Column(Integer, index=True)
    open_count = Column(Integer, nullable=False, server_default=text("'0'"))
    ip_address = Column(String(30))
    user_agent = Column(String(255))
    referrer = Column(String(255))
    created_at = Column(DateTime, index=True)
    external_created_at = Column(DateTime)
    external_updated_at = Column(DateTime)

    message = relationship(u'Message')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    code = Column(String(255), unique=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False, index=True)
    lead_type_id = Column(ForeignKey(u'lead_types.id'), nullable=False, index=True, server_default=text("'1'"))
    vpl = Column(Numeric(8, 2), server_default=text("'0.00'"))
    source_id = Column(String(255))
    is_exclusive = Column(Integer, server_default=text("'0'"))
    status = Column(Integer, server_default=text("'0'"))
    cap_daily = Column(Integer, nullable=False, server_default=text("'0'"))
    cap_monthly = Column(Integer, nullable=False, server_default=text("'0'"))
    cap_total = Column(Integer, nullable=False, server_default=text("'0'"))
    pixel_id = Column(Integer)
    target_url = Column(String(512))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')
    lead_type = relationship(u'LeadType')


class PingAttribute(Base):
    __tablename__ = 'ping_attributes'
    __table_args__ = (
        Index('lead_id', 'lead_id', 'attribute_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    lead_id = Column(ForeignKey(u'leads.id'), nullable=False)
    attribute_id = Column(ForeignKey(u'attributes.id'), nullable=False, index=True)
    value = Column(String(255), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    attribute = relationship(u'Attribute')
    lead = relationship(u'Lead')


class PixelFire(Base):
    __tablename__ = 'pixel_fires'
    __table_args__ = (
        Index('k_redirect_pixel_type', 'redirect_id', 'pixel_type', unique=True),
    )

    id = Column(Integer, primary_key=True)
    redirect_id = Column(ForeignKey(u'redirects.id'), nullable=False)
    pixel_type = Column(Integer, nullable=False)
    counter = Column(Integer, server_default=text("'1'"))
    ip_address = Column(String(30))
    user_agent = Column(String(255))
    referrer = Column(String(255))
    created_at = Column(DateTime)

    redirect = relationship(u'Redirect')


class PlayEvolution(Base):
    __tablename__ = 'play_evolutions'

    id = Column(Integer, primary_key=True)
    hash = Column(String(255), nullable=False)
    applied_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    apply_script = Column(String)
    revert_script = Column(String)
    state = Column(String(255))
    last_problem = Column(String)


class ProfileAttribute(Base):
    __tablename__ = 'profile_attributes'
    __table_args__ = (
        Index('idx_profile_attribute', 'user_profile_id', 'attribute_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'), nullable=False)
    attribute_id = Column(ForeignKey(u'attributes.id'), nullable=False, index=True)
    value = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    attribute = relationship(u'Attribute')
    user_profile = relationship(u'UserProfile')


class ProfileXlAttribute(Base):
    __tablename__ = 'profile_xl_attributes'
    __table_args__ = (
        Index('idx_profileXL_attribute', 'user_profile_id', 'attribute_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'), nullable=False)
    attribute_id = Column(ForeignKey(u'attributes.id'), nullable=False, index=True)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    attribute = relationship(u'Attribute')
    user_profile = relationship(u'UserProfile')


class PublisherListMember(Base):
    __tablename__ = 'publisher_list_members'

    id = Column(Integer, primary_key=True)
    publisher_list_id = Column(ForeignKey(u'publisher_lists.id'), nullable=False, index=True)
    publisher_id = Column(ForeignKey(u'publishers.id'), nullable=False, index=True)
    cpl = Column(Numeric(12, 2), nullable=False, server_default=text("'0.00'"))
    status = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    publisher = relationship(u'Publisher')
    publisher_list = relationship(u'PublisherList')


class PublisherListOrder(Base):
    __tablename__ = 'publisher_list_orders'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    publisher_list_id = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False)
    status = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class PublisherList(Base):
    __tablename__ = 'publisher_lists'

    id = Column(Integer, primary_key=True)
    lead_type_id = Column(ForeignKey(u'lead_types.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    ext_list_id = Column(String(25), nullable=False, unique=True)
    max_lead_units = Column(Integer, server_default=text("'1'"))
    status = Column(Integer, server_default=text("'0'"))
    is_direct = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    lead_type = relationship(u'LeadType')


class Publisher(Base):
    __tablename__ = 'publishers'
    __table_args__ = (
        Index('user_name', 'user_name', 'password'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    user_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    allow_duplicates = Column(Integer, server_default=text("'0'"))
    domain_name = Column(String(255))
    domain_token = Column(String(100))
    extended_validation = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Redirect(Base):
    __tablename__ = 'redirects'

    id = Column(Integer, primary_key=True)
    click_source_id = Column(ForeignKey(u'click_sources.id'), nullable=False, index=True)
    click_target_id = Column(ForeignKey(u'click_targets.id'), nullable=False, index=True)
    destination_path = Column(String(255))
    destination_query = Column(String(255))
    referrer_domain_id = Column(ForeignKey(u'domains.id'), index=True)
    ip_address = Column(String(30))
    user_agent = Column(String(255))
    referrer = Column(String(255))
    created_at = Column(DateTime)

    click_source = relationship(u'ClickSource')
    click_target = relationship(u'ClickTarget')
    referrer_domain = relationship(u'Domain')


class ResendMessageLog(Base):
    __tablename__ = 'resend_message_logs'
    __table_args__ = (
        Index('original_message_id', 'original_message_id', 'resend_sequence_id'),
    )

    id = Column(Integer, primary_key=True)
    resend_sequence_id = Column(ForeignKey(u'resend_sequences.id'), nullable=False, index=True)
    phase = Column(Integer, nullable=False, server_default=text("'0'"))
    original_message_id = Column(ForeignKey(u'messages.id'), nullable=False)
    message_id = Column(ForeignKey(u'messages.id'), nullable=False, index=True)
    created_at = Column(DateTime)
    delay_minutes = Column(Integer)

    message = relationship(u'Message', primaryjoin='ResendMessageLog.message_id == Message.id')
    original_message = relationship(u'Message', primaryjoin='ResendMessageLog.original_message_id == Message.id')
    resend_sequence = relationship(u'ResendSequence')


class ResendMessagePhase(Base):
    __tablename__ = 'resend_message_phases'
    __table_args__ = (
        Index('resend_sequence_id_2', 'resend_sequence_id', 'phase', 'original_message_id'),
        Index('original_message_id', 'original_message_id', 'resend_sequence_id', unique=True),
        Index('updated_at', 'updated_at', 'created_at', 'resend_sequence_id', 'phase'),
        Index('resend_sequence_id', 'resend_sequence_id', 'original_message_id')
    )

    id = Column(Integer, primary_key=True)
    resend_sequence_id = Column(ForeignKey(u'resend_sequences.id'), nullable=False)
    phase = Column(Integer, nullable=False, server_default=text("'0'"))
    original_message_id = Column(ForeignKey(u'messages.id'), nullable=False)
    message_id = Column(ForeignKey(u'messages.id'), nullable=False, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    message = relationship(u'Message', primaryjoin='ResendMessagePhase.message_id == Message.id')
    original_message = relationship(u'Message', primaryjoin='ResendMessagePhase.original_message_id == Message.id')
    resend_sequence = relationship(u'ResendSequence')


class ResendSequence(Base):
    __tablename__ = 'resend_sequences'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class RgrExclusivePricing(Base):
    __tablename__ = 'rgr_exclusive_pricing'
    __table_args__ = (
        Index('zip_code', 'zip_code', 'state', unique=True),
    )

    id = Column(Integer, primary_key=True)
    zip_code = Column(String(10), nullable=False)
    state = Column(String(3), nullable=False)
    price = Column(Numeric(12, 2), server_default=text("'0.00'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class RgrSemiExclusivePricing(Base):
    __tablename__ = 'rgr_semi_exclusive_pricing'
    __table_args__ = (
        Index('zip_code', 'zip_code', 'state', unique=True),
    )

    id = Column(Integer, primary_key=True)
    zip_code = Column(String(10), nullable=False)
    state = Column(String(3), nullable=False)
    price = Column(Numeric(12, 2), server_default=text("'0.00'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class SelectValue(Base):
    __tablename__ = 'select_values'
    __table_args__ = (
        Index('form_step_attribute_id', 'form_step_attribute_id', 'select_key', unique=True),
    )

    id = Column(Integer, primary_key=True)
    form_step_attribute_id = Column(ForeignKey(u'form_step_attributes.id'), nullable=False)
    select_key = Column(String(50), nullable=False)
    select_value = Column(String(100), nullable=False)
    pre_selected = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    form_step_attribute = relationship(u'FormStepAttribute')


class SendplexBounce(Base):
    __tablename__ = 'sendplex_bounces'

    host_id = Column(Integer, primary_key=True, nullable=False)
    bounce_id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    comment = Column(String(255))


class SendplexClick(Base):
    __tablename__ = 'sendplex_clicks'

    host_id = Column(Integer, primary_key=True, nullable=False)
    click_id = Column(Integer, primary_key=True, nullable=False)
    message_id = Column(Integer, nullable=False)
    click_count = Column(Integer, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class SendplexOpen(Base):
    __tablename__ = 'sendplex_opens'

    host_id = Column(Integer, primary_key=True, nullable=False)
    open_id = Column(Integer, primary_key=True, nullable=False)
    message_id = Column(Integer, nullable=False)
    open_count = Column(Integer, nullable=False)
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    referrer = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class SendplexUnsubscribe(Base):
    __tablename__ = 'sendplex_unsubscribes'

    host_id = Column(Integer, primary_key=True, nullable=False)
    unsub_id = Column(Integer, primary_key=True, nullable=False)
    message_id = Column(Integer, nullable=False)
    reason = Column(Text)
    created_at = Column(DateTime)


class SmtpProvider(Base):
    __tablename__ = 'smtp_providers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime)


class StateBroker(Base):
    __tablename__ = 'state_brokers'
    __table_args__ = (
        Index('state_broker', 'state_id', 'callcenter_broker_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    state_id = Column(ForeignKey(u'states.id'), nullable=False)
    callcenter_broker_id = Column(ForeignKey(u'callcenter_brokers.id'), nullable=False, index=True)
    created_at = Column(DateTime)

    callcenter_broker = relationship(u'CallcenterBroker')
    state = relationship(u'State')


class StateFilter(Base):
    __tablename__ = 'state_filters'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey(u'orders.id'), nullable=False, index=True)
    is_allow = Column(Integer, server_default=text("'1'"))
    pony_phase = Column(Integer)
    status = Column(Integer, server_default=text("'1'"))
    states = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    order = relationship(u'Order')


class State(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    state_code = Column(String(2), nullable=False, unique=True)
    created_at = Column(DateTime)


class SubjectLine(Base):
    __tablename__ = 'subject_lines'

    id = Column(Integer, primary_key=True)
    subject_line = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class TimeFilter(Base):
    __tablename__ = 'time_filters'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey(u'orders.id'), nullable=False, index=True)
    is_allow = Column(Integer, server_default=text("'1'"))
    pony_phase = Column(Integer)
    status = Column(Integer, server_default=text("'1'"))
    times = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    order = relationship(u'Order')


class Unsubscribe(Base):
    __tablename__ = 'unsubscribes'

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'), nullable=False, index=True)
    message_id = Column(ForeignKey(u'messages.id'), unique=True)
    external_id = Column(Integer, index=True)
    ip_address = Column(String(30))
    user_agent = Column(String(255))
    referrer = Column(String(255))
    created_at = Column(DateTime)
    external_created_at = Column(DateTime)

    message = relationship(u'Message')
    user_profile = relationship(u'UserProfile')


class UserListMember(Base):
    __tablename__ = 'user_list_members'

    id = Column(Integer, primary_key=True)
    user_list_id = Column(ForeignKey(u'user_lists.id'), nullable=False, index=True)
    user_profile_id = Column(ForeignKey(u'user_profiles.id'), nullable=False, index=True)

    user_list = relationship(u'UserList')
    user_profile = relationship(u'UserProfile')


class UserList(Base):
    __tablename__ = 'user_lists'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime)
    status = Column(Integer, server_default=text("'0'"))


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    email_md5 = Column(String(32), nullable=False, unique=True)
    mail_host_id = Column(ForeignKey(u'mail_hosts.id'), nullable=False, index=True)
    is_trap = Column(Integer, nullable=False, server_default=text("'0'"))
    created_at = Column(DateTime)
    last_seen_at = Column(DateTime)

    mail_host = relationship(u'MailHost')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    advertiser_id = Column(ForeignKey(u'advertisers.id'), nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    handle = Column(String(25), nullable=False)
    password_md5 = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    advertiser = relationship(u'Advertiser')


class UtilityLookup(Base):
    __tablename__ = 'utility_lookup'
    __table_args__ = (
        Index('state', 'state', 'lg_name', 'rgr_name', unique=True),
    )

    id = Column(Integer, primary_key=True)
    state = Column(String(3), nullable=False)
    lg_name = Column(String(100), nullable=False, server_default=text("'other'"))
    rgr_name = Column(String(100), nullable=False, server_default=text("'other'"))
    frequent = Column(Integer, server_default=text("'0'"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class ZipFilter(Base):
    __tablename__ = 'zip_filters'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey(u'orders.id'), nullable=False, index=True)
    is_allow = Column(Integer, server_default=text("'1'"))
    pony_phase = Column(Integer)
    status = Column(Integer, server_default=text("'1'"))
    zipcodes = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    order = relationship(u'Order')
