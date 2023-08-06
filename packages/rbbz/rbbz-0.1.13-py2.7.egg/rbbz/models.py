# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from djblets.siteconfig.models import SiteConfiguration
from djblets.util.decorators import simple_decorator
from reviewboard.reviews.errors import PublishError
from reviewboard.reviews.signals import (review_request_publishing,
                                         review_publishing, reply_publishing)
from reviewboard.site.urlresolvers import local_site_reverse

from rbbz.bugzilla import Bugzilla
from rbbz.diffs import build_plaintext_review
from rbbz.errors import (BugzillaError, ConfidentialBugError, InvalidBugsError,
                         InvalidBugIdError)

def review_request_url(review_request, site=None, siteconfig=None):
    if not site:
        site = Site.objects.get_current()

    if not siteconfig:
        siteconfig = SiteConfiguration.objects.get_current()

    return '%s://%s%s%s' % (
        siteconfig.get('site_domain_method'), site.domain,
        local_site_reverse('root').rstrip('/'),
        review_request.get_absolute_url())

def is_review_request_pushed(review_request):
    return str(review_request.extra_data.get('p2rb', False)) == "True"

def is_review_request_squashed(review_request):
    return str(review_request.extra_data.get('p2rb.is_squashed', False)) == "True"

@simple_decorator
def bugzilla_to_publish_errors(func):
    def _transform_errors(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BugzillaError as e:
            raise PublishError('Bugzilla error: %s' % e.msg)
    return _transform_errors


@bugzilla_to_publish_errors
def publish_review_request(user, review_request_draft, **kwargs):
    review_request = review_request_draft.get_review_request()

    # skip review requests that were not pushed
    if not is_review_request_pushed(review_request):
        return

    # The reviewid passed through p2rb is, for Mozilla's instance anyway, also
    # the bug ID.
    bug_id = review_request_draft.extra_data.get('p2rb.identifier', None)

    try:
        bug_id = int(bug_id)
    except (TypeError, ValueError):
        raise InvalidBugIdError(bug_id)

    b = Bugzilla(user.bzlogin, user.bzcookie)

    try:
        if b.is_bug_confidential(bug_id):
            raise ConfidentialBugError
    except xmlrpclib.Fault as e:
        # 100: Invalid Bug Alias
        # 101: Bug does not exist
        if e.faultCode == 100 or e.faultCode == 101:
            raise InvalidBugIdError(bug_id)
        raise

    # At this point, we know that the bug ID that we've got
    # is valid and accessible.
    review_request_draft.bugs_closed = str(bug_id)

    reviewers = [x.get_username() for x in
                 review_request_draft.target_people.all()]

    # Don't make attachments for child review requests, otherwise,
    # Bugzilla gets inundatated with lots of patches, and the squashed
    # one is the only one we want to post there.
    if is_review_request_squashed(review_request):
        b.post_rb_url(bug_id,
                      review_request.id,
                      review_request_draft.summary,
                      review_request_draft.description,
                      review_request_url(review_request),
                      reviewers)

def publish_review(user, review, **kwargs):
    review_request = review.review_request

    # skip review requests that were not pushed
    if not is_review_request_pushed(review_request):
        return

    bug_id = int(review_request.get_bug_list()[0])
    site = Site.objects.get_current()
    siteconfig = SiteConfiguration.objects.get_current()
    b = Bugzilla(user.bzlogin, user.bzcookie)

    b.post_comment(bug_id, build_plaintext_review(review, {"user": user}))

    if review.ship_it and not review_request.depends_on.count():
        b.r_plus_attachment(bug_id, review.user.username,
                            review_request_url(review_request, site,
                                               siteconfig))


def publish_reply(user, reply, **kwargs):
    review_request = reply.review_request

    # skip review requests that were not pushed
    if not is_review_request_pushed(review_request):
        return

    bug_id = int(review_request.get_bug_list()[0])
    b = Bugzilla(user.bzlogin, user.bzcookie)

    b.post_comment(bug_id, build_plaintext_review(reply, {"user": user}))


review_request_publishing.connect(publish_review_request)
review_publishing.connect(publish_review)
reply_publishing.connect(publish_reply)


class BugzillaUserMap(models.Model):
    user = models.OneToOneField(User)
    bugzilla_user_id = models.IntegerField(unique=True, db_index=True)


def get_or_create_bugzilla_users(user_data):
    # All users will have a stored password of "!", which Django uses to
    # indicate an invalid password.
    users = []

    for user in user_data['users']:
        bz_user_id = user['id']
        email = user['email']
        real_name = user['real_name']
        can_login = user['can_login']

        try:
            bugzilla_user_map = BugzillaUserMap.objects.get(
                bugzilla_user_id=bz_user_id)
        except BugzillaUserMap.DoesNotExist:
            user = User(username=email, password='!', first_name=real_name,
                        email=email, is_active=can_login)
            user.save()
            bugzilla_user_map = BugzillaUserMap(user=user,
                                                bugzilla_user_id=bz_user_id)
            bugzilla_user_map.save()
        else:
            modified = False
            user = bugzilla_user_map.user

            if user.username != email:
                user.username = email
                user.email = email
                modified = True

            if user.first_name != real_name:
                user.first_name = real_name
                modified = True

            if user.is_active != can_login:
                user.is_active = can_login
                modified = True

            if modified:
                user.save()

        users.append(user)
    return users
































#
