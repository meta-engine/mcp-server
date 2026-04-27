package com.metaengine.demo.analytics.aggregates;

import java.time.Instant;

/** Event aggregate root in the analytics domain. */
public record Event(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {
}
