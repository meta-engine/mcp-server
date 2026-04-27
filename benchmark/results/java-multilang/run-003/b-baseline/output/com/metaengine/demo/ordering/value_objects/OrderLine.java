package com.metaengine.demo.ordering.value_objects;

import java.time.Instant;

/** OrderLine value object. */
public record OrderLine(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
