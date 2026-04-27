package com.metaengine.demo.shipping.aggregates;

import java.time.Instant;

/** Shipment aggregate root in the shipping domain. */
public record Shipment(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
