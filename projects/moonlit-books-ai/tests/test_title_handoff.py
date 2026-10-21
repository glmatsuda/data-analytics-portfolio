import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import core

class TitleLookupTests(unittest.TestCase):
    def test_missing_named_titles(self):
        for title in ['The Invisible Marmalade Kingdom','The Clockwork Sea Otter']:
            with self.subTest(title=title):
                r=core.title_lookup('Do you stock a book called '+title+'?')
                self.assertEqual(r['status'],'absent')
                self.assertEqual(r['scope'],'cached_catalog_only')
                self.assertEqual(r['matched_book_ids'],[])
    def test_plain_title_stock_question(self):
        r=core.title_lookup('Do you have The Invisible Marmalade Kingdom in stock?')
        self.assertEqual(r['requested_title'],'The Invisible Marmalade Kingdom')
        self.assertEqual(r['status'],'absent')
        self.assertEqual(core.title_lookup('Do you have The Hobbit in stock?')['status'],'present')
    def test_generic_stock_question(self):
        for q in ['Do you have fantasy in stock?','Do you have science fiction books in stock?']:
            self.assertIsNone(core.title_lookup(q))
    def test_quoted_title(self):
        self.assertEqual(core.title_lookup('Can you find “The Clockwork Sea Otter”?')['status'],'absent')
    def test_existing_title_normalizes_case_and_punctuation(self):
        r=core.title_lookup('Do you stock a book titled "the HOBBIT"?')
        self.assertEqual(r['matched_book_ids'],['BK001'])
        self.assertEqual(r['status'],'present')
    def test_zero_stock_still_exists_in_catalog(self):
        r=core.title_lookup('Do you have a book called Jane Eyre?')
        self.assertEqual(r['status'],'present')
        self.assertEqual(r['matched_book_ids'],['BK011'])
        self.assertEqual(int(core.BOOK_MAP['BK011']['stock']),0)
    def test_reviewed_subtitle_alias(self):
        self.assertEqual(core.title_lookup('Do you have a book called Frankenstein?')['matched_book_ids'],['BK016'])
    def test_genre_and_policy_questions_not_treated_as_missing_titles(self):
        for question in ['Recommend fantasy under $20','Do you have science fiction books?','What is your return policy?']:
            self.assertIsNone(core.title_lookup(question))
    def test_no_fuzzy_stock_claim(self):
        self.assertEqual(core.title_lookup('Do you stock a book called The Hobbit Study Guide?')['status'],'absent')

class HandoffContractTests(unittest.TestCase):
    # Provider-shaped unit fixtures verify enforcement only; never benchmark output.
    def test_provider_false_flag_cannot_bypass_review(self):
        obj=dict(answer='Not listed in this cached catalog. Ask a bookseller.',book_ids=[],citations=['H02'],needs_human=False)
        with patch.object(core,'infer',return_value=(obj,{'mode':'unit-test-fixture'})):
            r=core.concierge('Do you stock a book called The Clockwork Sea Otter?')
        self.assertTrue(r['needs_human'])
        self.assertFalse(r['model_needs_human'])
        self.assertTrue(r['handoff_rule_applied'])
        self.assertEqual(r['catalog_lookup']['scope'],'cached_catalog_only')
        self.assertTrue(all(s['kind']=='handbook' for s in r['sources']))
    def test_missing_title_cannot_offer_unrelated_recommendation(self):
        obj=dict(answer='Try this other book',book_ids=['BK001'],citations=['H02'],needs_human=False)
        with patch.object(core,'infer',return_value=(obj,{})):
            with self.assertRaises(core.ModelError):core.concierge('Do you have a book called The Clockwork Sea Otter?')

if __name__=='__main__':unittest.main()
