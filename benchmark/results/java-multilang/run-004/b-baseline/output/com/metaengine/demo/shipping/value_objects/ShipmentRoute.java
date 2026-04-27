package com.metaengine.demo.shipping.value_objects;

import java.time.Instant;

/** ShipmentRoute value object. */
public record ShipmentRoute(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {
}
