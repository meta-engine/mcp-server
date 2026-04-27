#!/usr/bin/env python3
"""Generate a deterministic modular-monolith spec for the MetaEngine MCP benchmark.

Output: a JSON document describing modules with sub-modules, a shared kernel,
and top-level orchestrator services that span multiple modules. Same kind=
vocabulary as the DDD spec (aggregate / value_object / enum / service); what
changes is *organization* — asymmetric depth, shared types, cross-module refs.

Targets ~75 entities total to keep entity count comparable to the DDD spec.

Cross-module reference convention:
  Field / parameter / return entries that reference a type from a *different*
  module include a `module` field with that module's path. Same-module refs
  omit the field. Primitives (string, number, boolean, Date) have no `module`.
  The agent's prompt uses these annotations to build the right `templateRefs`
  placeholder + `typeIdentifier` mapping.
"""
import json, sys, argparse, os

# ─── Module catalog ──────────────────────────────────────────────────────────
# (module_name, path, aggregates, value_objects, enums, services)
MODULES = [
    ("shared",             "shared",
        [], ["Money", "Id", "Timestamp", "Result"], ["Currency"], []),

    ("catalog",            "catalog",
        ["Product"],
        ["Sku", "Category", "ProductVariant", "ProductDescription"],
        ["ProductState", "ProductCategoryKind"],
        ["ProductService", "InventoryService", "PricingEngine"]),

    ("customers",          "customers",
        ["Customer"],
        ["Email", "Address", "PaymentMethod", "Profile", "PhoneNumber"],
        ["CustomerStatus", "PaymentMethodKind"],
        ["CustomerService", "AddressService"]),

    ("orders",             "orders",
        ["Order"], ["OrderLine", "OrderTotal"], ["OrderStatus"],
        ["OrderService"]),

    ("orders.cart",        "orders/cart",
        ["Cart"], ["CartLine", "CartDiscount"], ["CartState"],
        ["CartService"]),

    ("orders.checkout",    "orders/checkout",
        [], ["CheckoutSession", "ShippingMethod", "Coupon"],
        ["CheckoutState"],
        ["CheckoutService", "DiscountService"]),

    ("orders.fulfillment", "orders/fulfillment",
        ["Shipment"], ["TrackingInfo", "DeliveryWindow", "ShipmentRoute"],
        ["ShipmentState", "Carrier"],
        ["FulfillmentService", "CarrierGateway"]),

    ("billing",            "billing",
        ["Invoice"], ["InvoiceLine", "Payment", "Refund", "TaxLine"],
        ["PaymentStatus", "RefundReason", "InvoiceStatus"],
        ["BillingService", "PaymentGateway", "RefundService"]),

    ("notifications",      "notifications",
        [], ["EmailTemplate", "NotificationContent"],
        ["NotificationKind", "DeliveryState"],
        ["NotificationService", "DeliveryDispatcher"]),
]

# ─── Shared-kernel value-object fields ───────────────────────────────────────
# These types live in `shared/` and are referenced by everyone.
SHARED_KERNEL_FIELDS = {
    "Money":     [{"name": "amount", "type": "number"},
                  {"name": "currency", "type": "Currency", "module": "shared"}],
    "Id":        [{"name": "value", "type": "string"}],
    "Timestamp": [{"name": "epochSeconds", "type": "number"},
                  {"name": "iso", "type": "string"}],
    "Result":    [{"name": "success", "type": "boolean"},
                  {"name": "errorMessage", "type": "string"}],
}

