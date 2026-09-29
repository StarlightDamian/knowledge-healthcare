"""Evidence impact and sequential, rate-limited link checks. HTTP != clinical support."""
from __future__ import annotations
import hashlib
import time
import urllib.request
from urllib.parse import urlparse
from .model import ValidationError, safe_url
ALLOWED=('nhs.uk','who.int','medlineplus.gov','nih.gov','cdc.gov','cancer.gov','nice.org.uk','fda.gov')

def impact(data:dict,source_id:str) -> list[dict]:
    if source_id not in {s['id'] for s in data['sources']}:raise ValidationError('Unknown source ID')
    return [{'id':c['id'],'fields':[k for k,v in c['sections'].items() if source_id in v['source_ids']]} for c in data['conditions'] if source_id in c['source_ids']]

def check_links(data:dict,limit:int=10) -> list[dict]:
    if not 1<=limit<=200:raise ValidationError('Limit must be 1..200')
    result=[]
    for s in data['sources'][:limit]:
        u=s['url'];host=urlparse(u).hostname or ''
        if not safe_url(u) or not any(host==a or host.endswith('.'+a) for a in ALLOWED):
            result.append({'id':s['id'],'state':'host_not_allowlisted'});continue
        # No automatic redirects: a redirection must be inspected before following it.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs):return None
        opener=urllib.request.build_opener(NoRedirect)
        req=urllib.request.Request(u,headers={'User-Agent':'OpenMedicalGuide-LinkCheck/0.1 (link integrity only)'},method='HEAD')
        try:
            with opener.open(req,timeout=8) as response:
                result.append({'id':s['id'],'state':'http_response','status':response.status,'claim_support':'not_checked'})
        except Exception as exc:
            result.append({'id':s['id'],'state':'needs_manual_check','reason':str(exc),'claim_support':'not_checked'})
        time.sleep(1)
    return result
