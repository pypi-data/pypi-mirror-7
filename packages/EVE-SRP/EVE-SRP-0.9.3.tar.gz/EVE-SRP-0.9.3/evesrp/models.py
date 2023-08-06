from __future__ import absolute_import
import datetime as dt
from decimal import Decimal
import six
from six.moves import filter, map, range
from sqlalchemy import event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import DDL, DropIndex
from flask import Markup

from . import db
from .util import DeclEnum, classproperty, AutoID, Timestamped, AutoName,\
        unistr, ensure_unicode, PrettyDecimal, PrettyNumeric, DateTime
from .auth import PermissionType


if six.PY3:
    unicode = str

class ActionType(DeclEnum):

    # The actual stored values are single character to make it easier on
    # engines that don't support native enum types.

    #: Status for a request being evaluated.
    evaluating = u'evaluating', u'Evaluating'

    #: Status for a request that has been evaluated and is awaitng payment.
    approved = u'approved', u'Approved'

    #: Status for a request that has been paid. This is a terminatint state.
    paid = u'paid', u'Paid'

    #: Status for a requests that has been rejected. This is a terminating
    #: state.
    rejected = u'rejected', u'Rejected'

    #: Status for a request that is missing details and needs further action.
    incomplete = u'incomplete', u'Incomplete'

    #: A special type of :py:class:`Action` representing a comment made on the
    #: request.
    comment = u'comment', u'Comment'

    @classproperty
    def finalized(cls):
        return frozenset((cls.paid, cls.rejected))

    @classproperty
    def pending(cls):
        return frozenset((cls.evaluating, cls.approved, cls.incomplete))

    @classproperty
    def statuses(cls):
        return frozenset((cls.evaluating, cls.approved, cls.paid, cls.rejected,
                cls.incomplete))


class ActionError(ValueError):
    """Error raised for invalid state changes for a :py:class:`Request`."""
    pass


class Action(db.Model, AutoID, Timestamped, AutoName):
    """Actions change the state of a Request.
    
    :py:class:`Request`\s enforce permissions when actions are added to them.
    If the user adding the action does not have the appropriate
    :py:class:`~.Permission`\s in the request's :py:class:`Division`, an
    :py:exc:`ActionError` will be raised.

    With the exception of the :py:attr:`comment <ActionType.comment>` action
    (which just adds text to a request), actions change the
    :py:attr:`~Request.status` of a Request.
    """

    #: The action be taken. See :py:class:`ActionType` for possible values.
    # See set_request_type below for the effect setting this attribute has on
    # the parent Request.
    type_ = db.Column(ActionType.db_type(), nullable=False)

    #: The ID of the :py:class:`Request` this action applies to.
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))

    #: The :py:class:`Request` this action applies to.
    request = db.relationship('Request', back_populates='actions')

    #: The ID of the :py:class:`~.User` who made this action.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #: The :py:class:`~.User` who made this action.
    user = db.relationship('User', back_populates='actions')

    #: Any additional notes for this action.
    note = db.Column(db.Text(convert_unicode=True))

    def __init__(self, request, user, note=None, type_=None):
        if type_ is not None:
            self.type_ = type_
        self.user = user
        self.note = ensure_unicode(note)
        # timestamp has to be an actual value (besides None) before the request
        # is set so thhe request's validation doesn't fail.
        self.timestamp = dt.datetime.utcnow()
        self.request = request

    @db.validates('type_')
    def _set_request_type(self, attr, type_):
        """Validator action for :py:attr:`type_` for updating the parent
        :py:class:`Request`\\'s :py:attr:`~Request.status`.

        It only updates the status for non-``None`` and non-comment actions.
        """
        if self.request is not None:
            if type_ != ActionType.comment and self.timestamp >=\
                    self.request.actions[0].timestamp:
                self.request.status = type_
        return type_

    def __repr__(self):
        return "{x.__class__.__name__}({x.request}, {x.user}, {x.type_})".\
                format(x=self)


