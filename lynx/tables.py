from sqlalchemy import Column, Integer, String, DECIMAL, DATE, BOOLEAN, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('mysql+pymysql://root:@localhost/easiersolar_testing')
Base = declarative_base(engine)
########################################################################
class Browsers(Base):
    """"""
    __tablename__ = 'browsers'

    id = Column(Integer, primary_key=True)
    browser_id = Column(String)
    session_children = relationship("Sessions", back_populates="browser")

#----------------------------------------------------------------------
    def __init__(self, id, browser_id, children):
        """"""
        self.id = id
        self.browser_id = browser_id
        self.session_children = children

    #----------------------------------------------------------------------
    def __repr__(self):
        """"""
        return "<Browser(%s: '%s') - Sessions: %s>" % (self.id, self.browser_id, self.session_children)
#----------------------------------------------------------------------
########################################################################
class Sessions(Base):
    """"""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    browser_id = Column(Integer, ForeignKey('browsers.id'))
    browser = relationship('Browsers')
    event_children = relationship("Events")
    attributes = relationship("SessionAttributes", back_populates='session')
    user_agent = Column(String)
    revenue = relationship("Revenues", uselist=False)
    created_at = Column(DATE)
    last_activity = Column(DATE)
    is_robot = Column(BOOLEAN)

#----------------------------------------------------------------------
    def __init__(self, id, browser_id, browser, events, attributes, user_agent, revenue, created_at, last_activity, is_robot):
        """"""
        self.id = id
        self.browser_id = browser_id
        self.browser = browser
        self.event_children = events
        self.attributes = attributes
        self.user_agent = user_agent
        self.revenue = revenue
        self.created_at = created_at
        self.last_activity = last_activity
        self.is_robot = is_robot

#----------------------------------------------------------------------
    def __repr__(self):
        """"""
        rep = "<Session(%s) - Events: %s>" % (self.id, self.event_children)
        if len(self.attributes) > 0:
            rep += " - Attributes: %s" % (self.attributes)
        if self.revenue :
            rep += " - Revenue: %s, %s" % (self.revenue.con_f, self.revenue.total_revenue)
        if self.browser:
            rep += " - Browser: %s" % (self.browser)
        return rep

    def as_dict(self):
        attrs = vars(self)
        return '| '.join("%s: '%s'" % item for item in attrs.items())
########################################################################
#----------------------------------------------------------------------
class Events(Base):
    """"""
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    event_type_id = Column(Integer, ForeignKey('event_types.id'))
    event_type = relationship("EventTypes")
    attributes = relationship("EventAttributes")
    parent_event_id = Column(Integer, ForeignKey('events.id'))
    form = relationship('Forms', uselist=False)
    created_at = Column(DATE)

#----------------------------------------------------------------------
    def __init__(self, id, session_id, event_type_id, event_type, parent_event_id, form, created_at):
        """"""
        self.id = id
        self.session_id = session_id
        self.event_type_id = event_type_id
        self.event_type = event_type
        self.parent_event_id = parent_event_id
        self.form = form
        self.created_at = created_at

#----------------------------------------------------------------------
    def __repr__(self):
        """"""
        rep = "<Event(%s, %s, parent_event:%s) >" % (self.id, self.event_type.name,
                                                                      self.parent_event_id)
        if len(self.attributes) > 0:
            rep += " - Attributes: %s" % (self.attributes)
        if self.form:
            rep += " - Form: %s" % (self.form)
        return rep

    def event_type_name(self):
        return self.event_type.name

    def as_dict(self):
        attrs = vars(self)
        return '| '.join("%s: '%s'" % item for item in attrs.items())
#----------------------------------------------------------------------
########################################################################
#----------------------------------------------------------------------
class EventTypes(Base):
    """"""
    __tablename__ = 'event_types'

    id = Column(Integer, primary_key=True)
    name = Column(String)

#----------------------------------------------------------------------
    def __init__(self, id, name):
        """"""
        self.id = id
        self.name = name

#----------------------------------------------------------------------
########################################################################
#----------------------------------------------------------------------
class Attributes(Base):
    """"""
    __tablename__ = 'attributes'

    id = Column(Integer, primary_key=True)
    name = Column(String)

#----------------------------------------------------------------------
    def __init__(self, id, name):
        """"""
        self.id = id
        self.name = name

#----------------------------------------------------------------------
    def __repr__(self):
        return "<Attributes(%s, %s)>" % (self.id, self.name)

