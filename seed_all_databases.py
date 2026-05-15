"""Seed test data into all CockroachDB databases."""
from __future__ import annotations
import json
from datetime import date, datetime
from decimal import Decimal

COCKROACH_BASE = "cockroachdb+psycopg2://cubiczan:oY-hPkgXtZjc6kGqY67Gyg@vortex-giraffe-15678.jxf.gcp-us-east1.cockroachlabs.cloud:26257/"


def _exec(conn, sql, params=None):
    conn.execute(sql, params or {})


def seed_closed_loop_finance():
    print("\n=== Seeding closed_loop_finance ===")
    from sqlalchemy import create_engine, text
    e = create_engine(f"{COCKROACH_BASE}closed_loop_finance?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        for n,code,ct,st in [("2026-03 March Close","2026-03","monthly","closed"),("2026-04 April Close","2026-04","monthly","in_progress"),("2026-Q1 Q1 Close","2026-Q1","quarterly","open")]:
            _exec(c, text("INSERT INTO finance_periods (period_name,period_code,close_type,status) VALUES (:n,:c,:ct,:s) ON CONFLICT DO NOTHING"), {"n":n,"c":code,"ct":ct,"s":st})
        for fn,kind,rows,sz,ps in [("March P&L","csv",45,12500,"parsed"),("Balance Sheet","xlsx",30,8200,"parsed"),("Cash Flow","csv",25,6800,"parsed"),("Board Deck","pdf",None,2400000,"pending")]:
            _exec(c, text("INSERT INTO evidence (period_id,file_name,file_kind,row_count,file_size_bytes,parse_status,file_path) VALUES ((SELECT period_id FROM finance_periods WHERE period_code='2026-03' LIMIT 1),:fn,:fk,:r,:sz,:ps,:fp) ON CONFLICT DO NOTHING"), {"fn":fn,"fk":kind,"r":rows,"sz":sz,"ps":ps,"fp":f"/data/{fn}.{kind}"})
        _exec(c, text("INSERT INTO findings (period_id,facts,likely_causes,open_questions,confidence_score,analyst_agent) VALUES ((SELECT period_id FROM finance_periods WHERE period_code='2026-03' LIMIT 1),:f,:c,:q,:conf,:ag) ON CONFLICT DO NOTHING"), {"f":json.dumps(["Revenue up 12% YoY","Gross margin expanded 200bps"]),"c":json.dumps(["New customer acquisition"]),"q":json.dumps(["Impact of Q2 pricing changes?"]),"conf":78,"ag":"claude"})
        for dt,txt,dd,cat,ow,dm,sim in [("prior","Approve $2M CapEx for warehouse expansion","2025-11-15","strategic","CFO","Approved by board",0.92),("prior","Switch to annual billing","2025-12-01","revenue","VP Revenue","Implemented Jan 1",0.88),("proposed","Implement dynamic pricing","2026-04-15","revenue","CFO","",0),("proposed","Reduce contractor headcount 15%","2026-04-15","expense","VP Ops","",0)]:
            _exec(c, text("INSERT INTO decisions (period_id,decision_type,decision_text,decision_date,category,owner,decision_made,similarity_score) VALUES ((SELECT period_id FROM finance_periods WHERE period_code='2026-04' LIMIT 1),:dt,:t,:dd,:cat,:ow,:dm,:sim) ON CONFLICT DO NOTHING"), {"dt":dt,"t":txt,"dd":dd,"cat":cat,"ow":ow,"dm":dm,"sim":sim})
        _exec(c, text("INSERT INTO audit_trail (period_id,action,actor,entity_type,message) VALUES ((SELECT period_id FROM finance_periods WHERE period_code='2026-03' LIMIT 1),'evidence_collected','system','evidence','4 files ingested') ON CONFLICT DO NOTHING"))
    print("  Seeded: 3 periods, 4 evidence, 1 finding, 4 decisions, 1 audit")


def seed_sec_earnings_workbench():
    print("\n=== Seeding sec_earnings_workbench ===")
    from sqlalchemy import create_engine, text
    e = create_engine(f"{COCKROACH_BASE}sec_earnings_workbench?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        for did,t,d,o,s,hs,fs in [("DC-AAPL-001","Apple Revenue Analysis","Technology","claude","CONVERGED",True,85),("DC-TSLA-002","Tesla Q1 Delivery Miss","Automotive","claude","LOCKED",True,72),("DC-MSFT-003","Azure Growth Deceleration","Technology","claude","PROVISIONAL",False,55)]:
            _exec(c, text("INSERT INTO decision_cases (decision_id,title,domain,owner,status,high_stakes,foundation_score,origin_system) VALUES (:did,:t,:d,:o,:s,:hs,:fs,:sys) ON CONFLICT DO NOTHING"), {"did":did,"t":t,"d":d,"o":o,"s":s,"hs":hs,"fs":fs,"sys":"Claude"})
        _exec(c, text("INSERT INTO dossiers (decision_id,core_problem,goal_state,scope) VALUES ('DC-AAPL-001',:cp,:gs,:sc) ON CONFLICT DO NOTHING"), {"cp":"Is Apple revenue growth sustainable?","gs":json.dumps(["8%+ growth through FY2028"]),"sc":json.dumps(["iPhone","Services","Mac"])})
        for did,at,co,tk,ti,ls in [("DC-AAPL-001","business_model_memo","Apple Inc","AAPL","Business Model Memo - AAPL","CONVERGED"),("DC-TSLA-002","sec_deep_dive","Tesla Inc","TSLA","SEC Deep-Dive - TSLA","LOCKED")]:
            _exec(c, text("INSERT INTO research_artifacts (decision_id,artifact_type,company,ticker,title,lock_state) VALUES (:did,:at,:co,:tk,:t,:ls) ON CONFLICT DO NOTHING"), {"did":did,"at":at,"co":co,"tk":tk,"t":ti,"ls":ls})
        for did,ph,rn,v in [("DC-AAPL-001","FOUNDATION",1,"PASS"),("DC-AAPL-001","SPEC",2,"PASS"),("DC-AAPL-001","IMPLEMENTATION",3,"CONVERGED")]:
            _exec(c, text("INSERT INTO round_records (decision_id,phase,round_number,verdict) VALUES (:did,:ph,:rn,:v) ON CONFLICT DO NOTHING"), {"did":did,"ph":ph,"rn":rn,"v":v})
        _exec(c, text("INSERT INTO validation_records (decision_id,validator,item,challenge,result,rationale) VALUES ('DC-AAPL-001','GPT-5.4','Services sustainability','Can 15% growth persist?','CONFIRM','Ecosystem lock-in supports projection') ON CONFLICT DO NOTHING"))
        for src,ep,tk,st,ms,ca in [("ALPHAVANTAGE","OVERVIEW","AAPL",200,340,False),("ALPHAVANTAGE","INCOME_STATEMENT","AAPL",200,520,False),("FRED","FRED Series","GDP",200,180,True),("EDGAR","10-K","AAPL",200,1200,False)]:
            _exec(c, text("INSERT INTO api_call_log (api_source,endpoint,ticker,response_status,response_time_ms,cached) VALUES (:s,:e,:t,:st,:m,:c) ON CONFLICT DO NOTHING"), {"s":src,"e":ep,"t":tk,"st":st,"m":ms,"c":ca})
        _exec(c, text("INSERT INTO research_cache (cache_key,cache_hash,value_json,ttl_seconds,hits) VALUES (:k,:h,:v,86400,:hi) ON CONFLICT DO NOTHING"), {"k":"av_overview_AAPL","h":"abc123","v":json.dumps({"symbol":"AAPL","marketCap":3000000000000}),"hi":3})
    print("  Seeded: 3 cases, 1 dossier, 2 artifacts, 3 rounds, 1 validation, 4 API logs, 1 cache")


def seed_autonomous_business_os():
    print("\n=== Seeding autonomous_business_os ===")
    from sqlalchemy import create_engine, text
    e = create_engine(f"{COCKROACH_BASE}autonomous_business_os?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        for k,t,s,src,a in [("lead-qualification","Lead Qual - Acme Corp","completed","webhook",2),("client-onboarding","Onboarding - TechStart","running","api",5),("delivery-monitoring","Delivery Health Q2","waiting_for_human","scheduled",1),("finance-review","Monthly Finance Apr","pending","scheduled",0)]:
            _exec(c, text("INSERT INTO workflows (id,kind,title,status,source,attempts) VALUES (gen_random_uuid(),:k,:t,:s,:src,:a)"), {"k":k,"t":t,"s":s,"src":src,"a":a})
        for ag,tl,st,out in [("lead_qualification","enrichment","completed","Enriched with Apollo"),("client_onboarding","crm_sync","running","Syncing to HubSpot"),("client_onboarding","email_draft","queued","")]:
            _exec(c, text("INSERT INTO agent_tasks (workflow_id,agent_name,tool_name,status,output_data) VALUES ((SELECT id FROM workflows WHERE status='running' LIMIT 1),:ag,:tl,:s,:o)"), {"ag":ag,"tl":tl,"s":st,"o":json.dumps({"result":out}) if out else "{}"})
        for ns,k,v in [("lead_qualification","acme_corp_profile",json.dumps({"company":"Acme Corp","employees":250})),("finance","april_variance",json.dumps({"revenue_variance_pct":3.2})),("delivery","q2_status",json.dumps({"on_track":18,"at_risk":3}))]:
            _exec(c, text("INSERT INTO memory_entries (namespace,key,value) VALUES (:ns,:k,:v)"), {"ns":ns,"k":k,"v":v})
        _exec(c, text("INSERT INTO human_approvals (workflow_id,title,reason,status,proposed_action) VALUES ((SELECT id FROM workflows WHERE status='waiting_for_human' LIMIT 1),'Approve Q2 Plan','3 tasks at risk','open',:pa) ON CONFLICT DO NOTHING"), {"pa":json.dumps({"action":"reallocate_engineers"})})
        for wf,ac,ac2,msg in [("lead-qualification","workflow_completed","system","Lead qual completed"),("client-onboarding","task_started","client_onboarding","Starting CRM sync")]:
            _exec(c, text("INSERT INTO audit_logs (workflow_id,action,actor,message) VALUES ((SELECT id FROM workflows WHERE kind=:wf LIMIT 1),:ac,:ac2,:msg) ON CONFLICT DO NOTHING"), {"wf":wf,"ac":ac,"ac2":ac2,"msg":msg})
        _exec(c, text("INSERT INTO escalations (severity,owner,reason,context) VALUES ('high','ops','HubSpot API rate limit',:ctx) ON CONFLICT DO NOTHING"), {"ctx":json.dumps({"retry_after":3600})})
        for em,co,nm,src,sc in [("sarah@techstart.io","TechStart","Sarah Chen","apollo",92),("james@acme.com","Acme Corp","James Wilson","inbound",85),("maria@nova.io","Nova Industries","Maria Garcia","referral",78),("david@cloudscale.io","CloudScale","David Kim","outbound",65)]:
            _exec(c, text("INSERT INTO leads (email,company,name,source,score) VALUES (:e,:co,:n,:s,:sc)"), {"e":em,"co":co,"n":nm,"s":src,"sc":sc})
    print("  Seeded: 4 workflows, 3 tasks, 3 memory, 1 approval, 2 audit, 1 escalation, 4 leads")


def seed_hedge_fund_13f_radar():
    print("\n=== Seeding hedge_fund_13f_radar ===")
    from sqlalchemy import create_engine, text
    e = create_engine(f"{COCKROACH_BASE}hedge_fund_13f_radar?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        for n,sty,aum in [("Bridgewater Associates","macro",150e9),("Renaissance Technologies","quant",130e9),("Citadel","multi-strategy",65e9),("Third Point","activist",12e9),("Elliott Management","activist",60e9)]:
            _exec(c, text("INSERT INTO fund_managers (name,style,aum_usd) VALUES (:n,:s,:a) ON CONFLICT DO NOTHING"), {"n":n,"s":sty,"a":Decimal(str(int(aum)))})
        for q,tk,co,sec,sh,pr,v,ac,cv in [("2025-Q4","AAPL","Apple Inc","Technology",5e6,4.8e6,950e6,"INCREASED","HIGH"),("2025-Q4","NVDA","NVIDIA","Technology",3e6,2e6,720e6,"INCREASED","HIGH"),("2025-Q4","MSFT","Microsoft","Technology",2e6,2.1e6,600e6,"DECREASED","MEDIUM"),("2025-Q4","AMZN","Amazon","Consumer",1.5e6,0,270e6,"INITIATED","HIGH"),("2025-Q4","JPM","JPMorgan","Financials",1.8e6,1.8e6,420e6,"HELD","MEDIUM"),("2025-Q4","LLY","Eli Lilly","Healthcare",6e5,4e5,360e6,"INCREASED","HIGH")]:
            _exec(c, text("INSERT INTO holdings (manager_id,quarter,ticker,company,sector,shares,prior_shares,value_usd,action,conviction) VALUES ((SELECT manager_id FROM fund_managers LIMIT 1),:q,:tk,:co,:s,:sh,:pr,:v,:a,:c)"), {"q":q,"tk":tk,"co":co,"s":sec,"sh":Decimal(str(int(sh))),"pr":Decimal(str(int(pr))),"v":Decimal(str(int(v))),"a":ac,"c":cv})
        _exec(c, text("INSERT INTO radar_reports (quarter,consensus_tickers,verification_status,verification_confidence,total_managers,total_holdings) VALUES ('2025-Q4',:ct,'CLEAR',90,5,8) ON CONFLICT DO NOTHING"), {"ct":json.dumps(["AAPL","NVDA","MSFT","JPM","LLY"])})
    print("  Seeded: 5 managers, 6 holdings, 1 report")


def seed_market_sentiment_fedgpt():
    print("\n=== Seeding market_sentiment_fedgpt ===")
    from sqlalchemy import create_engine, text
    e = create_engine(f"{COCKROACH_BASE}market_sentiment_fedgpt?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        for n,v,d,b,s,r in [("aaii_bull_bear",18.5,"2026-05-10","fearful",-2,"FEARFUL"),("naaim_exposure",72.3,"2026-05-10","neutral",0,"NEUTRAL"),("vix",18.2,"2026-05-10","neutral",0,"NEUTRAL"),("put_call",0.82,"2026-05-10","neutral",1,"NEUTRAL"),("consumer_confidence",88.5,"2026-05-10","neutral",-1,"NEUTRAL"),("umich_sentiment",72.1,"2026-05-10","fearful",-1,"NEUTRAL"),("naaim_exposure",88.0,"2026-04-10","exuberant",2,"EXUBERANT")]:
            _exec(c, text("INSERT INTO sentiment_indicators (name,value,source_date,bias,score,regime_at_time) VALUES (:n,:v,:d,:b,:s,:r)"), {"n":n,"v":v,"d":d,"b":b,"s":s,"r":r})
        _exec(c, text("INSERT INTO fed_speeches (speaker,title,speech_date,tone,net_score,hawkish_terms,dovish_terms) VALUES ('Jerome Powell','FOMC Press Conference','2026-05-01','BALANCED',1,:ht,:dt) ON CONFLICT DO NOTHING"), {"ht":json.dumps(["inflation","restrictive"]),"dt":json.dumps(["cooling","disinflation"])})
        _exec(c, text("INSERT INTO sentiment_reports (analysis_date,regime,fed_tone,sentiment_score,fed_score,policy_path,verification_status,verification_confidence) VALUES ('2026-05-10','NEUTRAL','BALANCED',-3,1,:pp,'CLEAR',100) ON CONFLICT DO NOTHING"), {"pp":json.dumps({"3_month_cut_probability":0.23,"6_month_cut_probability":0.34,"12_month_cut_probability":0.43})})
    print("  Seeded: 7 indicators, 1 Fed speech, 1 report")


def seed_remaining():
    print("\n=== Seeding WCO, CFOpt, Stratifi ===")
    from sqlalchemy import create_engine, text
    # WCO
    e = create_engine(f"{COCKROACH_BASE}working_capital_optimizer?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        for n,t,vc,a,di,dd,s,ab,do,di2,dp in [("INV-001","AP","Cloud Services Inc",125000,"2026-04-01","2026-05-01","open","1-30",30,2500,"2.0"),("INV-002","AR","Acme Corp",350000,"2026-03-15","2026-04-15","overdue","31-60",60,0,"0"),("INV-003","AP","Marketing LLC",45000,"2026-04-10","2026-05-10","open","current",5,900,"2.0")]:
            _exec(c, text("INSERT INTO invoices (invoice_number,invoice_type,vendor_customer,amount_usd,invoice_date,due_date,status,aging_bucket,days_outstanding,discount_available,discount_pct) VALUES (:n,:t,:vc,:a,:di,:dd,:s,:ab,:do,:di2,:dp)"), {"n":n,"t":t,"vc":vc,"a":a,"di":di,"dd":dd,"s":s,"ab":ab,"do":do,"di2":di2,"dp":dp})
        _exec(c, text("INSERT INTO cash_flow_forecasts (period,scenario,opening_balance,inflows,outflows,net_cash_flow,closing_balance,confidence) VALUES ('2026-05','base',2500000,1800000,1600000,200000,2700000,75) ON CONFLICT DO NOTHING"))
    print("  WCO: 3 invoices, 1 forecast")
    # CFOpt
    e = create_engine(f"{COCKROACH_BASE}cash_flow_optimizer?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        for p,beg,ocf,icf,fcf,net,end,rev,ox,ni,dso,dpo,dio,ccc in [("2026-01",2200000,1500000,-400000,-200000,900000,3100000,2800000,1800000,520000,45,60,30,75),("2026-02",3100000,1600000,-350000,-150000,1100000,4200000,3000000,1900000,680000,42,58,28,72),("2026-03",4200000,1750000,-500000,-250000,1000000,5200000,3200000,2000000,750000,40,55,25,70)]:
            _exec(c, text("INSERT INTO cash_flow_statements (period,period_type,beginning_cash,operating_cash_flow,investing_cash_flow,financing_cash_flow,net_change,ending_cash,revenue,opex,net_income,dso,dpo,dio,ccc) VALUES (:p,'monthly',:b,:ocf,:icf,:fcf,:n,:e,:r,:ox,:ni,:dso,:dpo,:dio,:ccc)"), {"p":p,"b":beg,"ocf":ocf,"icf":icf,"fcf":fcf,"n":net,"e":end,"r":rev,"ox":ox,"ni":ni,"dso":dso,"dpo":dpo,"dio":dio,"ccc":ccc})
        _exec(c, text("INSERT INTO projections (base_period,scenario,projected_revenue,projected_opex,projected_ocf,projected_fcf,runway_months,confidence) VALUES ('2026-03','base',3500000,2100000,850000,400000,24,72) ON CONFLICT DO NOTHING"))
    print("  CFOpt: 3 statements, 1 projection")
    # Stratifi
    e = create_engine(f"{COCKROACH_BASE}stratifi_core?sslmode=require", pool_pre_ping=True)
    with e.begin() as c:
        _exec(c, text("INSERT INTO analyses (title,domain,company,status,high_stakes,foundation_score) VALUES ('AAPL Revenue Sustainability','Technology','Apple Inc','locked',True,85),('TSLA Demand Analysis','Automotive','Tesla Inc','in_review',True,72) ON CONFLICT DO NOTHING"))
        _exec(c, text("INSERT INTO decision_cases (decision_id,title,domain,analysis_id,status,foundation_score) VALUES ('SC-AAPL-001','AAPL Revenue','Technology',(SELECT analysis_id FROM analyses WHERE company='Apple Inc' LIMIT 1),'LOCKED',85) ON CONFLICT DO NOTHING"))
        _exec(c, text("INSERT INTO risk_signals (analysis_id,category,description,severity,probability,impact) VALUES ((SELECT analysis_id FROM analyses WHERE company='Apple Inc' LIMIT 1),'structural','iPhone market saturation','high',0.6,0.8) ON CONFLICT DO NOTHING"))
    print("  Stratifi: 2 analyses, 1 decision, 1 risk signal")


if __name__ == "__main__":
    seed_closed_loop_finance()
    seed_sec_earnings_workbench()
    seed_autonomous_business_os()
    seed_hedge_fund_13f_radar()
    seed_market_sentiment_fedgpt()
    seed_remaining()
    print("\n All databases seeded!")
