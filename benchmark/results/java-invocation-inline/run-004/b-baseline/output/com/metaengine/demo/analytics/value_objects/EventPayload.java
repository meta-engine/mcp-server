package com.metaengine.demo.analytics.value_objects;

import java.time.Instant;

/** EventPayload value object. */
public record EventPayload(String id, Instant createdAt, Instant updatedAt, String name, String description) {
}
