import { hasPositiveTerm, normalize } from './search.mjs';
/** Finite safety prompts only; an empty alert list NEVER means safety. */
export function evaluateSafety(query, ruleSet, context={}) {
  const text=normalize(query).slice(0,2000);
  const alerts=ruleSet.rules.filter(rule=>rule.groups.every(group=>group.some(t=>hasPositiveTerm(text,t))))
    .map(rule=>({id:rule.id,action:rule.action,label:rule.label,source_ids:rule.source_ids}));
  const {ageMonths,temperatureC}=context;
  if(typeof ageMonths==='number' && typeof temperatureC==='number' && Number.isFinite(ageMonths)
    && Number.isFinite(temperatureC) && ageMonths>=0 && ageMonths<3 && temperatureC>=38 && temperatureC<=45) {
    alerts.push({id:'infant-fever-structured',action:'urgent_assessment',label:{'zh-CN':'不足3个月婴儿体温达到38°C：立即联系医疗人员评估；病情严重时呼叫急救。','en':'An infant under 3 months with a temperature of 38°C needs urgent professional assessment; call emergency services if severely unwell.'},source_ids:['nhs-child-fever','fever-secondary']});
  }
  return {alerts,assurance:false,clinicalValidation:ruleSet.status,languageScope:ruleSet.language_scope};
}
