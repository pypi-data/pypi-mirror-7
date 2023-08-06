collective.jazzport
===================

**collective.jazzport** is a yet another Zip export plugin for Plone.

It's a minimal export, supporting only rendered HTML content (without any url
rewriting) and those content types that get downloaded as files by default.

It differs from the other zip exports in that it's implemented as a ZPublisher
stream iterator, which means that it releases Zope worker threads as soon as
possible and downloads all the zipped files separately using their public
URLs.

(Note: this approach could be problematic for HAProxy configured to allow
only fixed number of requests, but works great with Varnish's health check
approach.)

After activation, **collective.jazzport** can display **Download Zip** document
action or object button, whenever its permission **collective.jazzport:
Download Zip** is available for the current user.

By default, the permission is not given to anyone, not even the Manager role.
Also those actions are set invisible and must be manually enabled from the
*portal_actions*-tool.
