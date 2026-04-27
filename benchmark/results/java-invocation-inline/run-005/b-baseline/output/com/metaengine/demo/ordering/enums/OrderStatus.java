package com.metaengine.demo.ordering.enums;

/** Lifecycle status of an Order. */
public enum OrderStatus {
    Draft(0),
    Placed(1),
    Paid(2),
    Shipped(3),
    Delivered(4),
    Cancelled(5);

    private final int value;

    OrderStatus(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
