import sys,unittest,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import core

class RetrievalTests(unittest.TestCase):
    def test_stock_and_budget(self):
        sources=core.search('Recommend fantasy books under $20 that are in stock.')
        books=[core.BOOK_MAP[s['book_id']] for s in sources if s['kind']=='catalog']
        self.assertTrue(books)
        self.assertTrue(all(int(b['stock'])>0 and float(b['price_usd'])<20 for b in books))
    def test_author_source(self):
        self.assertIn('C-BK010',[s['id'] for s in core.search('Which book by Jane Austen is in this catalog?')])
    def test_return_source(self):
        self.assertIn('H01',[s['id'] for s in core.search('How long do I have to return an unread book with a receipt?')])
    def test_missing_invoice_path(self):
        with self.assertRaises(ValueError):core.invoice_text('../../core')

class InvoiceTests(unittest.TestCase):
    def test_all_fixture_controls(self):
        for f in core.FIXTURES:
            with self.subTest(fixture=f['id']):
                text,method=core.invoice_text(f['id'])
                self.assertEqual(core.validate_invoice(f['expected'],text),sorted(f['expected_flags']))
                self.assertIn(f['expected']['invoice_id'],text)
    def test_currency_cannot_be_invented(self):
        f=core.FIXTURE_MAP['invoice-07'];obj=dict(f['expected'],currency='USD')
        self.assertIn('MISSING_CURRENCY',core.validate_invoice(obj,core.invoice_text(f['id'])[0]))
    def test_exact_money(self):
        self.assertEqual(core.money('0.1')+core.money('0.2'),core.money('0.30'))
        for value in ['NaN','Infinity','garbage',None]:
            with self.assertRaises(ValueError):core.money(value)
    def test_field_comparison(self):
        e=core.FIXTURES[0]['expected'];a=dict(e,total='56.980')
        self.assertTrue(all(core.compare_invoice_fields(a,e).values()))
        self.assertFalse(core.compare_invoice_fields(dict(e,total='0'),e)['total'])
    def test_empty_lines_flagged(self):
        e=dict(core.FIXTURES[0]['expected'],items=[])
        self.assertIn('INVALID_AMOUNTS_OR_LINES',core.validate_invoice(e,'Currency: USD'))

class ContractTests(unittest.TestCase):
    # These mocks test rejection paths only. They never populate evaluation results.
    def test_unknown_citation_rejected(self):
        obj=dict(answer='Example',book_ids=[],citations=['FAKE'],needs_human=False)
        with patch.object(core,'infer',return_value=(obj,{})):
            with self.assertRaises(core.ModelError):core.concierge('What is your return policy?')
    def test_uncited_recommendation_rejected(self):
        obj=dict(answer='Example',book_ids=['BK001'],citations=[],needs_human=True)
        with patch.object(core,'infer',return_value=(obj,{})):
            with self.assertRaises(core.ModelError):core.concierge('Recommend cozy fantasy under $20')
    def test_unsupported_answer_rejected(self):
        obj=dict(answer='Example',book_ids=[],citations=[],needs_human=False)
        with patch.object(core,'infer',return_value=(obj,{})):
            with self.assertRaises(core.ModelError):core.concierge('What is your address?')
    def test_blank_question_rejected(self):
        with self.assertRaises(ValueError):core.concierge(' ')

if __name__=='__main__':unittest.main()
