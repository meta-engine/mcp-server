package com.metaengine.demo.catalog.value_objects;

import java.time.Instant;

/** Value object representing a localized product description. */
public record ProductDescription(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
