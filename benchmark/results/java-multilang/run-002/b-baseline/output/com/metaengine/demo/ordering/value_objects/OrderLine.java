package com.metaengine.demo.ordering.value_objects;

import java.time.Instant;

/** OrderLine value object in the ordering domain. */
public record OrderLine(String id, Instant createdAt, Instant updatedAt, String name, String description) {
}
