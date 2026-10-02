import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {evaluateSafety} from '../src/web/safety.mjs';
const rules=JSON.parse(fs.readFileSync(new URL('../data/safety/rules.json',import.meta.url),'utf8'));
const positives=[
 ['胸痛 呼吸困难','chest-pain-danger'],['胸口痛 持续 冷汗','chest-pain-danger'],['persistent chest pain','chest-pain-danger'],['chest pain and sweating','chest-pain-danger'],
 ['喘不过气','severe-breathing'],['cannot breathe','severe-breathing'],['blue lips','severe-breathing'],['没有胸痛，有呼吸困难','severe-breathing'],['no chest pain but severe shortness of breath','severe-breathing'],
 ['突然一侧无力，说话不清','stroke-pattern'],['slurred speech','stroke-pattern'],['face drooping','stroke-pattern'],['不是没有胸痛，胸痛持续','chest-pain-danger'],
 ['喉咙肿胀','allergic-airway'],['tongue swelling','allergic-airway'],['throat swelling','allergic-airway'],
 ['突然剧烈头痛','sudden-headache'],['thunderclap headache','sudden-headache'],['worst headache of my life','sudden-headache'],
 ['想伤害自己','immediate-self-harm'],['我想自杀','immediate-self-harm'],['want to kill myself','immediate-self-harm'],
 ['怀孕 腹痛 出血','pregnancy-bleeding'],['pregnant and bleeding','pregnancy-bleeding'],['pregnancy severe pain','pregnancy-bleeding'],
 ['产后大量出血','postpartum-heavy-bleeding'],['生完孩子出血突然增多','postpartum-heavy-bleeding'],['postpartum sudden heavy bleeding','postpartum-heavy-bleeding'],['after giving birth bleeding suddenly gets heavier','postpartum-heavy-bleeding'],
 ['腰痛 会阴麻木','back-neurologic'],['back pain urinary retention','back-neurologic'],['背痛 尿不出','back-neurologic'],
 ['高温 意识混乱','heat-confusion'],['heat and confusion','heat-confusion'],['hot environment collapse','heat-confusion'],
 ['大量出血 晕厥','major-bleeding'],['heavy bleeding will not stop','major-bleeding'],['vomiting blood and fainting','major-bleeding'],
 ['2个月婴儿发烧','newborn-fever-text'],['newborn fever','newborn-fever-text'],['1 month old fever','newborn-fever-text'],
 ['产后 剧烈头痛','pregnancy-neurologic'],['pregnant severe headache','pregnancy-neurologic'],['postpartum vision changes','pregnancy-neurologic'],
 ['突然睾丸疼痛','acute-scrotal-pain'],['阴囊剧烈疼痛','acute-scrotal-pain'],['sudden testicle pain','acute-scrotal-pain'],['severe scrotal pain','acute-scrotal-pain']];
const negatives=['没有胸痛，只有咳嗽','no chest pain, only cough','没有呼吸困难','no difficulty breathing','without tongue swelling','否认喉咙肿胀','普通感冒','轻微鼻塞','PMOS','skin itching','cheating confusion','no slurred speech','没有发烧','no fever','dry eyes','no chest pain and no sweating'];
for(const [q,id] of positives)test('alert/'+q,()=>assert.ok(evaluateSafety(q,rules).alerts.some(r=>r.id===id)));
for(const q of negatives)test('no-phrase-match/'+q,()=>{const r=evaluateSafety(q,rules);assert.equal(r.alerts.length,0);assert.equal(r.assurance,false);});
test('structured young infant 38',()=>assert.ok(evaluateSafety('',rules,{ageMonths:2,temperatureC:38}).alerts.some(r=>r.id==='infant-fever-structured')));
test('exactly 3 months does not use under-3 threshold',()=>assert.equal(evaluateSafety('',rules,{ageMonths:3,temperatureC:38}).alerts.length,0));
test('blank numeric inputs are not zero',()=>assert.equal(evaluateSafety('',rules,{ageMonths:undefined,temperatureC:38}).alerts.length,0));
test('invalid negative age',()=>assert.equal(evaluateSafety('',rules,{ageMonths:-1,temperatureC:38}).alerts.length,0));
test('NaN never qualifies',()=>assert.equal(evaluateSafety('',rules,{ageMonths:NaN,temperatureC:38}).alerts.length,0));
test('normal young infant temperature does not trigger fever threshold',()=>assert.equal(evaluateSafety('',rules,{ageMonths:2,temperatureC:37}).alerts.length,0));
test('empty query is not a clinical all-clear',()=>assert.equal(evaluateSafety('',rules).assurance,false));
test('rules honestly disclose draft state',()=>assert.equal(evaluateSafety('',rules).clinicalValidation,'draft'));
for(const q of ['没有睾丸疼痛，突然头晕','no testicular pain but sudden dizziness','sudden shoulder pain','mild testicle pain'])
  test('scrotal alert requires non-negated organ and severity/'+q,()=>assert.ok(!evaluateSafety(q,rules).alerts.some(r=>r.id==='acute-scrotal-pain')));
for(const q of ['产后少量恶露','产后没有大量出血','postpartum no heavy bleeding','heavy bleeding from a cut'])
  test('postpartum alert requires context and non-negated heavy bleeding/'+q,()=>assert.ok(!evaluateSafety(q,rules).alerts.some(r=>r.id==='postpartum-heavy-bleeding')));