class ModifierError(ValueError):
    """Error raised when a modification is attempted to a :py:class:`Request`
    when it's in an invalid state.
    """
    pass


class Modifier(db.Model, AutoID, Timestamped, AutoName):
    """Modifiers apply bonuses or penalties to Requests.

    This is an abstract base class for the pair of concrete implementations.
    Modifiers can be voided at a later date. The user who voided a modifier and
    when it was voided are recorded.

    :py:class:`Request`\s enforce permissions when modifiers are added. If the
    user adding a modifier does not have the appropriate
    :py:class:`~.Permission`\s in the request's :py:class:`~.Division`, a
    :py:exc:`ModifierError` will be raised.
    """

    #: Discriminator column for SQLAlchemy
    _type = db.Column(db.String(20, convert_unicode=True), nullable=False)

    #: The ID of the :py:class:`Request` this modifier applies to.
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))

    #: The :py:class:`Request` this modifier applies to.
    request = db.relationship('Request', back_populates='modifiers')

    #: The ID of the :py:class`~.User` who added this modifier.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #: The :py:class:`~.User` who added this modifier.
    user = db.relationship('User', foreign_keys=[user_id])

    #: Any notes explaining this modification.
    note = db.Column(db.Text(convert_unicode=True))

    #: The ID of the :py:class:`~.User` who voided this modifier (if voided).
    voided_user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
            nullable=True)

    #: The :py:class:`~.User` who voided this modifier if it has been voided.
    voided_user = db.relationship('User', foreign_keys=[voided_user_id])

    #: If this modifier has been voided, this will be the timestamp of when it
    #: was voided.
    voided_timestamp = db.Column(DateTime)

    @hybrid_property
    def voided(self):
        return self.voided_user is not None and \
                self.voided_timestamp is not None

    @classmethod
    def _voided_select(cls):
        """Create a subquery with two columns, ``modifier_id`` and ``voided``.

        Used for the expressions of :py:attr:`voided` and
        :py:attr:`Request.payout`.
        """
        user = db.select([cls.id.label('modifier_id'),
                cls.voided_user_id.label('user_id')]).alias('user_sub')
        timestamp = db.select([cls.id.label('modifier_id'),
                cls.voided_timestamp.label('timestamp')]).alias('timestamp_sub')
        columns = [
            db.and_(
                user.c.user_id != None,
                timestamp.c.timestamp != None).label('voided'),
            user.c.modifier_id.label('modifier_id'),
        ]
        return db.select(columns).where(
                user.c.modifier_id == timestamp.c.modifier_id)\
                .alias('voided_sub')

    @voided.expression
    def voided(cls):
        return cls._voided_select().c.voided

    @declared_attr
    def __mapper_args__(cls):
        """SQLAlchemy late-binding attribute to set mapper arguments.

        Obviates subclasses from having to specify polymorphic identities.
        """
        cls_name = unicode(cls.__name__)
        args = {'polymorphic_identity': cls_name}
        if cls_name == u'Modifier':
            args['polymorphic_on'] = cls._type
        return args

    def __init__(self, request, user, note, value):
        self.user = user
        self.note = ensure_unicode(note)
        self.value = value
        self.request = request

    def __repr__(self):
        return ("{x.__class__.__name__}({x.request}, {x.user},"
                "{x}, {x.voided})".format(x=self, value=self))

    def void(self, user):
        """Mark this modifier as void.

        :param user: The user voiding this modifier
        :type user: :py:class:`~.User`
        """
        if self.request.status != ActionType.evaluating:
            raise ModifierError("Modifiers can only be voided when the request"
                                " is in the evaluating state.")
        if not user.has_permission(PermissionType.review,
                self.request.division):
            raise ModifierError("You must be a reviewer to be able to void "
                                "modifiers.")
        self.voided_user = user
        self.voided_timestamp = dt.datetime.utcnow()


