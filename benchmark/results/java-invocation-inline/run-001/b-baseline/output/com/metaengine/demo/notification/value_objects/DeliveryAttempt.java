package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** Value object representing a single delivery attempt for a notification. */
public record DeliveryAttempt(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
