/** Same-origin, immutable-release API. Search text and safety inputs never leave the page. */
export const PAGE_SIZE=50;
export const ONLINE_MESSAGES={
  loading:{'zh-CN':'正在加载…',en:'Loading…'},
  catalogLoading:{'zh-CN':'正在加载病症目录…',en:'Loading the condition catalog…'},
  catalogPartial:{'zh-CN':'目录仍在加载，当前结果仅包含已加载主题。',en:'The catalog is still loading. Results include loaded topics only.'},
  loadFailed:{'zh-CN':'内容暂时无法加载，请重试。危险信号提示仍可使用。',en:'Content could not be loaded. Please retry. Danger alerts remain available.'},
  retry:{'zh-CN':'重试',en:'Retry'},
  previousPage:{'zh-CN':'上一页',en:'Previous page'},
  nextPage:{'zh-CN':'下一页',en:'Next page'},
  pageStatus:{'zh-CN':'页',en:'Page'},
  onlineReading:{'zh-CN':'在线阅读 · 搜索词不上传',en:'Online reading · Searches stay on this page'},
  exportFailed:{'zh-CN':'导出暂时失败，请重试。',en:'The export failed. Please retry.'}
};

export function pageItems(items,page,size=PAGE_SIZE){return items.slice(page*size,(page+1)*size);}

export class GuideAPI {
  constructor(base,fetcher=globalThis.fetch.bind(globalThis)){
    this.base=base.endsWith('/')?base:base+'/';this.fetcher=fetcher;this.release=null;
    this.details=new Map();this.modules=new Map();this.pending=new Map();
  }
  async request(path,{body,pin=true}={}){
    if(pin&&!this.release)throw new Error('No release has been loaded');
    const url=new URL(path,this.base);
    if(pin&&!body)url.searchParams.set('release_id',this.release);
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),30000);
    try{
      const response=await this.fetcher(url.href,{method:body?'POST':'GET',credentials:'omit',referrerPolicy:'no-referrer',cache:'no-store',signal:controller.signal,
        ...(body?{headers:{'Content-Type':'application/json'},body:JSON.stringify({...body,release_id:this.release})}:{})});
      if(!response.ok)throw new Error('API '+response.status);
      const data=await response.json();
      if(!data.release_id||this.release&&data.release_id!==this.release)throw new Error('Release mismatch');
      return data;
    }finally{clearTimeout(timer);}
  }
  async bootstrap(){const data=await this.request('bootstrap',{pin:false});this.release=data.release_id;return data;}
  async *catalog(){
    let offset=0,total=null;const seen=new Set();
    do{
      const page=await this.request('catalog?offset='+offset+'&limit=1000');
      if(page.offset!==offset||!Array.isArray(page.items)||!Number.isInteger(page.total)||page.total<0||total!==null&&page.total!==total)throw new Error('Invalid catalog page');
      total=page.total;
      for(const item of page.items){if(seen.has(item.id))throw new Error('Duplicate catalog item');seen.add(item.id);}
      offset+=page.items.length;
      if(offset>total||offset<total&&!page.items.length)throw new Error('Incomplete catalog page');
      yield {...page,complete:offset===total};
    }while(offset<total);
  }
  async condition(id){
    if(this.details.has(id))return this.details.get(id);
    const key='condition:'+id;
    if(!this.pending.has(key))this.pending.set(key,this.request('conditions/'+encodeURIComponent(id)).then(data=>{
      if(data.condition.id!==id)throw new Error('Condition mismatch');this.details.set(id,data);return data;
    }).finally(()=>this.pending.delete(key)));
    return this.pending.get(key);
  }
  async batch(ids){
    const missing=[...new Set(ids)].filter(id=>!this.details.has(id));
    for(let offset=0;offset<missing.length;offset+=100){
      const requested=missing.slice(offset,offset+100),data=await this.request('conditions/batch',{body:{ids:requested}});
      if(data.conditions.length!==requested.length||data.conditions.some(c=>!requested.includes(c.id))||new Set(data.conditions.map(c=>c.id)).size!==requested.length)throw new Error('Incomplete comparison');
      for(const condition of data.conditions)this.details.set(condition.id,{release_id:data.release_id,condition,sources:data.sources,studies:data.studies});
    }
    return ids.map(id=>this.details.get(id));
  }
  async knowledge(id){
    if(this.modules.has(id))return this.modules.get(id);
    const key='module:'+id;
    if(!this.pending.has(key))this.pending.set(key,this.request('knowledge/'+encodeURIComponent(id)).then(data=>{
      this.modules.set(id,data.module);return data.module;
    }).finally(()=>this.pending.delete(key)));
    return this.pending.get(key);
  }
  exportRequest(ids,locale,all=false){
    if(!this.release)throw new Error('No release has been loaded');
    return {url:new URL('exports/conditions.csv',this.base).href,fields:{release_id:this.release,locale,scope:all?'all':'ids',ids:JSON.stringify(all?[]:[...new Set(ids)])}};
  }
}
