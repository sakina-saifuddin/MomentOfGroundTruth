"""Plain-language descriptions and pictures for the eight PHMSA cause categories."""

from __future__ import annotations

from pathlib import Path

ASSETS = Path(__file__).parent / "assets"

# label order matches data/processed/label_map.json
CAUSES: dict[str, dict[str, str | None]] = {
    "EQUIPMENT FAILURE": {
        "title": "Equipment failure",
        "blurb": "A component other than the pipe wall gives out: a valve, seal, coupling, regulator, compressor part or control device.",
        "image": "equipment-failure.jpg",
        "caption": "A compressor station, where much of the moving and pressure-control equipment sits.",
        "credit": "Steven Baltakatei Sandoval, CC BY-SA 4.0 (Wikimedia Commons)",
    },
    "CORROSION FAILURE": {
        "title": "Corrosion failure",
        "blurb": "The steel wall wears away from the inside or outside, leaving pits or thin spots that eventually leak.",
        "image": "corrosion-failure.jpg",
        "caption": "A corrosion pit in the wall of a buried gas pipeline.",
        "credit": "Cafe Nervosa / Derek Mawhinney, CC BY-SA 3.0 (Wikimedia Commons)",
    },
    "MATERIAL FAILURE OF PIPE OR WELD": {
        "title": "Material failure of pipe or weld",
        "blurb": "The pipe steel or a weld has a flaw or fatigue crack that grows under pressure until it opens.",
        "image": "material-failure.jpg",
        "caption": "A girth weld joining two lengths of gas pipe. This is a sound weld shown for illustration; failures start at flaws in welds like this one.",
        "credit": "Hamid Soufi, CC BY-SA 3.0 (Wikimedia Commons)",
    },
    "EXCAVATION DAMAGE": {
        "title": "Excavation damage",
        "blurb": "Digging equipment strikes the pipe: a backhoe, auger or trencher working near a line that was not marked or located.",
        "image": "excavation-damage.jpg",
        "caption": "Heavy machinery working in a pipeline trench in England (illustrative, not a U.S. incident).",
        "credit": "Peter Facey, CC BY-SA 2.0 (Wikimedia Commons)",
    },
    "NATURAL FORCE DAMAGE": {
        "title": "Natural force damage",
        "blurb": "Floods, landslides, washouts, earth movement, lightning or storms strain or expose the pipe.",
        "image": "natural-force-damage.jpg",
        "caption": "A gas pipeline crossing a river in England, one of the places where water and ground movement matter (illustrative).",
        "credit": "Bob1960evens, CC BY-SA 4.0 (Wikimedia Commons)",
    },
    "OTHER OUTSIDE FORCE DAMAGE": {
        "title": "Other outside force damage",
        "blurb": "Damage from outside the operator's work that is not digging or weather: vehicle impact, vandalism, gunfire, fire or explosion nearby.",
        "image": None,
        "caption": "No photograph yet for this cause.",
        "credit": None,
    },
    "OTHER INCIDENT CAUSE": {
        "title": "Other incident cause",
        "blurb": "A cause that fits none of the other categories, or one the report did not pin down.",
        "image": "other-incident-cause.jpg",
        "caption": "Aerial view after a natural gas pipeline rupture and fire, from an NTSB investigation (illustrative of an incident, not of this category).",
        "credit": "NTSB, public domain (Wikimedia Commons)",
    },
    "INCORRECT OPERATION": {
        "title": "Incorrect operation",
        "blurb": "A procedure goes wrong: a valve left in the wrong position, a safety device bypassed, a pressure limit exceeded.",
        "image": "incorrect-operation.jpg",
        "caption": "A fenced gas pipeline valve station in Scotland, equipment that operators open, close and monitor (illustrative).",
        "credit": "Derek Gray, CC BY-SA 2.0 (Wikimedia Commons)",
    },
}

LABELS = list(CAUSES)