#----------------------------------------------------------------------
########################################################################
#----------------------------------------------------------------------
class EventAttributes(Base):
    """"""
    __tablename__ = 'event_attributes'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    attribute_id = Column(Integer, ForeignKey('attributes.id'))
    attribute = relationship("Attributes")
    value = Column(String)

#----------------------------------------------------------------------
    def __init__(self, id, event_id, attribute_id, attribute, value):
        """"""
        self.id = id
        self.event_id = event_id
        self.attribute_id = attribute_id
        self.attribute = attribute
        self.value = value

#----------------------------------------------------------------------
    def __repr__(self):
        """"""
        if self.attribute :
            return "<Event Attribute(%s, %s)>" % (self.attribute.name, self.value)
        else:
            return "<Event Attribute(%s)>" % (self.value)

    def attribute_name(self):
        if self.attribute :
            return self.attribute.name
        else :
            return ""

    def as_dict(self):
        attrs = vars(self)
        return '| '.join("%s: '%s'" % item for item in attrs.items())
#----------------------------------------------------------------------
########################################################################
#----------------------------------------------------------------------
class SessionAttributes(Base):
    """"""
    __tablename__ = 'session_attributes'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    session = relationship('Sessions', back_populates='attributes')
    attribute_id = Column(Integer, ForeignKey('attributes.id'))
    attribute = relationship("Attributes")
    value = Column(String)
    created_at = Column(DATE)

    #----------------------------------------------------------------------
    def __init__(self, id, session_id, session, attribute_id, attribute, value):
        """"""
        self.id = id
        self.session_id = session_id
        self.session = session
        self.attribute_id = attribute_id
        self.attribute = attribute
        self.value = value

    #----------------------------------------------------------------------
    def __repr__(self):
        """"""
        return "<Session Attribute(%s, %s)>" % (self.attribute.name, self.value)

    def attribute_name(self):
        if self.attribute :
            return self.attribute.name
        else :
            return ""

    def as_dict(self):
        attrs = vars(self)
        return '| '.join("%s: '%s'" % item for item in attrs.items())
#----------------------------------------------------------------------
########################################################################
#----------------------------------------------------------------------
class Revenues(Base):
    """"""
    __tablename__ = 'revenues'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    total_revenue = Column(DECIMAL)
    con_f = Column(Integer)

    #----------------------------------------------------------------------
    def __init__(self, id, session_id, total_revenue, con_f):
        """"""
        self.id = id
        self.session_id = session_id
        self.total_revenue = total_revenue
        self.con_f = con_f

    #----------------------------------------------------------------------
    def __repr__(self):
        """"""
        return "<Revenue(%s, %s)>" % (self.total_revenue, self.con_f)
#----------------------------------------------------------------------
########################################################################
#----------------------------------------------------------------------
class Forms(Base):
    """"""
    __tablename__ = 'forms'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    property_ownership = Column(String)
    electric_bill = Column(String)
    electric_company = Column(String)
    phone_home = Column(String)
    leadid_token = Column(String)
    domtok = Column(String)
    ref = Column(String)
    xxTrustedFormCertUrl = Column(String)
    xxTrustedFormToken = Column(String)
    created_at = Column(DATE)

#----------------------------------------------------------------------
    def __init__(self, id, event_id, first_name, last_name, email, street, city, state, zip, property_ownership,
                 electric_bill, electric_company, phone_home, leadid_token, domtok, ref, xxTrustedFormCertUrl,
                 xxTrustedFormToken, created_at):
        """"""
        self.id = id
        self.event_id = event_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip
        self.property_ownership = property_ownership
        self.electric_bill = electric_bill
        self.electric_company = electric_company
        self.phone_home = phone_home
        self.leadid_token = leadid_token
        self.domtok = domtok
        self.ref = ref
        self.xxTrustedFormCertUrl = xxTrustedFormCertUrl
        self.xxTrustedFormToken = xxTrustedFormToken
        self.created_at = created_at

#----------------------------------------------------------------------
    def __repr__(self):
        """"""
        return "<Form(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)>"\
               % (self.id, self.event_id, self.first_name, self. last_name, self.email, self.street, self.city,
                  self.state, self.zip, self.property_ownership, self.electric_bill, self.electric_company,
                  self.phone_home, self.leadid_token, self.domtok, self.ref, self.xxTrustedFormCertUrl,
                  self.xxTrustedFormToken)

    def as_dict(self):
        attrs = vars(self)
        return '| '.join("%s: '%s'" % item for item in attrs.items())
#----------------------------------------------------------------------