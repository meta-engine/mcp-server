package com.metaengine.demo.catalog.aggregates;

import java.time.Instant;

/** Product aggregate root for the catalog domain. */
public record Product(
        String id,
        Instant createdAt,
        Instant updatedAt,
        String name,
        String description) {
}
