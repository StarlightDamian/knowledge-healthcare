import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {csvCell,comparisonCSV,safeSourceURL} from '../src/web/export.mjs';
for(const input of ['=HYPERLINK("x")','+SUM(1)','-1+2','@cmd','\t=SUM(1)','   =x','＝x'])test('csv injection/'+input,()=>assert.ok(csvCell(input).startsWith('"\'')));
test('csv commas quotes linebreaks',()=>assert.equal(csvCell('a,"b"\nc'),'"a,""b""\nc"'));
test('missing csv value',()=>assert.equal(csvCell(null),'""'));
for(const u of ['javascript:alert(1)','http://example.com','data:text/html,x','https://user:password@example.com','not a url'])test('unsafe-url/'+u,()=>assert.equal(safeSourceURL(u),null));
test('https links accepted',()=>assert.equal(safeSourceURL('https://www.nhs.uk/'),'https://www.nhs.uk/'));
test('export includes review state and BOM',()=>{
 const c=JSON.parse(fs.readFileSync(new URL('../data/conditions/common-cold.json',import.meta.url),'utf8'));
 const sources=JSON.parse(fs.readFileSync(new URL('../data/evidence/sources.json',import.meta.url),'utf8'));
 const result=comparisonCSV([c],[{id:'summary'}],sources,'zh-CN');
 assert.ok(result.startsWith('\uFEFF'));assert.ok(result.includes('editorial_draft'));assert.ok(result.includes('UNSPECIFIED'));assert.ok(result.includes('www.nhs.uk'));
});
