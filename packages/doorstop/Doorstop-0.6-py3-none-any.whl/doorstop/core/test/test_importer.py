"""Unit tests for the doorstop.core.importer module."""

import unittest
from unittest.mock import patch, Mock

import os

from doorstop.core import importer
from doorstop.core.tree import Tree, _set_tree
from doorstop.common import DoorstopError

from doorstop.core.test.test_document import MockItem


class TestNewDocument(unittest.TestCase):  # pylint: disable=R0904

    """Unit tests for the new_document function."""  # pylint: disable=C0103

    def setUp(self):
        # Create default document options
        self.prefix = 'PREFIX'
        self.root = 'ROOT'
        self.path = os.path.join(self.root, 'DIRECTORY')
        self.parent = 'PARENT_PREFIX'
        # Ensure the tree is reloaded
        mock_document = Mock()
        mock_document.root = self.root
        self.mock_tree = Tree(mock_document)
        _set_tree(self.mock_tree)

    @patch('doorstop.core.tree.Tree.new_document')
    def test_create_document(self, mock_new):
        """Verify a new document can be created to import items."""
        importer.new_document(self.prefix, self.path)
        mock_new.assert_called_once_with(self.path, self.prefix, parent=None)

    @patch('doorstop.core.tree.Tree.new_document')
    def test_create_document_with_parent(self, mock_new):
        """Verify a new document can be created with a parent."""
        importer.new_document(self.prefix, self.path, parent=self.parent)
        mock_new.assert_called_once_with(self.path, self.prefix,
                                         parent=self.parent)

    @patch('doorstop.core.tree.Tree.new_document',
           Mock(side_effect=DoorstopError))
    def test_create_document_already_exists(self):
        """Verify non-parent exceptions are re-raised."""
        self.assertRaises(DoorstopError,
                          importer.new_document, self.prefix, self.path)

    @patch('doorstop.core.tree.Tree.new_document',
           Mock(side_effect=DoorstopError))
    @patch('doorstop.core.document.Document.new')
    def test_create_document_unknown_parent(self, mock_new):
        """Verify documents can be created with unknown parents."""
        importer.new_document(self.prefix, self.path, parent=self.parent)
        mock_new.assert_called_once_with(self.mock_tree,
                                         self.path, self.root, self.prefix,
                                         parent=self.parent)


@patch('doorstop.core.item.Item', MockItem)  # pylint: disable=R0904
class TestAddItem(unittest.TestCase):  # pylint: disable=R0904

    """Unit tests for the add_item function."""  # pylint: disable=C0103

    prefix = 'PREFIX'
    root = 'ROOT'
    path = os.path.join(root, 'DIRECTORY')
    parent = 'PARENT_PREFIX'

    mock_document = Mock()

    def setUp(self):
        # Create default item attributes
        self.identifier = 'PREFIX-00042'
        # Ensure the tree is reloaded
        mock_document = Mock()
        mock_document.root = self.root
        mock_document.prefix = self.prefix
        self.mock_tree = Tree(mock_document)
        _set_tree(self.mock_tree)

    def mock_find_document(self, prefix):
        """Mock Tree.find_document() to return a mock document."""
        assert isinstance(self, Tree)
        assert prefix == TestAddItem.prefix
        TestAddItem.mock_document.prefix = prefix
        TestAddItem.mock_document.path = TestAddItem.path
        TestAddItem.mock_document.root = TestAddItem.root
        return TestAddItem.mock_document

    @patch('doorstop.core.tree.Tree.find_document', mock_find_document)
    @patch('doorstop.core.item.Item.new')
    def test_add_item(self, mock_new):
        """Verify an item can be imported into an existing document."""
        importer.add_item(self.prefix, self.identifier)
        mock_new.assert_called_once_with(self.mock_tree, self.mock_document,
                                         self.path, self.root, self.identifier,
                                         auto=False)

    @patch('doorstop.core.tree.Tree.find_document', mock_find_document)
    def test_add_item_with_attrs(self):
        """Verify an item can be imported with attributes."""
        attrs = {'text': "The item text.", 'ext': "External attrubte."}
        item = importer.add_item(self.prefix, self.identifier, attrs=attrs)
        self.assertEqual(self.identifier, item.id)
        self.assertEqual(attrs['text'], item.text)
        self.assertEqual(attrs['ext'], item.get('ext'))
