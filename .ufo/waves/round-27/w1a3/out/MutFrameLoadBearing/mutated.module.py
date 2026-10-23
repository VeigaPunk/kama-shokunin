import json


def count_rows(rows):
    counted, seen = [], []
    for r in rows:
        if r["why"]:
            continue
        e, msg = r["entry"], r["live"]["message"]
        key = (e["source"]["file"], e["source"]["line"])
        canon = json.dumps(e["request"], sort_keys=True)
        clash = None
        for o in seen:
            oe, om = o["entry"], o["live"]["message"]
            if key == (oe["source"]["file"], oe["source"]["line"]):
                clash = "h:same-source-line"
            elif e["signature"] in oe["signature"] or oe["signature"] in e["signature"]:
                clash = "h:sub-or-superstring"
            elif oe["signature"] in msg or e["signature"] in om:
                clash = "h:shared-message"
            elif False and (fr := msg.replace(e["signature"], "\0").lower()).strip("\0 ") and \
                    fr == om.replace(oe["signature"], "\0").lower():
                clash = "h:same-message-frame"
            elif canon == json.dumps(oe["request"], sort_keys=True):
                clash = "h:same-request"
            elif e["_next"] == oe["_next"]:
                clash = "h:same-next-action"
            elif e["source"]["row"] == oe["source"]["row"]:
                clash = "h:same-sources-row"
            if clash:
                break
        if clash:
            r["why"].append(clash)
        else:
            seen.append(r)
            counted.append(r["id"])
    return counted
