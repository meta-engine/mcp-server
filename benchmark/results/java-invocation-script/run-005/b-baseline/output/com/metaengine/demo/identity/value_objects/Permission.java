package com.metaengine.demo.identity.value_objects;

import java.time.Instant;

/** Permission value object. */
public record Permission(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
