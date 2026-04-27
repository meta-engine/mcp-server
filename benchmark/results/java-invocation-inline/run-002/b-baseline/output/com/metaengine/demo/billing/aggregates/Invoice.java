package com.metaengine.demo.billing.aggregates;

import java.time.Instant;

/** Invoice aggregate root for the billing domain. */
public record Invoice(
        String id,
        Instant createdAt,
        Instant updatedAt,
        String name,
        String description) {
}
