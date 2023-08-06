============================================
WikiSummarizer ----- A Wikipedia Summarizer
============================================

WikiSummarizer provides the simplest way possible to summarize the complete tex in a Wikipedia Document.

The usage is depicted by the following example:

from wiki_summary import summarize 

 sum = summarize.summarize("http://en.wikipedia.org/wiki/facebook")

 print sum


 Algorithm
 =================================================

 Given url => Fetch required Document => Parse the Wiki Page => Rank and Find the most contexually apt sentences => Reorder them to maintain coherence => return the summary 

 Dependencies
 =================================================

 BeautifulSoup4
 bleach
 nltk 

 Author 
 =================================================

 Sagar Pandey
 <sagarinocean@gmail.com>, <aigeano@gmail.com>
