from __future__ import absolute_import
from collections import OrderedDict
import re

from flask import render_template, abort, url_for, flash, Markup, request,\
    redirect, current_app, Blueprint, Markup, json, jsonify, make_response
from flask.views import View
from flask.ext.login import login_required, current_user
from flask.ext.wtf import Form
import six
from six.moves import map
from wtforms.fields import SelectField, SubmitField, TextAreaField, HiddenField
from wtforms.fields.html5 import URLField, DecimalField
from wtforms.validators import InputRequired, AnyOf, URL, ValidationError,\
    StopValidation

from .. import db
from ..models import Request, Modifier, Action, ActionType, ActionError,\
        ModifierError, AbsoluteModifier, RelativeModifier
from ..util import xmlify
from ..auth import PermissionType
from ..auth.models import Division, Pilot, Permission, User, Group, Note,\
    APIKey


if six.PY3:
    unicode = str


blueprint = Blueprint('requests', __name__)


class RequestListing(View):
    """Abstract class for lists of :py:class:`~evesrp.models.Request`\s.

    Subclasses will be able to respond to both normal HTML requests as well as
    to API requests with JSON.
    """

    #: The template to use for listing requests
    template = 'list_requests.html'

    #: Decorators to apply to the view functions
    decorators = [login_required]

    def requests(self, division_id=None):
        """Returns a list :py:class:`~.Request`\s belonging to
        the specified :py:class:`~.Division`, or all divisions if
        ``None``. Must be implemented by subclasses, as this is an abstract
        method.

        :param int division_id: ID number of a :py:class:`~.Division`, or
            ``None``.
        :returns: :py:class:`~.models.Request`\s
        :rtype: iterable
        """
        raise NotImplementedError()

    def dispatch_request(self, division_id=None, page=1, **kwargs):
        """Returns the response to requests.

        Part of the :py:class:`flask.views.View` interface.
        """
        if request.is_json or request.is_xhr:
            return jsonify(requests=self.requests(division_id))
        if request.is_rss:
            return xmlify('rss.xml', content_type='application/rss+xml',
                    requests=self.requests(division_id),
                    title=(kwargs['title'] if 'title' in kwargs else u''),
                    main_link=url_for(request.endpoint,
                        division_id=division_id, _external=True))
        if request.is_xml:
            return xmlify('request_list.xml',
                    requests=self.requests(division_id))
        pager = self.requests(division_id).paginate(page, per_page=20)
        return render_template(self.template,
                pager=pager, **kwargs)

    @property
    def _load_options(self):
        """Returns a sequence of
        :py:class:`~sqlalchemy.orm.strategy_options.Load` objects specifying
        which attributes to load (or really any load options necessary).
        """
        return (
                db.Load(Request).load_only('id', 'pilot_id', 'division_id',
                    'system', 'ship_type', 'status', 'timestamp',
                    'base_payout'),
                db.Load(Division).joinedload('name'),
                db.Load(Pilot).joinedload('name'),
        )


class APIKeyForm(Form):
    action = HiddenField(validators=[AnyOf(['add', 'delete'])])
    key_id = HiddenField()


class PersonalRequests(RequestListing):
    """Shows a list of all personally submitted requests and divisions the user
    has permissions in.

    It will show all requests the current user has submitted.
    """

    template = 'personal.html'

    methods = ['GET', 'POST']

    def dispatch_request(self, division_id=None, page=1, **kwargs):
        if request.method == 'POST':
            form = APIKeyForm()
            if form.validate():
                if form.action.data == 'add':
                    key = APIKey(current_user)
                else:
                    key = APIKey.query.get(int(form.key_id.data))
                    if key is not None:
                        db.session.delete(key)
                db.session.commit()
        # Handle API access in here, so we can add extra data
        if request.is_json or request.is_xhr:
            return jsonify(
                    requests=self.requests(division_id),
                    api_keys=current_user.api_keys)
        if request.is_xml:
            return xmlify('personal_list.xml',
                    requests=self.requests(division_id))
        return super(PersonalRequests, self).dispatch_request(
                division_id, page, key_form=APIKeyForm(formdata=None))

    def requests(self, division_id=None):
        requests = Request.query\
                .join(User)\
                .filter(User.id==current_user.id)\
                .options(*self._load_options)
        if division_id is not None:
            requests = requests.filter(Request.division_id==division_id)
        requests = requests.order_by(Request.timestamp.desc())
        return requests


