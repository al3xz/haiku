.. haiku documentation master file, created by
   sphinx-quickstart on Fri Dec  9 08:35:10 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to metahaiku's documentation!
=====================================
Metahaiku is project for automatic generation of haiku. This project is written using Python 3.5, utilizes the `Creamas <https://pypi.python.org/pypi/creamas/0.1.0>`_ multi-agent library atop of aiomas and the `NLTK <http://www.nltk.org/>`_ language processing toolkit. Ultimately, the goal is to produce valuable and surprising artifacts. The desired artifacts are Haiku which describe a topic noun without the use of that noun. Agents produce these Haiku artifacts using a secondary artifact, the metaphor, which links two nouns by their shared adjective. Metaphors, for the purpose of this project, represent a link between two nouns (topics) by an adjective (description) they both share.

Example outputs:

ANGEL:

grows chicken graceful

christmas rises graceful sparrow

christmas ere joyful


ELEPHANT:

yo fearful is mouse

grows finds strong chicken grey tree

grey and strong strong and


.. toctree::
   :maxdepth: 4
   :caption: Contents:

   HaikuAgent
   Main
   MetaHaikuEnvironment
   MetaphorAgent
   MetaphorMemory
   Model_Classes
   NounListGenerator


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
