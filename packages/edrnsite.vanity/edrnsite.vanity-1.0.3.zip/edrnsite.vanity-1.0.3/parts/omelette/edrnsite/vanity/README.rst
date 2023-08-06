This package provides vanity pages for members of the Early Detection Research
Network (EDRN).

To demonstrate the code, we'll classes in a series of functional tests.  And
to do so, we'll need a test browser::

    >>> app = layer['app']
    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
    >>> portal = layer['portal']    
    >>> portalURL = portal.absolute_url()

This browser has full manager permissions, but we'll need a plainer browser to
test some of the more user-level functions::

    >>> userBrowser = Browser(app)

Here we go.


Folder Organization
===================

The intent of bespoke pages is to provide EDRN members with vanity sites where
they can show off their research.  These will be stored in the member-pages
folder in the site root.  Each page will have an ID that matches the member's
account ID.



Logging In
==========

Logging in should trigger an event which checks to see if the user has a
bespoke page (a vanity page, personal page, etc.).  Let's see what



Bespoke Page
============

A bespoke page is a place for members to show off their stuff, customize their
personal attributes, etc.  For now, they can be added anywhere::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='edrnsite-vanity-bespokepage')
    >>> l.url.endswith('++add++edrnsite.vanity.bespokepage')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'John Yaya'
    >>> browser.getControl(name='form.widgets.description').value = u"I'm the boss."
    >>> browser.getControl(name='form.widgets.showMbox:list').value = True
    >>> browser.getControl(name='form.widgets.mbox').value = u'yaya@anus-mastery.com'
    >>> browser.getControl(name='form.widgets.edrnTitle').value = u'Boss Man'
    >>> browser.getControl(name='form.widgets.specialty').value = u'Proctology'
    >>> browser.getControl(name='form.widgets.phone').value = u'+33 1 43 54 23 31'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'john-yaya' in portal.keys()
    True

Notice that you can toggle display of your email address.  As created above,
John Yaya's email address is visible::

    >>> browser.open(portalURL + '/john-yaya')
    >>> u'yaya@anus-mastery.com' in browser.contents
    True

But it's not shown if the box is unchecked::

    >>> browser.getLink('Update It').click()
    >>> browser.getControl(name='form.widgets.showMbox:list').value = False
    >>> browser.getControl(name='form.buttons.save').click()
    >>> browser.open(portalURL + '/john-yaya')
    >>> u'yaya@anus-mastery.com' in browser.contents
    False

Speaking of, the email address better look like an email address::

    >>> browser.getLink('Update It').click()
    >>> browser.getControl(name='form.widgets.mbox').value = u'No, you.'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> browser.contents
    '...There were some errors...Email Address...Constraint not satisfied...'


