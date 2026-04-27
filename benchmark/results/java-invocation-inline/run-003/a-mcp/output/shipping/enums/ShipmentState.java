package com.metaengine.demo.shipping.enums;

// ShipmentState enum.

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

    public static ShipmentState fromValue(int value) {
        for (ShipmentState item : ShipmentState.values()) {
            if (item.value == value) {
                return item;
            }
        }
        throw new IllegalArgumentException("Unknown value: " + value);
    }
}
