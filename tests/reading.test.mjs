import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {textBlocks,firstParagraph} from '../src/web/text.mjs';
import {departmentNavigation} from '../src/web/navigation.mjs';
import {LocalSearch} from '../src/web/search.mjs';

test('paragraphs and independent bullet lists preserve all text',()=>{
  assert.deepEqual(textBlocks('Overview.\r\n\r\n- One\r\n- Two\r\n\r\nLimitations.\n- Three'),[
    {type:'paragraph',text:'Overview.'},{type:'list',items:['One','Two']},
    {type:'paragraph',text:'Limitations.'},{type:'list',items:['Three']}
  ]);
});
test('legacy text and empty text stay readable',()=>{
  assert.deepEqual(textBlocks('A single paragraph.'),[{type:'paragraph',text:'A single paragraph.'}]);
  assert.deepEqual(textBlocks(null),[]);
  assert.equal(firstParagraph('A short card.\n\n- Detailed information'),'A short card.');
});
test('HTML, Markdown links and formula characters remain literal text',()=>{
  const unsafe='<img src=x onerror=alert(1)> [link](javascript:alert(1))';
  assert.deepEqual(textBlocks('Read\n\n- '+unsafe),[{type:'paragraph',text:'Read'},{type:'list',items:[unsafe]}]);
});
test('group counts use the topic union and hide unused specialties',()=>{
  const topics=[{departments:['a','b']},{departments:['b']},{departments:['c']}];
  const nav=departmentNavigation(topics,[{id:'ab',departments:['a','b','unused']},{id:'empty',departments:['other']}]);
  assert.equal(nav.length,1);assert.equal(nav[0].count,2);
  assert.deepEqual(nav[0].children,[{id:'a',count:1},{id:'b',count:2}]);
});
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const groups=read('department-groups.json');
const conditions=fs.readdirSync(new URL('../data/conditions/',import.meta.url)).filter(n=>n.endsWith('.json')).map(n=>read('conditions/'+n));
test('every existing specialty has exactly one group and every topic is reachable',()=>{
  const mapped=groups.flatMap(g=>g.departments);
  assert.equal(new Set(mapped).size,mapped.length);
  assert.deepEqual([...mapped].sort(),Object.keys(read('departments.json')).sort());
  const visible=new Set(departmentNavigation(conditions,groups).flatMap(g=>g.children.map(d=>d.id)));
  assert.ok(conditions.every(c=>c.departments.some(d=>visible.has(d))));
});
test('department filter includes non-primary affiliations without duplicates',()=>{
  const result=new LocalSearch(conditions).search('',{departments:['pediatrics','primary-care']});
  assert.deepEqual(result.map(r=>r.condition.id).sort(),conditions.filter(c=>c.departments.some(d=>['pediatrics','primary-care'].includes(d))).map(c=>c.id).sort());
  assert.equal(new Set(result.map(r=>r.condition.id)).size,result.length);
});
test('department, domain and kind filters intersect',()=>{
  const result=new LocalSearch(conditions).search('',{departments:['primary-care'],domain:'general',kind:'symptom'});
  assert.ok(result.length>0);
  assert.ok(result.every(({condition:c})=>c.departments.includes('primary-care')&&c.primary_domain==='general'&&c.kind==='symptom'));
  assert.equal(new LocalSearch(conditions).search('',{departments:['nonexistent']}).length,0);
});
