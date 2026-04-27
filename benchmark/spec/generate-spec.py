#!/usr/bin/env python3
"""Generate a deterministic synthetic DDD spec for the MetaEngine MCP benchmark.

Output: a JSON document describing ~85 types + services across 8 DDD domains.
Both benchmark variants produce TypeScript code from the same spec.

Enum representation note:
  MetaEngine MCP's `generate_code` API requires enum member values to be Int32 —
  string-valued enum members are not supported (filed as triage). To keep the
  benchmark apples-to-apples we emit `members[{name, value}]` with numeric values.
  The original semantic strings are preserved in `valueLabels` for reference but
  are not consumed by the prompts.
"""
import json, sys, argparse, os

# Each tuple: (domain, aggregate, [value_objects], [services], [enums])
DOMAINS = [
    ("ordering",     "Order",        ["OrderLine", "ShippingAddress", "BillingAddress", "OrderTotal"],          ["OrderService", "OrderRepository", "OrderValidator"],                  ["OrderStatus"]),
    ("catalog",      "Product",      ["Sku", "Price", "ProductDescription", "Category"],                        ["ProductService", "ProductRepository", "PricingEngine"],                ["ProductState"]),
    ("billing",      "Invoice",      ["InvoiceLine", "TaxLine", "Discount", "PaymentTerms"],                    ["InvoiceService", "InvoiceRepository", "TaxCalculator"],                ["InvoiceStatus"]),
    ("shipping",     "Shipment",     ["TrackingNumber", "DeliveryWindow", "ShipmentRoute"],                      ["ShipmentService", "ShipmentRepository", "CarrierGateway"],             ["Carrier", "ShipmentState"]),
    ("identity",     "User",         ["Email", "PasswordHash", "Profile", "Permission"],                         ["UserService", "UserRepository", "AuthService", "TokenService"],         ["Role"]),
    ("inventory",    "StockItem",    ["WarehouseLocation", "Quantity", "Reservation"],                           ["StockService", "StockRepository", "ReservationService"],                ["StockState"]),
    ("notification", "Notification", ["Template", "Recipient", "DeliveryAttempt"],                               ["NotificationService", "NotificationRepository", "DeliveryDispatcher"],  ["Channel", "DeliveryState"]),
    ("analytics",    "Event",        ["EventPayload", "Metric", "Dimension"],                                    ["EventService", "EventRepository", "MetricsAggregator"],                 ["EventType"]),
]

VALUE_OBJECT_FIELDS = {
    "ShippingAddress": [{"name": "street", "type": "string"}, {"name": "city", "type": "string"}, {"name": "country", "type": "string"}, {"name": "postalCode", "type": "string"}],
    "BillingAddress":  [{"name": "street", "type": "string"}, {"name": "city", "type": "string"}, {"name": "country", "type": "string"}, {"name": "postalCode", "type": "string"}],
    "Email":           [{"name": "value", "type": "string"}],
    "PasswordHash":    [{"name": "value", "type": "string"}],
    "TrackingNumber":  [{"name": "value", "type": "string"}],
    "Sku":             [{"name": "value", "type": "string"}],
    "Price":           [{"name": "amount", "type": "number"}, {"name": "currency", "type": "string"}],
    "OrderTotal":      [{"name": "amount", "type": "number"}, {"name": "currency", "type": "string"}],
    "Quantity":        [{"name": "amount", "type": "number"}, {"name": "unit", "type": "string"}],
}

# Member labels (semantic) — numeric values are derived by enumerate().
ENUM_LABELS = {
    "OrderStatus":    ["draft", "placed", "paid", "shipped", "delivered", "cancelled"],
    "InvoiceStatus":  ["pending", "paid", "overdue", "void"],
    "Carrier":        ["ups", "fedex", "dhl", "usps"],
    "ShipmentState":  ["pending", "in_transit", "delivered", "lost"],
    "Role":           ["admin", "user", "service"],
    "StockState":     ["in_stock", "reserved", "depleted"],
    "Channel":        ["email", "sms", "push", "webhook"],
    "DeliveryState":  ["queued", "sent", "delivered", "failed"],
    "EventType":      ["click", "view", "purchase", "signup"],
    "ProductState":   ["draft", "active", "archived"],
}


def snake_to_pascal(s: str) -> str:
    return "".join(part.capitalize() for part in s.split("_"))


def fields_for(name: str):
    if name in VALUE_OBJECT_FIELDS:
        return VALUE_OBJECT_FIELDS[name]
    return [
        {"name": "id", "type": "string"},
        {"name": "createdAt", "type": "Date"},
        {"name": "updatedAt", "type": "Date"},
        {"name": "name", "type": "string"},
        {"name": "description", "type": "string"},
    ]


def members_for_enum(en: str):
    """Numeric-valued enum members. Values are 0..N indices.

    Names are PascalCase derivations of the original semantic labels. Both
    benchmark variants must emit exactly these (Name, value) pairs so the
    comparison stays apples-to-apples.
    """
    labels = ENUM_LABELS.get(en, ["unknown"])
    return [{"name": snake_to_pascal(l), "value": i} for i, l in enumerate(labels)]


def methods_for(aggregate: str):
    return [
        {"name": "create",   "params": [{"name": "input", "type": f"Partial<{aggregate}>"}], "returns": aggregate},
        {"name": "findById", "params": [{"name": "id", "type": "string"}],                  "returns": f"{aggregate} | null"},
        {"name": "list",     "params": [{"name": "limit", "type": "number"}],                "returns": f"{aggregate}[]"},
        {"name": "delete",   "params": [{"name": "id", "type": "string"}],                  "returns": "void"},
    ]


def build():
    domains = []
    for (dname, agg, vobjects, services, enums) in DOMAINS:
        types = [{"name": agg, "kind": "aggregate", "fields": fields_for(agg)}]
        for vo in vobjects:
            types.append({"name": vo, "kind": "value_object", "fields": fields_for(vo)})
        for en in enums:
            types.append({
                "name": en,
                "kind": "enum",
                "members": members_for_enum(en),
                "valueLabels": ENUM_LABELS.get(en, []),  # informational only
            })
        svcs = [{"name": s, "methods": methods_for(agg)} for s in services]
        domains.append({"name": dname, "types": types, "services": svcs})
    return {"domains": domains}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", help="Path for the generated spec JSON")
    args = ap.parse_args()

    spec = build()
    n_aggs    = sum(1 for d in spec["domains"] for t in d["types"] if t["kind"] == "aggregate")
    n_vos     = sum(1 for d in spec["domains"] for t in d["types"] if t["kind"] == "value_object")
    n_enums   = sum(1 for d in spec["domains"] for t in d["types"] if t["kind"] == "enum")
    n_svcs    = sum(len(d["services"]) for d in spec["domains"])

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"Wrote {args.output}")
    print(f"  Domains:        {len(spec['domains'])}")
    print(f"  Aggregates:     {n_aggs}")
    print(f"  Value objects:  {n_vos}")
    print(f"  Enums:          {n_enums} (numeric members; engine doesn't accept string values)")
    print(f"  Services:       {n_svcs}")
    print(f"  Grand total:    {n_aggs + n_vos + n_enums + n_svcs}")


if __name__ == "__main__":
    main()
