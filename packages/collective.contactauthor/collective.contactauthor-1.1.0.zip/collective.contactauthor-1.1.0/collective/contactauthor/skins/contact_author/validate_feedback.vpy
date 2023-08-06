## Controller Script Python "validate_author_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=referer,subject,message,author=None,email=None
##title=validates the form for sending feedback

from Products.CMFPlone import PloneMessageFactory as pmf
from collective.contactauthor import messageFactory as _

plone_utils=context.plone_utils
reg_tool=context.portal_registration 
contactauthor_settings = context.portal_url.getPortalObject().restrictedTraverse('@@contactauthor-status')

if not (subject and subject.strip()):
    state.setError('subject', pmf(u'Please enter a subject.'), 'email_required')

if not (message and message.strip()):
    state.setError('message', pmf(u'Please enter a message'), 'email_required')

if context.portal_membership.isAnonymousUser():
    if contactauthor_settings.protection_level() == 'anon-with-captcha':
        try:
            captcha_verify = context.restrictedTraverse('@@captcha').verify()
        except ValueError:
            context.plone_utils.addPortalMessage(pmf(u"Can't send message. Please contact the site administrator"), 'error')
            context.plone_log('ERROR: seems that recaptcha is not configured')
            return state.set(status='failure')
        if not captcha_verify:
            state.setError('recaptcha', _(u'Wrong captcha code provided'), 'recaptcha')

    if not email:
        state.setError('email', pmf(u'Please submit an email address.'), 'sender_from_address_required')
    else:
        if reg_tool.isValidEmail(email):
            pass
        else:
            state.setError('email', pmf(u'You entered an invalid email address.'), 'invalid_email')

if state.getErrors():
    context.plone_utils.addPortalMessage(pmf(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