# ─── Aggregate-specific field overrides ──────────────────────────────────────
AGGREGATE_FIELDS = {
    "Product":  [{"name": "id",       "type": "Id",            "module": "shared"},
                 {"name": "name",     "type": "string"},
                 {"name": "price",    "type": "Money",         "module": "shared"},
                 {"name": "state",    "type": "ProductState"}],
    "Customer": [{"name": "id",        "type": "Id",            "module": "shared"},
                 {"name": "email",     "type": "Email"},
                 {"name": "status",    "type": "CustomerStatus"},
                 {"name": "createdAt", "type": "Timestamp",     "module": "shared"}],
    "Order":    [{"name": "id",         "type": "Id",         "module": "shared"},
                 {"name": "customerId", "type": "Id",         "module": "shared"},
                 {"name": "status",     "type": "OrderStatus"},
                 {"name": "total",      "type": "OrderTotal"}],
    "Cart":     [{"name": "id",         "type": "Id",       "module": "shared"},
                 {"name": "customerId", "type": "Id",       "module": "shared"},
                 {"name": "state",      "type": "CartState"}],
    "Shipment": [{"name": "id",       "type": "Id",            "module": "shared"},
                 {"name": "orderId",  "type": "Id",            "module": "shared"},
                 {"name": "state",    "type": "ShipmentState"},
                 {"name": "tracking", "type": "TrackingInfo"}],
    "Invoice":  [{"name": "id",          "type": "Id",            "module": "shared"},
                 {"name": "orderId",     "type": "Id",            "module": "shared"},
                 {"name": "status",      "type": "InvoiceStatus"},
                 {"name": "totalAmount", "type": "Money",         "module": "shared"}],
}

# ─── Value-object field overrides (within their own modules) ────────────────
LOCAL_VO_FIELDS = {
    # catalog
    "Sku":             [{"name": "value", "type": "string"}],
    "ProductVariant":  [{"name": "sku",         "type": "Sku"},
                        {"name": "price",       "type": "Money", "module": "shared"},
                        {"name": "stockLevel",  "type": "number"}],
    # customers
    "Email":           [{"name": "value", "type": "string"}],
    "PhoneNumber":     [{"name": "value", "type": "string"}],
    "Address":         [{"name": "street",     "type": "string"},
                        {"name": "city",       "type": "string"},
                        {"name": "country",    "type": "string"},
                        {"name": "postalCode", "type": "string"}],
    "PaymentMethod":   [{"name": "kind",     "type": "PaymentMethodKind"},
                        {"name": "lastFour", "type": "string"}],
    # orders (module-level)
    "OrderLine":       [{"name": "productId", "type": "Id",    "module": "shared"},
                        {"name": "quantity",  "type": "number"},
                        {"name": "unitPrice", "type": "Money", "module": "shared"}],
    "OrderTotal":      [{"name": "subtotal",   "type": "Money", "module": "shared"},
                        {"name": "tax",        "type": "Money", "module": "shared"},
                        {"name": "grandTotal", "type": "Money", "module": "shared"}],
    # orders/cart
    "CartLine":        [{"name": "productId", "type": "Id",    "module": "shared"},
                        {"name": "quantity",  "type": "number"}],
    "CartDiscount":    [{"name": "code",   "type": "string"},
                        {"name": "amount", "type": "Money", "module": "shared"}],
    # orders/checkout
    "CheckoutSession": [{"name": "cartId",            "type": "Id", "module": "shared"},
                        {"name": "customerId",        "type": "Id", "module": "shared"},
                        {"name": "shippingMethodId",  "type": "Id", "module": "shared"}],
    "ShippingMethod":  [{"name": "name", "type": "string"},
                        {"name": "cost", "type": "Money", "module": "shared"}],
    "Coupon":          [{"name": "code",     "type": "string"},
                        {"name": "discount", "type": "Money", "module": "shared"}],
    # orders/fulfillment
    "TrackingInfo":    [{"name": "carrier",        "type": "Carrier"},
                        {"name": "trackingNumber", "type": "string"}],
    "DeliveryWindow":  [{"name": "earliest", "type": "Timestamp", "module": "shared"},
                        {"name": "latest",   "type": "Timestamp", "module": "shared"}],
    # billing
    "InvoiceLine":     [{"name": "description", "type": "string"},
                        {"name": "amount",      "type": "Money", "module": "shared"}],
    "Payment":         [{"name": "amount", "type": "Money", "module": "shared"},
                        {"name": "status", "type": "PaymentStatus"}],
    "Refund":          [{"name": "amount", "type": "Money", "module": "shared"},
                        {"name": "reason", "type": "RefundReason"}],
    "TaxLine":         [{"name": "rate",   "type": "number"},
                        {"name": "amount", "type": "Money", "module": "shared"}],
    # notifications
    "EmailTemplate":   [{"name": "subject", "type": "string"},
                        {"name": "body",    "type": "string"}],
    "NotificationContent": [{"name": "kind",    "type": "NotificationKind"},
                            {"name": "payload", "type": "string"}],
}

