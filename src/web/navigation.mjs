/** Counts are unique topics, never the sum of overlapping specialty memberships. */
export function departmentNavigation(conditions,groups) {
  return groups.map(group=>({
    ...group,
    count:conditions.filter(c=>c.departments.some(id=>group.departments.includes(id))).length,
    children:group.departments.map(id=>({id,count:conditions.filter(c=>c.departments.includes(id)).length})).filter(d=>d.count>0)
  })).filter(group=>group.count>0);
}
