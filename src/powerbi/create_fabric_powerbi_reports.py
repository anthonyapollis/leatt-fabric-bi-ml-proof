from __future__ import annotations

import base64
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
REPO = OUT / "leatt-fabric-bi-ml-git-proof"
PROOF = OUT / "powerbi_semantic_model_proof.json"
REPORT_ROOT = OUT / "fabric_powerbi_reports"


def read_proof() -> dict[str, str]:
    return json.loads(PROOF.read_text(encoding="utf-8"))


def az_token() -> str:
    az = shutil.which("az") or shutil.which("az.cmd") or r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    result = subprocess.run(
        [az, "account", "get-access-token", "--resource", "https://api.fabric.microsoft.com", "--query", "accessToken", "-o", "tsv"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def b64(obj: Any) -> str:
    if isinstance(obj, str):
        text = obj
    else:
        text = json.dumps(obj, indent=2)
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def source_ref(table: str) -> dict[str, Any]:
    return {"SourceRef": {"Entity": table}}


def column_field(table: str, column: str) -> dict[str, Any]:
    return {
        "Column": {
            "Expression": source_ref(table),
            "Property": column,
        }
    }


def measure_like(table: str, column: str) -> dict[str, Any]:
    # PBIR accepts column projections; Power BI applies the visual's default summarization for numeric columns.
    return column_field(table, column)


def visual(name: str, visual_type: str, x: float, y: float, w: float, h: float, roles: dict[str, list[tuple[str, str]]], z: int) -> dict[str, Any]:
    query_state = {}
    for role, fields in roles.items():
        projections = []
        for table, col in fields:
            projections.append(
                {
                    "field": column_field(table, col),
                    "queryRef": f"{table}.{col}",
                    "active": True,
                }
            )
        query_state[role] = {"projections": projections}
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {"visualType": visual_type, "query": {"queryState": query_state}, "drillFilterOtherVisuals": True},
    }


def textbox(name: str, x: float, y: float, w: float, h: float, text: str, z: int) -> dict[str, Any]:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": text,
                                            "textStyle": {"fontSize": "18pt", "fontWeight": "bold"},
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
        },
    }


def page(name: str, display: str, visuals: list[dict[str, Any]]) -> tuple[str, dict[str, Any], dict[str, dict[str, Any]]]:
    page_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
        "name": name,
        "displayName": display,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
    }
    return name, page_json, {v["name"]: v for v in visuals}


def report_definition(dataset_id: str, report_name: str) -> dict[str, Any]:
    pages = [
        page(
            "ExecutiveOverview",
            "Executive Overview",
            [
                textbox("TitleExecutive", 20, 20, 1240, 60, "Leatt Executive Ecommerce Overview", 1),
                visual("MonthlyRevenue", "lineChart", 30, 100, 590, 250, {"Category": [("MonthlyTrend", "month")], "Y": [("MonthlyTrend", "net_revenue_zar")]}, 10),
                visual("CategoryRevenue", "barChart", 650, 100, 590, 250, {"Category": [("CategoryKPI", "category")], "Y": [("CategoryKPI", "net_revenue_zar")]}, 11),
                visual("CategoryMargin", "clusteredColumnChart", 30, 390, 590, 250, {"Category": [("CategoryKPI", "category")], "Y": [("CategoryKPI", "gross_margin_zar")]}, 12),
                visual("ExecutiveTable", "tableEx", 650, 390, 590, 250, {"Values": [("ExecutiveKPI", "metric"), ("ExecutiveKPI", "display_value")]}, 13),
            ],
        ),
        page(
            "MarketingSEO",
            "Marketing And SEO",
            [
                textbox("TitleMarketing", 20, 20, 1240, 60, "Marketing Efficiency, SEO And Channel ROI", 1),
                visual("ChannelRevenue", "barChart", 30, 100, 590, 250, {"Category": [("ChannelROI", "channel")], "Y": [("ChannelROI", "net_revenue_zar")]}, 20),
                visual("ChannelROAS", "clusteredColumnChart", 650, 100, 590, 250, {"Category": [("ChannelROI", "channel")], "Y": [("ChannelROI", "roas")]}, 21),
                visual("ChannelSpend", "barChart", 30, 390, 590, 250, {"Category": [("ChannelROI", "channel")], "Y": [("ChannelROI", "estimated_spend_zar")]}, 22),
                visual("ChannelReturn", "clusteredColumnChart", 650, 390, 590, 250, {"Category": [("ChannelROI", "channel")], "Y": [("ChannelROI", "return_amount_zar")]}, 23),
            ],
        ),
        page(
            "MLReturns",
            "ML Return Risk",
            [
                textbox("TitleML", 20, 20, 1240, 60, "ML Return Risk And Margin Leakage", 1),
                visual("RiskByBand", "barChart", 30, 100, 590, 250, {"Category": [("MLReturnRisk", "risk_band")], "Y": [("MLReturnRisk", "net_revenue_zar")]}, 30),
                visual("RiskReturnRate", "clusteredColumnChart", 650, 100, 590, 250, {"Category": [("MLReturnRisk", "risk_band")], "Y": [("MLReturnRisk", "actual_return_rate")]}, 31),
                visual("RiskCategory", "barChart", 30, 390, 590, 250, {"Category": [("MLReturnRisk", "category")], "Y": [("MLReturnRisk", "avg_risk")]}, 32),
                visual("RiskTable", "tableEx", 650, 390, 590, 250, {"Values": [("MLReturnRisk", "risk_band"), ("MLReturnRisk", "category"), ("MLReturnRisk", "avg_risk"), ("MLReturnRisk", "actual_return_rate")]}, 33),
            ],
        ),
        page(
            "GovernanceProof",
            "Fabric Governance Proof",
            [
                textbox("TitleGovernance", 20, 20, 1240, 60, "Fabric, Governance And Proof Controls", 1),
                visual("FabricProof", "tableEx", 30, 100, 590, 250, {"Values": [("FabricProof", "artifact"), ("FabricProof", "value")]}, 40),
                visual("MLMetrics", "tableEx", 650, 100, 590, 250, {"Values": [("MLMetrics", "metric"), ("MLMetrics", "value")]}, 41),
                visual("RowsByMonth", "clusteredColumnChart", 30, 390, 590, 250, {"Category": [("MonthlyTrend", "month")], "Y": [("MonthlyTrend", "quantity")]}, 42),
                visual("ReturnsByMonth", "lineChart", 650, 390, 590, 250, {"Category": [("MonthlyTrend", "month")], "Y": [("MonthlyTrend", "return_amount_zar")]}, 43),
            ],
        ),
    ]
    page_order = [p[0] for p in pages]
    parts: list[dict[str, str]] = []
    definition_pbir = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byConnection": {"connectionString": f"semanticmodelid={dataset_id}"}},
    }
    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.0.0/schema.json",
        "layoutOptimization": "None",
        "themeCollection": {"baseTheme": {"name": "Default", "reportVersionAtImport": "1.0.0", "type": "SharedResources"}},
        "settings": {
            "useStylableVisualContainerHeader": True,
            "defaultFilterActionIsDataFilter": True,
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "allowInlineExploration": True,
            "useEnhancedTooltips": True,
        },
    }
    version_json = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "4.0.0"}
    pages_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": page_order,
        "activePageName": page_order[0],
    }
    for path, obj in [
        ("definition.pbir", definition_pbir),
        ("definition/report.json", report_json),
        ("definition/version.json", version_json),
        ("definition/pages/pages.json", pages_json),
    ]:
        parts.append({"path": path, "payload": b64(obj), "payloadType": "InlineBase64"})
    for page_name, page_json, visuals in pages:
        parts.append({"path": f"definition/pages/{page_name}/page.json", "payload": b64(page_json), "payloadType": "InlineBase64"})
        for visual_name, visual_json in visuals.items():
            parts.append({"path": f"definition/pages/{page_name}/visuals/{visual_name}/visual.json", "payload": b64(visual_json), "payloadType": "InlineBase64"})
    return {"displayName": report_name, "description": "Leatt ecommerce BI/ML report created from PBIR definition and bound to the Fabric semantic model.", "definition": {"format": "PBIR", "parts": parts}}


