"""Doorstop reporting functionality."""

import os
import textwrap
import logging

import markdown

from doorstop.common import DoorstopError
from doorstop import settings

CSS = os.path.join(os.path.dirname(__file__), 'files', 'doorstop.css')
INDEX = 'index.html'


def publish(obj, path, ext=None, ignored=None, **kwargs):
    """Publish a document to a given format.

    @param obj: Item, list of Items, or Document to publish
    @param path: output file location with desired extension
    @param ext: file extension to override output path's extension
    @param ignored: function to determine if a path should be skipped

    @raise DoorstopError: for unknown file formats

    """
    ext = ext or os.path.splitext(path)[-1]
    if ext in FORMAT:

        # Create output directory
        dirpath = os.path.dirname(path)
        if not os.path.isdir(dirpath):
            logging.info("creating {}...".format(dirpath))
            os.makedirs(dirpath)

        # Publish report
        logging.info("publishing {}...".format(path))
        with open(path, 'w') as outfile:  # pragma: no cover (integration test)
            for line in lines(obj, ext, ignored=ignored, **kwargs):
                outfile.write(line + '\n')
    else:
        raise DoorstopError("unknown format: {}".format(ext))


def index(directory, extensions=('.html',)):
    """Create an HTML index of all files in a directory.

    @param directory: directory for index
    @param extensions: file extensions to include

    """
    # Get paths for the index index
    filenames = []
    for filename in os.listdir(directory):
        if filename.endswith(extensions) and filename != INDEX:
            filenames.append(os.path.join(filename))

    # Create the index
    if filenames:
        path = os.path.join(directory, INDEX)
        logging.info("publishing {}...".format(path))
        with open(path, 'w') as outfile:
            for line in _lines_index(filenames):
                outfile.write(line + '\n')
    else:
        logging.warning("no files for {}".format(INDEX))


def _lines_index(filenames):
    """Yield lines of HTML for index.html."""
    yield '<!DOCTYPE html>'
    yield '<head>'
    yield '<style type="text/css">'
    yield ''
    with open(CSS) as infile:
        for line in infile:
            yield line
    yield '</style>'
    yield '</head>'
    yield '<body>'
    for filename in filenames:
        name = os.path.splitext(filename)[0]
        yield '<li> <a href="{f}">{n}</a> </li>'.format(f=filename, n=name)
    yield '</body>'
    yield '</html>'


def lines(obj, ext='.txt', ignored=None, **kwargs):
    """Yield lines for a report in the specified format.

    @param obj: Item, list of Items, or Document to publish
    @param ext: file extension to specify the output format
    @param ignored: function to determine if a path should be skipped

    @raise DoorstopError: for unknown file formats

    """
    if ext in FORMAT:
        logging.debug("yielding {} as lines of {}...".format(obj, ext))
        yield from FORMAT[ext](obj, ignored=ignored, **kwargs)
    else:
        raise DoorstopError("unknown format: {}".format(ext))


def lines_text(obj, ignored=None, indent=8, width=79):
    """Yield lines for a text report.

    @param obj: Item, list of Items, or Document to publish
    @param ignored: function to determine if a path should be skipped
    @param indent: number of spaces to indent text
    @param width: maximum line length

    @return: iterator of lines of text

    """
    for item in _get_items(obj):

        level = _format_level(item.level)

        if item.heading:

            # Level and Text
            yield "{l:<{s}}{t}".format(l=level, s=indent, t=item.text)

        else:

            # Level and ID
            yield "{l:<{s}}{i}".format(l=level, s=indent, i=item.id)

            # Text
            if item.text:
                yield ""  # break before text
                for line in item.text.splitlines():
                    yield from _chunks(line, width, indent)

                    if not line:  # pragma: no cover (integration test)
                        yield ""  # break between paragraphs

            # Reference
            if item.ref:
                yield ""  # break before reference
                ref = _ref(item, ignored=ignored)
                yield from _chunks(ref, width, indent)

            # Links
            if item.links:
                yield ""  # break before links
                if settings.PUBLISH_CHILD_LINKS:
                    label = "Parent links: "
                else:
                    label = "Links: "
                slinks = label + ', '.join(str(l) for l in item.links)
                yield from _chunks(slinks, width, indent)
            if settings.PUBLISH_CHILD_LINKS:
                links = item.find_child_links()
                if links:
                    yield ""  # break before links
                    slinks = "Child links: " + ', '.join(str(l) for l in links)
                    yield from _chunks(slinks, width, indent)

        yield ""  # break between items