class PermissionRequestListing(RequestListing):
    """Show all requests that the current user has permissions to access.

    This is used for the various permission-specific views.
    """

    def __init__(self, permissions, statuses):
        """Create a :py:class:`PermissionRequestListing` for the given
        permissions and statuses.

        :param tuple permissions: The permissions to filter by
        :param tuple statuses: A tuple of valid statuses for requests to be in
        """
        if permissions in PermissionType.all:
            permissions = (permissions,)
        # Admin permission has to be explicitly added because it's used in a
        # complicated query in requests()
        self.permissions = (PermissionType.admin,) + tuple(permissions)
        self.statuses = statuses

    def dispatch_request(self, division_id=None, page=1, **kwargs):
        if not current_user.has_permission(self.permissions):
            abort(403)
        else:
            if 'title' in kwargs:
                title = kwargs.pop('title')
            else:
                title = u', '.join(map(lambda s: s.description, self.statuses))
            return super(PermissionRequestListing, self).dispatch_request(
                    division_id,
                    page,
                    title=title,
                    **kwargs)

    def requests(self, division_id=None):
        user_perms = db.session.query(Permission.id.label('permission_id'),
                Permission.division_id.label('division_id'),
                Permission.permission.label('permission'))\
                .filter(Permission.entity==current_user)
        group_perms = db.session.query(Permission.id.label('permission_id'),
                Permission.division_id.label('division_id'),
                Permission.permission.label('permission'))\
                .join(Group)\
                .filter(Group.users.contains(current_user))
        perms = user_perms.union(group_perms)\
                .filter(Permission.permission.in_(self.permissions))
        if division_id is not None:
            perms = perms.filter(Permission.division_id==division_id)
        perms = perms.subquery()
        requests = Request.query\
                .join(perms, Request.division_id==perms.c.division_id)\
                .filter(Request.status.in_(self.statuses))\
                .order_by(Request.timestamp.desc())\
                .options(*self._load_options)
        return requests


class PayoutListing(PermissionRequestListing):
    """A special view made for quickly processing payouts for requests."""

    template = 'payout.html'

    def __init__(self):
        # Just a special case of PermissionRequestListing
        super(PayoutListing, self).__init__((PermissionType.pay,),
                (ActionType.approved,))

    def dispatch_request(self, division_id=None, page=1):
        if not current_user.has_permission(self.permissions):
            abort(403)
        return super(PayoutListing, self).dispatch_request(
                division_id,
                page,
                title=u', '.join(map(lambda s: s.description, self.statuses)),
                form=ActionForm())


def register_perm_request_listing(app, endpoint, path, permissions, statuses):
    """Utility function for creating :py:class:`PermissionRequestListing`
    views.

    :param app: The application to add the view to
    :type app: :py:class:`flask.Flask`
    :param str endpoint: The name of the view
    :param str path: The URL path for the view
    :param tuple permissions: Passed to
        :py:meth:`PermissionRequestListing.__init__`
    :param iterable statuses: Passed to
        :py:meth:`PermissionRequestListing.__init__`
    """
    if not path.endswith('/'):
        path += '/'
    view = PermissionRequestListing.as_view(endpoint, permissions=permissions,
            statuses=statuses)
    app.add_url_rule(path, view_func=view)
    app.add_url_rule('{}rss.xml'.format(path), view_func=view)
    if path != '/':
        app.add_url_rule('{}<int:division_id>/rss.xml'.format(path),
                view_func=view)
        app.add_url_rule('{}<int:page>/'.format(path), view_func=view)
        app.add_url_rule('{}<int:page>/<int:division_id>/'.format(path),
                view_func=view)