def fabric_request(method: str, url: str, token: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, str], str]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=120) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers), body


def write_definition_files(payload: dict[str, Any], folder: Path) -> None:
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    for part in payload["definition"]["parts"]:
        p = folder / part["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(base64.b64decode(part["payload"]))
    (folder / "create-report-payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    proof = read_proof()
    token = az_token()
    report_name = f"Leatt BI ML Executive Report {datetime.now().strftime('%Y%m%d%H%M')}"
    payload = report_definition(proof["dataset_id"], report_name)
    report_folder = REPORT_ROOT / f"{report_name}.Report"
    write_definition_files(payload, report_folder)
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{proof['workspace_id']}/reports"
    status, headers, body = fabric_request("POST", url, token, payload)
    proof_out = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "workspace_id": proof["workspace_id"],
        "dataset_id": proof["dataset_id"],
        "report_name": report_name,
        "request_status": status,
        "response_headers": {k: v for k, v in headers.items() if k.lower() in {"location", "x-ms-operation-id", "retry-after"}},
        "response_body": json.loads(body) if body and body.strip().startswith("{") else body,
        "definition_folder": str(report_folder),
        "source": "Fabric Reports Create API with PBIR definition",
    }
    if status == 202 and headers.get("Location"):
        op_url = headers["Location"]
        for _ in range(20):
            time.sleep(int(headers.get("Retry-After", "5")) if headers.get("Retry-After") else 5)
            op_status, op_headers, op_body = fabric_request("GET", op_url, token)
            proof_out["operation_status_code"] = op_status
            proof_out["operation_body"] = json.loads(op_body) if op_body and op_body.strip().startswith("{") else op_body
            if op_status not in (200, 202) or ("status" in str(op_body).lower() and "running" not in str(op_body).lower()):
                break
    if status in (200, 201, 202):
        body_obj = proof_out.get("response_body", {})
        report_id = body_obj.get("id") if isinstance(body_obj, dict) else None
        if not report_id and isinstance(proof_out.get("operation_body"), dict):
            report_id = proof_out["operation_body"].get("id") or proof_out["operation_body"].get("objectId")
        if report_id:
            proof_out["report_id"] = report_id
            proof_out["report_url"] = f"https://app.powerbi.com/groups/{proof['workspace_id']}/reports/{report_id}/ReportSection"
    out_path = OUT / "fabric_powerbi_report_creation_proof.json"
    out_path.write_text(json.dumps(proof_out, indent=2), encoding="utf-8")
    if REPO.exists():
        (REPO / "src" / "powerbi" / "report_definitions").mkdir(parents=True, exist_ok=True)
        target = REPO / "src" / "powerbi" / "report_definitions" / report_folder.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(report_folder, target)
        (REPO / "artifacts" / "data_samples").mkdir(parents=True, exist_ok=True)
        shutil.copy2(out_path, REPO / "artifacts" / "data_samples" / out_path.name)
    print(json.dumps(proof_out, indent=2))
    if status not in (200, 201, 202):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
