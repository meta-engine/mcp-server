package com.metaengine.demo.notification.enums;

/** Lifecycle state of a notification delivery. */
public enum DeliveryState {
    Queued(0),
    Sent(1),
    Delivered(2),
    Failed(3);

    private final int value;

    DeliveryState(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
