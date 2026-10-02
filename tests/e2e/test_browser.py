"""Real HTTP + PostgreSQL browser checks. Initialize the dedicated test database first.
HEALTHCARE_TEST_READ_DSN selects it; GUIDE_URL instead targets a deployed service.
"""
from pathlib import Path
import json
import os
import shutil
import unittest
import threading
import socket
import time
from playwright.sync_api import sync_playwright, expect
from src.guide.model import ROOT
from src.guide.build import build

class BrowserTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.conditions={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'data/conditions').glob('*.json')}
  cls.topic_count=len(cls.conditions)
  cls.knowledge={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'data/knowledge').glob('*.json')}
  cls.server=None
  if os.environ.get('GUIDE_URL'):
   cls.origin=os.environ['GUIDE_URL'].rstrip('/')
  else:
   import uvicorn
   from src.guide.api import create_app
   dsn=os.environ.get('HEALTHCARE_TEST_READ_DSN')
   if not dsn:raise RuntimeError('Set HEALTHCARE_TEST_READ_DSN to the initialized dedicated test database')
   build(ROOT)
   cls.socket=socket.socket();cls.socket.bind(('127.0.0.1',0))
   cls.origin=f'http://127.0.0.1:{cls.socket.getsockname()[1]}/healthcare'
   cls.server=uvicorn.Server(uvicorn.Config(create_app(dsn,root=ROOT),log_level='error'))
   cls.thread=threading.Thread(target=cls.server.run,kwargs={'sockets':[cls.socket]},daemon=True);cls.thread.start()
   deadline=time.monotonic()+15
   while not cls.server.started and cls.thread.is_alive() and time.monotonic()<deadline:time.sleep(.05)
   if not cls.server.started:raise RuntimeError('HTTP service did not start')
  cls.pw=sync_playwright().start()
  executable=os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium')
  cls.browser=cls.pw.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):
  cls.browser.close();cls.pw.stop()
  if cls.server:cls.server.should_exit=True;cls.thread.join(timeout=10);cls.socket.close()
 def setUp(self):
  self.context=self.browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
  self.page=self.context.new_page();self.errors=[];self.http=[]
  if os.environ.get('GUIDE_URL'):self.page.set_default_navigation_timeout(120000)
  self.page.on('pageerror',lambda e:self.errors.append(str(e)))
  self.requests=[]
  self.page.on('request',lambda req:self.requests.append({'url':req.url,'body':req.post_data or ''}))
  self.page.on('request',lambda req:self.http.append(req.url) if req.url.startswith(('https:','http:')) else None)
  self.load_page(ROOT/'index.html', self.origin);self.page.wait_for_selector('#result-view[data-catalog-status="ready"]')
 def load_page(self, path, origin):
  self.page.goto(origin+'/')
 def tearDown(self):
  self.assertEqual(self.errors,[],'Browser script errors');self.context.close()
 def test_online_shell_uses_only_same_origin_and_paged_catalog(self):
  self.assertEqual(self.page.locator('.card').count(),min(50,self.topic_count));self.assertTrue(all(url.startswith(self.origin+'/') for url in self.http))
  shell=self.page.locator('#guide-data').text_content();self.assertEqual(json.loads(shell)['conditions'],[])
  self.assertNotIn('diagnosis',json.dumps(json.loads(shell)['knowledge']))
  self.assertFalse(any('/conditions/' in url for url in self.http))
  self.assertEqual(self.page.locator('#warning,.card .badge').count(),0)
  specialties=len({d for c in self.conditions.values() for d in c['departments']})
  self.assertEqual(self.page.locator('#metrics strong').all_text_contents(),[str(self.topic_count),str(specialties),'2'])
  self.page.click('#content-info-link')
  self.assertTrue(self.page.locator('#evidence-summary').is_visible())
  self.assertIn('0 个主题完成临床签审',self.page.locator('#evidence-summary').inner_text())
  self.assertIn('最终目标为 100%',self.page.locator('#evidence-summary').inner_text())
  self.assertIn('95% 为阶段里程碑',self.page.locator('#evidence-summary').inner_text())
  expect(self.page.locator('#evidence-summary a[href$="/docs/icd-priorities/index.md"]')).to_be_visible()
 def test_database_failure_shows_error_and_keeps_emergency_rules(self):
  self.page.route('**/api/v1/**',lambda route:route.fulfill(status=503,json={'error':'unavailable'}))
  self.page.reload();self.page.wait_for_selector('#result-view[data-catalog-status="error"]')
  self.assertIn('无法加载',self.page.locator('#catalog-status').inner_text())
  self.assertNotIn('未找到匹配',self.page.locator('#cards').inner_text())
  self.page.fill('#query','胸痛 呼吸困难');expect(self.page.locator('[data-rule="chest-pain-danger"]')).to_be_visible()
  self.assertTrue(self.page.locator('#download').is_disabled())
 def test_short_search_and_detail(self):
  self.page.fill('#query','普通感冒');self.assertEqual(self.page.locator('.card').first.get_attribute('data-id'),'common-cold')
  self.page.locator('.card').first.locator('button').click();self.assertTrue(self.page.locator('#detail').is_visible())
  expect(self.page.locator('.detail-section')).to_have_count(14)
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
   self.assertEqual(self.page.locator('.card').count(),min(50,self.topic_count))
   self.assertEqual(self.page.locator('html').get_attribute('dir'),'rtl' if loc=='ar' else 'ltr')
 def test_all_topic_comparison_and_csv(self):
  self.page.click('#matrix');expect(self.page.locator('#comparison tbody tr')).to_have_count(min(50,self.topic_count))
  self.assertEqual(self.page.locator('#comparison thead th').count(),16)
  with self.page.expect_download() as info:self.page.click('#download')
  download=info.value;data=Path(download.path()).read_text(encoding='utf-8-sig')
  import csv,io
  rows=list(csv.reader(io.StringIO(data)));self.assertEqual(len(rows),self.topic_count+1)
  self.assertIn('editorial_draft',data);self.assertEqual(len(rows[0]),22)
 def test_all_matrix_ignores_search_filter(self):
  self.page.fill('#query','普通感冒');self.assertLess(self.page.locator('.card').count(),self.topic_count)
  self.page.click('#matrix');expect(self.page.locator('#comparison tbody tr')).to_have_count(min(50,self.topic_count))
 def test_selected_comparison(self):
  self.page.locator('.card input[type=checkbox]').nth(0).check();self.page.locator('.card input[type=checkbox]').nth(1).check();self.page.click('#compare')
  expect(self.page.locator('#comparison tbody tr')).to_have_count(2)
 def test_query_xss_and_no_history(self):
  self.page.fill('#query','<img src=x onerror=alert(1)>')
  self.assertEqual(self.page.locator('#cards img').count(),0)
  self.assertNotIn('onerror',self.page.url)
  self.assertEqual(self.page.evaluate('localStorage.length'),0)
  self.assertEqual(self.page.evaluate('sessionStorage.length'),0)
 def test_mobile_layout_no_body_overflow(self):
  self.page.set_viewport_size({'width':390,'height':844})
  self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
  self.page.click('#matrix')
  self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),390)
 def test_data_xss_does_not_escape_json_script(self):
  marker='</script><img src=x onerror="window.BAD=1">'
  def modify(route):
   response=route.fetch();data=response.json()
   if '/catalog?' in route.request.url:
    next(c for c in data['items'] if c['id']=='acne')['names']['zh-CN']=marker
   elif '/conditions/acne?' in route.request.url:
    data['condition']['sections']['summary']['text']['zh-CN']='Plain overview.\n\n- '+marker
   elif '/knowledge/lifecycle?' in route.request.url:
    entry=data['module']['entries'][0];entry['title']['zh-CN']=marker;entry['sections'][0]['text']['zh-CN']='Explanation.\n\n- '+marker
   route.fulfill(response=response,json=data)
  self.page.route('**/api/v1/**',modify);self.page.reload();self.page.wait_for_selector('#result-view[data-catalog-status="ready"]')
  self.assertIsNone(self.page.evaluate('window.BAD'));self.assertEqual(self.page.locator('.card img').count(),0)
  self.assertIn('</script>',self.page.locator('.card[data-id="acne"] h3').inner_text())
  self.page.locator('.card[data-id="acne"] button').click();expect(self.page.locator('.detail-section')).to_have_count(14)
  self.assertEqual(self.page.locator('#detail-summary img').count(),0);self.assertIn('<img',self.page.locator('#detail-summary li').inner_text())
  self.page.click('#close-detail');self.page.click('#mode-lifecycle');expect(self.page.locator('.knowledge-card')).to_have_count(len(self.knowledge['lifecycle']['entries']))
  self.assertIn('</script>',self.page.locator('.knowledge-card h3').first.inner_text())
  self.page.locator('.knowledge-card button').first.click();self.assertIn('<img',self.page.locator('.knowledge-section li').first.inner_text())
  self.assertEqual(self.page.locator('#knowledge-view img').count(),0);self.assertIsNone(self.page.evaluate('window.BAD'))
 def test_source_links_are_safe_external(self):
  self.page.locator('.card').first.locator('button').click();expect(self.page.locator('.detail-section')).to_have_count(14);links=self.page.locator('#detail-body a[target="_blank"]')
  self.assertGreater(links.count(),1)
  for a in links.all():self.assertTrue(a.get_attribute('href').startswith('https://'));self.assertIn('noopener',a.get_attribute('rel'))
 def select_skin_department(self):
  self.page.locator('.department-group[data-group="skin-allergy"]>summary').click()
  self.page.locator('[data-department="dermatology"]').click()
 def test_two_level_navigation_and_unique_membership(self):
  self.assertEqual(self.page.locator('#department-nav>.department-group').count(),11)
  self.assertEqual(self.page.locator('.department-group .department-group').count(),0)
  sleep_present=any('sleep-medicine' in c['departments'] for c in self.conditions.values())
  self.assertEqual(self.page.locator('[data-department="sleep-medicine"]').count(),int(sleep_present))
  self.select_skin_department()
  expected=sorted(c['id'] for c in self.conditions.values() if 'dermatology' in c['departments'])
  actual=self.page.locator('.card').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.id).sort()')
  self.assertEqual(actual,expected)
  self.assertEqual(self.page.locator('[data-department="dermatology"]').get_attribute('aria-current'),'page')
  self.page.click('#show-all');self.assertEqual(self.page.locator('.card').count(),min(50,self.topic_count))
 def test_group_count_is_union_and_filters_intersect(self):
  self.page.locator('.department-group[data-group="general-emergency"]>summary').click()
  expected=sum(bool({'primary-care','emergency'}&set(c['departments'])) for c in self.conditions.values())
  self.assertEqual(self.page.locator('.card').count(),min(50,expected))
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
  expect(self.page.locator('.detail-section')).to_have_count(14)
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
  expect(self.page.locator('.knowledge-card')).to_have_count(len(self.knowledge['cancer']['entries']))
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
  expect(self.page.locator('#knowledge-entry-title')).to_be_focused()
  self.assertEqual(self.page.locator('.knowledge-article').get_attribute('data-entry'),entry['id'])
  factor=next(e for e in self.knowledge['lifecycle']['entries'] if e['id']==entry['factor_ids'][0])
  self.page.get_by_role('button',name=factor['title']['en'],exact=True).click()
  self.assertEqual(self.page.locator('#mode-lifecycle').get_attribute('aria-pressed'),'true')
  expect(self.page.locator('.knowledge-article')).to_have_attribute('data-entry',factor['id'])
  expect(self.page.locator('#knowledge-entry-title')).to_be_focused()
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
 def test_knowledge_lazy_request_and_section_references(self):
  self.assertFalse(any('/knowledge/' in url for url in self.http))
  self.page.click('#mode-lifecycle')
  expect(self.page.locator('.knowledge-card')).to_have_count(len(self.knowledge['lifecycle']['entries']))
  self.assertTrue(any('/knowledge/lifecycle?' in url for url in self.http))
  self.page.locator('.knowledge-card button').first.click()
  for section in self.page.locator('.knowledge-article .knowledge-section').all():
   links=section.locator('.source-list a');self.assertGreater(links.count(),0)
   for a in links.all():self.assertTrue(a.get_attribute('href').startswith('https://'));self.assertIn('noopener',a.get_attribute('rel'))
 def test_selection_persists_across_pages_and_export_includes_both(self):
  first=self.page.locator('.card').first.get_attribute('data-id');self.page.locator('.card input').first.check()
  self.page.locator('#cards-pages button').last.click();second=self.page.locator('.card').first.get_attribute('data-id')
  self.page.locator('.card input').first.check();self.page.locator('#cards-pages button').first.click()
  self.assertTrue(self.page.locator(f'.card[data-id="{first}"] input').is_checked())
  self.page.click('#compare');expect(self.page.locator('#comparison tbody tr')).to_have_count(2)
  self.assertEqual(set(self.page.locator('#comparison tbody tr').evaluate_all('(ns)=>ns.map(n=>n.dataset.id)')),{first,second})
  with self.page.expect_download() as info:self.page.click('#download')
  import csv,io
  records=list(csv.DictReader(io.StringIO(Path(info.value.path()).read_text(encoding='utf-8-sig'))))
  self.assertEqual({r['id'] for r in records},{first,second})
 def test_failed_csv_preserves_reading_and_explains_failure(self):
  self.page.route('**/exports/conditions.csv',lambda route:route.fulfill(status=503,json={'detail':'unavailable'}))
  self.page.click('#download');expect(self.page.locator('#export-status')).to_be_visible()
  self.assertEqual(self.page.locator('.card').count(),50);self.assertTrue(self.page.url.endswith('/healthcare/'))
 def test_search_and_safety_inputs_do_not_make_requests(self):
  before=len(self.requests);probe='private-local-probe-920174'
  self.page.fill('#query',probe);self.page.locator('#context summary').click()
  self.page.fill('#age','2.5');self.page.fill('#temperature','38.6');self.page.wait_for_timeout(100)
  self.assertEqual(len(self.requests),before)
  self.assertNotIn(probe,json.dumps(self.requests));self.assertEqual(self.page.evaluate('localStorage.length+sessionStorage.length'),0)
 def test_all_content_requests_use_the_bootstrap_release(self):
  release=self.page.locator('html').get_attribute('data-release-id')
  self.page.locator('.card').first.locator('button').click();expect(self.page.locator('.detail-section')).to_have_count(14)
  self.page.click('#close-detail');self.page.click('#matrix');expect(self.page.locator('#comparison tbody tr')).to_have_count(50)
  from urllib.parse import urlparse,parse_qs
  for request in self.requests:
   if '/api/v1/' not in request['url'] or request['url'].endswith('/bootstrap'):continue
   actual=json.loads(request['body'])['release_id'] if request['body'] else parse_qs(urlparse(request['url']).query)['release_id'][0]
   self.assertEqual(actual,release)
 def test_late_detail_response_cannot_replace_new_selection(self):
  pending=[]
  def delay(route):pending.append((route,route.fetch()))
  self.page.route('**/conditions/acne?*',delay)
  self.page.locator('.card[data-id="acne"] button').click();self.page.wait_for_timeout(100)
  self.assertTrue(pending);self.page.click('#close-detail')
  other=next(c for c in self.conditions.values() if c['id']=='allergic-rhinitis')
  self.page.locator('.card[data-id="allergic-rhinitis"] button').click();expect(self.page.locator('.detail-section')).to_have_count(14)
  route,response=pending[0];route.fulfill(response=response);self.page.wait_for_timeout(100)
  self.assertEqual(self.page.locator('#detail-title').inner_text(),other['names']['zh-CN'])
 def test_catalog_incomplete_state_does_not_claim_full_search(self):
  pending=[];catalog=[]
  def split(route):
   if 'offset=0&' in route.request.url:
    data=route.fetch().json();catalog.extend(data['items']);data['items']=catalog[:36];route.fulfill(json=data)
   else:pending.append(route)
  self.page.route('**/catalog?*',split);self.page.reload()
  self.page.wait_for_selector('.card');expect(self.page.locator('#catalog-status')).to_contain_text('目录仍在加载')
  self.assertTrue(self.page.locator('#download').is_disabled());self.assertEqual(self.page.locator('.card').count(),36)
  self.assertTrue(pending);release=self.page.locator('html').get_attribute('data-release-id')
  pending[0].fulfill(json={'release_id':release,'offset':36,'total':len(catalog),'items':catalog[36:]})
  self.page.wait_for_selector('#result-view[data-catalog-status="ready"]');self.assertFalse(self.page.locator('#download').is_disabled())
 def test_synthetic_catalog_scale_keeps_dom_bounded_and_search_local(self):
  # Rendering capacity fixture only; these synthetic IDs are never medical coverage.
  import copy
  from urllib.parse import urlparse,parse_qs
  count=13155;source=None
  def large_catalog(route):
   nonlocal source
   offset=int(parse_qs(urlparse(route.request.url).query)['offset'][0])
   if source is None:source=route.fetch().json()['items'][0]
   items=[]
   for i in range(offset,min(offset+1000,count)):
    item=copy.deepcopy(source);item['id']=f'synthetic-{i}';item['names']={'zh-CN':f'容量样本 {i}', 'en':f'Capacity sample {i}'}
    item['aliases']={'zh-CN':[], 'en':[f'unique-token-{i}']};items.append(item)
   route.fulfill(json={'release_id':self.page.locator('html').get_attribute('data-release-id'),'offset':offset,'total':count,'items':items})
  self.page.route('**/catalog?*',large_catalog);self.page.reload()
  self.page.wait_for_selector('#result-view[data-catalog-status="ready"]',timeout=60000)
  self.assertEqual(self.page.locator('.card').count(),50);self.assertIn(str(count),self.page.locator('#result-count').inner_text())
  self.page.fill('#query','unique-token-13154');self.assertEqual(self.page.locator('.card').first.get_attribute('data-id'),'synthetic-13154')
  self.assertFalse(any('unique-token' in request['url'] or 'unique-token' in request['body'] for request in self.requests))
if __name__=='__main__':unittest.main()
