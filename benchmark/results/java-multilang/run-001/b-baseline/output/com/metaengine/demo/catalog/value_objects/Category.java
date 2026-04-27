package com.metaengine.demo.catalog.value_objects;

import java.time.Instant;

/** Category value object for the catalog domain. */
public record Category(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
