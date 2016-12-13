.. haiku documentation master file, created by
   sphinx-quickstart on Fri Dec  9 08:35:10 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MetaHaiku
=========

Table of Contents
-----------------

* :ref:`intro`
* :ref:`install`
* :ref:`goals`
* :ref:`syseval`
* :ref:`implement`
* :ref:`multi`
* :ref:`samples`

.. _intro:

Introduction
------------

.. _install:

Installation and Requirements
----------------------------------------------------

The system requires NLTK and gensim libraries,
gensim requires SciPy package, for installation please see `Installing the SciPy Stack <https://www.scipy.org/install.html>`_.
Once you have them, just run main.py.

Requirements
++++++++++++

* Python 3.5.2
* Creamas 0.1.1
* NLTK 3.2.1
* gensim 0.13.3
* SciPy 0.18.1
* NumPy 1.11.2

.. _goals:

Goals
--------------------------

The goal of MetaHaiku is to produce valuable and novel artifacts.  The type of artifact desired are haiku which allude
to a topic, but do not directly mention that topic.  If a human observer can puzzle out what the haiku is referring to
without it being too obvious or too difficult, the haiku is a success.

A secondary goal is to make use of metaphors which are novel and valuable in creating the haiku.  We can qualitatively
evaluate value by the 'truth' of the metaphor.  Within the system the value of a metaphor is evaluated based on the similarity
of the word2vec representations of the two nouns used.

.. _syseval:

Evaluation
---------------------------------

We can consider four types of evaluation for this system: Our own evaluation of the haiku produced by
the system, or our evaluation of the system as a whole and it's ability to produce novel and valuable artifacts, the
agent's evaluations of the metaphor artifacts, and the agent's evaluation of the haiku artifacts.

To evaluate the haiku produced by the system ourselves, we use a fairly simple test.  If the topic of the haiku can be
guessed from the content, and it isn't too obvious, then the artifact has some value.  We could also consider the artistic
value of the haiku- does it flow well, are words repeated too much, is there some grammatical structure; but the system
was not designed with this sort of evaluation in mind, so it is unlikely to perform well except by luck.

When considering the system as a whole and it's ability to produce good artifacts, we need to evaluate many different haiku
produced by the system.  Here, we are interested not only in our evaluation of the haiku by the test outlined above,
but also the variety and average value of the haiku.  If the system produces very similar haiku over and over, it does not
much matter how good they are.  If it produces a great haiku once in a while, but most are terrible, this may not be a very
good sign either.  What if it's just getting lucky?  We can also consider how the system evaluates its own input on average.
Are most haiku considered good?  Bad?  Are they often guessed unanimously?  Theses are interesting questiosn to answer, which
can help us form an opinion on the value of the whole system.

Evaluation of metaphors within the system is done by the MetaphorAgents. The evaluation has two weighted parts: value and novelty.
Value is based on the distance between nouns of metaphor using word2vec model. Words which are closer
together are considered better for metaphors because there is more 'truth' to their similarity.

For novelty, the agents measure three related quantities: shared nouns,
shared adjectives, and shared pairs.  Shared nouns count how many other metaphors within the agent's memory have a noun in
common with the metaphor under evaluation.  Shared adjectives does the same for adjectives.  Shared pairs counts the number
which have both nouns in common.  Each of these values is given a weight, but in the current implementation, only the shared
pairs weight is non-zero.  We found in practice that penalizing shared nouns and adjectives resulted in the metaphors being
very spread out among the possible nouns in the input text.  This was a problem, because topics are drawn from that list,
and if there are only one or two metaphors for each topic, the Haiku produced have little material to draw on.

The HaikuAgents evaluate the haiku other HaikuAgents produce.  They consider two measures: word variety, and guess-ability.
Word variety penalizes haiku which contain many repeated words.  This is a minor aspect of the evaluation, and represents
a consideration of artistic flow (repeated words are less appealing in this regard).  The main portion of the evaluation
comes from the guess score.  Evaluating a new haiku, a HaikuAgent will consider nouns and adjectives it recognizes, and
search it's own memory for common associations of these nouns and adjectives.  It will then come up with it's top three
guesses as to the topic of the haiku.  If it's first choice is correct, the haiku is given a high evaluation by that agent.
The second and third guesses being correct give a partial but smaller score.

Although each individual HaikuAgent rates a first guess highly, if all HaikuAgents can guess the topic on the first try,
that indicates the haiku might be too obvious.  To represent this, a penalty is applied at the environment level if 90% or
more of the HaikuAgents guessed the haiku on their first try.

.. _implement:

Implementation
---------------------------------------
.. toctree::
   :maxdepth: 4
   :caption: Modules:

   HaikuAgent
   Main
   MetaHaikuEnvironment
   MetaphorAgent
   MetaphorMemory
   Model_Classes
   NounListGenerator

.. _multi:

Mult-Agent Pros and Cons
---------------------------------------------

We can consider the pros and cons of having a multi-agent system for MetaphorAgents and HaikuAgents separately.

For MetaphorAgents, a single agent system would have been plausible.  On the pro side, we have the possibility to give
different MetaphorAgents different inspiring sets and the ability to distribute the problem of remembering what metaphors
have been created before.  Instead of search one giant list of memory, we have several smaller memories.  As the MetaphorAgent's
memories fill up and they start forgetting different things, they differentiate from each other, producing more specialized
metaphors.  This gives us more chances to get to an interesting state.

On the con side, there is a cost in the complexity of the system.  It's harder to understand exactly what's going on.  Why
did a certain metaphor get a better score than another? The answer requires understanding the memories of many different agents.
We also pay a performance cost in that each MetaphorAgent must remember and evaluate new Metaphors separately.

For HaikuAgents, the multi-agent setup is required for our evaluation scheme.  To check whether others could guess the Haiku
topic, we need to have *others*.  It is also very important that our HaikuAgents can differentiate themselves.  If they all
have the same memory (as they do at the beggining of the simulation), they will all have the same guesses for a given Haiku.
As their memories fill up and they differentiate by forgetting different older metaphors, the guessing evaluation becomes much
more interesting.  Most winning haikus are guessed by 2-4 of the 5 HaikuAgents in our normal simulation setup.

.. _samples:

Sample Output
------------------------------------

SHARE:
++++++

is how solace grows

solace small small ere solace

small looms solace such


Guessed by 5

1 metaphors used

There is a definite correlation between the number of metaphors used and the guess-ability of the haiku.  Here we see an example
with only one metaphor which was guessed by all five.


FRONT:
++++++

own wage own epic

wage is technology of

mine own how and how


Guessed by 4

11 metaphors used


An example of a Haiku with many metaphors used.  This one was guessed by most of the HaikuAgents.  Another thing to note about this
haiku is the use of the generic adjective 'own'.  This is very common, as 'own' can be used to describe many different nouns.  We
have considered filtering it out to avoid seeing it so much, as it provides very little meaning to a human observer, and ultimately
we want to produce artifacts that are interesting to us more than to the Agents.


Metaphor Examples:
++++++++++++++++++

antenna is as outside as a help

push is as big as a night

disappointment is as great as a leap

efficiency is as physical as a mean

era is as new as a well


relation is as common as a good

well is as small as a drum

care is as good as a professor

traveler is as such as a heard

heard is as such as a variation


A selection of metaphors generated by our MetaphorAgents.  We can see the problem of generic adjectives is significant, with
'new', 'good', and 'such' providing very little information.  This is something we would have liked to improve on.