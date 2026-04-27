package com.metaengine.demo.ordering.aggregates;

import java.time.Instant;

/** Order aggregate root for the ordering domain. */
public record Order(
        String id,
        Instant createdAt,
        Instant updatedAt,
        String name,
        String description) {
}
