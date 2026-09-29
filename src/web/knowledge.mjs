import { appendText } from './text.mjs';
import { safeSourceURL } from './export.mjs';

// Each entry has one canonical home; stages and disease pages are references.
export function knowledgeEntries(module,{group='',stage='',query=''}={}) {
  const stageIds=stage?new Set(module.stages.find(s=>s.id===stage).factor_ids):null;
  const terms=query.normalize('NFKC').toLowerCase().trim().split(/\s+/).filter(Boolean);
  return module.entries.filter(entry=>{
    if(group&&entry.group_id!==group)return false;
    if(stageIds&&!stageIds.has(entry.id))return false;
    const text=[...Object.values(entry.title),...Object.values(entry.summary),
      ...entry.sections.flatMap(s=>[...Object.values(s.title),...Object.values(s.text)])].join(' ').normalize('NFKC').toLowerCase();
    return terms.every(term=>text.includes(term));
  });
}

export function createKnowledgeView({root,modules,t,txt,medicalLang,conditions,openCondition,openModule}) {
  const state=Object.fromEntries(Object.keys(modules).map(id=>[id,{group:'',stage:'',query:'',entryId:null,expanded:new Set()}]));
  let active='cancer';
  const make=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  const action=(text,fn,cls='')=>{const b=make('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;};
  const language=node=>{node.lang=medicalLang();node.dir='ltr';return node;};
  const references=(ids,module)=>{
    const refs=make('div',undefined,'source-list');
    for(const id of ids){const source=module.sources.find(s=>s.id===id),a=make('a',source.title);
      a.href=safeSourceURL(source.url);a.target='_blank';a.rel='noopener noreferrer';a.referrerPolicy='no-referrer';refs.append(a);}
    return refs;
  };
  function appendSection(target,section,module,prefix){
    const node=language(make('section',undefined,'knowledge-section'));node.id=prefix+'-'+section.id;node.tabIndex=-1;
    node.append(make('h3',txt(section.title)));appendText(node,txt(section.text));node.append(references(section.source_ids,module));target.append(node);
  }
  function remember(details,key,record){
    details.open=record.expanded.has(key);
    details.addEventListener('toggle',()=>{if(!details.isConnected)return;if(details.open)record.expanded.add(key);else record.expanded.delete(key);});
  }
  function jump(target){target.scrollIntoView({block:'start'});target.focus({preventScroll:true});}
  function render(moduleId,query=''){
    // Capture current DOM synchronously: toggle events may not have fired yet.
    for(const d of root.querySelectorAll('details[data-memory]')){
      const expanded=state[active].expanded;if(d.open)expanded.add(d.dataset.memory);else expanded.delete(d.dataset.memory);
    }
    active=moduleId;const module=modules[moduleId],record=state[moduleId];
    if(query!==record.query)record.entryId=null;
    record.query=query;root.replaceChildren();root.dataset.module=moduleId;
    const heading=make('div',undefined,'knowledge-heading');
    const title=language(make('h2',txt(module.title)));title.id='knowledge-title';title.tabIndex=-1;
    heading.append(title);root.append(heading);
    if(record.entryId){renderEntry(module,record);return;}
    const intro=language(make('div',undefined,'knowledge-intro'));appendText(intro,txt(module.intro));root.append(intro);
    const filters=make('div',undefined,'knowledge-filters');
    const groupLabel=make('label',t('mapGroup')),group=make('select');group.id='knowledge-group';group.add(new Option(t('mapAll'),''));
    for(const g of module.groups)group.add(new Option(txt(g.label),g.id));group.value=record.group;
    group.addEventListener('change',()=>{record.group=group.value;render(active,record.query);root.querySelector('#knowledge-group').focus();});
    groupLabel.append(group);filters.append(groupLabel);
    if(module.stages){
      const stageLabel=make('label',t('mapStage')),stage=make('select');stage.id='knowledge-stage';stage.add(new Option(t('mapAllStages'),''));
      for(const [kind,key] of [['age','mapAgeGroups'],['overlay','mapContexts']]){
        const optgroup=make('optgroup');optgroup.label=t(key);
        for(const s of module.stages.filter(s=>s.kind===kind))optgroup.append(new Option(txt(s.title),s.id));stage.append(optgroup);
      }
      stage.value=record.stage;stage.addEventListener('change',()=>{record.stage=stage.value;render(active,record.query);root.querySelector('#knowledge-stage').focus();});
      stageLabel.append(stage);filters.append(stageLabel);
    }
    filters.append(action(t('mapReset'),()=>{record.group='';record.stage='';render(active,record.query);},'text-button'));root.append(filters);
    const selectedStage=module.stages?.find(s=>s.id===record.stage);
    if(selectedStage){
      const panel=make('section',undefined,'knowledge-stage');panel.dataset.stage=selectedStage.id;
      panel.append(language(make('h3',txt(selectedStage.title))));const intro=language(make('div'));appendText(intro,txt(selectedStage.intro));panel.append(intro);
      for(const section of selectedStage.sections)appendSection(panel,section,module,'stage-'+selectedStage.id);
      root.append(panel);
    }
    const overview=make('details',undefined,'knowledge-overview');overview.dataset.memory='overview';remember(overview,'overview',record);
    overview.append(make('summary',t('mapGuide')));
    for(const section of module.sections)appendSection(overview,section,module,'map-'+moduleId);
    root.append(overview);
    const entries=knowledgeEntries(module,record);
    const status=make('p',`${t('mapResults')} · ${entries.length} / ${module.entries.length}`,'subtle');status.id='knowledge-count';status.setAttribute('role','status');root.append(status);
    const cards=make('div',undefined,'knowledge-cards');
    if(!entries.length)cards.append(make('p',t('noResults'),'empty'));
    for(const entry of entries){
      const card=make('article',undefined,'knowledge-card');card.dataset.entry=entry.id;
      const groupTitle=txt(module.groups.find(g=>g.id===entry.group_id).label);
      if(groupTitle!==txt(entry.title))card.append(language(make('span',groupTitle,'domain-label')));
      card.append(language(make('h3',txt(entry.title))),language(make('p',txt(entry.summary))));
      const button=action(t('mapRead'),()=>{record.entryId=entry.id;render(active,record.query);jump(root.querySelector('#knowledge-entry-title'));},'primary');
      button.setAttribute('aria-label',t('mapRead')+' '+txt(entry.title));card.append(button);cards.append(card);
    }
    root.append(cards);
  }
  function renderEntry(module,record){
    const entry=module.entries.find(e=>e.id===record.entryId);
    root.append(action(t('mapBack'),()=>{record.entryId=null;render(active,record.query);jump(root.querySelector('#knowledge-title'));},'text-button'));
    const article=make('article',undefined,'knowledge-article');article.dataset.entry=entry.id;
    const title=language(make('h2',txt(entry.title)));title.id='knowledge-entry-title';title.tabIndex=-1;
    article.append(title,language(make('p',txt(entry.summary),'knowledge-lead')));
    const toc=language(make('nav',undefined,'knowledge-toc'));toc.setAttribute('aria-label',t('chapterIndex'));
    for(const section of entry.sections){const a=make('a',txt(section.title));a.href='#entry-'+entry.id+'-'+section.id;
      a.addEventListener('click',event=>{event.preventDefault();jump(article.querySelector(a.getAttribute('href')));});toc.append(a);}
    article.append(toc);
    for(const section of entry.sections)appendSection(article,section,module,'entry-'+entry.id);
    if(entry.condition_ids.length){
      const related=make('section',undefined,'knowledge-related');related.append(make('h3',t('mapDiseases')));
      const buttons=make('div',undefined,'filters');
      for(const cid of entry.condition_ids){const condition=conditions.get(cid);buttons.append(action(txt(condition.names),()=>openCondition(cid)));}
      related.append(buttons);article.append(related);
    }
    if(entry.factor_ids.length){
      const related=make('section',undefined,'knowledge-related');related.append(make('h3',t('mapFactors')));
      const buttons=make('div',undefined,'filters');
      for(const id of entry.factor_ids){const factor=modules.lifecycle.entries.find(e=>e.id===id);
        buttons.append(action(txt(factor.title),()=>openModule('lifecycle',{entryId:id})));}
      related.append(buttons);article.append(related);
    }
    const evidence=make('details',undefined,'knowledge-evidence');const key='sources:'+entry.id;evidence.dataset.memory=key;remember(evidence,key,record);
    evidence.append(make('summary',t('sourceInfo')));
    evidence.append(make('p',t('reviewDate')+': '+module.review.updated_at,'subtle'));
    for(const sid of entry.source_ids){const source=module.sources.find(s=>s.id===sid),card=make('div',undefined,'evidence-card');
      card.append(references([sid],module),make('p',source.scope),make('p',source.accessed_at,'subtle'));evidence.append(card);}
    article.append(evidence);root.append(article);
  }
  return {render,selectEntry(moduleId,id){state[moduleId].entryId=id;state[moduleId].query='';},get active(){return active;}};
}
