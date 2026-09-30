import requests
from config import TSE

class TSEClient:
    def __init__(self, mode="official", timeout=10):
        self.cfg=TSE[mode]; self.timeout=timeout
        self.s=requests.Session()
        self.s.headers.update({"User-Agent":"JAP-Apuracao-2026/1.0"})
    def election_id(self,office):
        return self.cfg["federal_election"] if str(office) in {"1","6"} else self.cfg["state_election"]
    def _get(self,url):
        r=self.s.get(url,timeout=self.timeout); r.raise_for_status(); return r.json()
    def result_url(self,uf,scope,office):
        eid=self.election_id(office); c=self.cfg
        return f'{c["base"]}/{c["environment"]}/{c["cycle"]}/{eid}/dados/{uf.lower()}/{scope.lower()}-c{int(office):04d}-e{int(eid):06d}-u.json'
    def fetch_result(self,uf,scope,office):
        return self._get(self.result_url(uf,scope,office))
    @staticmethod
    def _arrays(payload):
        found=[]
        def walk(o):
            if isinstance(o,dict):
                for k,v in o.items():
                    if k.lower() in {"cand","cands","candidatos"} and isinstance(v,list):
                        found.extend(x for x in v if isinstance(x,dict))
                    walk(v)
            elif isinstance(o,list):
                for v in o: walk(v)
        walk(payload); return found
    @staticmethod
    def pick(d,keys,default=""):
        for k in keys:
            if k in d and d[k] not in ("",None): return d[k]
        return default
    def candidates(self,payload):
        out=[]
        for c in self._arrays(payload):
            n=str(self.pick(c,["n","nr","numero","nrcand"]))
            nm=str(self.pick(c,["nm","nmu","nome","nmurna"]))
            votes=self.pick(c,["vap","v","votos","qtv"],0)
            pct=self.pick(c,["pvap","p","percentual"],"")
            sq=str(self.pick(c,["sqcand","sq","sequencial"]))
            try: votes=int(str(votes).replace(".",""))
            except: votes=0
            if n: out.append({"number":n,"name":nm,"votes":votes,"pct":pct,"sqcand":sq})
        return out
    def find(self,payload,number):
        return next((x for x in self.candidates(payload) if x["number"]==str(number)),None)
    def photo_url(self,uf,sqcand,office):
        if not sqcand:return None
        eid=self.election_id(office); c=self.cfg
        return f'{c["base"]}/{c["environment"]}/{c["cycle"]}/{eid}/fotos/{uf.lower()}/{sqcand}.jpeg'
