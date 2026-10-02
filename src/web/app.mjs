import { LocalSearch } from './search.mjs';
import { evaluateSafety } from './safety.mjs';
import { safeSourceURL } from './export.mjs';
import { appendText, firstParagraph, textBlocks } from './text.mjs';
import { departmentNavigation } from './navigation.mjs';
import { createKnowledgeView } from './knowledge.mjs';
import { GuideAPI, ONLINE_MESSAGES, PAGE_SIZE, pageItems } from './api.mjs';
// The shell contains safety rules; content is read from one immutable database release.
const D=JSON.parse(document.getElementById('guide-data').textContent);
const api=new GuideAPI(new URL(D.api_base,document.baseURI).href);
let engine=new LocalSearch(D.conditions);
const byId=new Map(D.conditions.map(c=>[c.id,c]));
const bySource=new Map(D.sources.map(s=>[s.id,s]));
const byDomain=new Map(D.taxonomy.map(t=>[t.id,t]));
let navigation=departmentNavigation(D.conditions,D.department_groups);
const state={locale:'zh-CN',mode:'conditions',queries:{conditions:'',cancer:'',lifecycle:''},selected:new Set(),view:'cards',results:[],group:'',department:'',detailId:null,detailTrigger:null,openGroups:new Set(['internal-medicine']),page:0,tablePage:0,catalogStatus:'loading',catalogTotal:0,detailRequest:0,tableRequest:0};
const el=id=>document.getElementById(id);
const t=key=>D.locales[state.locale].strings[key]||ONLINE_MESSAGES[key]?.[state.locale]||ONLINE_MESSAGES[key]?.en||D.locales.en.strings[key]||key;
const medicalLang=()=>D.locales[state.locale].medical_locale;
const txt=value=>typeof value==='string'?value:value?.[medicalLang()]??value?.en??t('unknown');
const knowledgeView=createKnowledgeView({root:el('knowledge-view'),modules:D.knowledge,t,txt,medicalLang,conditions:byId,openCondition:showDetail,openModule:setMode});
function node(tag,text,cls) {
  const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(cls)n.className=cls;return n;
}
function link(source) {
  const a=node('a',source.title);const url=safeSourceURL(source.url);
  if(url){a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.referrerPolicy='no-referrer';}
  return a;
}
function dept(c){return c.departments.map(id=>txt(D.departments[id])).join(' · ');}
function translatedButton(key,fn,cls=''){const b=node('button',t(key),cls);b.type='button';b.addEventListener('click',fn);return b;}
function scopeDepartments(){return state.department?[state.department]:navigation.find(g=>g.id===state.group)?.departments??[];}
function scopeLabel(){return state.department?txt(D.departments[state.department]):state.group?txt(navigation.find(g=>g.id===state.group).label):t('showAll');}
function chooseScope(group='',department='') {
  state.group=group;state.department=department;
  if(group)state.openGroups.add(group);
  state.view='cards';state.page=0;setMode('conditions');
}
async function setMode(mode,{entryId}={}) {
  state.queries[state.mode]=el('query').value;state.mode=mode;
  if(entryId){state.queries[mode]='';knowledgeView.selectEntry(mode,entryId);}
  el('query').value=state.queries[mode];update();
  if(mode!=='conditions')await loadKnowledge(mode);
  if(entryId&&state.mode===mode){const title=el('knowledge-entry-title');title?.scrollIntoView({block:'start'});title?.focus({preventScroll:true});}
}
async function loadKnowledge(mode){
  if(D.knowledge[mode].entries)return;
  const target=el('knowledge-view');target.replaceChildren(node('p',t('loading'),'empty'));
  try{Object.assign(D.knowledge[mode],await api.knowledge(mode));if(state.mode===mode)update();}
  catch{if(state.mode===mode)showLoadError(target,()=>loadKnowledge(mode));}
}
function showLoadError(target,retry){target.replaceChildren(node('p',t('loadFailed'),'empty'),translatedButton('retry',retry));}
function mergeReferences(data){
  for(const source of data.sources||[])bySource.set(source.id,source);
  for(const study of data.studies||[])if(!D.studies.some(s=>s.id===study.id))D.studies.push(study);
}
function renderCatalogStatus(){
  const target=el('catalog-status');target.replaceChildren();target.hidden=state.catalogStatus==='ready';
  el('result-view').dataset.catalogStatus=state.catalogStatus;
  if(state.catalogStatus!=='ready'){
    target.append(node('p',t(state.catalogStatus==='error'?'loadFailed':D.conditions.length?'catalogPartial':'catalogLoading')));
    if(state.catalogStatus==='error')target.append(translatedButton('retry',loadCatalog));
  }
  el('download').disabled=state.catalogStatus!=='ready';
}
let catalogLoading=false;
async function loadCatalog(){
  if(catalogLoading)return;catalogLoading=true;
  state.catalogStatus='loading';renderCatalogStatus();
  try{
    if(!api.release){
      const bootstrap=await api.bootstrap();const modules=D.knowledge;
      Object.assign(D,bootstrap);D.knowledge=modules;
      for(const [id,metadata] of Object.entries(bootstrap.knowledge))Object.assign(modules[id],metadata);
      mergeReferences(bootstrap);byDomain.clear();for(const domain of D.taxonomy)byDomain.set(domain.id,domain);
      document.documentElement.dataset.releaseId=api.release;refreshLocale();
    }
    const rows=new Map();
    for await(const page of api.catalog()){
      for(const item of page.items)rows.set(item.id,item);
      D.conditions=[...rows.values()];state.catalogTotal=page.total;
      for(const item of D.conditions)byId.set(item.id,item);
      engine=new LocalSearch(D.conditions);navigation=departmentNavigation(D.conditions,D.department_groups);
      state.catalogStatus=page.complete?'ready':'loading';renderNavigation();renderCatalogStatus();update();
    }
    refreshLocale();
  }catch{state.catalogStatus='error';renderCatalogStatus();update();}
  finally{catalogLoading=false;}
}
function renderNavigation() {
  const nav=el('department-nav');nav.replaceChildren();nav.setAttribute('aria-label',t('navHeading'));
  const all=translatedButton('showAll',()=>{chooseScope();setMenu(false);},'nav-all');all.id='nav-all';
  all.append(node('span',D.conditions.length,'nav-count'));nav.append(all);
  for(const group of navigation) {
    const details=node('details',undefined,'department-group');details.dataset.group=group.id;details.open=state.openGroups.has(group.id);
    const summary=node('summary');summary.dataset.group=group.id;
    summary.append(node('span',txt(group.label)),node('span',group.count,'nav-count'));
    summary.addEventListener('click',()=>chooseScope(group.id));
    details.addEventListener('toggle',()=>{if(details.open)state.openGroups.add(group.id);else state.openGroups.delete(group.id);});
    const children=node('div',undefined,'department-children');
    for(const department of group.children) {
      const button=node('button',undefined,'nav-department');button.type='button';button.dataset.department=department.id;
      button.append(node('span',txt(D.departments[department.id])),node('span',department.count,'nav-count'));
      button.addEventListener('click',()=>{chooseScope(group.id,department.id);setMenu(false);});children.append(button);
    }
    details.append(summary,children);nav.append(details);
  }
  updateNavigation();
}
function updateNavigation() {
  for(const target of el('department-nav').querySelectorAll('[aria-current]'))target.removeAttribute('aria-current');
  const active=state.department?el('department-nav').querySelector(`[data-department="${state.department}"]`):state.group?el('department-nav').querySelector(`summary[data-group="${state.group}"]`):el('nav-all');
  active?.setAttribute('aria-current','page');
  el('active-scope').textContent=t('searchWithin')+' · '+scopeLabel();
  el('results-label').textContent=state.group?scopeLabel():t('results');
}
function setMenu(open) {
  const hadFocus=el('sidebar').contains(document.activeElement);
  if(!window.matchMedia('(max-width: 850px)').matches)open=false;
  el('sidebar').toggleAttribute('data-open',open);el('menu-backdrop').hidden=!open;
  el('menu-toggle').setAttribute('aria-expanded',String(open));
  el('sidebar').inert=window.matchMedia('(max-width: 850px)').matches&&!open;
  document.body.classList.toggle('menu-open',open);
  if(open)el('menu-close').focus();
  else if(hadFocus&&window.matchMedia('(max-width: 850px)').matches)el('menu-toggle').focus();
}
function refreshLocale() {
  const cfg=D.locales[state.locale];document.documentElement.lang=state.locale;document.documentElement.dir=cfg.dir;
  el('main').dir=cfg.dir;el('sidebar').dir=cfg.dir;
  el('locale').value=state.locale;el('detail-locale').value=state.locale;
  document.title=t('title');
  const labels={'title':'title','subtitle':'subtitle','locale-label':'language','query-label':'search','scope':'scope','reset':'clear','manual-label':'manualDanger','manual-text':'dangerAction','safety-note':'safetyUnknown','matrix':'matrix','download':'export','results-label':'results','not-diagnostic':'notDiagnostic','back':'back','evidence-title':'evidence','privacy':'privacy','close-detail':'close','studies-title':'study','brand-subtitle':'title','department-heading':'navHeading','sidebar-local':'localReading','sidebar-note':'navNote','library-label':'library','show-all':'showAll','reading-label':'reading','context-label':'infantContext','age-label':'ageMonths','temperature-label':'temperature','context-note':'contextNote'};
  for(const [id,key] of Object.entries(labels))el(id).textContent=t(key);
  el('sidebar-local').textContent=t('onlineReading');
  el('content-info-link').textContent=t('evidence');
  for(const [mode,key] of [['conditions','topics'],['cancer','cancerMap'],['lifecycle','lifecycleMap']])el('mode-'+mode).textContent=t(key);
  el('fallback').hidden=['zh-CN','en'].includes(state.locale);el('fallback').textContent=t('fallback');
  el('domain').setAttribute('aria-label',t('domains'));el('kind').setAttribute('aria-label',t('anyKind'));
  for(const id of ['menu-toggle','menu-close','menu-backdrop'])el(id).setAttribute('aria-label',t(id==='menu-toggle'?'menuOpen':'menuClose'));
  el('sidebar').setAttribute('aria-label',t('navHeading'));el('detail-locale').setAttribute('aria-label',t('language'));
  const metrics=el('metrics');metrics.replaceChildren();
  for(const [v,key] of [[api.release?D.stats.conditions:'…','topics'],[api.release?navigation.reduce((n,g)=>n+g.children.length,0):'…','specialties'],[new Set(Object.values(D.locales).map(l=>l.medical_locale)).size,'bodyLanguages']]){
    const m=node('div',undefined,'metric');m.append(node('strong',v),node('span',t(key)));metrics.append(m);
  }
  const domainValue=el('domain').value;el('domain').replaceChildren(new Option(t('all'),''));
  for(const domain of D.taxonomy)el('domain').add(new Option(txt(domain.label),domain.id));el('domain').value=domainValue;
  const kindValue=el('kind').value;el('kind').replaceChildren(new Option(t('anyKind'),''),new Option(t('condition'),'condition'),new Option(t('symptom'),'symptom'));el('kind').value=kindValue;
  const ev=el('evidence-summary');ev.replaceChildren();
  const clinical=medicalLang()==='zh-CN';
  const coverage=D.coverage||D.project.coverage_target,measured=coverage.fraction??coverage.measured;
  const denominator=coverage.denominator,rate=typeof measured==='number'?(100*measured).toFixed(2)+'%':null;
  const target=100*coverage.target,milestone=100*(coverage.milestone??coverage.target);
  const coverageText=denominator&&rate?(clinical?
    `ICD-11 MMS 2026-01 已冻结 ${denominator} 个合格独立类别。已逐项核验的类别覆盖率为 ${rate}，最终目标为 ${target}%，${milestone}% 为阶段里程碑。达标需要完整双语正文、独立来源交叉核验和类别对应审核；现有病症主题另行计数。知识地图、别名和文章中的提及不计入，类别覆盖率不表示真实患者覆盖率。`:
    `The ICD-11 MMS 2026-01 denominator is frozen at ${denominator} eligible independent categories. Fully audited category coverage is ${rate}; the final target is ${target}%, with ${milestone}% as an intermediate milestone. Qualification requires complete bilingual content, independent-source cross-checking and confirmed category mapping; existing article counts are reported separately. Maps, aliases and mentions do not count, and category coverage does not measure real patient coverage.`):
    (clinical?'最终目标为完整覆盖 ICD-11 MMS 2026-01 合格独立病症类别，95%为阶段里程碑。当前完整覆盖率尚未测定；标题待办、完整正文和医学签审分别统计。':'The final target is complete coverage of eligible independent condition categories in ICD-11 MMS 2026-01;95% is an intermediate milestone. Coverage is currently unmeasured; title-only tasks, complete articles and clinician approval are counted separately.');
  ev.append(node('p',clinical?'正文依据各节所列资料编写，提供病症知识和常见就医行动。独立医学审阅、译文审核和危险提示规则的临床验证待完成；地区诊疗路径按当地规定。':'The articles explain conditions and common care actions using the references linked in each section. Independent medical and translation review and clinical validation of alert rules are pending; local care pathways follow local guidance.'),
    node('p',clinical?`病症正文：${D.stats.sources} 条来源记录 · ${D.stats.total_sections} 个正文章节 · ${D.stats.verified_sections} 个章节完成逐项双源核验 · ${D.stats.clinically_reviewed} 个主题完成临床签审。`:
      `Condition articles: ${D.stats.sources} source records · ${D.stats.total_sections} sections · ${D.stats.verified_sections} sections verified against independent sources · ${D.stats.clinically_reviewed} clinician-approved topics.`),
    node('p',coverageText));
  const priorities=node('p');priorities.append(link({title:clinical?'全病症专业优先清单与补充顺序':'Full condition priority list and completion queue',url:'https://github.com/StarlightDamian/knowledge-healthcare/blob/main/docs/icd-priorities/index.md'}));ev.append(priorities);
  ev.lang=medicalLang();ev.dir='ltr';
  const maps=D.stats.knowledge,mapSources=Object.values(maps.by_module).reduce((n,m)=>n+m.sources,0);
  ev.append(node('p',clinical?`癌症与生命周期地图另有${maps.entries}个知识单元、${maps.sections}个章节和${mapSources}条来源记录，复用已有病症正文和健康因素。研报整合与来源定位已记录，独立医学审阅待完成；这些地图单元另行统计。`:`The cancer and life-course maps have ${maps.entries} knowledge units, ${maps.sections} sections and ${mapSources} source records, linking to existing condition articles and shared factors. Report integration and source locations are recorded; independent medical review is pending. Map units are counted separately.`));
  renderNavigation();renderStudies();renderCatalogStatus();update();
  if(el('detail').open&&state.detailId){
    const scroll=el('detail').scrollTop,expanded=new Set([...el('detail-body').querySelectorAll('details[open]')].map(d=>d.id));
    const cached=api.details.get(state.detailId);if(cached)renderDetail(cached.condition,false);
    for(const details of el('detail-body').querySelectorAll('details'))details.open=expanded.has(details.id);
    el('detail').scrollTop=scroll;
  }
}
function renderStudies() {
  const target=el('studies');target.replaceChildren();
  for(const s of D.studies){
    const card=node('div',undefined,'study-card');card.lang='en';
    card.append(link(bySource.get(s.id)),node('p',`${s.year} · ${s.extraction_status} · PMID ${s.pmid}`,'subtle'),
      node('p',s.population),node('p',s.finding||'No finding extracted. Bibliographic metadata only.'),node('p',s.limitations,'subtle'));
    if(s.correction)card.append(node('p',`Correction: ${s.correction.doi}. ${s.correction.status}`,'subtle'));
    target.append(card);
  }
}
function updateSafety() {
  const age=el('age').value,temp=el('temperature').value;
  const context={ageMonths:age===''?undefined:Number(age),temperatureC:temp===''?undefined:Number(temp)};
  const result=evaluateSafety(el('query').value,D.rules,context);
  const target=el('alerts');target.replaceChildren();
  for(const alert of result.alerts){
    const box=node('div',undefined,'alert');box.dataset.rule=alert.id;
    box.append(node('h3',txt(alert.label)),node('p',t('dangerAction')));
    const refs=node('div',undefined,'source-list');
    for(const id of alert.source_ids){const s=bySource.get(id);if(s)refs.append(link(s));}
    box.append(refs);target.append(box);
  }
  // The action-relevant limitation stays visible when no rule matches.
  el('safety-note').textContent=t('safetyUnknown');
}
function update() {
  updateSafety(); // independent of domain/type filters and all ranking results
  const topics=state.mode==='conditions';
  for(const mode of ['conditions','cancer','lifecycle'])el('mode-'+mode).setAttribute('aria-pressed',String(state.mode===mode));
  el('condition-filters').hidden=!topics;el('condition-tools').hidden=!topics;
  el('result-view').hidden=!topics||state.view!=='cards';el('table-view').hidden=!topics||state.view==='cards';
  el('knowledge-view').hidden=topics;
  el('query').placeholder=t(topics?'placeholder':state.mode==='cancer'?'cancerSearch':'lifecycleSearch');
  if(!topics){
    for(const target of el('department-nav').querySelectorAll('[aria-current]'))target.removeAttribute('aria-current');
    el('active-scope').textContent=t('searchWithin')+' · '+txt(D.knowledge[state.mode].title);
    el('show-all').hidden=true;el('scope').textContent=t('mapSearchScope');
    if(D.knowledge[state.mode].entries)knowledgeView.render(state.mode,el('query').value);return;
  }
  el('show-all').hidden=false;el('scope').textContent=t('scope');
  const departments=scopeDepartments();
  state.results=engine.search(el('query').value,{domain:el('domain').value,kind:el('kind').value,departments,limit:D.conditions.length});
  const total=departments.length?D.conditions.filter(c=>c.departments.some(id=>departments.includes(id))).length:D.conditions.length;
  el('result-count').textContent=`${state.results.length} / ${total}`;
  updateNavigation();
  renderCards();renderSelection();if(state.view!=='cards')renderTable();
}
function renderSelection(){
  el('selection-count').textContent=t('selected')+': '+state.selected.size;
  el('compare').textContent=t('compare')+` (${state.selected.size})`;el('compare').disabled=state.selected.size<2;
}
function renderCards(){
  const cards=el('cards');cards.replaceChildren();
  state.page=Math.min(state.page,Math.max(0,Math.ceil(state.results.length/PAGE_SIZE)-1));
  renderPagination('cards-pages',state.results.length,state.page,page=>{state.page=page;renderCards();el('result-view').scrollIntoView({block:'start'});});
  if(!state.results.length){if(state.catalogStatus==='ready')cards.append(node('p',t('noResults'),'empty'));return;}
  for(const {condition:c,reasons} of pageItems(state.results,state.page)){
    const card=node('article',undefined,'card');card.dataset.id=c.id;
    const heading=node('h3',txt(c.names));heading.lang=medicalLang();
    card.append(node('span',txt(byDomain.get(c.primary_domain).label),'domain-label'),heading);
    if(medicalLang()==='zh-CN')card.append(node('div',c.names.en,'english-name'));
    const desc=node('p',firstParagraph(txt(c.sections.summary.text)),'description');desc.lang=medicalLang();card.append(desc);
    if(reasons.length)card.append(node('div',reasons.map(r=>r.term).join(' · '),'match'));
    card.append(node('div',dept(c),'department'));
    const bottom=node('div',undefined,'card-bottom');const label=node('label');const check=node('input');check.type='checkbox';check.checked=state.selected.has(c.id);
    check.setAttribute('aria-label',t('compare')+' '+txt(c.names));
    check.addEventListener('change',()=>{if(check.checked)state.selected.add(c.id);else state.selected.delete(c.id);renderSelection();});
    label.append(check,document.createTextNode(t('compare')));
    bottom.append(label,translatedButton('read',()=>showDetail(c.id),'primary'));card.append(bottom);cards.append(card);
  }
}
function renderPagination(id,total,page,onChange){
  const target=el(id),pages=Math.ceil(total/PAGE_SIZE);target.replaceChildren();target.hidden=pages<2;
  if(pages<2)return;
  const previous=translatedButton('previousPage',()=>onChange(page-1)),next=translatedButton('nextPage',()=>onChange(page+1));
  previous.disabled=page===0;next.disabled=page+1>=pages;
  target.append(previous,node('span',`${t('pageStatus')} ${page+1} / ${pages}`),next);
}
async function showDetail(id,resetScroll=true){
  if(!el('detail').open)state.detailTrigger=document.activeElement;
  state.detailId=id;const request=++state.detailRequest;
  const body=el('detail-body'),title=node('h2',txt(byId.get(id)?.names)||t('loading'));title.id='detail-title';
  body.replaceChildren(title,node('p',t('loading')));
  if(!el('detail').open)el('detail').showModal();
  try{
    const data=await api.condition(id);mergeReferences(data);
    if(request!==state.detailRequest||state.detailId!==id||!el('detail').open)return;
    renderDetail(data.condition,resetScroll);
  }catch{if(request===state.detailRequest&&state.detailId===id){showLoadError(body,()=>showDetail(id));body.prepend(title);}}
}
function renderDetail(c,resetScroll=true){
  const body=el('detail-body');body.replaceChildren();body.lang=medicalLang();body.dir='ltr';
  const title=node('h2',txt(c.names));title.id='detail-title';
  body.append(title);
  if(medicalLang()==='zh-CN')body.append(node('p',c.names.en,'subtle'));
  body.append(node('p',`${t('reviewDate')}: ${c.review.editorial_updated_at}`,'subtle'),node('p',`${t('departments')}: ${dept(c)}`),node('p',`${t('symptoms')}: ${c.symptom_terms.map(txt).join(' · ')}`));
  if(c.terminology_note)body.append(node('p',txt(c.terminology_note),'notice fallback'));
  const orderedFields=[D.fields.find(f=>f.id==='red_flags'),...D.fields.filter(f=>f.id!=='red_flags')];
  const toc=node('details',undefined,'detail-toc');toc.id='detail-toc';toc.open=!window.matchMedia('(max-width: 600px)').matches;
  toc.append(node('summary',t('chapterIndex')));const tocNav=node('nav');tocNav.setAttribute('aria-label',t('chapterIndex'));
  for(const field of orderedFields){const a=node('a',txt(field.label));a.href='#detail-'+field.id;a.addEventListener('click',event=>{event.preventDefault();const target=el('detail-'+field.id);target.scrollIntoView({block:'start'});target.focus({preventScroll:true});});tocNav.append(a);}
  toc.append(tocNav);
  for(const field of orderedFields){
    const sec=c.sections[field.id];const section=node('section',undefined,field.id==='red_flags'?'detail-section detail-warning':'detail-section');
    section.id='detail-'+field.id;section.tabIndex=-1;
    section.append(node('h3',txt(field.label)));appendText(section,txt(sec.text));
    const refs=node('div',undefined,'source-list');for(const sid of sec.source_ids)refs.append(link(bySource.get(sid)));section.append(refs);body.append(section);
    if(field.id==='red_flags')body.append(toc);
  }
  const evidence=node('details');evidence.id='detail-evidence';evidence.append(node('summary',t('sourceInfo')));
  const zh=medicalLang()==='zh-CN',verified=Object.values(c.sections).filter(s=>s.support_status==='verified').length;
  const reviewState=c.review.status==='medically_reviewed'?(zh?'已完成':'Completed'):c.review.status==='retired'?(zh?'已退役':'Retired'):(zh?'待完成':'Pending');
  evidence.append(node('p',zh?`独立医学审阅：${reviewState}。逐项来源核验：${verified} / ${D.fields.length} 节完成。`:`Independent medical review: ${reviewState}. Claim verification: ${verified} / ${D.fields.length} sections complete.`),node('p',`${t('reviewDate')}: ${c.review.editorial_updated_at}`,'subtle'));
  evidence.append(node('p',zh?'所列资料支持正文编辑；具体地区的诊疗路径、药品批准与筛查安排需结合当地资料。':'The references inform the articles; regional care pathways, medicine approvals and screening schedules use local guidance.','subtle'));
  const missing=node('details');missing.id='detail-advanced';missing.append(node('summary',t('more')));
  missing.append(node('p',zh?'以下专业字段尚未整理：':'The following advanced fields await curation:','subtle'));
  for(const [k,v] of Object.entries(c.advanced_fields))missing.append(node('p',`${k}: ${v??t('unknown')}`,'subtle'));evidence.append(missing);
  evidence.append(node('h3',t('sources')));
  for(const sid of c.source_ids){
    const s=bySource.get(sid);const card=node('div',undefined,'evidence-card');
    card.append(link(s),node('p',`${s.type} · ${s.independence_group} · ${s.jurisdiction}`),node('p',`Accessed ${s.accessed_at} · ${s.retrieval_status}`),node('p',s.retrieval_scope));evidence.append(card);
  }
  if(c.study_ids.length){evidence.append(node('h3',t('study')));for(const sid of c.study_ids){const s=D.studies.find(x=>x.id===sid);const p=node('p',s.finding||s.limitations,'subtle');p.lang='en';evidence.append(link(bySource.get(sid)),p);}}
  body.append(evidence);
  if(c.related_ids.length){body.append(node('h3',t('related')));const related=node('div',undefined,'filters');for(const rid of c.related_ids){const b=node('button',txt(byId.get(rid)?.names)||rid);b.type='button';b.addEventListener('click',()=>showDetail(rid));related.append(b);}body.append(related);}
  if(!el('detail').open)el('detail').showModal();if(resetScroll)el('detail').scrollTop=0;
}
function shownForTable(){return state.view==='selected'?[...state.selected]:D.conditions.map(c=>c.id);}
async function renderTable(){
  const request=++state.tableRequest;
  el('result-view').hidden=true;el('table-view').hidden=false;
  el('table-title').textContent=state.view==='selected'?t('compare'):t('matrix');
  el('matrix-note').textContent=t('comparisonHelp');
  const table=el('comparison');const expanded=new Set([...table.querySelectorAll('details[open]')].map(d=>d.dataset.cell));
  const ids=shownForTable();state.tablePage=Math.min(state.tablePage,Math.max(0,Math.ceil(ids.length/PAGE_SIZE)-1));
  renderPagination('table-pages',ids.length,state.tablePage,page=>{state.tablePage=page;renderTable();el('table-view').scrollIntoView({block:'start'});});
  el('table-status').replaceChildren(node('p',t('loading')));
  let data;
  try{data=await api.batch(pageItems(ids,state.tablePage));}
  catch{if(request===state.tableRequest){table.replaceChildren();showLoadError(el('table-status'),renderTable);}return;}
  if(request!==state.tableRequest||state.view==='cards')return;
  el('table-status').replaceChildren();for(const result of data)mergeReferences(result);
  table.replaceChildren();const thead=node('thead'),hr=node('tr');
  for(const f of [{id:'name',label:{en:t('topics'),'zh-CN':t('topics')}},{id:'departments',label:{en:t('departments'),'zh-CN':t('departments')}},...D.fields]){
    const th=node('th',txt(f.label));th.scope='col';hr.append(th);
  }
  thead.append(hr);table.append(thead);const tbody=node('tbody');
  for(const {condition:c} of data){
    const row=node('tr');row.dataset.id=c.id;const name=node('th',txt(c.names));name.scope='row';row.append(name,node('td',dept(c)));
    for(const f of D.fields){
      const text=txt(c.sections[f.id].text);const td=node('td',undefined,'cell-text');td.lang=medicalLang();td.dir='ltr';
      td.append(node('p',firstParagraph(text)));
      if(textBlocks(text).length>1){const details=node('details');details.dataset.cell=c.id+':'+f.id;details.open=expanded.has(details.dataset.cell);details.append(node('summary',t('expandContent')));appendText(details,text);td.append(details);}
      row.append(td);
    }tbody.append(row);
  }
  table.append(tbody);
}
function switchView(view){state.view=view;state.tablePage=0;if(view==='cards'){++state.tableRequest;el('result-view').hidden=false;el('table-view').hidden=true;}else renderTable();}
function downloadCSV(){
  if(state.catalogStatus!=='ready')return;
  el('export-status')?.remove();
  const ids=state.view==='selected'?[...state.selected]:state.results.map(r=>r.condition.id);
  const request=api.exportRequest(ids,medicalLang(),state.view==='matrix');
  // Native form downloads stream directly to disk, including all selected pages.
  let target=el('export-target');
  if(!target){target=node('iframe');target.id='export-target';target.name='export-target';target.hidden=true;
    target.addEventListener('load',()=>{if(target.contentDocument?.body?.textContent.trim()){
      const message=node('p',t('exportFailed'));message.id='export-status';message.setAttribute('role','alert');el('condition-tools').append(message);
    }});document.body.append(target);}
  let form=el('export-form');if(!form){form=node('form');form.id='export-form';form.hidden=true;document.body.append(form);}
  form.replaceChildren();form.method='POST';form.action=request.url;form.target='export-target';
  for(const [name,value] of Object.entries(request.fields)){const input=node('input');input.type='hidden';input.name=name;input.value=value;form.append(input);}
  form.submit();
}
for(const id of ['locale','detail-locale']){
  for(const [locale,cfg] of Object.entries(D.locales))el(id).add(new Option(cfg.name,locale));el(id).value=state.locale;
  el(id).addEventListener('change',()=>{state.locale=el(id).value;refreshLocale();});
}
for(const mode of ['conditions','cancer','lifecycle'])el('mode-'+mode).addEventListener('click',()=>setMode(mode));
for(const [id,event] of [['query','input'],['domain','change'],['kind','change']])el(id).addEventListener(event,()=>{state.page=0;update();});
el('age').addEventListener('input',updateSafety);el('temperature').addEventListener('input',updateSafety);
el('reset').addEventListener('click',()=>{el('query').value='';el('domain').value='';el('kind').value='';el('age').value='';el('temperature').value='';state.selected.clear();chooseScope();el('query').focus();});
el('show-all').addEventListener('click',()=>{el('domain').value='';el('kind').value='';chooseScope();});
el('menu-toggle').addEventListener('click',()=>setMenu(el('menu-toggle').getAttribute('aria-expanded')!=='true'));
el('menu-close').addEventListener('click',()=>setMenu(false));el('menu-backdrop').addEventListener('click',()=>setMenu(false));
document.addEventListener('keydown',event=>{
  if(!el('sidebar').hasAttribute('data-open'))return;
  if(event.key==='Escape'){event.preventDefault();setMenu(false);}
  if(event.key==='Tab'){
    const targets=[...el('sidebar').querySelectorAll('a,button,summary')].filter(n=>n.getClientRects().length&&!n.disabled);
    const first=targets[0],last=targets.at(-1);
    if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
  }
});
window.matchMedia('(max-width: 850px)').addEventListener('change',()=>setMenu(false));
el('compare').addEventListener('click',()=>switchView('selected'));el('matrix').addEventListener('click',()=>switchView('matrix'));el('back').addEventListener('click',()=>switchView('cards'));
el('download').addEventListener('click',downloadCSV);el('close-detail').addEventListener('click',()=>el('detail').close());
el('detail').addEventListener('close',()=>{const id=state.detailId;state.detailId=null;++state.detailRequest;if(state.mode==='conditions'&&id)el('cards').querySelector(`[data-id="${id}"] button`)?.focus();else if(state.detailTrigger?.isConnected)state.detailTrigger.focus();else el('knowledge-entry-title')?.focus();});
refreshLocale();setMenu(false);loadCatalog();
