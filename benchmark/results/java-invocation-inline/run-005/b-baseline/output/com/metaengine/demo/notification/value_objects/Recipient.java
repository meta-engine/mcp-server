package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** Recipient value object — addressed party for a notification. */
public record Recipient(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {}
