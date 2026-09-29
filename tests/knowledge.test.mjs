import test from 'node:test';
import assert from 'node:assert/strict';
import {knowledgeEntries} from '../src/web/knowledge.mjs';

const bilingual=(zh,en)=>({'zh-CN':zh,en});
const entry=(id,group,zh,en,body)=>({id,group_id:group,title:bilingual(zh,en),summary:bilingual('概览','Overview'),sections:[{title:bilingual('解释','Explanation'),text:bilingual(body,body)}]});
const module={entries:[
  entry('pressure','metabolic','血压','Blood pressure','Repeated measurements help interpret readings.'),
  entry('activity','behavior','身体活动','Physical activity','Activity can lower blood pressure.'),
  entry('sleep','behavior','睡眠','Sleep','Regular sleep schedule.')
],stages:[{id:'older',factor_ids:['pressure','activity']},{id:'child',factor_ids:['activity','sleep']}]};

test('stage, canonical group and query filters intersect without duplicate entries',()=>{
  const results=knowledgeEntries(module,{stage:'older',group:'behavior',query:'pressure'});
  assert.deepEqual(results.map(e=>e.id),['activity']);
  assert.equal(results[0],module.entries[1]);
});
test('bilingual body search uses all terms and Unicode normalization',()=>{
  assert.deepEqual(knowledgeEntries(module,{query:' ＢＬＯＯＤ  readings '}).map(e=>e.id),['pressure']);
  assert.deepEqual(knowledgeEntries(module,{query:'睡眠'}).map(e=>e.id),['sleep']);
  assert.deepEqual(knowledgeEntries(module,{query:'blood schedule'}),[]);
});
test('age-stage cross references do not create independent copies of factors',()=>{
  const older=knowledgeEntries(module,{stage:'older'}),child=knowledgeEntries(module,{stage:'child'});
  assert.equal(older.find(e=>e.id==='activity'),child.find(e=>e.id==='activity'));
  assert.equal(knowledgeEntries(module).length,3);
});
test('filtering leaves data and ordering unchanged',()=>{
  const before=JSON.stringify(module);
  knowledgeEntries(module,{group:'behavior',query:'sleep'});
  assert.equal(JSON.stringify(module),before);
  assert.deepEqual(knowledgeEntries(module,{query:'   '}).map(e=>e.id),['pressure','activity','sleep']);
});
test('markup and punctuation are literal search terms',()=>{
  assert.deepEqual(knowledgeEntries(module,{query:'<img onerror=alert(1)>'}),[]);
  assert.deepEqual(knowledgeEntries(module,{query:'['}),[]);
});
