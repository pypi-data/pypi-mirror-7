This package provides representation of LabCAS_ data within the EDRN_ portal.

To demonstrate how it works, we'll do a series of functional tests.  And to do
so, we'll need a test browser::

    >>> app = layer['app']
    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
    >>> portal = layer['portal']    
    >>> portalURL = portal.absolute_url()

Here we go.


LabCAS Folders
==============

LabCAS Folders are used to contain LabCAS datasets.  They may be created
anywhere::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='eke-labcas-labcasfolder')
    >>> l.url.endswith('++add++eke.labcas.labcasfolder')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Anal Datasets'
    >>> browser.getControl(name='form.widgets.description').value = u'Where I keep my proctology dataz.'
    >>> browser.getControl(name='form.widgets.rdfDataSource').value = u'testscheme://localhost/labcas/example'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'anal-datasets' in portal.keys()
    True
    >>> folder = portal['anal-datasets']
    >>> folder.title
    u'Anal Datasets'
    >>> folder.description
    u'Where I keep my proctology dataz.'
    >>> folder.rdfDataSource
    u'testscheme://localhost/labcas/example'

The RDF data source had better be a URL.  Let's see what happens when it's not::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='form.widgets.rdfDataSource').value = u'I like pie.'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> browser.contents
    '...There were some errors...Constraint not satisfied...'
    >>> browser.getControl(name='form.buttons.cancel').click()


LabCAS Datasets
===============

LabCAS Datasets go in LabCAS folders.  They may be created solely within LabCAS
Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='eke-labcas-labcasdataset')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/anal-datasets')
    >>> l = browser.getLink(id='eke-labcas-labcasdataset')
    >>> l.url.endswith('++add++eke.labcas.labcasdataset')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Leakage 1'
    >>> browser.getControl(name='form.widgets.description').value = u'A strangely colored ooze.'
    >>> browser.getControl(name='form.widgets.identifier').value = u'urn:edrn:labcas:datasets:leakage-1'
    >>> browser.getControl(name='form.widgets.uploader').value = u'linda-lovelace'
    >>> browser.getControl(name='form.widgets.datasetID').value = u'leakage-1'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'leakage-1' in folder.keys()
    True
    >>> dataset = folder['leakage-1']
    >>> dataset.title
    u'Leakage 1'
    >>> dataset.description
    u'A strangely colored ooze.'
    >>> dataset.identifier
    u'urn:edrn:labcas:datasets:leakage-1'
    >>> dataset.uploader
    u'linda-lovelace'
    >>> dataset.datasetID
    u'leakage-1'


RDF Ingestion
=============

Dan hates curating things in Plone for some reason, so typically LabCAS will
tell the EDRN Portal what datasets exist through RDF.  We've set the "Anal
Datasets" folder's ingestion URL, so we just need to ingest the data from the
simple testing RDF input::

    >>> browser.open(portalURL + '/anal-datasets/ingest')
    >>> browser.contents
    '...Number of datasets ingested:...20...'

We should now how a lot more datasets::

    >>> len(folder.keys())
    20

Neat, huh?


.. References:
.. _LabCAS: http://labcas.jpl.nasa.gov/
.. _EDRN: http://edrn.nci.nih.gov/
