xpinyin
==========

.. image:: https://badge.fury.io/py/xpinyin.png
    :target: http://badge.fury.io/py/xpinyin

.. image:: https://travis-ci.org/lxneng/xpinyin.png?branch=master
   :target: https://travis-ci.org/lxneng/xpinyin

.. image:: https://pypip.in/d/xpinyin/badge.png
        :target: https://crate.io/packages/xpinyin/

translate chinese hanzi to pinyin by python, inspired by flyerhzm’s
`chinese\_pinyin`_ gem

Install
----------

::

    pip install xpinyin


Usage
-----

::

    >>> from xpinyin import Pinyin
    >>> p = Pinyin()
    >>> # default splitter is `-`
    >>> p.get_pinyin(u"上海")
    'shang-hai'
    >>> # show tone marks
    >>> p.get_pinyin(u"上海", show_tone_marks=True)
    'shàng-hǎi'
    >>> # remove splitter
    >>> p.get_pinyin(u"上海", '')
    'shanghai'
    >>> # set splitter as whitespace
    >>> p.get_pinyin(u"上海", ' ')
    'shang hai'
    >>> p.get_initial(u"上")
    'S'
    >>> p.get_initials(u"上海")
    'S-H'
    >>> p.get_initials(u"上海", u'')
    'SH'
    >>> p.get_initials(u"上海", u' ')
    'S H'

请输入utf8编码汉字

.. _chinese\_pinyin: https://github.com/flyerhzm/chinese_pinyin


Changelog
=========


0.5.1 - Jul. 6, 2014
----------------------

- show tone marks

0.4.9 - Oct. 25, 2013
----------------------

- change README and get_initials; add get_initial
  [tangsty]


0.4.8 - Jun. 16, 2013
----------------------

- change README and get_initials; add get_initial
  [tangsty]

- add download status image to README.rst
  [lxneng]

- add travis status image to README.rst
  [lxneng]

- add .travis.yml
  [lxneng]

- 添加测试
  [lxneng]

- 解决翻译中英文混合句子问题
  [lxneng]


