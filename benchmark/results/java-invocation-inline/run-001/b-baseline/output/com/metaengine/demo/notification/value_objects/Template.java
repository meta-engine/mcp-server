package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** Value object representing a notification template. */
public record Template(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
