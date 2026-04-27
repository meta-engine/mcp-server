package com.metaengine.demo.catalog.value_objects;

import java.time.Instant;

/** ProductDescription value object in the catalog domain. */
public record ProductDescription(String id, Instant createdAt, Instant updatedAt, String name, String description) {
}
