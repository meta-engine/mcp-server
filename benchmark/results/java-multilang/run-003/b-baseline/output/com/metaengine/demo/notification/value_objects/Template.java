package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** Template value object. */
public record Template(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
