package com.metaengine.demo.ordering.value_objects;

/** OrderTotal value object for the ordering domain. */
public record OrderTotal(
        double amount,
        String currency) {
}
