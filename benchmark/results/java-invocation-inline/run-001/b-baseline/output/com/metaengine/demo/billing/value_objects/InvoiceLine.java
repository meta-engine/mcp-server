package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** Value object representing a line item on an invoice. */
public record InvoiceLine(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