@unistr
class AbsoluteModifier(Modifier):
    """Subclass of :py:class:`Modifier` for representing absolute
    modifications.

    Absolute modifications are those that are not dependent on the value of
    :py:attr:`Request.base_payout`.
    """

    id = db.Column(db.Integer, db.ForeignKey('modifier.id'), primary_key=True)

    #: How much ISK to add or remove from the payout
    value = db.Column(PrettyNumeric(precision=15, scale=2), nullable=False,
            default=Decimal(0))

    def __unicode__(self):
        return u'{}M ISK {}'.format(self.value / 1000000,
                u'bonus' if self.value >= 0 else u'penalty')


@unistr
class RelativeModifier(Modifier):
    """Subclass of :py:class:`Modifier` for representing relative modifiers.

    Relative modifiers depend on the value of :py:attr:`Modifier.base_payout`
    to calculate their effect.
    """

    id = db.Column(db.Integer, db.ForeignKey('modifier.id'), primary_key=True)

    #: What percentage of the payout to add or remove
    value = db.Column(db.Numeric(precision=8, scale=5), nullable=False,
            default=Decimal(0))

    def __unicode__(self):
        pretty_value = unicode(self.value * 100)
        pretty_value = pretty_value.lstrip('-')
        pretty_value = pretty_value.rstrip('0')
        pretty_value = pretty_value.rstrip('.')
        return u'{}% {}'.format(pretty_value,
                u'bonus' if self.value >= 0 else u'penalty')