ENUM_LABELS = {
    "Currency":            ["usd", "eur", "gbp", "jpy"],
    "ProductState":        ["draft", "active", "archived"],
    "ProductCategoryKind": ["physical", "digital", "service"],
    "CustomerStatus":      ["active", "suspended", "deleted"],
    "PaymentMethodKind":   ["credit_card", "debit_card", "bank_transfer", "wallet"],
    "OrderStatus":         ["draft", "placed", "paid", "shipped", "delivered", "cancelled"],
    "CartState":           ["active", "abandoned", "checked_out"],
    "CheckoutState":       ["pending", "ready", "confirmed", "failed"],
    "ShipmentState":       ["pending", "in_transit", "delivered", "lost"],
    "Carrier":             ["ups", "fedex", "dhl", "usps"],
    "PaymentStatus":       ["pending", "succeeded", "failed", "refunded"],
    "RefundReason":        ["customer_request", "defective", "duplicate"],
    "InvoiceStatus":       ["pending", "paid", "overdue", "void"],
    "NotificationKind":    ["email", "sms", "push", "webhook"],
    "DeliveryState":       ["queued", "sent", "delivered", "failed"],
}

# ─── Top-level orchestrators (span multiple modules) ─────────────────────────
ORCHESTRATORS = [
    {
        "name": "CheckoutOrchestrator",
        "methods": [
            {
                "name": "placeOrder",
                "params": [
                    {"name": "cartId",          "type": "Id",            "module": "shared"},
                    {"name": "customerId",      "type": "Id",            "module": "shared"},
                    {"name": "paymentMethodId", "type": "PaymentMethod", "module": "customers"},
                ],
                "returns": {"type": "Order", "module": "orders"},
            },
            {
                "name": "validateCart",
                "params": [{"name": "cart", "type": "Cart", "module": "orders/cart"}],
                "returns": {"type": "Result", "module": "shared"},
            },
            {
                "name": "computeTotal",
                "params": [{"name": "cart", "type": "Cart", "module": "orders/cart"}],
                "returns": {"type": "Money", "module": "shared"},
            },
        ],
    },
    {
        "name": "FulfillmentOrchestrator",
        "methods": [
            {
                "name": "shipOrder",
                "params": [{"name": "orderId", "type": "Id", "module": "shared"}],
                "returns": {"type": "Shipment", "module": "orders/fulfillment"},
            },
            {
                "name": "notifyCustomer",
                "params": [
                    {"name": "customer", "type": "Customer", "module": "customers"},
                    {"name": "shipment", "type": "Shipment", "module": "orders/fulfillment"},
                ],
                "returns": {"type": "Result", "module": "shared"},
            },
            {
                "name": "trackShipment",
                "params": [{"name": "shipmentId", "type": "Id", "module": "shared"}],
                "returns": {"type": "TrackingInfo", "module": "orders/fulfillment"},
            },
        ],
    },
]


# ─── Helpers ─────────────────────────────────────────────────────────────────

def snake_to_pascal(s: str) -> str:
    return "".join(p.capitalize() for p in s.split("_"))


