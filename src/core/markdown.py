"""Shared markdown rendering with selective line numbers.

python-Markdown's codehilite extension only supports a single global
``linenums`` setting - there is no per-block way to opt a fenced block out
of line numbering. We render with ``linenums=True`` for every block (so
language-labeled blocks get real Pygments highlighting + a numbered
gutter), then post-process the HTML to strip the gutter back out of blocks
that produced no highlighted tokens (i.e. unlabeled blocks such as ASCII
diagrams).
"""
import re

import markdown

_BLOCK_RE = re.compile(
    r'<div class="codehilite"><table class="codehilitetable">.*?</table></div>',
    re.DOTALL,
)

_CODE_CELL_RE = re.compile(
    r'^<div class="codehilite"><table class="codehilitetable">'
    r'<tr><td class="linenos">.*?</td><td class="code">(?P<code>.*)</td></tr>'
    r'</table></div>$',
    re.DOTALL,
)

_TOKEN_SPAN_RE = re.compile(r'<span class="[a-zA-Z0-9]+">')

_PRE_RE = re.compile(r'<pre>.*</pre>', re.DOTALL)


def render_markdown(text):
    if not text:
        return ''
    html = markdown.markdown(
        text,
        extensions=['extra', 'codehilite'],
        extension_configs={'codehilite': {'guess_lang': False, 'linenums': True}},
    )
    return _strip_linenos_from_plain_blocks(html)


def _strip_linenos_from_plain_blocks(html):
    return _BLOCK_RE.sub(_strip_block_if_plain, html)


def _strip_block_if_plain(match):
    block = match.group(0)
    cell_match = _CODE_CELL_RE.match(block)
    if not cell_match:
        return block

    code_cell = cell_match.group('code')
    if _TOKEN_SPAN_RE.search(code_cell):
        return block

    pre_match = _PRE_RE.search(code_cell)
    if not pre_match:
        return block

    return '<div class="codehilite">{}</div>'.format(pre_match.group(0))
