/** Deterministic local retrieval. Scores are relevance weights, NEVER probabilities. */
export function normalize(value) {
  return String(value ?? '').normalize('NFKC').toLowerCase().replace(/\s+/gu, ' ').trim();
}
export function splitClauses(value) {
  return normalize(value).split(/[，,。.!?！？;；\n]|\bbut\b|\bhowever\b|但是|但/u).filter(Boolean);
}
export function isNegated(clause, index) {
  const before = clause.slice(0, index);
  // A bounded, deliberately small heuristic. Ambiguous/double negation stays positive.
  if (/不是没有|并非没有|不能排除|不排除|not without|cannot rule out/u.test(before)) return false;
  return /(?:没有|无|否认|不是|未出现|不伴)(?:明显|明显的|任何)?[^，,。;；]{0,10}$/u.test(before)
    || /\b(?:no|not|without|denies|denied)\b(?:\s+[\p{L}'-]+){0,5}\s*$/u.test(before);
}
export function hasPositiveTerm(value, term) {
  const needle=normalize(term);
  if (!needle) return false;
  return splitClauses(value).some(clause=>{
    let i=clause.indexOf(needle);
    while(i!==-1) {
      // English word boundaries avoid 'heat' in 'cheat'. Chinese terms are substrings.
      const latin=/^[a-z]/.test(needle);
      const bounded=!latin || (!/[a-z]/.test(clause[i-1]||'') && !/[a-z]/.test(clause[i+needle.length]||''));
      if(bounded && !isNegated(clause,i))return true;
      i=clause.indexOf(needle,i+1);
    }
    return false;
  });
}
export function positiveQuery(value) {
  return splitClauses(value).filter(c=>!/^\s*(?:没有|无(?:明显)?|否认|未出现|no\b|without\b|denies\b)/u.test(c)).join(' ');
}
export function tokenize(value) {
  const s=normalize(value);const tokens=[];
  for(const chunk of s.match(/[\p{Script=Han}]+|[\p{L}\p{N}]+/gu)||[]) {
    if(/\p{Script=Han}/u.test(chunk)) {
      if(chunk.length===1)tokens.push(chunk);
      for(let i=0;i<chunk.length-1;i++)tokens.push(chunk.slice(i,i+2));
    } else if(!new Set(['the','a','an','i','my','is','have','with','and','only','有','只有']).has(chunk)) tokens.push(chunk);
  }
  return tokens;
}
export class LocalSearch {
  constructor(conditions) {
    this.conditions=conditions;
    this.docs=conditions.map(c=>{
      const names=[...Object.values(c.names),...Object.values(c.aliases).flat()];
      const symptoms=c.symptom_terms.flatMap(t=>Object.values(t));
      const tokens=tokenize([...names,...names,...names,...symptoms,...symptoms].join(' '));
      const tf=new Map();for(const t of tokens)tf.set(t,(tf.get(t)||0)+1);
      return {c,names,symptoms,tf,length:tokens.length};
    });
    this.df=new Map();for(const doc of this.docs)for(const t of doc.tf.keys())this.df.set(t,(this.df.get(t)||0)+1);
    this.avg=this.docs.reduce((n,d)=>n+d.length,0)/(this.docs.length||1)||1;
  }
  search(query,{domain='',kind='',departments=[],limit=this.conditions.length}={}) {
    if(!Number.isFinite(limit)||limit<0)throw new TypeError('Invalid result limit');
    const raw=normalize(query).slice(0,500);const q=positiveQuery(raw);const ts=[...new Set(tokenize(q))];
    const out=[];
    for(const d of this.docs) {
      const c=d.c;if(domain && c.primary_domain!==domain || kind && c.kind!==kind)continue;
      if(departments.length && !c.departments.some(id=>departments.includes(id)))continue;
      if(!raw){out.push({condition:c,score:0,reasons:[]});continue;}
      if(!q || !ts.length)continue;
      let score=0;const reasons=[];
      for(const t of ts) {
        const tf=d.tf.get(t)||0;const df=this.df.get(t)||0;if(!tf)continue;
        const idf=Math.log(1+(this.docs.length-df+0.5)/(df+0.5));
        score+=idf*(tf*2.2)/(tf+1.2*(0.25+0.75*d.length/this.avg));
      }
      for(const name of Object.values(c.names)) {
        const n=normalize(name);
        if(q===n){score+=10000;reasons.push({type:'name',term:name});}
        else if(n.length>=2 && hasPositiveTerm(q,n)){score+=100+n.length;reasons.push({type:'name',term:name});}
      }
      for(const alias of Object.values(c.aliases).flat()) {
        if(q===normalize(alias)){score+=5000;reasons.push({type:'alias',term:alias});}
        else if(normalize(alias).length>=3 && hasPositiveTerm(q,alias)){score+=65;reasons.push({type:'alias',term:alias});}
      }
      for(const term of d.symptoms)if(hasPositiveTerm(raw,term)){score+=180;reasons.push({type:'symptom',term});}
      if(score>0)out.push({condition:c,score,reasons:reasons.slice(0,4)});
    }
    return out.sort((a,b)=>b.score-a.score || a.condition.id.localeCompare(b.condition.id)).slice(0,limit);
  }
}
