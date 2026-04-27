package com.metaengine.demo.notification.value_objects;

import java.time.Instant;

/** DeliveryAttempt value object in the notification domain. */
public record DeliveryAttempt(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
