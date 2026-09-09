"""Generate a precise SVG architecture figure; no external rendering dependency."""
from html import escape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parts=['''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1500" viewBox="0 0 1280 1500">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#64748b"/></marker></defs>
<rect width="1280" height="1500" fill="#f7f9fc"/>
<style>text{font-family:Arial,Helvetica,sans-serif}.title{font-size:34px;font-weight:700;fill:#12243b}.sub{font-size:19px;fill:#4b6078}.name{font-size:21px;font-weight:700;fill:#12243b}.detail{font-size:17px;fill:#425a72}.label{font-size:16px;font-weight:700;fill:#425a72}</style>
<text x="65" y="65" class="title">Resident Maintenance Triage</text>
<text x="65" y="100" class="sub">n8n orchestration · atomic state · bounded classification · human review</text>
<rect x="65" y="121" width="1150" height="42" rx="10" fill="#e8edf5"/>
<text x="85" y="148" class="detail">Synthetic lab. Fixture default; live Claude integration demonstrated separately.</text>''']

def box(x,y,w,title,lines,fill='#ffffff',stroke='#b7c7d8',h=90):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    parts.append(f'<text x="{x+18}" y="{y+32}" class="name">{escape(title)}</text>')
    for i,line in enumerate(lines):parts.append(f'<text x="{x+18}" y="{y+59+i*23}" class="detail">{escape(line)}</text>')
def edge(d,label='',x=0,y=0):
    parts.append(f'<path d="{d}" fill="none" stroke="#64748b" stroke-width="2.4" marker-end="url(#arrow)"/>')
    if label:parts.append(f'<text x="{x}" y="{y}" class="label">{escape(label)}</text>')

# Draw connectors behind the blocks.
for a,b in [(280,320),(410,450),(540,580),(670,730),(820,860),(950,990),(1080,1140),(1230,1270)]:edge(f'M640 {a}V{b}')
edge('M465 365H360','invalid',375,348)
edge('M815 495H920','replay',842,478)
edge('M465 625H215V730','review',264,608)
edge('M465 905H370V795H360','review',377,888)
edge('M815 1035H920','failed',844,1018)
edge('M815 775H865V935H1065V990','API failure',891,915)
edge('M215 840V1185H465','persist outcome',235,1164)
edge('M1065 1080V1185H815','persist outcome',933,1164)

box(465,190,350,'Authenticated intake',['POST /maintenance'])
box(465,320,350,'Validate and trace',['Allowlisted synthetic JSON'])
box(65,320,295,'Reject intake',['Controlled 4xx response'],'#fff2e7','#e9a775')
box(465,450,350,'Redact and claim',['Atomic event ownership'])
box(920,450,295,'Replay or conflict',['Prior outcome or HTTP 409'],'#eaf2ff','#8cb3e8')
box(465,580,350,'Deterministic safety gate',['Emergency / injection cues'])
box(65,730,295,'Human review',['Model bypass or uncertain','classification'],'#fff2e7','#e9a775',110)
box(465,730,350,'Bounded model call',['Claude API or fixture'])
box(465,860,350,'Validate model output',['Schema, flags, urgency, confidence'])
box(465,990,350,'Checkpoint and ticket',['Idempotent mock ticket API'])
box(920,990,295,'Recovery record',['Saved IDs and checkpoint'],'#fff2e7','#e9a775')
box(465,1140,350,'Commit durable outcome',['Audit + queue + mock outbox'])
box(465,1270,350,'Accurate acknowledgement',['Ticket, review, or recovery'])
parts += ['''<rect x="65" y="1400" width="1150" height="65" rx="14" fill="#12243b"/>
<text x="88" y="1427" font-size="19" fill="white" font-weight="700">24 integration scenarios passed inside real n8n</text>
<text x="88" y="1450" font-size="17" fill="#dbe8fa">State failure: explicit 503 → linked Error Trigger → reconciliation. See the runbook for limits.</text>
</svg>''']
(ROOT/'docs/architecture.svg').write_text('\n'.join(parts))
