import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {LocalSearch,normalize,tokenize,hasPositiveTerm,positiveQuery} from '../src/web/search.mjs';
const conditions=fs.readdirSync(new URL('../data/conditions/',import.meta.url)).filter(x=>x.endsWith('.json')).sort().map(n=>JSON.parse(fs.readFileSync(new URL('../data/conditions/'+n,import.meta.url),'utf8')));
const engine=new LocalSearch(conditions);
for(const c of conditions)for(const locale of ['zh-CN','en'])test('exact-name/'+locale+'/'+c.id,()=>{
 assert.equal(engine.search(c.names[locale],{limit:1})[0]?.condition.id,c.id);
});
for(const c of conditions)test('aliases/'+c.id,()=>{
 for(const alias of Object.values(c.aliases).flat())assert.ok(engine.search(alias,{limit:10}).some(r=>r.condition.id===c.id),'Alias missing: '+alias);
});
const queries=[['流鼻涕 咳嗽','common-cold'],['鼻痒 打喷嚏','allergic-rhinitis'],['尿痛 尿频','lower-uti'],['关节红肿 大脚趾痛','gout'],['口渴 尿少','dehydration'],['heartburn','reflux'],['胸痛','chest-pain'],['PCOS','pcos'],['PMOS','pcos']];
for(const [q,id] of queries)test('synthetic symptom/'+q,()=>assert.ok(engine.search(q,{limit:10}).some(r=>r.condition.id===id)));
test('unknown does not invent a candidate',()=>assert.equal(engine.search('qzxvjkpt').length,0));
test('empty query lists all 72 records',()=>assert.equal(engine.search('').length,72));
test('filters are respected',()=>assert.ok(engine.search('',{domain:'ophthalmic'}).every(r=>r.condition.primary_domain==='ophthalmic')));
test('symptom-kind is separate',()=>assert.ok(engine.search('',{kind:'symptom'}).every(r=>r.condition.kind==='symptom')));
test('query input object normalization',()=>assert.equal(normalize(null),''));
test('unicode normalization',()=>assert.equal(normalize('ＰＣＯＳ'),'pcos'));
test('Chinese bigrams',()=>assert.deepEqual(tokenize('头痛'),['头痛']));
test('word boundary',()=>assert.equal(hasPositiveTerm('cheating','heat'),false));
test('bounded negative scope',()=>assert.equal(hasPositiveTerm('no chest pain but severe shortness of breath','chest pain'),false));
test('Chinese positive after comma',()=>assert.equal(hasPositiveTerm('没有胸痛，有呼吸困难','呼吸困难'),true));
test('double negation is not silently safe',()=>assert.equal(hasPositiveTerm('不是没有胸痛','胸痛'),true));
test('denial query does not rank denied-only disease',()=>assert.equal(positiveQuery('没有胸痛，只有咳嗽').includes('胸痛'),false));
test('negative limit rejected',()=>assert.throws(()=>engine.search('a',{limit:-1}),TypeError));
test('empty corpus',()=>assert.deepEqual(new LocalSearch([]).search('cough'),[]));
test('no probabilities in result contract',()=>assert.ok(engine.search('咳嗽').every(r=>!('probability' in r))));
