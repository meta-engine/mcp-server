package com.metaengine.demo.shipping.value_objects;

import java.time.Instant;

/** Value object describing a target delivery window. */
public record DeliveryWindow(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
