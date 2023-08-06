This package provides Plone 3 content objects for the EDRN Knowledge
Environment (EKE_)'s management, display, and RDF ingest of publication data.


Content Types
=============

The content types introduced in this package include the following:

Publication Folder
    A folder that contains Publications.  It can also repopulate its
    contents from an RDF data source.
Publication
    A single publication identified by URI_.

The remainder of this document demonstrates the content types and RDF ingest
using a series of functional tests.


Tests
=====

First we have to set up some things and login to the site::

    >>> app = layer['app']
    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
    >>> portal = layer['portal']    
    >>> portalURL = portal.absolute_url()

We'll also have a second browser that's unprivileged for some later
demonstrations::

    >>> unprivilegedBrowser = Browser(app)

Now we can check out the new types introduced in this package.


Addable Content
---------------

Here we'll exercise some of the content objects available in this project and
demonstrate their properties and constraints.


Publication Folder
~~~~~~~~~~~~~~~~~~

A publication folder contains publications.  They can be created anywhere
in the portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='publication-folder')
    >>> l.url.endswith('createObject?type_name=Publication+Folder')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'My Magazine Collection'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/pubs/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'my-magazine-collection' in portal.objectIds()
    True
    >>> f = portal['my-magazine-collection']
    >>> f.title
    'My Magazine Collection'
    >>> f.description
    'This folder is just for functional tests.'
    >>> f.rdfDataSource
    'testscheme://localhost/pubs/a'

Publication folders hold Publications as well as other Publication Folders.
We'll test adding Publications below, but let's make sure there's a link to
created nested Publication Folders::

    >>> browser.open(portalURL + '/my-magazine-collection')
    >>> l = browser.getLink(id='publication-folder')
    >>> l.url.endswith('createObject?type_name=Publication+Folder')
    True


Publication
~~~~~~~~~~~

A single Publication object corresponds with a single real-world publication.
In EDRN, all publications are assumed to be published in a journal—even
standalone books.  Unfortunate, but there we are.  Anyway, Publications can be
created on in Publication Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='publication')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's create one in our above Publication Folder::

    >>> browser.open(portalURL + '/my-magazine-collection')
    >>> l = browser.getLink(id='publication')
    >>> l.url.endswith('createObject?type_name=Publication')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'S.W.I.T.C.H.: a new model for release of norepinephrine'
    >>> browser.getControl(name='description').value = 'Repeated use of our S.W.I.T.C.H. model have shown high success.'
    >>> browser.getControl(name='abstract').value = 'The model produced enormous levels of norepinephrine.'
    >>> browser.getControl(name='authors:lines').value = u'Faetishe, JM\nDivine, HR'
    >>> browser.getControl(name='identifier').value = 'http://unknown.com/pub13792'
    >>> browser.getControl(name='year').value = '1964'
    >>> browser.getControl(name='journal').value = 'Roue'
    >>> browser.getControl(name='issue').value = '3'
    >>> browser.getControl(name='volume').value = '4'
    >>> browser.getControl(name='pubMedID').value = '1645221Q'
    >>> browser.getControl(name='pubURL').value = 'http://unknown.com/printable/pub13792'
    >>> browser.getControl(name='form.button.save').click()
    >>> 's-w-i-t-c-h-a-new-model-for-release-of-norepinephrine' in f.objectIds()
    True
    >>> pub = f['s-w-i-t-c-h-a-new-model-for-release-of-norepinephrine']
    >>> pub.title
    'S.W.I.T.C.H.: a new model for release of norepinephrine'
    >>> pub.description
    'Repeated use of our S.W.I.T.C.H. model have shown high success.'
    >>> pub.abstract
    'The model produced enormous levels of norepinephrine.'
    >>> pub.authors
    ('Faetishe, JM', 'Divine, HR')
    >>> pub.identifier
    'http://unknown.com/pub13792'
    >>> pub.year
    '1964'
    >>> pub.journal
    'Roue'
    >>> pub.issue
    '3'
    >>> pub.volume
    '4'
    >>> pub.pubMedID
    '1645221Q'
    >>> pub.pubURL
    'http://unknown.com/printable/pub13792'
    
A publication page should include a link to its PubMed entry as well to its URL:

    >>> browser.contents
    '...<a href="http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&amp;Cmd=DetailsSearch&amp;Term=1645221Q%5Buid%5D">...'
    >>> browser.contents
    '...<a href="http://unknown.com/printable/pub13792">...'

http://oodt.jpl.nasa.gov/jira/browse/CA-474 specifies a specific format for
publications.  Let's see if we're actually following that format::

    >>> browser.contents
    '...Faetishe, JM, Divine, HR...S.W.I.T.C.H...<cite>...Roue...</cite>...1964;...4...'

