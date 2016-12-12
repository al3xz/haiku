# MetaHaiku

## Table of Contents

* [Introduction](#intro)
* [Installation and Requirements](#install)
* [Goals](#goals)
* [System Evaluation](#syseval)
* [Implementation](#implement)
* * [Metaphor Agent](#metaphoragent)
* * [Haiku Agent](#haikuagent)
* * [Environment](#environment)
* [Multi-agent Pros and Cons](#multi)
* [Sample Output](#samples)


## Introduction <a name="intro"></a>

## Installation and Requirements <a name="install"></a>

The system requires NLTK and gensim libraries, 
gensim requires SciPy package, for installation please see 
<a href="https://www.scipy.org/install.html">Installing the SciPy Stack</a>.
Once you have them, just run main.py.

#### Requirements

* Python 3.5.2
* Creamas 0.1.1
* NLTK 3.2.1
* gensim 0.13.3
* SciPy 0.18.1
* NumPy 1.11.2

## Goals <a name="goals"></a>

The goal of MetaHaiku is to produce valuable and novel artifacts.  The type of artifact desired are haiku which allude
to a topic, but do not directly mention that topic.  If a human observer can puzzle out what the haiku is referring to
without it being too obvious or too difficult, the haiku is a success.

A secondary goal is to make use of metaphors which are novel and valuable in creating the haiku.  We qualitatively
evaluate value by the 'truth' of the metaphor, though evaluating that quality of 'truth' within the system is outside the scope of
this project.

## Evaluation <a name="syseval"></a>

We can consider four types of evaluation for this system.  We can consider our own evaluation of the haiku produced by
the system, or our evaluation of the system as a whole and it's ability to produce novel and valuable artifacts.  We
can also consider the agent's evaluations of the metaphor and haiku artifacts.

To evaluate the haiku produced by the system ourselves, we use a fairly simple test.  If the topic of the haiku can be
guessed from the content, and this is not too obvious, then the artifact has some value.  We could also consider the artistic
value of the haiku- does it flow well, are words repeated too much, is there some grammatical structure; but the system
was not designed with this sort of evaluation in mind, so it is unlikely to perform well except by luck.

When considering the system as a whole and it's ability to produce good artifacts, we need to evaluate many different haiku
produced by the system.  Here, we are insterested not only in our evaluation of the haiku by the test outlined above,
but also the variety and average value of the haiku.  If the system produces very similar haiku over and over, it does not
much matter how good they are.  If it produces a great haiku once in a while, but most are terrible, this may not be a very
good sign either.  What if it's just getting lucky?  We can also consider how the system evaluates its own input on average.
Are most haiku considered good?  Bad?  Are they often guessed unanimously?  Theses are interesting questiosn to answer, which
can help us form an opinion on the value of the whole system.

Evaluation of metaphors within the system is done by the MetaphorAgents. The evaluation has two part, that have 
equal weights. The first part evaluates distance between nouns of metaphor using word2vec model. The more
far away the words are, the better. That way we emphasize novelty and surprise.

In the second part the agents measure three related quantities: shared nouns,
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

## Implementation <a name="implement"></a>
The code documentation can be located on [https://al3xz.github.io/haiku/](https://al3xz.github.io/haiku/)

### Metaphor Agent <a name="metaphoragent"></a>

### Haiku Agent <a name="haikuagent"></a>

### Environment <a name="environment"></a>

## Mult-Agent Pros and Cons <a name="multi"></a>

## Sample Output <a name="samples"></a>

### TEDDY-BEAR:

rises and and rises looms

finds cat cat is cuddly yo

cat furred cat cat mouse


### SNAKE:

looms how rises looms grows

armadillo looms grows leaves

yo armadillo


### ELEPHANT:

building fearful such

building building massive finds

building building looms


### CARROT:

delicious looms looms

looms chicken chicken yo how

delicious is rises


### SNOW:

sugar sugar rises

white is white white sugar yo

cold err cold how grows
