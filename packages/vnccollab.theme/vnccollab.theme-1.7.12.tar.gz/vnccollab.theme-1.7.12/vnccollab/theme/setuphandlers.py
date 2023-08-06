import logging

from Products.CMFCore.utils import getToolByName

from .config import CATALOG_INDEXES

PROFILE_ID = 'profile-vnccollab.theme:default'


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('vnccollab.theme_various.txt') is None:
        return

    # Add additional setup code here

def import_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if context.readDataFile('vnccollab.theme_catalog_indexes.txt') is None:
        return

    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('vnccollab.theme')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.
    # Remove these lines when you have no catalog.xml file.
    portal = context.getSite()
    setup = getToolByName(portal, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(portal, 'portal_catalog')
    indexes = catalog.indexes()
    indexables = []
    for name, meta_type in CATALOG_INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        # TODO: make this code work, now it raises error
        catalog.manage_reindexIndex(ids=indexables)
