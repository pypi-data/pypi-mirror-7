Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Description: ===========
        textblob-de
        ===========
        
        .. image:: https://badge.fury.io/py/textblob-de.png
            :target: http://badge.fury.io/py/textblob-de
            :alt: Latest version
        
        .. image:: https://travis-ci.org/markuskiller/textblob-de.png
            :target: https://travis-ci.org/markuskiller/textblob-de
            :alt: Travis-CI
        
        German language support for `TextBlob`_.
        
        Features
        --------
        
        * Part-of-speech tagging (``PatternTagger``)
        * Supports Python 2 and 3
        
        Installing/Upgrading
        --------------------
        
        If you have `pip`_ installed (you should), run ::
        
            $ pip install -U textblob-de
        
        
        .. note::
        
            `TextBlob`_ will be installed and updated automatically by running the 
            above commands.
        
        Usage
        -----
        .. code-block:: python
        
            >>> from textblob import TextBlob
            >>> from textblob_de import PatternTagger
            >>> text = "Das ist ein schönes Auto."
            >>> blob = TextBlob(text, pos_tagger=PatternTagger())
            >>> blob.tags
            [('Das', 'DT'), ('ist', 'VB'), ('ein', 'DT'), ('schönes', 'JJ'), ('Auto', 'NN')]
        
        
        .. note::
        
            Make sure that you use unicode strings on Python2 if your input contains
            non-ascii charachters (e.g. ``word = u"schönes"``)
        
        Requirements
        ------------
        
        - Python >= 2.6 or >= 3.3
        
        TODO
        ----
        
        - Fix handling of sentence final punctuation
        - German Tokenization (adapt English ``PatternTokenizer``)
        - NLTK tagging
        - Parsing
        - Sentiment analysis (no subjectivity lexicon in `pattern-de`_)
        
        
        License
        -------
        
        MIT licensed. See the bundled `LICENSE`_  file for more details.
        
        .. _pip: https://pip.pypa.io/en/latest/installing.html
        .. _TextBlob: https://textblob.readthedocs.org/
        .. _pattern-de: http://www.clips.ua.ac.be/pages/pattern-de
        .. _LICENSE: https://github.com/markuskiller/textblob-de/blob/master/LICENSE
        
        
        Changelog
        ---------
        
        0.1.3 (09/07/2014)
        ++++++++++++++++++
        
        * First release on PyPi
        
        0.1.0 - 0.1.2 (09/07/2014)
        ++++++++++++++++++++++++++
        
        * First release on github
        * A number of experimental releases for testing purposes
        * Adapted version badges, tests & travis-ci config
        * Code adapted from sample extension `textblob-fr`_
        * Language specific linguistic resources copied from `pattern-de`_
        
        .. _textblob-fr: https://github.com/sloria/textblob-fr
        .. _pattern-de: https://github.com/clips/pattern/tree/master/pattern/text/de
        
Keywords: textblob_de
Platform: UNKNOWN
Classifier: Development Status :: 2 - Pre-Alpha
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: German
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
