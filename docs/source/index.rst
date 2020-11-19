:github_url: https://github.com/davebulaval/python2latex


.. meta::

  :description: Python2LaTeX: The Python to LaTeX converter
  :keywords: python, latex, pytorch
  :author: Jean-Samuel Leboeuf
  :property="og:image": https://deepparse.org/_static/logos/logo.png # todo add or not?


Python2LaTeX: The Python to LaTeX converter
===========================================

Did you ever feel overwhelmed by the cumbersomeness of LaTeX to produce quality tables and figures? Fear no more,
Python2LaTeX is here! Produce perfect tables automatically and easily, create figures and plots that integrates
seamlessly into your tex file, or even write your complete article directly from Python! All that effortlessly
(or almost) with Python2LaTeX.

Use Python2LaTeX to:

- Automate table generation direcly from your code.
- Create effortless LaTeX table using Python.

Read the documentation at `deepparse.org <https://deepparse.org>`_. #todo update link

Prerequisites
-------------

The package makes use of numpy and assumes a distribution of LaTeX that uses ``pdflatex`` is installed on your computer.
Some LaTeX packages are used, such as ``booktabs``, ``tikz``, ``pgfplots`` and ``pgfplotstable``. Your LaTeX distribution should inform you if such package needs to be installed.

Cite
----

# todo to update. (keep or not?)
.. code-block:: bib

   @misc{python2latex,
       title={{Python2LaTeX: The Python to LaTeX converter}},
       author={Jean-Samuel Leboeuf},
       year={2019}
   }

Getting started
===============

.. code-block:: python

    from python2latex import Document

    doc = Document(filename='simple_document_example', filepath='./examples/simple document example', doc_type='article', options=('12pt',))
    doc.set_margins(top='3cm', bottom='3cm', margins='2cm')
    sec = doc.new_section('Spam and Egg', label='spam_egg')
    sec.add_text('The Monty Python slays the Spam and eats the Egg.')

    tex = doc.build() # Builds to tex and compile to pdf
    print(tex) # Prints the tex string that generated the pdf


Installation
============

To install the package, simply run in your terminal the command

    pip install python2latex

**Install the latest development version of Python2LaTeX:**

    pip install -U git+https://github.com/jsleb333/python2latex.git@dev


License
=======
Python2LaTeX is MIT licensed, as found in the `LICENSE file <https://github.com/jsleb333/python2latex/blob/master/LICENSE>`_.


API Reference
=============

.. toctree::
  :maxdepth: 1
  :caption: API

  ...


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