@blueprint.record
def register_class_views(state):
    """Called when the blueprint is registered, this function defines routes
    for and attaches the class-based views to the app.
    """
    try:
        prefixes = state.app.request_prefixes
    except AttributeError:
        prefixes = []
        state.app.request_prefixes = prefixes
    prefixes.append(state.url_prefix if state.url_prefix is not None else '')
    # Personal list
    personal_view = PersonalRequests.as_view('personal_requests')
    state.add_url_rule('/personal/', view_func=personal_view)
    state.add_url_rule('/personal/rss.xml', view_func=personal_view)
    state.add_url_rule('/personal/<int:division_id>/rss.xml',
            view_func=personal_view)
    state.add_url_rule('/personal/<int:page>/', view_func=personal_view)
    state.add_url_rule('/personal/<int:page>/<int:division_id>',
            view_func=personal_view)
    # Payout list
    payout_view = PayoutListing.as_view('list_approved_requests')
    payout_url_stub = '/pay/'
    state.add_url_rule(payout_url_stub, view_func=payout_view)
    state.add_url_rule(payout_url_stub + 'rss.xml', view_func=payout_view)
    state.add_url_rule(payout_url_stub + '<int:division_id>/rss.xml',
            view_func=payout_view)
    state.add_url_rule(payout_url_stub + '<int:page>/', view_func=payout_view)
    state.add_url_rule(payout_url_stub + '<int:page>/<int:division_id>/',
            view_func=payout_view)
    # Other more generalized listings
    register_perm_request_listing(state, 'list_pending_requests',
            '/pending/', (PermissionType.review,), ActionType.pending)
    register_perm_request_listing(state, 'list_completed_requests',
            '/completed/', PermissionType.elevated, ActionType.finalized)
    # Special all listing, mainly intended for API users
    register_perm_request_listing(state, 'list_all_requests',
            '/', PermissionType.elevated, ActionType.statuses)


class ValidKillmail(URL):
    """Custom :py:class:'~.Field' validator that checks if any
    :py:class:`~.Killmail` accepts the given URL.
    """
    def __init__(self, mail_class, **kwargs):
        self.mail_class = mail_class
        super(ValidKillmail, self).__init__(**kwargs)

    def __call__(self, form, field):
        super(ValidKillmail, self).__call__(form, field)
        try:
            mail = self.mail_class(field.data)
        except ValueError as e:
            if six.PY2:
                raise ValidationError(unicode(e))
        except LookupError as e:
            if six.PY2:
                raise ValidationError(unicode(e))
        else:
            if mail.verified:
                form.killmail = mail
                raise StopValidation
            else:
                raise ValidationError(
                        u'{} cannot be verified.'.format(field.data))


def get_killmail_validators():
    """Get a list of :py:class:`ValidKillmail`\s for each killmail source.

    This method is used to delay accessing `current_app` until we're in a
    request context.
    :returns: a list of :py:class:`ValidKillmail`\s
    :rtype list:
    """
    validators = [ValidKillmail(s) for s in current_app.killmail_sources]
    validators.append(InputRequired())
    return validators


def get_killmail_descriptions():
    description = Markup(u"Acceptable Killmail Links:<ul>")
    desc_entry = Markup(u"<li>{}</li>")
    killmail_descs = [desc_entry.format(km.description) for km in\
            current_app.killmail_sources]
    description += Markup(u"").join(killmail_descs)
    description += Markup(u"</ul>")
    return description


