package com.metaengine.demo.notification.aggregates;

import java.time.Instant;

/** Notification aggregate root for the notification domain. */
public record Notification(
        String id,
        Instant createdAt,
        Instant updatedAt,
        String name,
        String description) {
}
