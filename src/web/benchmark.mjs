/** Reproducible regression metrics, NOT clinical validation or population coverage. */
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {LocalSearch} from './search.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const conditions=fs.readdirSync(path.join(root,'data/conditions')).filter(x=>x.endsWith('.json')).sort().map(x=>JSON.parse(fs.readFileSync(path.join(root,'data/conditions',x),'utf8')));
const index=new LocalSearch(conditions);
const golden=JSON.parse(fs.readFileSync(path.join(root,'tests/fixtures/search-golden.json'),'utf8'));
function evaluate(queries){
 const rows=queries.map(({query,expected_id})=>{
  const ids=index.search(query,{limit:10}).map(r=>r.condition.id);
  return {query,expected_id,rank:ids.includes(expected_id)?ids.indexOf(expected_id)+1:null};
 });
 return {n:rows.length,recall_at_10:rows.filter(x=>x.rank!==null).length/rows.length,
   mrr_at_10:rows.reduce((s,x)=>s+(x.rank?1/x.rank:0),0)/rows.length,rows};
}
const names=conditions.flatMap(c=>['zh-CN','en'].map(loc=>({query:c.names[loc],expected_id:c.id})));
const report={version:'0.1.0-preview',dataset_kind:'synthetic_regression',
 independent_clinical_validation:false,population_coverage:null,
 warning:'Queries were authored with this corpus. Exact-name tests are lookup checks; symptom queries are only nine developer examples. These metrics are not diagnostic accuracy, emergency sensitivity, clinical specificity or representative coverage.',
 exact_names:evaluate(names),symptom_and_alias_examples:evaluate(golden)};
fs.mkdirSync(path.join(root,'reports'),{recursive:true});
fs.writeFileSync(path.join(root,'reports/search-benchmark.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({name_queries:report.exact_names.n,name_recall_at_10:report.exact_names.recall_at_10,name_mrr_at_10:report.exact_names.mrr_at_10,
 example_queries:report.symptom_and_alias_examples.n,example_recall_at_10:report.symptom_and_alias_examples.recall_at_10,clinical_validation:false},null,2));
if(report.exact_names.recall_at_10!==1 || report.symptom_and_alias_examples.recall_at_10!==1)process.exitCode=1;
