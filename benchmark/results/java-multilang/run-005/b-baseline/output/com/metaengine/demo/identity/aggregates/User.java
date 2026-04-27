package com.metaengine.demo.identity.aggregates;

import java.time.Instant;

/** User aggregate root in the identity domain. */
public record User(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
