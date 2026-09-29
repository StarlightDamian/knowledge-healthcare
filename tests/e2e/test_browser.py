"""Browser integration tests; run explicitly after building index.html.
Requires optional Playwright; supports system Chromium or installed Playwright browser.
BROWSER_TRANSPORT=html renders HTML in-memory when navigation is restricted.
That mode validates DOM/interaction, NOT file/HTTP loading or origin storage behavior.
GUIDE_URL targets an existing deployment; public navigation allows 120 seconds.
"""
from pathlib import Path
import json
import os
import shutil
import tempfile
import unittest
import threading
from contextlib import contextmanager
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

@contextmanager
def serve(directory):
 class QuietHandler(SimpleHTTPRequestHandler):
  def log_message(self, *args): pass
 server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(directory)))
 thread = threading.Thread(target=server.serve_forever, daemon=True)
 thread.start()
 try: yield f"http://127.0.0.1:{server.server_port}"
 finally: server.shutdown(); server.server_close(); thread.join(timeout=3)
from playwright.sync_api import sync_playwright
from src.guide.model import ROOT
from src.guide.build import build

class BrowserTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.conditions={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'data/conditions').glob('*.json')}
  cls.topic_count=len(cls.conditions)
  cls.knowledge={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'data/knowledge').glob('*.json')}
  cls.server_context=serve(ROOT);local_origin=cls.server_context.__enter__()
  cls.origin=os.environ.get('GUIDE_URL',local_origin).rstrip('/')
  cls.pw=sync_playwright().start()
  executable=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium')
  cls.browser=cls.pw.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.server_context.__exit__(None,None,None)
 def setUp(self):
  self.context=self.browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
  self.page=self.context.new_page();self.errors=[];self.http=[]
  if os.environ.get('GUIDE_URL'):self.page.set_default_navigation_timeout(120000)
  self.page.on('pageerror',lambda e:self.errors.append(str(e)))
  self.page.on('request',lambda req:self.http.append(req.url) if req.url.startswith(('https:','http:')) else None)
  self.load_page(ROOT/'index.html', self.origin);self.page.wait_for_selector('.card')
 def load_page(self, path, origin):
  if os.environ.get('BROWSER_TRANSPORT') == 'html':
   self.page.set_content(path.read_text(encoding='utf-8'), wait_until='load')
  else:
   self.page.goto(origin+'/index.html')
 def tearDown(self):
  self.assertEqual(self.errors,[],'Browser script errors');self.context.close()
 def test_offline_no_remote_requests(self):
  self.assertEqual(self.page.locator('.card').count(),self.topic_count);self.assertTrue(all(url.startswith(self.origin+'/') for url in self.http))
  self.assertEqual(self.page.locator('#warning,.card .badge').count(),0)
  self.assertEqual(self.page.locator('#metrics strong').all_text_contents(),['72','32','2'])
  self.page.click('#content-info-link')
  self.assertTrue(self.page.locator('#evidence-summary').is_visible())
  self.assertIn('0 个主题完成临床签审',self.page.locator('#evidence-summary').inner_text())
 def test_file_can_reopen_without_network(self):
  if os.environ.get('BROWSER_TRANSPORT')=='html':self.skipTest('In-memory mode cannot verify offline file access')
  self.context.set_offline(True);self.page.goto((ROOT/'index.html').as_uri())
  self.assertEqual(self.page.locator('.card').count(),self.topic_count)
  self.page.fill('#query','普通感冒');self.page.locator('.card[data-id="common-cold"] button').click()
  self.assertEqual(self.page.locator('.detail-section').count(),14)
  self.assertGreater(self.page.locator('#detail-care li').count(),0)
 def test_short_search_and_detail(self):
  self.page.fill('#query','普通感冒');self.assertEqual(self.page.locator('.card').first.get_attribute('data-id'),'common-cold')
  self.page.locator('.card').first.locator('button').click();self.assertTrue(self.page.locator('#detail').is_visible())
  self.assertEqual(self.page.locator('.detail-section').count(),14)
  self.page.keyboard.press('Escape');self.assertFalse(self.page.locator('#detail').is_visible())
 def test_safety_independent_of_filter(self):
  self.page.select_option('#domain','ophthalmic');self.page.fill('#query','胸痛 呼吸困难')
  self.assertGreaterEqual(self.page.locator('.alert').count(),1)
  self.assertTrue(self.page.locator('[data-rule="chest-pain-danger"]').is_visible())
 def test_negation_and_critical_regression(self):
  self.page.fill('#query','没有胸痛，只有咳嗽');self.assertEqual(self.page.locator('.alert').count(),0)
  self.assertTrue(self.page.locator('#safety-note').is_visible())
  self.page.fill('#query','喘不过气');self.assertTrue(self.page.locator('[data-rule="severe-breathing"]').is_visible())
 def test_infant_context(self):
  self.page.locator('#context summary').click();self.page.fill('#age','2');self.page.fill('#temperature','38')
  self.assertTrue(self.page.locator('[data-rule="infant-fever-structured"]').is_visible())
 def test_all_locales_and_explicit_fallback(self):
  for loc in ['en','zh-CN','es','fr','pt-BR','ar','ja','ko','de','ru','hi','id']:
   self.page.select_option('#locale',loc);self.assertEqual(self.page.locator('html').get_attribute('lang'),loc)
   self.assertEqual(self.page.locator('#fallback').is_visible(),loc not in ('zh-CN','en'))
   self.assertEqual(self.page.locator('.card').count(),self.topic_count)
   self.assertEqual(self.page.locator('html').get_attribute('dir'),'rtl' if loc=='ar' else 'ltr')
 def test_all_topic_comparison_and_csv(self):
  self.page.click('#matrix');self.assertEqual(self.page.locator('#comparison tbody tr').count(),self.topic_count)
  self.assertEqual(self.page.locator('#comparison thead th').count(),16)
  with self.page.expect_download() as info:self.page.click('#download')
  download=info.value;data=Path(download.path()).read_text(encoding='utf-8-sig')
  import csv,io
  rows=list(csv.reader(io.StringIO(data)));self.assertEqual(len(rows),self.topic_count+1)
  self.assertIn('editorial_draft',data);self.assertEqual(len(rows[0]),22)
 def test_all_matrix_ignores_search_filter(self):
  self.page.fill('#query','普通感冒');self.assertLess(self.page.locator('.card').count(),self.topic_count)
  self.page.click('#matrix');self.assertEqual(self.page.locator('#comparison tbody tr').count(),self.topic_count)
 def test_selected_comparison(self):
  self.page.locator('.card input[type=checkbox]').nth(0).check();self.page.locator('.card input[type=checkbox]').nth(1).check();self.page.click('#compare')
  self.assertEqual(self.page.locator('#comparison tbody tr').count(),2)
 def test_query_xss_and_no_history(self):
  self.page.fill('#query','<img src=x onerror=alert(1)>')
  self.assertEqual(self.page.locator('#cards img').count(),0)
  self.assertNotIn('onerror',self.page.url)
  if os.environ.get('BROWSER_TRANSPORT') != 'html':
   self.assertEqual(self.page.evaluate('localStorage.length'),0)
   self.assertEqual(self.page.evaluate('sessionStorage.length'),0)
  else:
   code=(ROOT/'src/web/app.mjs').read_text()
   self.assertNotIn('localStorage',code);self.assertNotIn('sessionStorage',code)
 def test_mobile_layout_no_body_overflow(self):
  self.page.set_viewport_size({'width':390,'height':844})
  self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
  self.page.click('#matrix')
  self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
 def test_data_xss_does_not_escape_json_script(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);shutil.copytree(ROOT/'src',r/'src');shutil.copytree(ROOT/'data',r/'data')
   p=r/'data/conditions/acne.json';c=json.loads(p.read_text(encoding='utf-8'));c['names']['zh-CN']='</script><img src=x onerror="window.BAD=1">'
   c['sections']['summary']['text']['zh-CN']='Plain overview.\n\n- <img src=x onerror="window.BAD=1">';p.write_text(json.dumps(c,ensure_ascii=False),encoding='utf-8')
   kp=r/'data/knowledge/lifecycle.json';knowledge=json.loads(kp.read_text(encoding='utf-8'));entry=knowledge['entries'][0]
   entry['title']['zh-CN']='</script><img src=x onerror="window.BAD=1">'
   entry['sections'][0]['text']['zh-CN']='Explanation.\n\n- <img src=x onerror="window.BAD=1">';kp.write_text(json.dumps(knowledge,ensure_ascii=False),encoding='utf-8')
   build(r)
   with serve(r) as origin:
    self.load_page(r/'index.html',origin);self.page.wait_for_selector('.card')
   self.assertIsNone(self.page.evaluate('window.BAD'));self.assertEqual(self.page.locator('.card img').count(),0)
   self.assertIn('</script>',self.page.locator('.card[data-id="acne"] h3').inner_text())
   self.page.locator('.card[data-id="acne"] button').click()
   self.assertEqual(self.page.locator('#detail-summary img').count(),0)
   self.assertIn('<img',self.page.locator('#detail-summary li').inner_text())
   self.assertIsNone(self.page.evaluate('window.BAD'))
   self.page.click('#close-detail');self.page.click('#mode-lifecycle')
   self.assertIn('</script>',self.page.locator('.knowledge-card h3').first.inner_text())
   self.page.locator('.knowledge-card button').first.click()
   self.assertIn('<img',self.page.locator('.knowledge-section li').first.inner_text())
   self.assertEqual(self.page.locator('#knowledge-view img').count(),0)
   self.assertIsNone(self.page.evaluate('window.BAD'))
 def test_source_links_are_safe_external(self):
  self.page.locator('.card').first.locator('button').click();links=self.page.locator('#detail-body a[target="_blank"]')
  self.assertGreater(links.count(),1)
  for a in links.all():self.assertTrue(a.get_attribute('href').startswith('https://'));self.assertIn('noopener',a.get_attribute('rel'))
 def select_skin_department(self):
  self.page.locator('.department-group[data-group="skin-allergy"]>summary').click()
  self.page.locator('[data-department="dermatology"]').click()
 def test_two_level_navigation_and_unique_membership(self):
  self.assertEqual(self.page.locator('#department-nav>.department-group').count(),11)
  self.assertEqual(self.page.locator('.department-group .department-group').count(),0)
  self.assertEqual(self.page.locator('[data-department="sleep-medicine"]').count(),0)
  self.select_skin_department()
  expected=sorted(c['id'] for c in self.conditions.values() if 'dermatology' in c['departments'])
  actual=self.page.locator('.card').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.id).sort()')
  self.assertEqual(actual,expected)
  self.assertEqual(self.page.locator('[data-department="dermatology"]').get_attribute('aria-current'),'page')
  self.page.click('#show-all');self.assertEqual(self.page.locator('.card').count(),self.topic_count)
 def test_group_count_is_union_and_filters_intersect(self):
  self.page.locator('.department-group[data-group="general-emergency"]>summary').click()
  expected=sum(bool({'primary-care','emergency'}&set(c['departments'])) for c in self.conditions.values())
  self.assertEqual(self.page.locator('.card').count(),expected)
  self.page.select_option('#kind','symptom')
  expected_ids=sorted(c['id'] for c in self.conditions.values() if c['kind']=='symptom' and {'primary-care','emergency'}&set(c['departments']))
  self.assertEqual(self.page.locator('.card').evaluate_all('(ns)=>ns.map(n=>n.dataset.id).sort()'),expected_ids)
 def test_department_does_not_suppress_safety(self):
  self.select_skin_department();self.page.fill('#query','胸痛 呼吸困难')
  self.assertTrue(self.page.locator('[data-rule="chest-pain-danger"]').is_visible())
 def test_language_keeps_department_query_selection_and_open_detail(self):
  self.select_skin_department();self.page.fill('#query','acne')
  self.page.locator('.card[data-id="acne"] input').check()
  self.page.select_option('#locale','en')
  self.assertEqual(self.page.locator('#query').input_value(),'acne')
  self.assertTrue(self.page.locator('.card[data-id="acne"] input').is_checked())
  self.assertEqual(self.page.locator('[data-department="dermatology"]').get_attribute('aria-current'),'page')
  self.page.locator('.card[data-id="acne"] button').click()
  self.page.locator('.detail-toc>summary').click()
  self.assertFalse(self.page.locator('.detail-toc').evaluate('(e)=>e.open'))
  self.page.locator('#detail-evidence>summary').click()
  self.page.select_option('#detail-locale','zh-CN')
  self.assertTrue(self.page.locator('#detail').is_visible())
  self.assertFalse(self.page.locator('.detail-toc').evaluate('(e)=>e.open'))
  self.assertTrue(self.page.locator('#detail-evidence').evaluate('(e)=>e.open'))
  self.assertEqual(self.page.locator('#detail-title').inner_text(),self.conditions['acne']['names']['zh-CN'])
  self.page.click('#close-detail');self.assertTrue(self.page.locator('.card[data-id="acne"] input').is_checked())
 def test_full_body_lists_toc_and_danger_first(self):
  self.page.fill('#query','common cold');self.page.locator('.card[data-id="common-cold"] button').click()
  self.assertEqual(self.page.locator('.detail-section').first.get_attribute('id'),'detail-red_flags')
  self.assertEqual(self.page.locator('.detail-toc a').count(),14)
  expected=sum(s['text']['zh-CN'].count('\n- ') for s in self.conditions['common-cold']['sections'].values())
  self.assertEqual(self.page.locator('.detail-section li').count(),expected)
  self.assertGreater(expected,14)
  self.page.locator('.detail-toc a[href="#detail-diagnosis"]').click()
  self.assertEqual(self.page.evaluate('document.activeElement.id'),'detail-diagnosis')
  self.assertNotIn('detail-diagnosis',self.page.url)
  self.page.click('#close-detail');self.assertFalse(self.page.locator('#detail').is_visible())
 def test_comparison_expansion_and_multiline_csv_roundtrip(self):
  self.page.fill('#query','common cold');self.page.click('#matrix')
  row=self.page.locator('#comparison tbody tr[data-id="common-cold"]')
  summary=row.locator('td.cell-text').first
  summary.locator('summary').click();self.assertGreater(summary.locator('li').count(),0)
  self.page.select_option('#locale','en')
  self.assertTrue(summary.locator('details').evaluate('(e)=>e.open'))
  self.assertFalse(summary.locator(':scope > p').is_visible())
  self.page.select_option('#locale','zh-CN')
  self.assertTrue(summary.locator('details').evaluate('(e)=>e.open'))
  with self.page.expect_download() as info:self.page.click('#download')
  import csv,io
  records=list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig'))))
  cold=next(r for r in records if r['id']=='common-cold')
  self.assertEqual(cold['diagnosis'],self.conditions['common-cold']['sections']['diagnosis']['text']['zh-CN'])
 def test_mobile_menu_keyboard_and_reading_layout(self):
  self.page.set_viewport_size({'width':390,'height':844});self.page.click('#menu-toggle')
  self.assertTrue(self.page.locator('#sidebar').is_visible())
  self.assertEqual(self.page.locator('#menu-toggle').get_attribute('aria-expanded'),'true')
  self.page.keyboard.press('Escape')
  self.assertEqual(self.page.locator('#menu-toggle').get_attribute('aria-expanded'),'false')
  self.assertEqual(self.page.evaluate('document.activeElement.id'),'menu-toggle')
  self.page.click('#menu-toggle');self.select_skin_department()
  self.assertEqual(self.page.locator('#menu-toggle').get_attribute('aria-expanded'),'false')
  self.page.locator('.card').first.locator('button').click()
  self.assertEqual(self.page.locator('body').evaluate('(e)=>getComputedStyle(e).overflow'),'hidden')
  self.assertLessEqual(self.page.locator('#detail').evaluate('(e)=>e.scrollWidth'),390)
  self.page.select_option('#detail-locale','ar')
  self.assertEqual(self.page.locator('html').get_attribute('dir'),'rtl')
  self.assertEqual(self.page.locator('#detail-body').get_attribute('lang'),'en')
  self.assertLessEqual(self.page.locator('#detail').evaluate('(e)=>e.scrollWidth'),390)
 def test_arabic_keeps_physical_shell_positions(self):
  self.page.select_option('#locale','ar')
  self.assertEqual(self.page.locator('#result-count').evaluate('(e)=>getComputedStyle(e).direction'),'ltr')
  self.assertEqual(self.page.locator('#sidebar').bounding_box()['x'],0)
  self.assertGreater(self.page.locator('#locale').bounding_box()['x'],self.page.locator('#query').bounding_box()['x'])
 def test_review_information_is_centralized_and_sources_remain(self):
  for locale in ('zh-CN','en','ar'):
   self.page.select_option('#locale',locale)
   self.page.locator('.card[data-id="common-cold"] button').click()
   self.assertEqual(self.page.locator('#detail-body .badge,#detail-body .notice.warning').count(),0)
   for section in self.page.locator('.detail-section').all():
    self.assertGreater(section.locator('.source-list a').count(),0)
    self.assertEqual(section.locator(':scope > p.subtle').count(),0)
   evidence=self.page.locator('#detail-evidence')
   self.assertFalse(evidence.evaluate('(e)=>e.open'))
   evidence.locator('summary').first.click()
   self.assertIn('0 / 14',evidence.inner_text())
   self.assertGreater(evidence.locator('.evidence-card').count(),0)
   self.assertIn('待完成' if locale=='zh-CN' else 'Pending',evidence.inner_text())
   self.page.click('#close-detail')
 def test_knowledge_modes_keep_separate_queries_and_condition_selection(self):
  self.select_skin_department();self.page.fill('#query','acne')
  self.page.locator('.card[data-id="acne"] input').check()
  self.page.click('#mode-cancer');self.page.fill('#query','lung')
  self.assertFalse(self.page.locator('#condition-tools').is_visible())
  self.assertEqual(self.page.locator('#department-nav [aria-current]').count(),0)
  self.page.click('#mode-lifecycle');self.assertEqual(self.page.locator('#query').input_value(),'')
  self.page.click('#mode-cancer');self.assertEqual(self.page.locator('#query').input_value(),'lung')
  self.page.click('#mode-conditions');self.assertEqual(self.page.locator('#query').input_value(),'acne')
  self.assertTrue(self.page.locator('.card[data-id="acne"] input').is_checked())
  self.assertEqual(self.page.locator('[data-department="dermatology"]').get_attribute('aria-current'),'page')
 def test_cancer_entry_reuses_disease_and_shared_factor_with_locale_state(self):
  entry=next(e for e in self.knowledge['cancer']['entries'] if 'breast-cancer' in e['condition_ids'] and e['factor_ids'])
  self.page.click('#mode-cancer')
  self.assertEqual(self.page.locator('.knowledge-card').count(),len(self.knowledge['cancer']['entries']))
  self.page.locator(f'.knowledge-card[data-entry="{entry["id"]}"] button').click()
  self.page.locator('.knowledge-toc a').last.click()
  self.assertEqual(self.page.evaluate('document.activeElement.id'),'entry-'+entry['id']+'-'+entry['sections'][-1]['id'])
  self.assertNotIn('entry-',self.page.url)
  self.page.locator('.knowledge-evidence>summary').click();self.page.select_option('#locale','en')
  self.assertEqual(self.page.locator('.knowledge-article').get_attribute('data-entry'),entry['id'])
  self.assertTrue(self.page.locator('.knowledge-evidence').evaluate('(e)=>e.open'))
  self.page.get_by_role('button',name=self.conditions['breast-cancer']['names']['en'],exact=True).click()
  self.assertEqual(self.page.locator('#detail-title').inner_text(),self.conditions['breast-cancer']['names']['en'])
  self.page.select_option('#detail-locale','ar');self.page.click('#close-detail')
  self.assertEqual(self.page.evaluate('document.activeElement.id'),'knowledge-entry-title')
  self.assertEqual(self.page.locator('.knowledge-article').get_attribute('data-entry'),entry['id'])
  factor=next(e for e in self.knowledge['lifecycle']['entries'] if e['id']==entry['factor_ids'][0])
  self.page.get_by_role('button',name=factor['title']['en'],exact=True).click()
  self.assertEqual(self.page.locator('#mode-lifecycle').get_attribute('aria-pressed'),'true')
  self.assertEqual(self.page.locator('.knowledge-article').get_attribute('data-entry'),factor['id'])
  self.assertEqual(self.page.evaluate('document.activeElement.id'),'knowledge-entry-title')
 def test_lifecycle_stage_group_intersection_and_mobile_fallback(self):
  self.page.set_viewport_size({'width':390,'height':844});self.page.click('#mode-lifecycle')
  module=self.knowledge['lifecycle'];stage=next(s for s in module['stages'] if s['kind']=='age')
  group=next(e['group_id'] for e in module['entries'] if e['id'] in stage['factor_ids'])
  self.page.select_option('#knowledge-stage',stage['id']);self.page.select_option('#knowledge-group',group)
  expected=sorted(e['id'] for e in module['entries'] if e['id'] in stage['factor_ids'] and e['group_id']==group)
  self.assertEqual(self.page.locator('.knowledge-card').evaluate_all('(ns)=>ns.map(n=>n.dataset.entry).sort()'),expected)
  self.assertEqual(self.page.locator('#knowledge-stage optgroup').count(),2)
  self.page.select_option('#locale','ar')
  self.assertEqual(self.page.locator('#knowledge-stage').input_value(),stage['id'])
  self.assertEqual(self.page.locator('#knowledge-group').input_value(),group)
  self.assertEqual(self.page.locator('.knowledge-stage h3').first.inner_text(),stage['title']['en'])
  self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
  self.page.locator('.knowledge-card button').first.click()
  self.assertGreater(self.page.locator('.knowledge-section li').count(),0)
  self.assertEqual(self.page.locator('#knowledge-entry-title').get_attribute('lang'),'en')
  self.assertEqual(self.page.locator('.knowledge-toc').get_attribute('dir'),'ltr')
  self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
 def test_knowledge_search_preserves_independent_danger_alerts_and_privacy(self):
  self.page.click('#mode-cancer');self.page.fill('#query','胸痛 呼吸困难')
  self.assertTrue(self.page.locator('[data-rule="chest-pain-danger"]').is_visible())
  self.page.fill('#query','<img src=x onerror=alert(1)>')
  self.assertEqual(self.page.locator('#knowledge-view img').count(),0)
  self.assertNotIn('onerror',self.page.url)
  self.assertTrue(all(url.startswith(self.origin+'/') for url in self.http))
  self.assertEqual(self.page.evaluate('localStorage.length'),0)
  self.assertEqual(self.page.evaluate('sessionStorage.length'),0)
 def test_knowledge_offline_reopen_and_section_references(self):
  if os.environ.get('BROWSER_TRANSPORT')=='html':self.skipTest('In-memory mode cannot verify offline file access')
  self.context.set_offline(True);self.page.goto((ROOT/'index.html').as_uri());self.page.click('#mode-lifecycle')
  self.assertEqual(self.page.locator('.knowledge-card').count(),len(self.knowledge['lifecycle']['entries']))
  self.page.locator('.knowledge-card button').first.click()
  for section in self.page.locator('.knowledge-article .knowledge-section').all():
   links=section.locator('.source-list a');self.assertGreater(links.count(),0)
   for a in links.all():self.assertTrue(a.get_attribute('href').startswith('https://'));self.assertIn('noopener',a.get_attribute('rel'))
if __name__=='__main__':unittest.main()
