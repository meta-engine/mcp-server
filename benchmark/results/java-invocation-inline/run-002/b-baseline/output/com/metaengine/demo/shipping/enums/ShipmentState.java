package com.metaengine.demo.shipping.enums;

/** ShipmentState enum for the shipping domain. */
public enum ShipmentState {
    PENDING(0),
    IN_TRANSIT(1),
    DELIVERED(2),
    LOST(3);

    private final int value;

    ShipmentState(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