Lookin' good.


RDF Ingestion
-------------

Publication folders support a URL-callable method that causes them to ingest
content via RDF, just like Knowledge Folders in the ``eke.knowledge`` package.

First, let's create a new, empty folder with which to play::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='publication-folder').click()
    >>> browser.getControl(name='title').value = "Cook's Bookshelf"
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/pubs/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/cooks-bookshelf/content_status_modify?workflow_action=publish')
    >>> f = portal['cooks-bookshelf']

Ingesting from the RDF data source ``testscheme://localhost/pubs/a``::

    >>> browser.open(portalURL + '/cooks-bookshelf/ingest')
    >>> browser.contents
    '...The following items have been created...Glazed Roast Chicken...'
    >>> f.objectIds()
    ['glazed-roast-chicken']
    >>> pub = f['glazed-roast-chicken']
    >>> pub.title
    'Glazed Roast Chicken'
    >>> pub.description
    'Applying a glaze to a whole chicken can land you in a sweet mess.'
    >>> pub.abstract
    'Most glazed roast chicken recipes offer some variation on these instructions.'
    >>> 'Gavorick, M' in pub.authors and 'Kimball, C' in pub.authors
    True
    >>> pub.identifier
    'http://is.gd/pVKq'
    >>> pub.year
    '2009'
    >>> pub.journal
    "Cook's Illustrated"
    >>> pub.issue
    'March'
    >>> pub.volume
    '12'
    >>> pub.pubMedID
    '123456X'
    >>> pub.pubURL
    'http://is.gd/pVKq'

The source ``testscheme://localhost/pub/b`` contains both the Glazed Roast
Chicken article *and* an article on Teriyaki Beef.  Since ingestion purges
existing objects, we shouldn't get duplicate copies of the chicken recipe::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/pubs/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> objIDs = f.objectIds()
    >>> objIDs.sort()
    >>> objIDs
    ['glazed-roast-chicken', 'teriyaki-beef']
    
Although the PubMed ID is a required attribute, it's often missing in the RDF
we get from the DMCC.  In such a case, we shouldn't generate an invalid link
to PubMed in the folder's view.  Let's check that!  It just so happens the
Teriyaki Beef recipe's RDF is missing a statement as to its PubMed ID; is
there a URL? Checking::

    >>> browser.open(portalURL + '/cooks-bookshelf')
    >>> 'http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&amp;Cmd=DetailsSearch&amp;Term=%5Buid%5D">' not in browser.contents
    True


Multiple Data Sources
~~~~~~~~~~~~~~~~~~~~~

As we'e seen, publication folders have a main RDF data source.  But they also
support zero or more additional sources of data.  Let's toss some of this
additional data in and see it can successfully ingest it::

	>>> browser.getLink('Edit').click()
	>>> browser.getControl(name='additionalDataSources:lines').value = 'testscheme://localhost/pubs/c\ntestscheme://localhost/pubs/d'
	>>> browser.getControl(name='form.button.save').click()
	>>> browser.getLink('Ingest').click()
	>>> len(f.objectIds())
	6


HTML Markup
~~~~~~~~~~~

http://oodt.jpl.nasa.gov/jira/browse/CA-472 reveals that RDF from the DMCC
doesn't contain plain text, but HTML markup.  Sigh.  Let's see if we deal with
that appropriately.  This new data source contains some nasty markup::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/pubs/e'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> browser.open(portalURL + '/cooks-bookshelf/how-to-serve-man')
    >>> 'How to "Serve" Man' in browser.contents
    True
    >>> 'Applying a glaze to a whole man can land you in a sweet mess.' in browser.contents
    True
    >>> '<em>Most</em> glazed man recipes offer some variation on these instructions.' in browser.contents
    True
	

Vocabularies
------------

This package provides one vocabulary: a vocabulary of existing publications.
Here's what you get::

    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> from zope.component import getUtility
    >>> v = getUtility(IVocabularyFactory, name='eke.publications.PublicationsVocabulary')
    >>> type(v(portal))
    <class 'zope.schema.vocabulary.SimpleVocabulary'>


Searching
---------

Issue http://oodt.jpl.nasa.gov/jira/browse/CA-514 says searching by author
name doesn't work.  Let's find out::

    >>> from Products.CMFCore.utils import getToolByName
    >>> catalog = getToolByName(portal, 'portal_catalog')
    >>> results = catalog.unrestrictedSearchResults(SearchableText='Voodoo')
	>>> [i.Title for i in results if i.portal_type == 'Publication']
	['How to "Serve" Man']

Works!


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