class RequestForm(Form):
    url = URLField(u'Killmail URL')
    details = TextAreaField(u'Details', validators=[InputRequired()],
            description=u'Supporting details about your loss.')
    division = SelectField(u'Division', coerce=int)
    submit = SubmitField(u'Submit')

    def validate_url(form, field):
        failures = set()
        for v in get_killmail_validators():
            try:
                v(form, field)
            except ValidationError as e:
                failures.add(unicode(e))
            else:
                continue
        else:
            # If execution reached here, it means a StopValidation exception
            # wasn't raised (meaning the killmail isn't valid).
            raise ValidationError([e for e in failures])


@blueprint.route('/add/', methods=['GET', 'POST'])
@login_required
def submit_request():
    """Submit a :py:class:`~.models.Request`\.

    Displays a form for submitting a request and then processes the submitted
    information. Verifies that the user has the appropriate permissions to
    submit a request for the chosen division and that the killmail URL given is
    valid. Also enforces that the user submitting this requests controls the
    character from the killmail and prevents duplicate requests.
    """
    if not current_user.has_permission(PermissionType.submit):
        abort(403)
    form = RequestForm()
    # Do it in here so we can access current_app (needs to be in an app
    # context)
    form.url.description = get_killmail_descriptions()
    # Create a list of divisions this user can submit to
    form.division.choices = current_user.submit_divisions()

    if form.validate_on_submit():
        mail = form.killmail
        # Prevent submitting other people's killmails
        pilot = Pilot.query.get(mail.pilot_id)
        if not pilot or pilot not in current_user.pilots:
            flash(u"You can only submit killmails of characters you control",
                    u'warning')
            return render_template('form.html', form=form)
        # Prevent duplicate killmails
        # The name 'request' is already used by Flask.
        # Hooray name collisions!
        srp_request = Request.query.get(mail.kill_id)
        if srp_request is None:
            division = Division.query.get(form.division.data)
            srp_request = Request(current_user, form.details.data, division,
                    mail)
            srp_request.pilot = pilot
            db.session.add(srp_request)
            db.session.commit()
            return redirect(url_for('.get_request_details',
                request_id=srp_request.id))
        else:
            flash(u"This kill has already been submitted", u'warning')
            return redirect(url_for('.get_request_details',
                request_id=srp_request.id))
    return render_template('form.html', form=form)


class ModifierForm(Form):
    id_ = HiddenField(default='modifier')
    value = DecimalField(u'Value')
    # TODO: add a validator for the type
    type_ = HiddenField(validators=[AnyOf(('rel-bonus', 'rel-deduct',
            'abs-bonus', 'abs-deduct'))])
    note = TextAreaField(u'Reason')


class VoidModifierForm(Form):
    id_ = HiddenField(default='void')
    modifier_id = HiddenField()
    void = SubmitField(Markup(u'x'))

    def __init__(self, modifier=None, *args, **kwargs):
        if modifier is not None:
            self.modifier_id = modifier.id
        super(VoidModifierForm, self).__init__(*args, **kwargs)


class PayoutForm(Form):
    id_ = HiddenField(default='payout')
    value = DecimalField(u'M ISK', validators=[InputRequired()])


class ActionForm(Form):
    id_ = HiddenField(default='action')
    note = TextAreaField(u'Note')
    type_ = HiddenField(default='comment',
            validators=[AnyOf(ActionType.values())])


class ChangeDetailsForm(Form):
    id_ = HiddenField(default='details')
    details = TextAreaField(u'Details', validators=[InputRequired()])


class AddNote(Form):
    id_ = HiddenField(default='note')
    note = TextAreaField(u'Add Note',
            description=( "If you have something like '#{Kill ID}', it will be"
                         u" linkified to the corresponding request "
                         u"(if it exists). For example, #1234567 would be "
                         u"linked to the request for the kill with ID "
                         u"1234567."),
            validators=[InputRequired()])


killmail_re = re.compile(r'#(\d+)')


