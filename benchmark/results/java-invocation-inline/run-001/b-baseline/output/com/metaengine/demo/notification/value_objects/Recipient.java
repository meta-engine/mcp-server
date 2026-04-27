package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** Value object representing the recipient of a notification. */
public record Recipient(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
