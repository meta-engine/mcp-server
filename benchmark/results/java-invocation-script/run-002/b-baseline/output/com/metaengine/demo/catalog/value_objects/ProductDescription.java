package com.metaengine.demo.catalog.value_objects;

import java.time.Instant;

/** ProductDescription value object. */
public record ProductDescription(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
