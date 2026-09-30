import test from 'node:test';
import assert from 'node:assert/strict';
import {GuideAPI,pageItems} from '../src/web/api.mjs';

const answer=value=>({ok:true,json:async()=>value});
test('catalog requests pin release and never contain local search terms',async()=>{
  const calls=[];
  const api=new GuideAPI('https://example.test/healthcare/api/v1/',async(url,options)=>{
    calls.push({url,options});
    if(url.endsWith('bootstrap'))return answer({release_id:'release-a'});
    const offset=Number(new URL(url).searchParams.get('offset'));
    return answer({release_id:'release-a',total:2,offset,items:[{id:offset?'b':'a'}]});
  });
  await api.bootstrap();const pages=[];for await(const page of api.catalog())pages.push(page);
  assert.equal(pages.length,2);assert.equal(pages.at(-1).complete,true);
  assert.ok(calls.slice(1).every(c=>new URL(c.url).searchParams.get('release_id')==='release-a'));
  assert.ok(calls.every(c=>c.options.credentials==='omit'&&c.options.referrerPolicy==='no-referrer'));
});
test('release mismatch and empty catalog continuation fail explicitly',async()=>{
  const api=new GuideAPI('https://example.test/',async()=>answer({release_id:'b'}));api.release='a';
  await assert.rejects(api.condition('cold'),/Release mismatch/);
  api.fetcher=async()=>answer({release_id:'a',offset:0,total:10,items:[]});
  await assert.rejects(async()=>{for await(const p of api.catalog()){}},/Incomplete catalog/);
});
test('batch limits network groups to 100 while preserving selected order and caching',async()=>{
  const requests=[];
  const api=new GuideAPI('https://example.test/',async(url,options)=>{
    const body=JSON.parse(options.body);requests.push(body);
    return answer({release_id:'a',conditions:body.ids.map(id=>({id})),sources:[],studies:[]});
  });api.release='a';
  const ids=Array.from({length:213},(_,i)=>'topic-'+i),data=await api.batch(ids);
  assert.deepEqual(requests.map(r=>r.ids.length),[100,100,13]);
  assert.deepEqual(data.map(r=>r.condition.id),ids);
  await api.batch(ids);assert.equal(requests.length,3);
});
test('request failures do not poison detail cache and concurrent opens share one fetch',async()=>{
  let count=0;const api=new GuideAPI('https://example.test/',async()=>{
    count++;if(count===1)throw Error('offline');return answer({release_id:'a',condition:{id:'cold'}});
  });api.release='a';await assert.rejects(api.condition('cold'),/offline/);
  await Promise.all([api.condition('cold'),api.condition('cold')]);assert.equal(count,2);
});
test('50 item rendering and full selected export remain independent',()=>{
  const ids=Array.from({length:16040},(_,i)=>'topic-'+i);
  assert.equal(pageItems(ids,0).length,50);assert.equal(pageItems(ids,320).length,40);
  const api=new GuideAPI('https://example.test/healthcare/api/v1/');api.release='a';
  const request=api.exportRequest(ids,'en');
  assert.equal(JSON.parse(request.fields.ids).length,16040);
  assert.equal(request.fields.release_id,'a');assert.equal(request.fields.locale,'en');
});