@blueprint.route('/<int:request_id>/', methods=['GET'])
@login_required
def get_request_details(request_id=None, srp_request=None):
    """Handles responding to all of the :py:class:`~.models.Request` detail
    functions.

    The various modifier functions all depend on this function to create the
    actual response content.
    Only one of the arguments is required. The ``srp_request`` argument is a
    conveniece to other functions calling this function that have already
    retrieved the request.

    :param int request_id: the ID of the request.
    :param srp_request: the request.
    :type srp_request: :py:class:`~.models.Request`
    """
    if srp_request is None:
        srp_request = Request.query.get_or_404(request_id)
    # Different templates are used for different roles
    if current_user.has_permission(PermissionType.review,
            srp_request.division):
        template = 'request_review.html'
    elif current_user.has_permission(PermissionType.pay, srp_request.division):
        template = 'request_pay.html'
    elif current_user == srp_request.submitter:
        template = 'request_detail.html'
    else:
        abort(403)
    if request.is_json:
        # dump the load to encode srp_request as json and then get a dictionary
        # form of it. We need this to add a few bits of information to the
        # standard request encoding
        enc_request = json.loads(json.dumps(srp_request))
        enc_request[u'actions'] = srp_request.actions
        enc_request[u'modifiers'] = srp_request.modifiers
        valid_actions = map(
                lambda a: a.value,
                srp_request.valid_actions(current_user))
        enc_request[u'valid_actions'] = valid_actions
        enc_request[u'current_user'] = current_user._get_current_object()
        return jsonify(enc_request)
    if request.is_xml:
        return xmlify('request.xml', srp_request=srp_request)
    return render_template(template, srp_request=srp_request,
            modifier_form=ModifierForm(formdata=None),
            payout_form=PayoutForm(formdata=None),
            action_form=ActionForm(formdata=None),
            void_form=VoidModifierForm(formdata=None),
            details_form=ChangeDetailsForm(formdata=None, obj=srp_request),
            note_form=AddNote(formdata=None))


def _add_modifier(srp_request):
    form = ModifierForm()
    if form.validate():
        if 'bonus' in form.type_.data:
            value = form.value.data
        elif 'deduct' in form.type_.data:
            value = form.value.data * -1
        if 'abs' in form.type_.data:
            ModClass = AbsoluteModifier
            value *= 1000000
        elif 'rel' in form.type_.data:
            ModClass = RelativeModifier
            value /= 100
        try:
            mod = ModClass(srp_request, current_user, form.note.data, value)
            db.session.add(mod)
            db.session.commit()
        except ModifierError as e:
            flash(unicode(e), u'error')
    return get_request_details(srp_request=srp_request)


def _change_payout(srp_request):
    form = PayoutForm()
    if not current_user.has_permission(PermissionType.review, srp_request):
        flash(u"Only reviewers can change the base payout.", u'error')
    elif form.validate():
        try:
            srp_request.base_payout = form.value.data * 1000000
            db.session.commit()
        except ModifierError as e:
            flash(unicode(e), u'error')
    return get_request_details(srp_request=srp_request)


def _add_action(srp_request):
    form = ActionForm()
    if form.validate():
        type_ = ActionType.from_string(form.type_.data)
        try:
            Action(srp_request, current_user, form.note.data, type_)
            db.session.commit()
        except ActionError as e:
            flash(unicode(e), u'error')
    return get_request_details(srp_request=srp_request)


def _void_modifier(srp_request):
    form = VoidModifierForm()
    if form.validate():
        modifier_id = int(form.modifier_id.data)
        modifier = Modifier.query.get(modifier_id)
        if modifier is None:
            flash(u"Invalid modifier ID {}.".format(modifier_id),
                    u'error')
        else:
            try:
                modifier.void(current_user)
                db.session.commit()
            except ModifierError as e:
                flash(unicode(e), u'error')
    return get_request_details(srp_request=srp_request)


