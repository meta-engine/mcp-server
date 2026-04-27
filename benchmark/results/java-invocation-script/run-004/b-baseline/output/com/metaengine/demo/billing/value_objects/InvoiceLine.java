package com.metaengine.demo.billing.value_objects;

import java.time.Instant;

/** InvoiceLine value object in the billing domain. */
public record InvoiceLine(String id, Instant createdAt, Instant updatedAt, String name, String description) {}
