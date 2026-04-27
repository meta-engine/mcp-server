package com.metaengine.demo.catalog.value_objects;

import java.time.Instant;

/** Value object representing a product category. */
public record Category(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
