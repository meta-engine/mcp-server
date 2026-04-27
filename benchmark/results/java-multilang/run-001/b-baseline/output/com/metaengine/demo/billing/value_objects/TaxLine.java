package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** TaxLine value object for the billing domain. */
public record TaxLine(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
