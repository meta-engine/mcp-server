package com.metaengine.demo.inventory.aggregates;

import java.time.Instant;

/** StockItem aggregate root in the inventory domain. */
public record StockItem(
    String id,
    Instant createdAt,
    Instant updatedAt,
    String name,
    String description
) {
}
