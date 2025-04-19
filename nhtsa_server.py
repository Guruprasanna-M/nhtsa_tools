from mcp.server.fastmcp import FastMCP
import requests, re

mcp = FastMCP("nhtsa_tools")

VPIC      = "https://vpic.nhtsa.dot.gov/api/vehicles"
RECALLS   = "https://api.nhtsa.gov/recalls/recallsByVehicle"
SAFETY    = "https://api.nhtsa.gov/SafetyRatings"
COMPLAINT = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
TIMEOUT   = 15

def _decode_vin(vin):
    url = f"{VPIC}/DecodeVinValuesExtended/{vin}?format=json"
    r   = requests.get(url, timeout=TIMEOUT).json()["Results"][0]
    return r["Make"], r["Model"], r["ModelYear"]

def _get(url):
    return requests.get(url, timeout=TIMEOUT).json()

@mcp.tool()
def ask_nhtsa(question: str) -> dict:
    """Simple natural‑language router."""
    vin = re.search(r"\b[A-HJ-NPR-Z0-9]{17}\b", question.upper())
    if vin and "complaint" in question.lower():
        make, model, year = _decode_vin(vin.group())
        return _get(f"{COMPLAINT}?make={make}&model={model}&modelYear={year}")
    if vin and "recall" in question.lower():
        make, model, year = _decode_vin(vin.group())
        return _get(f"{RECALLS}?make={make}&model={model}&modelYear={year}")
    ymm = re.search(r"(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\-]+)", question)
    if ymm and "rating" in question.lower():
        y, mk, md = ymm.groups()
        return _get(f"{SAFETY}/modelyear/{y}/make/{mk}/model/{md}?format=json")
    return {"hint": "Ask about recalls, complaints, or ratings and include a VIN or year‑make‑model."}

if __name__ == "__main__":
    print("🚀  NHTSA server ready on http://127.0.0.1:3333")
    mcp.run()
