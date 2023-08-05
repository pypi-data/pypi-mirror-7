from logging import getLogger
from Products.CMFCore.utils import getToolByName

PROFILE_ID = 'profile-bise.theme:default'


def ploneglossary_1001(context, logger=None):
    if logger is None:
        logger = getLogger('ploneglossary_1001')

    js_registry = getToolByName(context, 'portal_javascripts')
    resource = js_registry.getResource('ploneglossary_definitions.js')
    resource.setInline(False)
    logger.info('Upgraded')


def reload_css_1001(context, logger=None):
    if logger is None:
        logger = getLogger('reload_css_1001')

    default_profile = 'profile-bise.biodiversityfactsheet:default'
    context.runImportStepFromProfile(default_profile, 'jsregistry')
    logger.info('Upgraded')


def upgrade_to_1002(context, logger=None):
    if logger is None:
        logger = getLogger('reload_css_1002')

    setup = getToolByName(context, 'portal_setup')

    setup.runAllImportStepsFromProfile('profile-plone.app.versioningbehavior:default')
    setup.runAllImportStepsFromProfile('profile-plone.app.iterate:plone.app.iterate')

    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    setup.runImportStepFromProfile(PROFILE_ID, 'repositorytool')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone-difftool')
    logger.info('Upgrade steps executed')
