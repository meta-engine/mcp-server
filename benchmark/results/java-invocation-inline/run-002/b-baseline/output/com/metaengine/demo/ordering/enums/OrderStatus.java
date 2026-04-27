package com.metaengine.demo.ordering.enums;

/** OrderStatus enum for the ordering domain. */
public enum OrderStatus {
    DRAFT(0),
    PLACED(1),
    PAID(2),
    SHIPPED(3),
    DELIVERED(4),
    CANCELLED(5);

    private final int value;

    OrderStatus(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
