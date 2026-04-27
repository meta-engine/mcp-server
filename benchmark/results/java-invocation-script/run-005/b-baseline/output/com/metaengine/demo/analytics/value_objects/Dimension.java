package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** Dimension value object. */
public record Dimension(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
