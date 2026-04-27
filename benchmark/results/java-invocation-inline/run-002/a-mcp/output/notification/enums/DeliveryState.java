package com.metaengine.demo.notification.enums;

// DeliveryState enum.

public enum DeliveryState {
    QUEUED(0),
    SENT(1),
    DELIVERED(2),
    FAILED(3);

    private final int value;

    DeliveryState(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public static DeliveryState fromValue(int value) {
        for (DeliveryState item : DeliveryState.values()) {
            if (item.value == value) {
                return item;
            }
        }
        throw new IllegalArgumentException("Unknown value: " + value);
    }
}