def _change_details(srp_request):
    form = ChangeDetailsForm()
    if current_user != srp_request.submitter:
        flash(u"Only the submitter can change the request details.", u'error')
    elif srp_request.finalized:
        flash(u"Details con only be changed when the request is still "
                u"pending.", u'error')
    elif form.validate():
        archive_note = u"Old Details: " + srp_request.details
        archive_action = Action(srp_request, current_user, archive_note)
        archive_action.type_ = ActionType.evaluating
        srp_request.details = form.details.data
        db.session.commit()
    return get_request_details(srp_request=srp_request)


def _add_note(srp_request):
    form = AddNote()
    if not current_user.has_permission(PermissionType.elevated):
        flash(u"You do not have permission to add a note to a user.", u'error')
    elif form.validate():
        # Linkify killmail IDs
        note_content = Markup.escape(form.note.data)
        for match in killmail_re.findall(note_content):
            kill_id = int(match)
            check_request = db.session.query(Request.id).filter_by(id=kill_id)
            if db.session.query(check_request.exists()):
                link = u'<a href="{url}">#{kill_id}</a>'.format(
                        url=url_for('.get_request_details',
                                request_id=kill_id),
                        kill_id=kill_id)
                link = Markup(link)
                note_content = note_content.replace(u'#' + match, link)
        # Create the note
        note = Note(srp_request.submitter, current_user, note_content)
        db.session.commit()
    return get_request_details(srp_request=srp_request)


@blueprint.route('/<int:request_id>/', methods=['POST'])
@login_required
def modify_request(request_id):
    """Handles POST requests that modify :py:class:`~.models.Request`\s.

    Because of the numerous possible forms, this function bounces execution to
    a more specific function base on the form's "id_" field.

    :param int request_id: the ID of the request.
    """
    srp_request = Request.query.get_or_404(request_id)
    if request.form['id_'] == 'modifier':
        return _add_modifier(srp_request)
    elif request.form['id_'] == 'payout':
        return _change_payout(srp_request)
    elif request.form['id_'] == 'action':
        return _add_action(srp_request)
    elif request.form['id_'] == 'void':
        return _void_modifier(srp_request)
    elif request.form['id_'] == 'details':
        return _change_details(srp_request)
    elif request.form['id_'] == 'note':
        return _add_note(srp_request)
    else:
        return abort(400)


class DivisionChange(Form):
    division = SelectField(u'Divisions', coerce=int)
    submit = SubmitField(u'Submit')


@blueprint.route('/<int:request_id>/division', methods=['GET', 'POST'])
@login_required
def request_change_division(request_id):
    srp_request = Request.query.get_or_404(request_id)
    review_perm = ReviewRequestsPermission(srp_request)
    if not review_perm.can() and \
            current_user != srp_request.submitter or \
            srp_request.finalized:
        abort(403)
    division_choices = srp_request.submitter.submit_divisions()
    if len(division_choices) < 2:
        flash(u"No other divisions to move to.", u'info')
        return redirect(url_for('.get_request_details', request_id=request_id))
    form = DivisionChange()
    form.division.choices = division_choices
    if form.validate_on_submit():
        new_division = Division.query.get(form.division.data)
        archive_note = u"Moving from division '{}' to division '{}'.".format(
                srp_request.division.name,
                new_division.name)
        archive_action = Action(srp_request, current_user, archive_note)
        archive_action.type_ = ActionType.evaluating
        srp_request.division = new_division
        db.session.commit()
        flash(u'Request #{} moved to {} division'.format(srp_request.id,
                new_division.name), u'success')
        if current_user.has_permission(PermissionType.elevated, new_division) \
                or current_user == srp_request.submitter:
            return redirect(url_for('.get_request_details',
                    request_id=request_id))
        else:
            return redirect(url_for('.list_pending_requests'))
    form.division.data = srp_request.division.id
    return render_template('form.html', form=form)
