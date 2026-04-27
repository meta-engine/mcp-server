package com.metaengine.demo.inventory.value_objects;

/** Quantity value object for the inventory domain. */
public record Quantity(
        double amount,
        String unit) {
}
