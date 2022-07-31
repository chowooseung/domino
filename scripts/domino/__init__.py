# domino
from .api import log
from domino import menu
from domino_edition.api import utils as edition_utils

__version__ = [1, 0, 0]
__version_str__ = ". ".join([str(x) for x in __version__])


def install():
    log.Logger.info("Domino Installing...")

    edition_utils.register_editions()  # DOMINO_DEFAULT_EDITION, DOMINO_CUSTOM_EDITION
    menu.install()
