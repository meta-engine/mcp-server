package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** Discount value object. */
public record Discount(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
