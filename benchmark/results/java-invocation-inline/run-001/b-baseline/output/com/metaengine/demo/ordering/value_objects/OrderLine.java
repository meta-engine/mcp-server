package com.metaengine.demo.ordering.value_objects;

import java.time.Instant;

/** Value object representing a line item on an order. */
public record OrderLine(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
