#!/usr/bin/env python
# coding: utf-8
import wcwidth


def test_hello_jp():
    """
    Width of Japanese phrase: コンニチハ, セカイ!

    Given a phrase of 5 and 3 Katakana ideographs, joined with
    3 English-ASCII punctuation characters, totaling 11, this
    phrase consumes 19 cells of a terminal emulator.
    """
    # given,
    phrase = u'コンニチハ, セカイ!'
    expect_length_each = (2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1)
    expect_length_phrase = sum(expect_length_each)

    # exercise,
    length_each = tuple(map(wcwidth.wcwidth, phrase))
    length_phrase = wcwidth.wcswidth(phrase, len(phrase))

    # verify,
    assert length_each == expect_length_each
    assert length_phrase == expect_length_phrase


def test_null_width_0():
    """
    NULL (0) reports width 0.
    """
    # given,
    phrase = u'abc\x00def'
    expect_length_each = (1, 1, 1, 0, 1, 1, 1)
    expect_length_phrase = sum(expect_length_each)

    # exercise,
    length_each = tuple(map(wcwidth.wcwidth, phrase))
    length_phrase = wcwidth.wcswidth(phrase, len(phrase))

    # verify,
    assert length_each == expect_length_each
    assert length_phrase == expect_length_phrase


def test_control_c0_width_negative_1():
    """
    CSI (Control sequence initiate) reports width -1.
    """
    # given,
    phrase = u'\x1b[0m'
    expect_length_each = (-1, 1, 1, 1)
    expect_length_phrase = -1

    # exercise,
    length_each = tuple(map(wcwidth.wcwidth, phrase))
    length_phrase = wcwidth.wcswidth(phrase, len(phrase))

    # verify,
    assert length_each == expect_length_each
    assert length_phrase == expect_length_phrase


def test_combining_width_negative_1():
    """
    Simple test combining reports width -1.
    """
    # given,
    phrase = u'--\u05bf--'
    expect_length_each = (1, 1, -1, 1, 1)
    expect_length_phrase = -1

    # exercise,
    length_each = tuple(map(wcwidth.wcwidth, phrase))
    length_phrase = wcwidth.wcswidth(phrase, len(phrase))

    # verify,
    assert length_each == expect_length_each
    assert length_phrase == expect_length_phrase
