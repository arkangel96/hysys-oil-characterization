from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class QAResult:
    status: str
    flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

def normalize_light_ends(assay: dict[str, Any]) -> QAResult:
    le=assay.get("light_ends",{}); basis=le.get("basis"); bulk=le.get("light_ends_bulk_wt_pct_of_crude"); comps=le.get("components",{})
    numeric={k:float(v) for k,v in comps.items() if v is not None}; total=sum(numeric.values())
    if basis=="OF_WHOLE_CRUDE": return QAResult("PASS",metrics={"whole_crude_wt_pct":numeric,"sum":total})
    if basis!="OF_LIGHT_ENDS_CUT": return QAResult("FAIL",flags=["UNRESOLVED_LIGHT_ENDS_BASIS"])
    if bulk is None: return QAResult("FAIL",flags=["MISSING_LIGHT_ENDS_BULK_FRACTION"])
    if not numeric: return QAResult("FAIL",flags=["MISSING_LIGHT_ENDS_COMPONENTS"])
    if total<95 or total>105: return QAResult("FAIL",flags=["LIGHT_ENDS_COMPONENT_SUM_OUTSIDE_95_105"],metrics={"sum":total})
    warnings=[] if 98<=total<=102 else ["LIGHT_ENDS_COMPONENTS_RENORMALIZED"]
    frac={k:v/total for k,v in numeric.items()}
    whole={k:float(bulk)*f for k,f in frac.items()}
    return QAResult("PASS",warnings=warnings,metrics={"raw_sum":total,"normalized_cut_fraction":frac,"whole_crude_wt_pct":whole})

def validate_tbp(assay: dict[str, Any]) -> QAResult:
    pts=[]
    for p in assay.get("tbp",{}).get("points",[]):
        if p.get("temperature_C") is not None and p.get("cumulative_wt_pct") is not None: pts.append((float(p["temperature_C"]),float(p["cumulative_wt_pct"])))
    if len(pts)<5: return QAResult("FAIL",flags=["INSUFFICIENT_TBP_POINTS"])
    flags=[]; warnings=[]
    for i,(t,y) in enumerate(pts):
        if not 0<=y<=100: flags.append(f"TBP_YIELD_OUT_OF_RANGE_AT_{i}")
        if i:
            pt,py=pts[i-1]
            if t<pt: flags.append(f"TBP_TEMPERATURE_NON_MONOTONIC_AT_{i}")
            if y<py: flags.append(f"TBP_YIELD_NON_MONOTONIC_AT_{i}")
            if t==pt and y!=py: warnings.append(f"DUPLICATE_TEMPERATURE_AT_{i}")
            if y==py and t!=pt: warnings.append(f"DUPLICATE_YIELD_AT_{i}")
    maxy=max(y for _,y in pts)
    if maxy<90: flags.append("TBP_COVERAGE_BELOW_O2")
    elif maxy<97: warnings.append("TBP_COVERAGE_BELOW_O3")
    return QAResult("FAIL" if flags else "PASS",flags=flags,warnings=warnings,metrics={"point_count":len(pts),"max_cumulative_wt_pct":maxy})

def completeness_check(assay: dict[str, Any]) -> QAResult:
    flags=[]; warnings=[]; bulk=assay.get("bulk",{}); source=assay.get("source",{})
    if not assay.get("crude_id"): flags.append("MISSING_CRUDE_ID")
    if not source.get("tag"): flags.append("MISSING_SOURCE_TAG")
    if bulk.get("api_gravity") is None and bulk.get("specific_gravity_15C") is None: flags.append("MISSING_API_OR_SG")
    if not any(bulk.get(k) is not None for k in ["viscosity_cSt_40C","viscosity_cSt_50C","viscosity_cSt_100C"]): flags.append("MISSING_VISCOSITY")
    if bulk.get("sulfur_wt_pct") is None: flags.append("MISSING_SULFUR")
    tbp=validate_tbp(assay); le=normalize_light_ends(assay); flags+=tbp.flags+le.flags; warnings+=tbp.warnings+le.warnings
    if flags: return QAResult("OX",flags=sorted(set(flags)),warnings=sorted(set(warnings)))
    strong=["specific_gravity_15C","rvp_kPa","ccr_wt_pct","asphaltenes_wt_pct","nitrogen_wt_ppm","tan_mgKOH_g","water_wt_pct","salt_ptb","vanadium_wt_ppm","nickel_wt_ppm"]
    coverage=100*sum(bulk.get(k) is not None for k in strong)/len(strong)
    status="O3" if coverage>=75 and tbp.metrics.get("max_cumulative_wt_pct",0)>=97 and source.get("confidence") in {"high","medium"} else "O2"
    return QAResult(status,warnings=sorted(set(warnings)),metrics={"strong_field_coverage_percent":coverage,"tbp":tbp.metrics,"light_ends":le.metrics})