def fields_for(name: str):
    if name in SHARED_KERNEL_FIELDS:
        return SHARED_KERNEL_FIELDS[name]
    if name in AGGREGATE_FIELDS:
        return AGGREGATE_FIELDS[name]
    if name in LOCAL_VO_FIELDS:
        return LOCAL_VO_FIELDS[name]
    # Generic fallback — references shared types so they aren't isolated.
    return [
        {"name": "id",          "type": "Id",        "module": "shared"},
        {"name": "createdAt",   "type": "Timestamp", "module": "shared"},
        {"name": "updatedAt",   "type": "Timestamp", "module": "shared"},
        {"name": "name",        "type": "string"},
        {"name": "description", "type": "string"},
    ]


def members_for_enum(en: str):
    labels = ENUM_LABELS.get(en, ["unknown"])
    return [{"name": snake_to_pascal(l), "value": i} for i, l in enumerate(labels)]


def methods_for_service(primary: str):
    """Default CRUD-ish method set referencing the module's primary type."""
    if not primary:
        return [{
            "name": "execute",
            "params":  [{"name": "input", "type": "string"}],
            "returns": {"type": "Result", "module": "shared"},
        }]
    return [
        {"name": "create",   "params": [{"name": "input", "type": f"Partial<{primary}>"}],
                             "returns": primary},
        {"name": "findById", "params": [{"name": "id", "type": "Id", "module": "shared"}],
                             "returns": f"{primary} | null"},
        {"name": "list",     "params": [{"name": "limit", "type": "number"}],
                             "returns": f"{primary}[]"},
        {"name": "delete",   "params": [{"name": "id", "type": "Id", "module": "shared"}],
                             "returns": "void"},
    ]


def primary_type(aggs, vos):
    if aggs:
        return aggs[0]
    if vos:
        return vos[0]
    return None


# ─── Build ───────────────────────────────────────────────────────────────────

def build():
    modules = []
    for (mname, path, aggs, vos, enums, svc_names) in MODULES:
        types = []
        for agg in aggs:
            types.append({"name": agg, "kind": "aggregate", "fields": fields_for(agg)})
        for vo in vos:
            types.append({"name": vo, "kind": "value_object", "fields": fields_for(vo)})
        for en in enums:
            types.append({
                "name":        en,
                "kind":        "enum",
                "members":     members_for_enum(en),
                "valueLabels": ENUM_LABELS.get(en, []),
            })
        primary = primary_type(aggs, vos)
        services = [{"name": s, "methods": methods_for_service(primary)} for s in svc_names]
        modules.append({
            "name":     mname,
            "path":     path,
            "types":    types,
            "services": services,
        })

    return {
        "shape":         "modular-monolith",
        "modules":       modules,
        "orchestrators": {
            "name":     "orchestrators",
            "path":     "orchestrators",
            "services": ORCHESTRATORS,
        },
    }


def count(spec):
    """Return entity counts for reporting."""
    n_aggs = n_vos = n_enums = n_svcs = 0
    for m in spec["modules"]:
        for t in m["types"]:
            if   t["kind"] == "aggregate":     n_aggs  += 1
            elif t["kind"] == "value_object":  n_vos   += 1
            elif t["kind"] == "enum":          n_enums += 1
        n_svcs += len(m["services"])
    n_svcs += len(spec["orchestrators"]["services"])
    return n_aggs, n_vos, n_enums, n_svcs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", help="Path for the generated spec JSON")
    args = ap.parse_args()

    spec = build()
    n_aggs, n_vos, n_enums, n_svcs = count(spec)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(spec, f, indent=2)

    print(f"Wrote {args.output}")
    print(f"  Shape:          modular-monolith")
    print(f"  Modules:        {len(spec['modules'])} ({sum(1 for m in spec['modules'] if '/' in m['path'])} sub-modules)")
    print(f"  Aggregates:     {n_aggs}")
    print(f"  Value objects:  {n_vos}")
    print(f"  Enums:          {n_enums}")
    print(f"  Services:       {n_svcs} ({len(spec['orchestrators']['services'])} are top-level orchestrators)")
    print(f"  Grand total:    {n_aggs + n_vos + n_enums + n_svcs}")


if __name__ == "__main__":
    main()