class Request(db.Model, AutoID, Timestamped, AutoName):
    """Requests represent SRP requests."""

    #: The ID of the :py:class:`~.User` who submitted this request.
    submitter_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #: The :py:class:`~.User` who submitted this request.
    submitter = db.relationship('User', back_populates='requests')

    #: The ID of the :py:class`~.Division` this request was submitted to.
    division_id = db.Column(db.Integer, db.ForeignKey('division.id'),
            nullable=False)

    #: The :py:class:`~.Division` this request was submitted to.
    division = db.relationship('Division', back_populates='requests')

    #: A list of :py:class:`Action`\s that have been applied to this request,
    #: sorted in the order they were applied.
    actions = db.relationship('Action', back_populates='request',
            order_by='desc(Action.timestamp)')

    #: A list of all :py:class:`Modifier`\s that have been applied to this
    #: request, regardless of wether they have been voided or not. They're
    #: sorted in the order they were added.
    modifiers = db.relationship('Modifier', back_populates='request',
            order_by='desc(Modifier.timestamp)', lazy='dynamic')

    #: The URL of the source killmail.
    killmail_url = db.Column(db.String(512, convert_unicode=True),
            nullable=False)

    #: The ID of the :py:class:`~.Pilot` for the killmail.
    pilot_id = db.Column(db.Integer, db.ForeignKey('pilot.id'), nullable=False)

    #: The :py:class:`~.Pilot` who was the victim in the killmail.
    pilot = db.relationship('Pilot', back_populates='requests')

    #: The corporation of the :py:attr:`pilot` at the time of the killmail.
    corporation = db.Column(db.String(150, convert_unicode=True),
            nullable=False, index=True)

    #: The alliance of the :py:attr:`pilot` at the time of the killmail.
    alliance = db.Column(db.String(150, convert_unicode=True), nullable=True,
            index=True)

    #: The type of ship that was destroyed.
    ship_type = db.Column(db.String(75, convert_unicode=True), nullable=False,
            index=True)

    # TODO: include timezones
    #: The date and time of when the ship was destroyed.
    kill_timestamp = db.Column(DateTime, nullable=False, index=True)

    base_payout = db.Column(PrettyNumeric(precision=15, scale=2), default=0.0)
    """The base payout for this request.

    This value is clamped to a lower limit of 0. It can only be changed when
    this request is in an :py:attr:`~ActionType.evaluating` state, or else a
    :py:exc:`ModifierError` will be raised.
    """

    #: Supporting information for the request.
    details = db.deferred(db.Column(db.Text(convert_unicode=True)))

    #: The current status of this request
    status = db.Column(ActionType.db_type(), nullable=False,
            default=ActionType.evaluating)
    """This attribute is automatically kept in sync as :py:class:`Action`\s are
    added to the request. It should not be set otherwise.

    At the time an :py:class:`Action` is added to this request, the type of
    action is checked and the state diagram below is enforced. If the action is
    invalid, an :py:exc:`ActionError` is raised.

    .. digraph:: request_workflow

        rankdir="LR";

        sub [label="submitted", shape=plaintext];

        node [style="dashed, filled"];

        eval [label="evaluating", fillcolor="#fcf8e3"];
        rej [label="rejected", style="solid, filled", fillcolor="#f2dede"];
        app [label="approved", fillcolor="#d9edf7"];
        inc [label="incomplete", fillcolor="#f2dede"];
        paid [label="paid", style="solid, filled", fillcolor="#dff0d8"];

        sub -> eval;
        eval -> rej [label="R"];
        eval -> app [label="R"];
        eval -> inc [label="R"];
        rej -> eval [label="R"];
        inc -> eval [label="R, S"];
        inc -> rej [label="R"];
        app -> paid [label="P"];
        app -> eval [label="R"];
        paid -> eval [label="P"];
        paid -> app [label="P"];

    R means a reviewer can make that change, S means the submitter can make
    that change, and P means payers can make that change. Solid borders are
    terminal states.
    """

    #: The solar system this loss occured in.
    system = db.Column(db.String(25, convert_unicode=True), nullable=False,
            index=True)

    #: The constellation this loss occured in.
    constellation = db.Column(db.String(25, convert_unicode=True),
            nullable=False, index=True)

    #: The region this loss occured in.
    region = db.Column(db.String(25, convert_unicode=True), nullable=False,
            index=True)

    @hybrid_property
    def payout(self):
        # Evaluation method for payout:
        # almost_payout = (sum(absolute_modifiers) + base_payout)
        # payout = almost_payout + (sum(percentage_modifiers) * almost_payout)
        voided = Modifier._voided_select()
        abs_mods = db.session.query(db.func.sum(AbsoluteModifier.value))\
                .join(Request)\
                .filter(Modifier.request_id==self.id)\
                .filter(~voided.c.voided)\
                .filter(voided.c.modifier_id==Modifier.id)
        rel_mods = db.session.query(db.func.sum(RelativeModifier.value))\
                .join(Request)\
                .filter(Modifier.request_id==self.id)\
                .filter(~voided.c.voided)\
                .filter(voided.c.modifier_id==Modifier.id)
        absolute = abs_mods.one()[0]
        if absolute is None:
            absolute = Decimal(0)
        relative = rel_mods.one()[0]
        if relative is None:
            relative = Decimal(0)
        payout = self.base_payout + absolute
        payout = payout + (payout * relative)

        return PrettyDecimal(payout)

    @classmethod
    def _payout_expression(cls):
        # Get the sum of all absolute and relative modifiers
        voided = Modifier._voided_select()
        # Was having trouble bending SQLAlchemy to my will, specifically with
        # it adding joins for sublasses modifiers.
        mod_table = Modifier.__table__
        abs_table = AbsoluteModifier.__table__
        rel_table = RelativeModifier.__table__
        # Prepare subqueries for the eventual summing
        absolute = db.select([
                        mod_table.c.id.label('id'),
                        abs_table.c.value.label('value'),
                        mod_table.c.request_id.label('request_id')])\
                .select_from(db.join(abs_table, mod_table,
                        mod_table.c.id == abs_table.c.id))\
                .alias()
        absolute = db.select([
                        absolute.c.value.label('value'),
                        absolute.c.request_id.label('request_id')])\
                .where(~voided.c.voided)\
                .select_from(db.join(absolute, voided,
                        absolute.c.id == voided.c.modifier_id)).alias()
        relative = db.select([
                        mod_table.c.id.label('id'),
                        rel_table.c.value.label('value'),
                        mod_table.c.request_id.label('request_id')])\
                .select_from(db.join(rel_table, mod_table,
                        mod_table.c.id == rel_table.c.id))\
                .alias()
        relative = db.select([
                        relative.c.value.label('value'),
                        relative.c.request_id.label('request_id')])\
                .where(~voided.c.voided)\
                .select_from(db.join(relative, voided,
                        relative.c.id == voided.c.modifier_id)).alias()
        # Sum modifiers grouped by request id
        abs_sum = db.select([
                        cls.id.label('request_id'),
                        cls.base_payout.label('base_payout'),
                        db.func.sum(absolute.c.value).label('sum')])\
                .select_from(db.outerjoin(Request, absolute,
                        Request.id == absolute.c.request_id))\
                .group_by(Request.id)\
                .alias()
        rel_sum = db.select([
                        cls.id.label('request_id'),
                        db.func.sum(relative.c.value).label('sum')])\
                .select_from(db.outerjoin(Request, relative,
                        Request.id == relative.c.request_id))\
                .group_by(Request.id)\
                .alias()
        # Return a subquery with the request id and the caclulated payout.
        # missing values are assumed to be 0.
        total_sum = db.select([
                        abs_sum.c.request_id.label('id'),
                        ((
                            abs_sum.c.base_payout.label('base_payout') +
                            db.case([(abs_sum.c.sum == None, Decimal(0))],
                                    else_=abs_sum.c.sum).label('absolute')) *
                        (
                            1 +
                            db.case([(rel_sum.c.sum == None, Decimal(0))],
                                    else_=rel_sum.c.sum).label('relative')))\
                        .label('payout')])\
                .select_from(db.join(abs_sum, rel_sum,
                        abs_sum.c.request_id == rel_sum.c.request_id))\
                .alias()
        return total_sum

    @payout.expression
    def payout(cls):
        payouts = cls._payout_expression()
        stmt = db.select([payouts.c.payout])\
                .where(cls.id == payouts.c.id)\
                .label('payout')
        return stmt

    @hybrid_property
    def finalized(self):
        return self.status in ActionType.finalized

    @finalized.expression
    def finalized(cls):
        return db.or_(cls.status == ActionType.paid,
                cls.status == ActionType.rejected)

    def __init__(self, submitter, details, division, killmail, **kwargs):
        """Create a :py:class:`Request`.

        :param submitter: The user submitting this request
        :type submitter: :py:class:`~.User`
        :param str details: Supporting details for this request
        :param division: The division this request is being submitted to
        :type division: :py:class:`~.Division`
        :param killmail: The killmail this request pertains to
        :type killmail: :py:class:`~.Killmail`
        """
        self.division = division
        self.details = details
        self.submitter = submitter
        # Pull basically everything else from the killmail object
        # The base Killmail object has an iterator defined that returns tuples
        # of Request attributes and values for those attributes
        for attr, value in killmail:
            setattr(self, attr, value)
        # Set default values before a flush
        if self.base_payout is None and 'base_payout' not in kwargs:
            self.base_payout = Decimal(0)
        super(Request, self).__init__(**kwargs)

    @db.validates('base_payout')
    def _validate_payout(self, attr, value):
        """Ensures that base_payout is positive. The value is clamped to 0."""
        if self.status == ActionType.evaluating or self.status is None:
            if value is None or value < 0:
                return Decimal('0')
            else:
                return Decimal(value)
        else:
            raise ModifierError(u"The request must be in the evaluating state "
                                u"to change the base payout.")

    state_rules = {
        ActionType.evaluating: {
            ActionType.incomplete: (PermissionType.review,),
            ActionType.rejected: (PermissionType.review,),
            ActionType.approved: (PermissionType.review,),
            ActionType.evaluating: (PermissionType.review,
                PermissionType.submit),
        },
        ActionType.incomplete: {
            ActionType.rejected: (PermissionType.review,),
            ActionType.evaluating: (PermissionType.review,
                PermissionType.submit),
        },
        ActionType.rejected: {
            ActionType.evaluating: (PermissionType.review,),
        },
        ActionType.approved: {
            ActionType.evaluating: (PermissionType.review,),
            ActionType.paid: (PermissionType.pay,),
        },
        ActionType.paid: {
            ActionType.approved: (PermissionType.pay,),
            ActionType.evaluating: (PermissionType.pay,),
        },
    }

    def valid_actions(self, user):
        """Get valid actions (besides comment) the given user can perform."""
        possible_actions = self.state_rules[self.status]
        def action_filter(action):
            return user.has_permission(possible_actions[action],
                    self.division)
        return filter(action_filter, possible_actions)

    @db.validates('status')
    def _validate_status(self, attr, new_status):
        """Enforces that status changes follow the status state diagram below.
        When an invalid change is attempted, :py:class:`ActionError` is
        raised.

        """

        def check_status(*valid_states):
            if new_status not in valid_states:
                raise ActionError(u"{} is not a valid status to change "
                        u"to from {} (valid options: {})".format(new_status,
                                self.status, valid_states))


        if new_status == ActionType.comment:
            raise ValueError(u"ActionType.comment is not a valid status")
        # Initial status
        if self.status is None:
            return new_status
        rules = self.state_rules[self.status]
        if new_status not in rules:
            raise ActionError(u"{} is not a valid status to change to from {} "
                    u"(valid options: {})".format(new_status,
                            self.status, list(six.iterkeys(rules))))
        return new_status

    @db.validates('actions')
    def _update_status_from_action(self, attr, action):
        """Updates :py:attr:`status` whenever a new :py:class:`~.Action`
        is added and verifies permissions.
        """
        if action.type_ is None:
            # Action.type_ are not nullable, so rely on the fact that it will
            # be set later to let it slide now.
            return action
        elif action.type_ != ActionType.comment:
            rules = self.state_rules[self.status]
            self.status = action.type_
            permissions = rules[action.type_]
            if not action.user.has_permission(permissions, self.division):
                raise ActionError(u"Insufficient permissions to perform that "
                                  u"action.")
        elif action.type_ == ActionType.comment:
            if action.user != self.submitter \
                    and not action.user.has_permission(PermissionType.elevated,
                            self.division):
                raise ActionError(u"You must either own or have special"
                                  u"privileges to comment on this request.")
        return action

    def __repr__(self):
        return "{x.__class__.__name__}({x.submitter}, {x.division}, {x.id})".\
                format(x=self)

    @db.validates('modifiers')
    def _validate_add_modifier(self, attr, modifier):
        if self.status != ActionType.evaluating:
            raise ModifierError(u"Modifiers can only be added when the request"
                                u" is in an evaluating state.")
        if not modifier.user.has_permission(PermissionType.review,
                self.division):
            raise ModifierError(u"Only reviewers can add modifiers.")
        return modifier

    @property
    def transformed(self):
        """Get a special HTML representation of an attribute.

        Divisions can have a transformer defined on various attributes that
        output a URL associated with that attribute. This property provides
        easy access to the output of any transformed attributes on this
        request.
        """
        class RequestTransformer(object):
            def __getattr__(self, attr):
                raw_value = getattr(self._request, attr)
                if attr in self._request.division.transformers:
                    transformer = self._request.division.transformers[attr]
                    return Markup(u'<a href="{link}">{value}</a>').format(
                            link=transformer(raw_value), value=str(raw_value))
                else:
                    return raw_value

            def __init__(self, request):
                self._request = request
        return RequestTransformer(self)


# The next few lines are responsible for adding a full text search index on the
# Request.details column for MySQL.
_create_fts = DDL('CREATE FULLTEXT INDEX ix_%(table)s_details_fulltext '
                       'ON %(table)s (details);')
_drop_fts = DDL('DROP INDEX ix_%(table)s_details_fulltext ON %(table)s')


event.listen(
        Request.__table__,
        'after_create',
        _create_fts.execute_if(dialect='mysql')
)


event.listen(
        Request.__table__,
        'before_drop',
        _drop_fts.execute_if(dialect='mysql')
)
