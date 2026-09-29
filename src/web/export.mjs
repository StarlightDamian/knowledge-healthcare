/** CSV hardening and safe external links. */
export function csvCell(value) {
  let s=String(value??'');
  // Guard formula injection including leading spaces/tabs and full-width variants.
  if(/^[\s\uFEFF]*[=+@\-＝＋＠－]/u.test(s) || /^[\t\r\n]/u.test(s))s="'"+s;
  return '"'+s.replaceAll('"','""')+'"';
}
export function comparisonCSV(conditions,fields,sources,lang='en') {
  const headers=['id','name','kind','primary_domain','review_status','clinical_region','editorial_updated_at',...fields.map(f=>f.id),'source_urls'];
  const sm=new Map(sources.map(s=>[s.id,s.url]));
  const rows=conditions.map(c=>[c.id,c.names[lang]||c.names.en,c.kind,c.primary_domain,c.review.status,c.clinical_region,c.review.editorial_updated_at,...fields.map(f=>c.sections[f.id].text[lang]||c.sections[f.id].text.en),c.source_ids.map(s=>sm.get(s)).join(' | ')]);
  return '\uFEFF'+[headers,...rows].map(r=>r.map(csvCell).join(',')).join('\r\n');
}
export function safeSourceURL(value) {
  try {const u=new URL(value);return u.protocol==='https:' && !u.username && !u.password ? u.href : null;}catch{return null;}
}
