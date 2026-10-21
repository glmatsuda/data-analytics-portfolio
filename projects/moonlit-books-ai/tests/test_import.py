import sys,unittest,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import import_openlibrary as importer
import core

class LookupMatchingTests(unittest.TestCase):
    # Small invented API-shaped fixtures test matching only, not measured import results.
    def test_punctuation_and_diacritics(self):
        doc={'title':'LEGENDS AND LATTES','author_name':['Travis Baldree']}
        self.assertTrue(importer.matching(doc,'Legends & Lattes','Travis Baldree'))
        self.assertEqual(importer.norm('Brontë'),importer.norm('Bronte'))
    def test_wrong_author_rejected(self):
        doc={'title':'The Hobbit','author_name':['Another Writer']}
        self.assertFalse(importer.matching(doc,'The Hobbit','Tolkien'))
    def test_adaptation_title_rejected(self):
        doc={'title':'The Hobbit Study Guide','author_name':['J. R. R. Tolkien']}
        self.assertFalse(importer.matching(doc,'The Hobbit','Tolkien'))

class ImportedProvenanceTests(unittest.TestCase):
    def test_all_active_records_have_sources(self):
        self.assertEqual(core.CATALOG_INFO.get('catalog_kind'),'openlibrary','Run the real importer before validating the new catalog.')
        self.assertGreaterEqual(len(core.BOOKS),18)
        raw=[]
        for path in (core.ROOT/'data/openlibrary').glob('*.json'):
            data=json.loads(path.read_text())
            self.assertTrue(data['request_url'].startswith('https://openlibrary.org/search.json?'))
            raw.extend(data['response']['docs'])
        for book in core.BOOKS:
            with self.subTest(book=book['book_id']):
                self.assertRegex(book['source_url'],r'^https://openlibrary\.org/works/OL\d+W$')
                matches=[d for d in raw if d.get('key','').split('/')[-1]==book['openlibrary_work_id']]
                self.assertTrue(matches)
                self.assertTrue(any(d['title']==book['title'] and '; '.join(d['author_name'])==book['author'] for d in matches))
                self.assertNotIn('fictional',book['metadata_source'].lower())
        self.assertEqual(core.CATALOG_INFO['catalog_sha256'],core.CATALOG_HASH)

if __name__=='__main__':unittest.main()
