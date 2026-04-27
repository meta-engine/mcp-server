package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** Metric value object. */
public record Metric(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {
}