def _chunks(text, width, indent):
    """Yield wrapped lines of text."""
    yield from textwrap.wrap(text, width,
                             initial_indent=' ' * indent,
                             subsequent_indent=' ' * indent)


def lines_markdown(obj, ignored=None):
    """Yield lines for a Markdown report.

    @param obj: Item, list of Items, or Document to publish
    @param ignored: function to determine if a path should be skipped

    @return: iterator of lines of text

    """
    for item in _get_items(obj):

        heading = '#' * item.depth
        level = _format_level(item.level)

        if item.heading:

            # Level and Text
            yield "{h} {l} {t}".format(h=heading, l=level, t=item.text)

        else:

            # Level and ID
            yield "{h} {l} {i}".format(h=heading, l=level, i=item.id)

            # Text
            if item.text:
                yield ""  # break before text
                yield from item.text.splitlines()

            # Reference
            if item.ref:
                yield ""  # break before reference
                yield _ref(item, ignored=ignored)

            # Links
            if item.links:
                yield ""  # break before links
                if settings.PUBLISH_CHILD_LINKS:
                    label = "Parent links: "
                else:
                    label = "Links: "
                slinks = label + ', '.join(str(l) for l in item.links)
                yield '*' + slinks + '*'
            if settings.PUBLISH_CHILD_LINKS:
                links = item.find_child_links()
                if links:
                    yield ""  # break before links
                    slinks = "Child links: " + ', '.join(str(l) for l in links)
                    yield '*' + slinks + '*'

        yield ""  # break between items


def _get_items(obj):
    """Get an iterator of items from from an item, list, or document."""
    if hasattr(obj, 'items'):
        # a document
        return (i for i in obj.items if i.active)
    try:
        # an iterable
        return iter(obj)
    except TypeError:
        # an item
        return [obj]  # an item


def _format_level(level):
    """Convert a level to a string and keep zeros if not a top level."""
    text = str(level)
    if text.endswith('.0') and len(text) > 3:
        text = text[:-2]
    return text


def _ref(item, ignored=None):
    """Format an external reference for publishing."""
    if settings.CHECK_REF:
        path, line = item.find_ref(ignored=ignored)
        path = path.replace('\\', '/')  # always use unix-style paths
        return "Reference: {p} (line {l})".format(p=path, l=line)
    else:
        return "Reference: '{r}'".format(r=item.ref)


def lines_html(obj, ignored=None):
    """Yield lines for an HTML report.

    @param obj: Item, list of Items, or Document to publish
    @param ignored: function to determine if a path should be skipped

    @return: iterator of lines of text

    """
    # Determine if a full HTML document should be generated
    try:
        iter(obj)
    except TypeError:
        document = False
    else:
        document = True
    # Generate HTML
    if document:
        yield '<!DOCTYPE html>'
        yield '<head>'
        yield '<style type="text/css">'
        yield ''
        with open(CSS) as infile:
            for line in infile:  # pragma: no cover (integration test)
                yield line
        yield '</style>'
        yield '</head>'
        yield '<body>'
    html = markdown.markdown('\n'.join(lines_markdown(obj, ignored=ignored)))
    yield from html.splitlines()
    if document:
        yield '</body>'
        yield '</html>'


# Mapping from file extension to lines generator
FORMAT = {'.txt': lines_text,
          '.md': lines_markdown,
          '.html': lines_html}
