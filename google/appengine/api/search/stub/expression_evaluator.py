#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Expression evaluator for Full Text Search API stub."""




import logging


from google.appengine.api.search import expression_parser
from google.appengine.api.search import ExpressionParser
from google.appengine.api.search import query_parser
from google.appengine.api.search import search_util
from google.appengine.api.search.stub import simple_tokenizer
from google.appengine.api.search.stub import tokens


class _ExpressionError(Exception):
  """Raised when evaluating an expression fails."""


class ExpressionEvaluator(object):
  """Evaluates an expression on scored documents."""

  def __init__(self, document, inverted_index):
    """Creates an ExpressionEvaluator.

    Args:
      document: The ScoredDocument to evaluate the expression for.
      inverted_index: The search index (used for snippeting).
    """
    self._doc = document
    self._doc_pb = document.document
    self._inverted_index = inverted_index
    self._tokenizer = simple_tokenizer.SimpleTokenizer(preserve_case=False)
    self._case_preserving_tokenizer = simple_tokenizer.SimpleTokenizer(
        preserve_case=True)
    self._function_table = {
        'max': self._Max,
        'min': self._Min,
        'count': self._Count,
        'snippet': self._Snippet,
        'distance': self._Unsupported('distance'),
        }

  def _Min(self, *nodes):
    return min(self._Eval(node) for node in nodes)

  def _Max(self, *nodes):
    return max(self._Eval(node) for node in nodes)

  def _Count(self, node):
    return search_util.GetFieldCountInDocument(
        self._doc_pb, query_parser.GetQueryNodeText(node))

  def _GenerateSnippet(self, doc_words, position, max_length):
    """Generate a snippet that fills a given length from a list of tokens.

    Args:
      doc_words: A list of tokens from the document.
      position: The index of the highlighted word.
      max_length: The maximum length of the output snippet.

    Returns:
      A summary of the given words with the word at index position highlighted.
    """
    snippet = '<b>%s</b>' % doc_words[position]
    if position + 1 < len(doc_words):

      next_len = len(doc_words[position+1]) + 1
    if position > 0:

      prev_len = len(doc_words[position-1]) + 1


    i = 1

    while (len(snippet) + next_len + prev_len + 6 < max_length and
           (position + i < len(doc_words) or position - i > 0)):
      if position + i < len(doc_words):
        snippet = '%s %s' % (snippet, doc_words[position+i])

        next_len = len(doc_words[position+i]) + 1
      else:
        next_len = 0

      if position - i >= 0:
        snippet = '%s %s' % (doc_words[position-i], snippet)

        prev_len = len(doc_words[position-i]) + 1
      else:
        prev_len = 0

      i += 1
    return '...%s...' % snippet

  def _Snippet(self, query, field, *args):
    field = query_parser.GetQueryNodeText(field)
    terms = self._tokenizer.TokenizeText(
        query_parser.GetQueryNodeText(query).strip('"'))
    for term in terms:
      search_token = tokens.Token(chars=u'%s:%s' % (field, term.chars))
      postings = self._inverted_index.GetPostingsForToken(search_token)
      for posting in postings:
        if posting.doc_id != self._doc_pb.id() or not posting.positions:
          continue

        field_val = search_util.GetFieldValue(
            search_util.GetFieldInDocument(self._doc_pb, field))
        doc_words = [token.chars for token in
                     self._case_preserving_tokenizer.TokenizeText(field_val)]

        position = posting.positions[0]
        return self._GenerateSnippet(
            doc_words, position, search_util.DEFAULT_MAX_SNIPPET_LENGTH)

  def _Unsupported(self, method):
    def RaiseUnsupported(*args):
      raise search_util.UnsupportedOnDevError(
          '%s is currently unsupported on dev_appserver.' % method)
    return RaiseUnsupported

  def _EvalBinaryOp(self, op, op_name, node):
    if len(node.children) != 2:
      raise ValueError('%s operator must always have two arguments' % op_name)
    n1, n2 = node.children
    return op(self._Eval(n1), self._Eval(n2))

  def _EvalUnaryOp(self, op, op_name, node):
    if len(node.children) != 1:
      raise ValueError('%s operator must always have two arguments' % op_name)
    return op(self._Eval(node.children[0]))

  def _Eval(self, node):
    if node.getType() is ExpressionParser.FN:
      func = self._function_table[query_parser.GetQueryNodeText(node)]


      return func(*node.children)

    if node.getType() is ExpressionParser.PLUS:
      return self._EvalBinaryOp(lambda a, b: a + b, 'addition', node)
    if node.getType() is ExpressionParser.MINUS:
      return self._EvalBinaryOp(lambda a, b: a - b, 'subtraction', node)
    if node.getType() is ExpressionParser.DIV:
      return self._EvalBinaryOp(lambda a, b: a / b, 'division', node)
    if node.getType() is ExpressionParser.TIMES:
      return self._EvalBinaryOp(lambda a, b: a * b, 'multiplication', node)
    if node.getType() is ExpressionParser.NEG:
      return self._EvalUnaryOp(lambda a: -a, 'negation', node)

    if node.getType() in (ExpressionParser.INT, ExpressionParser.FLOAT):
      return float(query_parser.GetQueryNodeText(node))
    if node.getType() is ExpressionParser.PHRASE:
      return query_parser.GetQueryNodeText(node).strip('"')

    if node.getType() is ExpressionParser.NAME:
      name = query_parser.GetQueryNodeText(node)
      if name == '_score':
        return self._doc.score
      field = search_util.GetFieldInDocument(self._doc_pb, name)
      if field:
        return search_util.GetFieldValue(field)
      raise _ExpressionError('No field %s in document' % name)

    raise _ExpressionError('Unable to handle node %s' % node)

  def Evaluate(self, expression):
    """Evaluates the expression for a document and attaches the result.

    Args:
      expression: The Expression protobuffer object.
    """

    name = expression.name()
    expression_tree = ExpressionEvaluator.Parse(expression.expression())
    if not expression_tree.getType() and expression_tree.children:
      expression_tree = expression_tree.children[0]

    try:
      result = self._Eval(expression_tree)
      self._doc.expressions[name] = result
    except _ExpressionError, e:


      logging.debug('Skipping expression %s: %s', name, e)
    except search_util.UnsupportedOnDevError, e:


      logging.warning(e.args[0])

  @staticmethod
  def Parse(expression):
    return expression_parser.Parse(expression).tree
