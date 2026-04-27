package com.metaengine.demo.shipping.value_objects;

import java.time.Instant;

/** DeliveryWindow value object. */
public record DeliveryWindow(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
